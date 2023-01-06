"""FEVEROUS dataset."""

import json
import textwrap

import datasets


class FeverousConfig(datasets.BuilderConfig):
    """BuilderConfig for FEVER."""

    def __init__(self, homepage: str = None, citation: str = None, base_url: str = None, urls: dict = None, **kwargs):
        """BuilderConfig for FEVEROUS.

        Args:
            homepage (`str`): Homepage.
            citation (`str`): Citation reference.
            base_url (`str`): Data base URL that precedes all data URLs.
            urls (`dict`): Data URLs (each URL will pe preceded by `base_url`).
            **kwargs: keyword arguments forwarded to super.
        """
        super().__init__(**kwargs)
        self.homepage = homepage
        self.citation = citation
        self.base_url = base_url
        self.urls = {key: f"{base_url}/{url}" for key, url in urls.items()}


class FeverOUS(datasets.GeneratorBasedBuilder):
    """FEVEROUS dataset."""

    BUILDER_CONFIGS = [
        FeverousConfig(
            version=datasets.Version("1.0.0"),
            description=textwrap.dedent(
                "FEVEROUS:\n"
                "FEVEROUS (Fact Extraction and VERification Over Unstructured and Structured information) is a fact "
                "verification dataset which consists of 87,026 verified claims. Each claim is annotated with evidence "
                "in the form of sentences and/or cells from tables in Wikipedia, as well as a label indicating whether "
                "this evidence supports, refutes, or does not provide enough information to reach a verdict. The "
                "dataset also contains annotation metadata such as annotator actions (query keywords, clicks on page, "
                "time signatures), and the type of challenge each claim poses."
            ),
            homepage="https://fever.ai/dataset/feverous.html",
            citation=textwrap.dedent(
                """\
                @inproceedings{Aly21Feverous,
                    author = {Aly, Rami and Guo, Zhijiang and Schlichtkrull, Michael Sejr and Thorne, James and Vlachos, Andreas and Christodoulopoulos, Christos and Cocarascu, Oana and Mittal, Arpit},
                    title = {{FEVEROUS}: Fact Extraction and {VERification} Over Unstructured and Structured information},
                    eprint={2106.05707},
                    archivePrefix={arXiv},
                    primaryClass={cs.CL},
                    year = {2021}
                }"""
            ),
            base_url="https://fever.ai/download/feverous",
            urls={
                datasets.Split.TRAIN: "feverous_train_challenges.jsonl",
                datasets.Split.VALIDATION: "feverous_dev_challenges.jsonl",
                datasets.Split.TEST: "feverous_test_unlabeled.jsonl",
            },
        ),
    ]

    def _info(self):
        features = {
            "id": datasets.Value("int32"),
            "label": datasets.ClassLabel(names=["SUPPORTS", "REFUTES", "NOT ENOUGH INFO"]),
            "claim": datasets.Value("string"),
            "evidence": [
                {
                    "content": [datasets.Value("string")],
                    "context": [[datasets.Value("string")]],
                }
            ],
            "annotator_operations": [
                {
                    "operation": datasets.Value("string"),
                    "value": datasets.Value("string"),
                    "time": datasets.Value("float"),
                }
            ],
            "expected_challenge": datasets.Value("string"),
            "challenge": datasets.Value("string"),
        }
        return datasets.DatasetInfo(
            description=self.config.description,
            features=datasets.Features(features),
            homepage=self.config.homepage,
            citation=self.config.citation,
        )

    def _split_generators(self, dl_manager):
        dl_paths = dl_manager.download_and_extract(self.config.urls)
        return [
            datasets.SplitGenerator(
                name=split,
                gen_kwargs={
                    "filepath": dl_paths[split],
                },
            )
            for split in dl_paths.keys()
        ]

    def _generate_examples(self, filepath):
        with open(filepath, encoding="utf-8") as f:
            for id_, row in enumerate(f):
                data = json.loads(row)
                # First item in "train" has all values equal to empty strings
                if [value for value in data.values() if value]:
                    evidence = data.get("evidence", [])
                    if evidence:
                        for evidence_set in evidence:
                            # Transform "context" from dict to list (analogue to "content")
                            evidence_set["context"] = [
                                evidence_set["context"][element_id] for element_id in evidence_set["content"]
                            ]
                    yield id_, {
                        "id": data.get("id"),
                        "label": data.get("label", -1),
                        "claim": data.get("claim", ""),
                        "evidence": evidence,
                        "annotator_operations": data.get("annotator_operations", []),
                        "expected_challenge": data.get("expected_challenge", ""),
                        "challenge": data.get("challenge", ""),
                    }
