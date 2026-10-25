# AGENTS.md — traffic-rag 協定層

本 repo 為 TAICA 第六週 RAG 作業（交通規則罰則問答）的唯一真相來源。
設計文件（SDD v1.0）正式檔存於 Vibe Canvas（traffic-rag-sdd）；repo 內 docs/ 為設計摘录與修正紀錄。

## 流程

- **SDD v1.0 已定版**（2026-10-25 14:56，三方簽齊）：實作期一律走 **D4 P0 修正版流程**——發現問題記錄於 `docs/ai-trace/d4-log.md`，不重開設計討論。
- 衝突一律由 HO（Nicky）拍板；審查者只有否決權，沒有提案權；工人有提案權（開 issue），無拍板權。
- issue 即任務市場：開單用 `.github/ISSUE_TEMPLATE.md`，領工即 assignee，完工以 PR 附 `.github/PULL_REQUEST_TEMPLATE.md` 走驗收。

## 角色 → 權限邊界矩陣

| 角色 | 提案（issue） | 審查否決 | 建置／QA | merge | Write Scope |
| --- | --- | --- | --- | --- | --- |
| Instinct | ✓ | ✗（糾錯以回報提出） | 語料切塊、manifest、生效清單 | ✗ | `rag-data/**`、manifest 檔 |
| Muse | ✓ | ✗ | manifest 相容性、RAG 01 索引驗收、rag01 notebook | ✗ | `tests/**`、`colab/rag01*` |
| Cue | ✓ | ✗ | prompt、回答格式、題組生成驗收、rag02 notebook | ✗ | `tests/**`、`prompts/**`、`colab/rag02*`、`docs/**` |
| Vibe（PM 幕僚） | ✓ | ✗ | repo 初始化、文件、排程盯場 | ✗ | 根目錄 README／AGENTS.md、`docs/**` |
| **Nicky（HO／PM）** | ✓ | ✓（拍板） | 最終驗收、兩份 Colab 手動執行 | **✓ 唯一** | 全 repo |

- 一個 agent 一個主職；兼任必須明寫；軌道命名與實際 agent 一一對應，不留幽靈軌道（wirelab 教訓，2026-10-19）。
- Colab 本體無公開執行 API：notebook 檔由 agent 產出（.ipynb 入版），**執行一律由 HO 手動**；執行版留痕入 `colab/executed/`。

## 分支紀律

- agent 一律走 `agent/<name>-*` 分支，**不得直接推 main**；最終 merge 由 HO 人肉拍板。
- issue 為任務隊列；assignee 即認領，防止撞車。

## 憑證防線（硬性）

- **任何 agent 不得向任何人索取帳號密碼**；GitHub 存取走 GitHub App connector 或細粒度 PAT，憑證永不進 repo、不進訊息、不進 handoff。
- `.gitignore` 已排除 `.env`／`*.key`；發現疑似憑證入版，立即通報 HO 並視為 P0。

## Handoff 格式

- 交接檔統一放 `handoff/`，編號管理（`000-主題.md` 起算）。
- 固定欄位：**當前狀態／未完成清單／已知問題／交接對象**。
- 中途換軌、退場、發現阻擋問題，先記 handoff 再離場。

## 文件同步義務

- 隨變更更新 `docs/ai-trace/`（AI 留痕，繳交註三評分證據）與 `docs/ai-trace/d4-log.md`（修正紀錄）。
- metadata 欄位以 `rag-data/metadata-schema.md` 為單一真相；prompt 以 `prompts/` 版本化；notebook 版控規則見 `colab/README.md`（主檔清 output、執行版入 executed/、一份 notebook 一個 owner）。
- zip 檔不進 git（見 `.gitignore`）；語料以文字檔入版。
