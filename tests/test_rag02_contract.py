"""Offline contract tests for the RAG02 notebook; no model, corpus, or API calls."""
import ast
import hashlib
import io
import json
import re
import tempfile
import unittest
import zipfile
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "colab" / "rag02-chatbot.ipynb"


class FakeIndexFlatIP:
    def __init__(self, dimension=4, count=1):
        self.d = dimension
        self.ntotal = count
        self.metric_type = 123


class FakeFaiss:
    IndexFlatIP = FakeIndexFlatIP
    METRIC_INNER_PRODUCT = 123

    @staticmethod
    def read_index(_path):
        return FakeIndexFlatIP()


def notebook_environment():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    wanted_functions = {
        "metadata_value", "canonical_status", "canonical_article", "canonical_item",
        "canonical_subitem", "sha256_bytes", "normalize_ref", "aliases_for_value",
        "context_ref_values", "record_aliases",
        "ref_aliases", "resolve_same_package_refs", "normalized_revision_date",
        "explicit_article_numbers", "explicit_revision_dates", "pending_corresponds",
        "article_item_label", "normalized_quote", "validate_and_render_answer",
        "effective_date_label", "build_context", "load_vector_package", "download_public_zip",
    }
    wanted_assignments = {"REQUIRED_PACKAGE_FILES", "CITATION_PATTERN", "QUOTE_PATTERN"}
    selected = []
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "\n".join(line for line in "".join(cell["source"]).splitlines()
                            if not line.lstrip().startswith("%"))
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name in wanted_functions:
                selected.append(node)
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                names = {t.id for t in targets if isinstance(t, ast.Name)}
                if names & wanted_assignments:
                    selected.append(node)
    env = {
        "re": re, "json": json, "hashlib": hashlib, "io": io,
        "zipfile": zipfile, "tempfile": tempfile, "Path": Path,
        "urlparse": urlparse, "urllib": __import__("urllib"),
        "faiss": FakeFaiss, "EXPECTED_MODEL_ID": "google/embeddinggemma-2",
        "EXPECTED_QUERY_TEMPLATE": "task: search result | query: {question}",
    }
    module = ast.Module(body=selected, type_ignores=[])
    exec(compile(module, str(NOTEBOOK_PATH), "exec"), env)
    return env, notebook


def make_package_zip(namespace="core:", status="current", article="35", item="1"):
    env, _ = notebook_environment()
    index_bytes = b"synthetic-faiss-index"
    document = {
        "doc_id": "art35_para1",
        "text": "機車駕駛人處新臺幣一萬五千元以上九萬元以下罰鍰",
        "metadata": {
            "id": "art35_para1", "chunk_id": namespace + "art35_para1",
            "article": article, "item": item, "章": "違規處罰",
            "修正日期": "2026-01-14", "生效狀態": status,
            "context_refs": [],
        },
    }
    docs_bytes = json.dumps([document], ensure_ascii=False).encode("utf-8")
    ids_bytes = json.dumps([document["doc_id"]]).encode("utf-8")
    config = {
        "format_version": "1.0", "model_id": "google/embeddinggemma-2",
        "model_revision": "a" * 40,
        "model_config_kwargs": {"vision_config": None, "audio_config": None},
        "normalize_embeddings": True, "index_type": "IndexFlatIP",
        "metric": "cosine_similarity_via_normalized_inner_product",
        "query_template": "task: search result | query: {question}",
        "encode_prompt": "", "dimension": 4, "document_count": 1,
        "max_seq_length": 128,
        "file_sha256": {
            "index.faiss": hashlib.sha256(index_bytes).hexdigest(),
            "documents.json": hashlib.sha256(docs_bytes).hexdigest(),
            "index_doc_ids.json": hashlib.sha256(ids_bytes).hexdigest(),
        },
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        archive.writestr("index.faiss", index_bytes)
        archive.writestr("documents.json", docs_bytes)
        archive.writestr("index_doc_ids.json", ids_bytes)
        archive.writestr("config.json", json.dumps(config).encode("utf-8"))
    return output.getvalue()


class NotebookStaticTests(unittest.TestCase):
    def test_notebook_valid_and_clean(self):
        notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
        self.assertEqual(notebook["nbformat"], 4)
        self.assertEqual(sum(len(c.get("outputs", [])) for c in notebook["cells"]), 0)
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] != "code":
                continue
            source = "\n".join(line for line in "".join(cell["source"]).splitlines()
                                if not line.lstrip().startswith("%"))
            ast.parse(source, filename=f"notebook-cell-{index}")
        code = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
        self.assertIn('RAG_MODE = "B"', code)
        self.assertIn('pending_store = load_vector_package(pending_zip_bytes, "pending") if RAG_MODE == "A" else None', code)
        all_source = "\n".join("".join(c["source"]) for c in notebook["cells"])
        self.assertIn('rag-data.zip', all_source)
        self.assertIn('rag-data-pending.zip', all_source)
        code_cells = ["".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code"]
        downloader_index = next(i for i, source in enumerate(code_cells) if "RAG_DATA_URL" in source)
        install_index = next(i for i, source in enumerate(code_cells) if "%pip install" in source)
        self.assertLess(downloader_index, install_index)
        self.assertIn("urlopen", code_cells[downloader_index])
        self.assertIn("zipfile.is_zipfile", code_cells[downloader_index])
        self.assertIn("https", code_cells[downloader_index])
        self.assertNotIn("https://github.com/", code_cells[downloader_index])
        self.assertNotIn("https://raw.githubusercontent.com/", code_cells[downloader_index])
        self.assertIn('RAG_PENDING_URL = ""', code_cells[downloader_index])
        self.assertIn('if RAG_MODE == "A":', code_cells[downloader_index])
        for version in ["sentence-transformers==6.1.0", "transformers==5.20.1", "faiss-cpu==1.15.1", "aisuite[groq]==0.2.0", "groq==0.37.1", "gradio==6.30.0"]:
            self.assertIn(version, code)

    def test_test_matrix_has_t1_to_t5_and_not_run_baseline(self):
        suite = json.loads((ROOT / "tests" / "rag02-t1-t5.json").read_text(encoding="utf-8"))
        ids = [case["case_id"] for case in suite["cases"]]
        for case_id in ["T1", "T2", "T3-B", "T3-A", "T4-core", "T4-pending", "T5-A", "T5-B"]:
            self.assertIn(case_id, ids)
        self.assertFalse(suite["package_contract"]["actual_data_available"])
        self.assertEqual(suite["result_record_template"]["overall"], "NOT RUN")


class MetadataAndGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env, _ = notebook_environment()

    def test_metadata_status_and_article_item_normalization(self):
        e = self.env
        self.assertEqual(e["canonical_status"]({"生效狀態": "current"}), "current")
        self.assertEqual(e["canonical_status"]({"生效狀態": "pending"}), "not_yet_effective")
        self.assertEqual(e["canonical_article"]({"條號": "第 35 條第 1 項"}), "35")
        self.assertEqual(e["canonical_item"]({"條號": "第 35 條第 1 項"}), "1")

    def test_package_loader_preserves_metadata_and_fails_closed(self):
        e = self.env
        core = e["load_vector_package"](make_package_zip(), "core")
        record = core["records_by_chunk_id"]["core:art35_para1"]
        self.assertEqual(record["status"], "current")
        self.assertEqual(record["metadata"]["生效狀態"], "current")
        pending = e["load_vector_package"](make_package_zip("pending:", "pending"), "pending")
        self.assertEqual(next(iter(pending["records_by_chunk_id"].values()))["status"], "not_yet_effective")
        with self.assertRaisesRegex(ValueError, "chunk_id"):
            e["load_vector_package"](make_package_zip("pending:", "pending"), "core")
        with self.assertRaisesRegex(ValueError, "status"):
            e["load_vector_package"](make_package_zip("core:", "pending"), "core")

    def test_context_refs_resolve_in_same_package_and_record_edge(self):
        e = self.env
        paragraph_one = {
            "doc_id": "art35_para1", "chunk_id": "core:art35_para1", "article": "35", "item": "1",
            "metadata": {"id": "art35_para1", "條號": "第35條第1項", "context_refs": []},
            "package": "core", "status": "current", "text": "first", "score": 0.9,
        }
        paragraph_four = {
            "doc_id": "art35_para4", "chunk_id": "core:art35_para4", "article": "35", "item": "4",
            "metadata": {"id": "art35_para4", "條號": "第35條第4項", "context_refs": ["第35條第1項"]},
            "package": "core", "status": "current", "text": "fourth", "score": 0.8,
        }
        store = {"name": "core", "namespace": "core:", "records_by_chunk_id": {
            paragraph_one["chunk_id"]: paragraph_one, paragraph_four["chunk_id"]: paragraph_four,
        }}
        linked = e["resolve_same_package_refs"](store, paragraph_four)
        self.assertEqual([item["chunk_id"] for item in linked], ["core:art35_para1"])
        self.assertEqual(paragraph_four["context_ref_edges"][0]["to_item"], "1")
        paragraph_four["metadata"]["context_refs"] = ["pending:art35_para1"]
        self.assertEqual(e["resolve_same_package_refs"](store, paragraph_four), [])

    def test_pending_match_requires_exact_article_item_and_revision_date(self):
        e = self.env
        hits = [
            {"chunk_id": "pending:art35_para1_v2026", "article": "35", "item": "1",
             "metadata": {"修正日期": "民國 115 年 8 月 17 日"}, "text": "new"},
            {"chunk_id": "pending:art35_para6_v2025", "article": "35", "item": "6",
             "metadata": {"修正日期": "民國 114 年 11 月 19 日"}, "text": "older pending"},
        ]
        query = "2026-08-17 修正公布第35條第1項的施行日期？"
        matches = e["pending_corresponds"](query, hits)
        self.assertEqual([hit["chunk_id"] for hit in matches], ["pending:art35_para1_v2026"])
        self.assertEqual(e["normalized_revision_date"]("民國 114 年 11 月 19 日"), "2025-11-19")

    def test_cloud_downloader_validates_https_zip_without_live_network(self):
        e = self.env
        payload = make_package_zip()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return payload

        e["urllib"] = SimpleNamespace(request=SimpleNamespace(urlopen=lambda *_args, **_kwargs: FakeResponse()))
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "rag-data.zip"
            e["download_public_zip"]("https://cloud.example/rag-data.zip", destination)
            self.assertEqual(destination.read_bytes(), payload)
            with self.assertRaisesRegex(ValueError, "HTTPS"):
                e["download_public_zip"]("http://cloud.example/rag-data.zip", destination)
            with self.assertRaisesRegex(ValueError, "GitHub raw"):
                e["download_public_zip"]("https://raw.githubusercontent.com/org/repo/main/rag-data.zip", destination)
            with self.assertRaisesRegex(ValueError, "帳號或密碼"):
                e["download_public_zip"]("https://alice:secret@cloud.example/rag-data.zip", destination)

        class BadResponse(FakeResponse):
            def read(self):
                return b"not-a-zip"

        e["urllib"] = SimpleNamespace(request=SimpleNamespace(urlopen=lambda *_args, **_kwargs: BadResponse()))
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "有效的"):
                e["download_public_zip"]("https://cloud.example/rag-data.zip", Path(directory) / "rag-data.zip")

    def test_citation_validation_requires_retrieved_id_and_exact_quote(self):
        e = self.env
        quote = "機車駕駛人處新臺幣一萬五千元以上九萬元以下罰鍰"
        retrieved = [{
            "package": "core", "chunk_id": "core:art35_para1", "article": "35", "item": "1",
            "status": "current", "metadata": {"生效狀態": "current"}, "text": quote,
        }, {
            "package": "core", "chunk_id": "core:art63_para2", "article": "63", "item": "2",
            "status": "current", "metadata": {"生效狀態": "current"}, "text": "已受吊扣或吊銷駕駛執照處分者，不予記違規點數",
        }]
        answer = f"罰鍰依據為「{quote}」。[[cite:core:art35_para1]]"
        rendered, note = e["validate_and_render_answer"](answer, retrieved)
        self.assertIn("〔第35條第1項｜current〕", rendered)
        self.assertIn("已程式驗證", note)
        invalid, _ = e["validate_and_render_answer"]("罰鍰為新臺幣九萬元。[[cite:pending:art35_para1]]", retrieved)
        self.assertIn("本資料庫查不到", invalid)
        unsupported, _ = e["validate_and_render_answer"]("罰鍰為新臺幣九萬元。[[cite:core:art35_para1]]", retrieved)
        self.assertIn("原文引句", unsupported)
        mismatched, note = e["validate_and_render_answer"](
            f"罰鍰依據為「{quote}」。[[cite:core:art63_para2]]", retrieved)
        self.assertIn("本資料庫查不到", mismatched)
        self.assertIn("cited chunk", note)

    def test_context_passes_raw_metadata_end_to_end(self):
        e = self.env
        metadata = {"條號": "第35條第1項", "生效狀態": "current", "context_refs": ["core:art35_para1"], "extra": {"keep": True}}
        result = {"package": "core", "chunk_id": "core:art35_para1", "article": "35", "item": "1", "subitem": None, "text": "原文", "metadata": metadata}
        context = json.loads(e["build_context"]([result]))
        self.assertEqual(context[0]["metadata"], metadata)


if __name__ == "__main__":
    unittest.main()
