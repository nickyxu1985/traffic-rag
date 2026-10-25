# rag-data 語料

## 切塊與命名

- 一條一檔：`art35.txt`；長條按項：`art35_para6.txt`
- 增訂條文：`art35-2.txt`
- metadata 必含：條號、章、修正日期、生效狀態（pending 另含預定施行日期）

## 資料夾

- `core/`：現行有效法規（固定基準日）。五份小樣本起步，驗收通過後擴全量。
- `pending/`：未生效法規隔離區，不混入主庫。

## 資料來源與交接狀態

- 小樣本包（Instinct 產出）：`rag-data-sample-core.zip`（B 五份）、`rag-data-sample-pending.zip`（三份）、`manifest-bundle.zip`（清單＋排除紀錄＋D4 紀錄）。
- 排除紀錄：§35 第 6 項（憲法法庭 111 年憲判字第 1 號設有失效期限，舊文不能標為現行有效），以 §16 補足五份樣本；詳見 `docs/ai-trace/d4-log.md`。
- zip 檔不進 git（見 `.gitignore`），解壓後的文字檔放入對應資料夾。

## 打包

由 `rag-data/core/` 打包 `rag-data.zip` 供 RAG 01 Colab 建向量庫；pending 另包、隔離跑。
