import logging
import os
import sys
import json
from dataclasses import dataclass, field
from typing import Optional, List
from sklearn.metrics import f1_score
from copy import deepcopy

import numpy as np

from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer, EvalPrediction
from transformers import (
    HfArgumentParser,
    Trainer,
    TrainingArguments,
    set_seed,
)

from vitaminc.processing.multitask_sent_pair_cls import (
    VitCFactVerificationProcessor,
    VitCDataTrainingArguments,
    VitCDataset,
    )


logger = logging.getLogger(__name__)


@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """
    model_name_or_path: str = field(
        metadata={"help": "Path to pretrained model or model identifier from huggingface.co/models"}
    )
    config_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained config name or path if not the same as model_name"}
    )
    tokenizer_name: Optional[str] = field(
        default=None, metadata={"help": "Pretrained tokenizer name or path if not the same as model_name"}
    )
    cache_dir: Optional[str] = field(
        default=None, metadata={"help": "Where do you want to store the pretrained models downloaded from s3"}
    )


@dataclass
class VitCTrainingArgs(TrainingArguments):
    eval_all_checkpoints: bool = field(
        default=False, metadata={"help": "Run evaluation on all checkpoints."}
    )
    do_test: bool = field(
        default=False, metadata={"help": "Run evaluation on test set (needs labels)."}
    )
    test_on_best_ckpt: bool = field(
        default=False, metadata={"help": "Load best ckpt for testing (after running with eval_all_checkpoints)."}
    )


def main():
    parser = HfArgumentParser((ModelArguments, VitCDataTrainingArguments, VitCTrainingArgs))

    if len(sys.argv) == 2 and sys.argv[1].endswith(".json"):
        # If we pass only one argument to the script and it's the path to a json file,
        # let's parse it to get our arguments.
        model_args, data_args, training_args = parser.parse_json_file(json_file=os.path.abspath(sys.argv[1]))
    else:
        model_args, data_args, training_args = parser.parse_args_into_dataclasses()

    if (
        os.path.exists(training_args.output_dir)
        and os.listdir(training_args.output_dir)
        and training_args.do_train
        and not training_args.overwrite_output_dir
    ):
        raise ValueError(
            f"Output directory ({training_args.output_dir}) already exists and is not empty. Use --overwrite_output_dir to overcome."
        )

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO if training_args.local_rank in [-1, 0] else logging.WARN,
    )

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S")
    os.makedirs(training_args.output_dir, exist_ok=True)
    fh = logging.FileHandler(os.path.join(training_args.output_dir, 'log.txt'))
    logging.getLogger("transformers").setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logging.getLogger("transformers").addHandler(fh)
    logging.root.addHandler(fh)

    logger.warning(
        "Process rank: %s, device: %s, n_gpu: %s, distributed training: %s, 16-bits training: %s",
        training_args.local_rank,
        training_args.device,
        training_args.n_gpu,
        bool(training_args.local_rank != -1),
        training_args.fp16,
    )
    logger.info("Training/evaluation parameters %s", training_args)

    # Set seed
    set_seed(training_args.seed)

    num_labels = len(VitCFactVerificationProcessor().get_labels())

    config = AutoConfig.from_pretrained(
        model_args.config_name if model_args.config_name else model_args.model_name_or_path,
        num_labels=num_labels,
        finetuning_task=data_args.tasks_names,
        cache_dir=model_args.cache_dir,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_args.model_name_or_path,
        from_tf=bool(".ckpt" in model_args.model_name_or_path),
        config=config,
        cache_dir=model_args.cache_dir,
    )

    # Get datasets
    train_dataset = (
        VitCDataset(data_args, tokenizer=tokenizer, cache_dir=model_args.cache_dir, file_path=data_args.train_file) if training_args.do_train else None
    )
    eval_dataset = (
        VitCDataset(data_args, tokenizer=tokenizer, mode="dev", cache_dir=model_args.cache_dir, file_path=data_args.validation_file)
        if training_args.do_eval
        else None
    )

    def compute_metrics_fn(p: EvalPrediction):

        with open('evaluationFile.json', "w") as outfile:
            data = {
                "label_ids": p.label_ids.tolist(),
                "prediction": np.argmax(p.predictions, axis=1).tolist()
            }
            json.dump(data, outfile)

        preds = np.argmax(p.predictions, axis=1)
        acc = (preds == p.label_ids).mean()
        f1 = f1_score(y_true=p.label_ids, y_pred=preds, average="macro", labels=np.unique(p.label_ids))
        return {
            "acc": acc,
            "macro_f1": f1,
        }

    # Initialize Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics_fn
    )

    # Training
    if training_args.do_train:
        trainer.train(
            model_path=model_args.model_name_or_path if os.path.isdir(model_args.model_name_or_path) else None
        )
        trainer.save_model()
        if trainer.is_world_process_zero():
            tokenizer.save_pretrained(training_args.output_dir)

    # Evaluation
    eval_results = {}
    output_best_ckpt_file = os.path.join(
        training_args.output_dir, "eval_best_ckpt.txt"
    )
    if training_args.do_eval:
        logger.info("*** Evaluate ***")

        tasks_str = "-".join(eval_dataset.args.tasks_names)
        output_eval_file = os.path.join(
            training_args.output_dir, f"eval_results_{tasks_str}.txt"
        )
        eval_result = trainer.evaluate(eval_dataset=eval_dataset)

        if trainer.is_world_process_zero():
            with open(output_eval_file, "w") as writer:
                logger.info("***** Eval results {} *****".format(tasks_str))
                for key, value in eval_result.items():
                    logger.info("  %s = %s", key, value)
                    writer.write("%s = %s\n" % (key, value))

        eval_results.update(eval_result)

        if training_args.eval_all_checkpoints:
            checkpoints = trainer._sorted_checkpoints()
            best_ckpt = ''
            highest_acc = 0
            for ckpt in checkpoints:
                model = AutoModelForSequenceClassification.from_pretrained(ckpt)
                trainer = Trainer(
                    model=model,
                    args=training_args,
                    eval_dataset=eval_dataset,
                    compute_metrics=compute_metrics_fn
                )
                eval_result = trainer.evaluate(eval_dataset=eval_dataset)
                if trainer.is_world_process_zero():
                    with open(output_eval_file, "a") as writer:
                        logger.info("***** Eval results {}: {} *****".format(tasks_str, ckpt))
                        for key, value in eval_result.items():
                            logger.info("  %s = %s", key, value)
                            writer.write("%s: %s = %s\n" % (ckpt, key, value))
                            if 'acc' in key and value > highest_acc:
                                highest_acc = value
                                best_ckpt = ckpt

            with open(output_eval_file, "a") as writer:
                logger.info("***** Best eval accuracy: {}, '{}' *****".format(highest_acc, best_ckpt))
                writer.write("best acc: %s ('%s')\n" % (highest_acc, best_ckpt))
            with open(output_best_ckpt_file, "w") as writer:
                writer.write("%s" % best_ckpt)

            model = AutoModelForSequenceClassification.from_pretrained(best_ckpt)
            trainer = Trainer(
                model=model,
                args=training_args,
                eval_dataset=eval_dataset,
                compute_metrics=compute_metrics_fn
            )

    if training_args.do_test or training_args.do_predict:
        if training_args.test_on_best_ckpt:
            with open(output_best_ckpt_file, "r") as reader:
                best_ckpt = reader.readlines()[0].strip()
                logger.info("Loading best model from %s", best_ckpt)
                model = AutoModelForSequenceClassification.from_pretrained(best_ckpt)
        test_args = deepcopy(data_args)
        test_args.dataset_size = None
        test_args.tasks_ratios = [1.]
        if data_args.test_file is not None:
            data_args.test_tasks = ['from_file']
        for task_name in data_args.test_tasks:
            test_args = deepcopy(test_args)
            test_args.tasks_names = [task_name]
            test_dataset = VitCDataset(
                                test_args,
                                tokenizer=tokenizer,
                                mode="test",
                                cache_dir=model_args.cache_dir,
                                file_path=data_args.test_file,
            )
            trainer = Trainer(
                model=model,
                args=training_args,
                eval_dataset=test_dataset,
                compute_metrics=compute_metrics_fn
            )
            if training_args.do_predict:
                logger.info("Predicting for %s", task_name)
                predictions = trainer.predict(test_dataset=test_dataset).predictions
                pred_labels = np.argmax(predictions, axis=1)
            if training_args.do_test:
                # TODO: Use predictions from do_predict for evaluation instead of running twice.
                logger.info("Evaluating on %s", test_dataset.args.tasks_names[0])
                eval_result = trainer.evaluate(eval_dataset=test_dataset)

            output_eval_file = os.path.join(
                training_args.output_dir, f"test_results_{task_name}.txt"
            )
            output_pred_file = os.path.join(
                training_args.output_dir, f"test_preds_{task_name}.txt"
            )
            output_scores_file = os.path.join(
                training_args.output_dir, f"test_scores_{task_name}.txt"
            )
            if trainer.is_world_process_zero():
                if training_args.do_test:
                    with open(output_eval_file, "w") as writer:
                        logger.info("***** Test results {} *****".format(test_dataset.args.tasks_names[0]))
                        for key, value in eval_result.items():
                            logger.info("  %s = %s", key, value)
                            writer.write("%s = %s\n" % (key, value))

                if training_args.do_predict:
                    if data_args.test_file is not None:
                        examples = test_dataset.processor.get_examples_from_file(data_args.test_file, "test")
                    task_data_dir = os.path.join(data_args.data_dir, test_dataset.args.tasks_names[0])
                    examples = test_dataset.processor.get_test_examples(task_data_dir)
                    with open(output_pred_file, "w") as writer:
                        writer.write("index\t|\tclaim\t|\tevidence\t|\tprediction\n")
                        for index, item in enumerate(pred_labels):
                            item = test_dataset.get_labels()[item]
                            writer.write("%d\t|\t%s\t|\t%s\t|\t%s\n" % (index, examples[index].text_b, examples[index].text_a, item))

                    with open(output_scores_file, "w") as writer:
                        writer.write("index\t%s\n" % "\t".join(test_dataset.get_labels()))
                        for index, scores in enumerate(predictions):
                            writer.write("%d\t%s\n" % (index, "\t".join([str(x) for x in scores])))

    return eval_results


def _mp_fn(index):
    # For xla_spawn (TPUs)
    main()


if __name__ == "__main__":
    main()
