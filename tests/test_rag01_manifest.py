#!/usr/bin/env python3
# RAG 01 manifest compatibility + notebook acceptance checks (traffic-rag issue #3).
# Pure stdlib. Run from a repo checkout:
#   python3 tests/test_rag01_manifest.py [--repo-root .]
# Exit code: 0 = no blocking failure (indexing unblocked).
#   PASS    = check passed.
#   FINDING = data-quality / doc issue for its owner (Instinct / HO / Vibe);
#             non-blocking for indexing, listed for follow-up, does NOT fail the run.
#   FAIL    = blocks indexing / build; must be fixed before the Colab run.
# What this script does NOT do: embedding, FAISS build, Colab execution.
# Those run only in Colab by the PM (HO); see tests/rag01_acceptance_report.md.
import argparse
import ast
import json
import re
import sys
from pathlib import Path

EXPECTED_CORE_FILES = ["art16.txt", "art21.txt", "art35-2.txt", "art35_para1.txt", "art35_para4.txt"]
EXPECTED_PENDING_FILES = ["art18-1_para6.txt", "art35_para6.txt", "art92-2.txt"]
REQUIRED_NOTEBOOK_STRINGS = [
    "google/embeddinggemma-2",
    "sentence-transformers==6.1.0",
    "transformers==5.20.1",
    "faiss-cpu==1.15.1",
    "IndexFlatIP",
    "rag-data.zip",
    "rag-data-pending.zip",
    "normalize_embeddings",
    "DOCUMENT_TEMPLATE",
    "QUERY_TEMPLATE",
]

results = []


def record(check_id, status, detail):
    results.append((check_id, status, detail))
    print(f"[{status}] {check_id}: {detail}")


def norm_para(value):
    if value in (None, "", "all"):
        return None
    return str(value)


def read_header_field(normalized, name):
    match = re.search(rf"^{re.escape(name)}[：:][ \t]*(.*)$", normalized, flags=re.MULTILINE)
    return match.group(1).strip() or None if match else None


def parse_txt_header(raw_text):
    normalized = raw_text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    header = {}
    for name in ["law_name", "article", "paragraph", "chapter", "version_date",
                 "effective_status", "effective_date", "source", "retrieved_at", "chunk_id"]:
        header[name] = read_header_field(normalized, name)
    header["title"] = read_header_field(normalized, "標題")
    return header


def load_manifest(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=None,
                        help="Repo checkout root (default: parent of tests/).")
    args = parser.parse_args()
    root = Path(args.repo_root) if args.repo_root else Path(__file__).resolve().parent.parent

    # M1: manifests load + structure.
    try:
        core = load_manifest(root / "rag-data" / "core_manifest.json")
        pend = load_manifest(root / "rag-data" / "pending_manifest.json")
        audit = load_manifest(root / "rag-data" / "audit_manifest.json")
    except (OSError, json.JSONDecodeError) as exc:
        record("M1-manifests-load", "FAIL", f"manifest 載入失敗：{exc}")
        print_summary()
        return 1
    record("M1-manifests-load",
           "PASS" if (core.get("package") == "core" and pend.get("package") == "pending"
                      and audit.get("package") == "audit") else "FAIL",
           f"core={core.get("package")} chunks={len(core.get("chunks", []))} "
           f"pending={pend.get('package')} {len(pend.get('chunks', []))} "
           f"audit={audit.get('package')} {len(audit.get('chunks', []))} "
           f"reference_date={core.get('reference_date')}")
    core_by_id = {e["chunk_id"]: e for e in core["chunks"]}
    pend_by_id = {e["chunk_id"]: e for e in pend["chunks"]}
    all_ids = set(core_by_id) | set(pend_by_id)

    # M2: chunk_id prefix discipline + uniqueness within each package.
    for name, manifest, pkg in [("core", core, "core"), ("pending", pend, "pending")]:
        ids = [e["chunk_id"] for e in manifest["chunks"]]
        bad_prefix = [i for i in ids if not i.startswith(pkg + ":")]
        dup = len(ids) - len(set(ids))
        record(f"M2-chunk-id-{name}",
               "PASS" if not bad_prefix and dup == 0 else "FAIL",
               f"n={len(ids)} unique={len(set(ids))} bad_prefix={bad_prefix[:5]}")

    # M3: status vocabulary per package.
    core_status = {e.get("effective_status") for e in core["chunks"]}
    pend_status = {e.get("effective_status") for e in pend["chunks"]}
    record("M3-status-vocabulary",
           "PASS" if core_status == {"effective"} and pend_status == {"not_yet_effective"} else "FAIL",
           f"core={sorted(core_status)} pending={sorted(pend_status)}")

    # M4: effective_date rules (core all real dates; pending date-or-未定）.
    date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    core_nondate = [e["chunk_id"] for e in core["chunks"]
                    if not date_re.match(str(e.get("effective_date")))]
    pend_nondate = [e["chunk_id"] for e in pend["chunks"]
                    if not date_re.match(str(e.get("effective_date")))]
    pend_undetermined = [e["chunk_id"] for e in pend["chunks"] if e.get("effective_date") == "未定"]
    record("M4-effective-date",
           "PASS" if not core_nondate else "FAIL",
           f"core 非日期值 {len(core_nondate)} 筆；pending 非日期值 {len(pend_nondate)} 筆"
           f"（其中「未定」{len(pend_undetermined)} 筆，條件式顯示處理，見 FINDING-04）")
    if pend_nondate and all(e.get("effective_date") == "未定" for e in pend["chunks"]):
        record("M4-pending-undetermined-note", "FINDING",
               "pending 23/23 筆 effective_date 皆為「未定」字串（非 date 型別）；"
               "notebook 以條件式顯示處理，未來有真實日期者顯示該日期。")

    # M5: delivered files vs manifest entries (header <-> manifest, teacher format).
    delivered = []
    for pkg, files, manifest_by_id in [("core", EXPECTED_CORE_FILES, core_by_id),
                                       ("pending", EXPECTED_PENDING_FILES, pend_by_id)]:
        for fname in files:
            path = root / "rag-data" / pkg / fname
            if not path.exists():
                record(f"M5-delivered-{pkg}-{fname}", "FAIL", "檔案缺失。")
                continue
            raw = path.read_text(encoding="utf-8-sig")
            header = parse_txt_header(raw)
            chunk_id = header.get("chunk_id")
            entry = manifest_by_id.get(chunk_id) if chunk_id else None
            if entry is None:
                record(f"M5-delivered-{pkg}-{fname}", "FAIL",
                       f"標頭 chunk_id={chunk_id} 在 {pkg} manifest 無對應條目。")
                continue
            diffs = []
            for field, hv, ev in [
                ("article", header.get("article"), str(entry.get("article"))),
                ("paragraph", norm_para(header.get("paragraph")), norm_para(entry.get("paragraph"))),
                ("chapter", header.get("chapter"), entry.get("chapter")),
                ("version_date", header.get("version_date"), entry.get("version_date")),
                ("effective_status", header.get("effective_status"), entry.get("effective_status")),
                ("effective_date", header.get("effective_date"), str(entry.get("effective_date"))),
            ]:
                if hv is not None and str(hv) != str(ev):
                    diffs.append(f"{field}: txt={hv} vs manifest={ev}")
            if entry.get("file") != fname:
                diffs.append(f"file: manifest={entry.get('file')} vs actual={fname}")
            has_title = "標題：" in raw
            has_body = "【內容】" in raw
            if not has_title or not has_body:
                diffs.append(f"教師格式缺失（標題：{has_title}／【內容】{has_body}）")
            delivered.append((pkg, chunk_id, entry))
            record(f"M5-delivered-{pkg}-{fname}",
                   "PASS" if not diffs else "FAIL",
                   f"{chunk_id} 標頭與 manifest 一致" if not diffs else "；".join(diffs))
    delivered_ids = {cid for _, cid, _ in delivered}

    # M6: package separation + audit exclusions honored.
    record("M6-void-exclusion",
           "PASS" if "core:art35_para6" not in core_by_id else "FAIL",
           "core_manifest 無 core:art35_para6（違憲失效項正確排除）。"
           if "core:art35_para6" not in core_by_id else "core_manifest 含已失效的 core:art35_para6！")
    audit_ids = {e["chunk_id"] for e in audit["chunks"]}
    leaked = sorted(audit_ids & {cid for pkg, cid, _ in delivered if pkg == "core"})
    record("M6-audit-not-indexed",
           "PASS" if not leaked else "FAIL",
           f"交付 core 檔中無 audit 排除項（leaked={leaked}）；"
           "pending:art35_para6 屬 pending 包新版，不在 audit 的 core: 排除集合內，允許。")

    # M7: context_refs resolvability (full manifests vs delivered files).
    for pkg, chunk_id, entry in delivered:
        refs = entry.get("context_refs") or []
        for ref in refs:
            in_full = ref in all_ids
            in_delivered = ref in delivered_ids
            if in_full and in_delivered:
                record(f"M7-context-refs-{chunk_id}->{ref}", "PASS", "全量與小樣本皆可解析。")
            elif in_full and not in_delivered:
                record(f"M7-context-refs-{chunk_id}->{ref}", "FINDING",
                       "全量 manifest 可解析，但目標檔未在小樣本交付內（小樣本不可驗，待全量驗證；"
                       "txt 已內嵌背景參照 prelude 補足可讀性）。")
            else:
                record(f"M7-context-refs-{chunk_id}->{ref}", "FAIL", "全量 manifest 亦無此目標（懸空引用）。")

    # M8: source_ref presence.
    n_source_ref = sum(1 for m in (core, pend) for e in m["chunks"] if "source_ref" in e)
    n_total = len(core["chunks"]) + len(pend["chunks"])
    record("M8-source-ref", "FINDING" if n_source_ref == 0 else "PASS",
           f"manifest 含 source_ref 者 {n_source_ref}/{n_total} 筆；"
           "schema v0.2 要求 source_ref（raw/ 檔名＋頁碼／條號定位），目前僅有 source_url（MOJ 網頁）。"
           if n_source_ref == 0 else f"manifest 含 source_ref 者 {n_source_ref}/{n_total} 筆。")

    # M9: schema mapping drift.
    schema_path = root / "rag-data" / "metadata-schema.md"
    if schema_path.exists():
        schema_text = schema_path.read_text(encoding="utf-8")
        record("M9-schema-drift", "FINDING",
               "schema v0.2 欄位名（id／條號／章／修正日期／生效狀態 current-pending／預定施行日期）"
               "與 manifest 實作（chunk_id／article+paragraph／chapter／version_date／"
               "effective_status effective-not_yet_effective／effective_date）存在命名與詞彙漂移；"
               "notebook 依 SDD 採用 manifest 詞彙，schema 文件待 HO／Vibe 升版對齊（不由本 PR 單方改規格）。")
    else:
        record("M9-schema-drift", "FAIL", "rag-data/metadata-schema.md 缺失。")

    # M10: audit manifest internal consistency.
    record("M10-audit-counts",
           "PASS" if audit.get("excluded_count") == len(audit["chunks"]) else "FAIL",
           f"excluded_count={audit.get('excluded_count')}／實際 {len(audit['chunks'])} 筆。")
    if audit.get("chunk_count") != len(audit["chunks"]):
        record("M10-audit-chunk-count-field", "FINDING",
               f"audit_manifest chunk_count 欄位＝{audit.get('chunk_count')}，與實際 {len(audit['chunks'])} 筆不符；"
               "notebook 與本腳本皆以 len(chunks) 為準，不受影響，欄位待 Instinct 修正。")
    void_entries = [e for e in audit["chunks"] if e.get("excluded_status") == "void_unconstitutional"]
    record("M10-audit-void-record",
           "PASS" if void_entries and all(e.get("void_date") and e.get("void_source") for e in void_entries)
           else "FAIL",
           f"違憲失效紀錄 {len(void_entries)} 筆（含 void_date／void_source）。")

    # M11: raw/ traceability folders.
    raw_pdfs = list((root / "raw").glob("*.pdf")) if (root / "raw").exists() else []
    raw_dir = root / "RAW" if (root / "RAW").exists() else None
    raw_upper_pdfs = list(raw_dir.glob("*.pdf")) if raw_dir else []
    if not raw_pdfs:
        record("M11-raw-pdf", "FINDING",
               f"raw/ 無 PDF（僅 README／.gitkeep）；"
               f"RAW/ 目錄{'存在，含 PDF ' + str(len(raw_upper_pdfs)) + ' 個' if raw_dir else '在本 layout 不存在'}；"
               "raw/README 登記表仍待填（檔名慣例＋版本＋下載日＋SHA-256），溯源鏈待 HO／Instinct 補齊。")

    # M12: notebook deliverable checks.
    nb_path = root / "colab" / "rag01-build-vector-db.ipynb"
    if not nb_path.exists():
        record("M12-notebook", "FAIL", "colab/rag01-build-vector-db.ipynb 缺失。")
    else:
        try:
            nb = json.loads(nb_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            record("M12-notebook", "FAIL", f"notebook JSON 解析失敗：{exc}")
            nb = None
        if nb is not None:
            problems = []
            if nb.get("nbformat") != 4:
                problems.append("nbformat 非 4")
            code_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "code"]
            md_cells = [c for c in nb.get("cells", []) if c.get("cell_type") == "markdown"]
            for cell in code_cells:
                if cell.get("outputs") != [] or cell.get("execution_count") is not None:
                    problems.append("有 code cell 含 output 或 execution_count（主檔須清 output）")
                    break
                src = "".join(cell.get("source", []))
                if "TODO(Muse)" in src or "TODO(Cue)" in src:
                    problems.append("仍有 TODO 標記未實作")
                    break
                stripped = "\n".join(
                    line for line in src.split("\n")
                    if not line.strip().startswith(("%", "!"))
                )
                try:
                    ast.parse(stripped)
                except SyntaxError as exc:
                    problems.append(f"語法錯誤：{exc}")
                    break
            joined_code = "\n".join("".join(c.get("source", [])) for c in code_cells)
            missing = [s for s in REQUIRED_NOTEBOOK_STRINGS if s not in joined_code]
            if missing:
                problems.append(f"缺必要字串：{missing}")
            record("M12-notebook",
                   "PASS" if not problems else "FAIL",
                   f"cells={len(nb.get('cells', []))}（markdown {len(md_cells)}／code {len(code_cells)}）；"
                   + ("；".join(problems) if problems else "JSON、語法、清 output、必要字串皆通過。"))

    return print_summary()


def print_summary():
    n_pass = sum(1 for _, s, _ in results if s == "PASS")
    n_finding = sum(1 for _, s, _ in results if s == "FINDING")
    n_fail = sum(1 for _, s, _ in results if s == "FAIL")
    print(f"\nSUMMARY: PASS={n_pass} FINDING={n_finding} FAIL={n_fail}")
    if n_fail:
        print("RESULT: BLOCKED（有 FAIL，須先修正再跑 Colab）")
        return 1
    print("RESULT: OK（無 blocking 失敗；FINDING 項目為待追蹤事項，不阻斷建庫）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
