# RAG 01 驗收報告（issue #3・小樣本）

- 作者：Muse（issue #3）｜日期：2026-10-25｜基準日：2026-10-25（manifest reference_date）
- 依據：SDD v1.0 定版、issue #3 驗收條件、PR #6（#2 語料＋manifests）、`rag-data/metadata-schema.md` v0.2
- 驗證腳本：`tests/test_rag01_manifest.py`（純標準函式庫，可重現；見第 2 節）

## 1. 驗收範圍

- 小樣本 8 檔：core 5 份（art16、art21、art35-2、art35_para1、art35_para4）＋ pending 3 份（art18-1_para6、art35_para6、art92-2）。
- manifests 為全量覆蓋表，非小樣本清單：core 147 chunk、pending 23 chunk、audit 排除 3 筆。未交付檔案的 manifest 條目不是小樣本失敗；notebook 以「警告跳過」處理，全量執行時 PM 上傳全部檔案即無警告。
- audit 3 筆：§35 第 6 項違憲失效（void_unconstitutional，失效日 2024-02-25，憲法法庭 111 年憲判字第 1 號）＋ core 缺漏 2 筆（art18-1_para6、art35_para13，absent_in_core）。

## 2. 方法與可重現性

```bash
python3 tests/test_rag01_manifest.py [--repo-root .]
```

- 腳本語義：PASS＝通過；FINDING＝待追蹤事項（非阻斷，歸屬見第 5 節）；FAIL＝阻斷建庫。結束碼 0 表示無 blocking 失敗。
- 本次本地實測（2026-10-25）：**PASS=19、FINDING=7、FAIL=0，結束碼 0**。本地驗證皆為確定性檢查（manifest／txt／notebook 結構與一致性），不含 embedding。
- 本地未跑項目（皆須 PM 於 Colab 執行，見第 7 節）：embedding（本機無 torch／transformers／faiss）、FAISS 建庫、重載驗證、試查、zip 下載與雲端托管。驗收單所列「跑通後由 HO 於 Colab 執行」即指此段；本 PR 不以「應該可以」代替，執行結果由 PM 回填。
- 測試 layout 說明：腳本於本地鏡像執行（manifests＋8 檔 txt＋notebook＋schema＋raw/README）；RAW/ PDF 存在性取自 GitHub repo 檔案清單（435,112 bytes），未將二進位檔納入本地鏡像。

## 3. Schema v0.2 ↔ manifest 對照

| schema v0.2 欄位 | manifest 實作 | 判定 |
| --- | --- | --- |
| id（例 art35、art35_para6、art35-2） | chunk_id（含包別前綴 core:/pending:，SDD 命名空間規則） | 形式漂移，見 F3；notebook 採 manifest 形式 |
| 條號（字串，如「第 35 條第 6 項」） | article＋paragraph（結構化兩欄，可合成條號字串） | 形式漂移，notebook 合成條號字串供引用 |
| 章 | chapter | 內容一致 |
| 修正日期 | version_date（沿革發布日） | 一致 |
| 生效狀態 current／pending | effective_status：effective／not_yet_effective（SDD 索引列舉契約） | 詞彙漂移，見 F3；notebook 採 manifest 詞彙 |
| 預定施行日期（pending 必填，條件式） | effective_date；未定者填「未定」字串（非 date 型別） | 見 F4；notebook 條件式顯示 |
| source_ref（raw/ 檔名＋頁碼／條號定位，必填） | 缺失（0/170 筆）；僅有 source_url（MOJ 網頁） | 見 F1（最重） |
| context_refs（引用他條時） | 有；core:art35_para4→core:art35_para1，pending 兩筆見 F5 | 小樣本部分可驗 |
| （schema 未載） | file、law_name、notes、retrieved_at、source_url、cross_refs、standalone、context_inlined | 附加欄位，notebook 保留進向量 metadata |

## 4. 逐項結果（摘要）

| 檢查 | 結果 |
| --- | --- |
| M1 manifests 載入與 package／reference_date | PASS |
| M2 chunk_id 前綴與包內唯一性（core 147、pending 23） | PASS |
| M3 生效狀態詞彙（core 全 effective、pending 全 not_yet_effective） | PASS |
| M4 effective_date（core 全真實日期；pending 23 筆皆「未定」） | PASS＋F4 |
| M5 交付 8 檔：標頭↔manifest 全欄位一致、教師格式（標題：＋【內容】）8/8 | PASS |
| M6 包分離：core 無 art35_para6；交付 core 檔無 audit 排除項 | PASS |
| M7 context_refs：core 對全量＋小樣本皆可解析；pending 兩筆僅全量可解析 | PASS＋F5 |
| M8 source_ref 缺失 0/170 | FINDING（F1） |
| M9 schema 漂移 | FINDING（F3） |
| M10 audit：excluded_count＝3 實筆＝3；void 紀錄含 void_date／void_source；chunk_count 欄位＝1 不符 | PASS＋F2 |
| M11 raw/ 無 PDF；RAW/ 有 PDF 但未登記、檔名慣例不符 | FINDING（F1） |
| M12 notebook：26 cells（markdown 14／code 12）、JSON、語法、清 output、必要字串 | PASS |

## 5. FINDING 清單（皆非阻斷，歸屬明確）

- **F1（高，owner：Instinct／HO）——溯源鏈缺口**：manifest 0/170 筆有 source_ref；raw/ 無 PDF（僅 README／.gitkeep），PDF 實際在 RAW/（檔名 `道路交通管理處罰條例_全國法規資料庫_115-08-17.pdf`，與 raw/README 慣例「連字號＋下載日」不符，且登記表仍空白）。依 schema／AGENTS.md，端到端溯源（切塊文字逐字對原檔、回答可回查原檔）目前無法驗證。處置：notebook 保留 source_url 並標記 source_ref 缺失，不捏造；是否移檔＋登記＋補 source_ref，由 HO 拍板（raw/** 為 Instinct 範圍，Muse 不跨改）。
- **F2（中，owner：Instinct）——audit 欄位不一致**：audit_manifest chunk_count 欄位＝1，實際 chunks＝3（excluded_count＝3 正確）。notebook 與驗證腳本皆以 len(chunks) 為準，不受影響；欄位待修正。
- **F3（中，owner：HO／Vibe）——schema 文件漂移**：schema v0.2 仍為中文欄位名與 current／pending 詞彙，與 manifest／SDD 實作不一致（見第 3 節）。notebook 依 SDD 採用 manifest 詞彙；schema 文件升版由 HO／Vibe 決定，不由本 PR 單方改規格。
- **F4（低，notebook 已處理）——pending effective_date 皆為「未定」字串**：23/23 筆，無一筆帶真實預定日期。notebook 以條件式顯示處理（真實日期顯示該日期，否則顯示未定）；未來有日期的 pending 條目不需改程式。
- **F5（低，小樣本範圍）——pending context_refs 小樣本不可驗**：pending:art18-1_para6→core:art18-1_para1、pending:art35_para6→pending:art35_para1 兩筆目標皆在全量 manifest 內，但目標檔未在小樣本交付內；txt 已內嵌背景參照 prelude 補足可讀性（設計如此）。全量執行時驗證。
- **F6（資訊，已處理）——paragraph「all」↔ null 等價**：全文條 txt 標頭寫 all，manifest 寫 null；notebook 正規化為等價，不視為不一致。
- **F7（資訊，owner：Vibe／PM）——根目錄 README 舊命名**：PR #5 觀察：repo 根目錄 README 仍有一處舊 `vector_embedding.zip` 命名。根目錄 README 為 Vibe 範圍，Muse 不跨改；請 Vibe／PM 同步（本 PR 不動該檔）。
- **F8（資訊，owner：docs 範圍角色）——docs/ai-trace 轉錄待辦**：本 PR 依 Write Scope 不寫 docs/**；本報告與 PR 內文即為轉錄來源，請 docs 範圍角色將 FINDING 記入 `docs/ai-trace/d4-log.md`（D4 流程）與 ai-trace 留痕。

## 6. Notebook 改編清單（老師模板 → 本案）

基底：yenlung/Generative-AI《RAG_01_打造你的_RAG_系統.ipynb》（yenlung.me/rag01colab）。固定套件沿用老師版：`sentence-transformers==6.1.0`、`transformers==5.20.1`、`faiss-cpu==1.15.1`；DOCUMENT_TEMPLATE（title: none）與 QUERY_TEMPLATE（task: search result）保留老師版；IndexFlatIP＋雙邊正規化（cosine similarity）保留老師版；四檔匯出格式（index.faiss／documents.json／index_doc_ids.json／config.json）與重載驗證流程保留老師版。
本案改編：雙庫物理隔離（core／pending 各自索引與 zip）；doc_id＝chunk_id；manifest join 校驗（fail-closed：無 manifest 條目拒絕索引、標頭與 manifest 不一致報錯、包前綴與生效狀態錯包拒絕混入）；小樣本警告跳過（manifest 全量覆蓋、未上傳條目警告）；條號字串合成供引用；effective_date 條件式顯示；source_ref 缺失標記（不捏造）；匯出檔名改為作業七規定的 rag-data.zip／rag-data-pending.zip；試查三項（T1 取回、T4 連動、pending 隔離）。

## 7. 待 PM Colab 執行項目（本 PR 不宣稱已跑）

1. 依 notebook 上傳 core zip＋core_manifest.json、pending zip＋pending_manifest.json（manifest 由 repo 下載，不走 raw link、不嵌帳密）。
2. 執行全部 cells：embedding（google/embeddinggemma-2）、core 5 份建庫、pending 3 份隔離另跑、重載驗證、試查三項。
3. 下載 rag-data.zip 與 rag-data-pending.zip，上傳雲端轉可下載網址，填入 RAG 02 下載 cell；執行版（帶 output）存 colab/executed/（檔名帶日期）。
4. 回填執行結果（成功／失敗項目與原因）至 issue #3；失敗項目不得以「應該可以」結案。

## 8. 未更動範圍（Write Scope 遵守）

本 PR 僅觸及 Muse 範圍：`tests/**`（本報告＋驗證腳本）、`colab/rag01*`（本 notebook）。未動：`rag-data/**`、manifests、`raw/**`、`RAW/`、`prompts/**`、`colab/rag02*`、`docs/**`、根目錄 README／AGENTS.md。合併權僅 HO；本 PR 不合併、不部署、不改 live Colab。
