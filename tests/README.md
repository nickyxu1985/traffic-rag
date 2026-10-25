# 驗證題組（T1–T5）

依 SDD v1.0 規劃，題組內容由 Cue 維護，以下為題型架構（詳細題目以 Cue 版本為準）：

Issue #1 定稿題目、官方來源引文、expected package/article/item/status、檢索與生成檢查，以及逐題 PASS/FAIL 紀錄欄位見 [`rag02-t1-t5.md`](rag02-t1-t5.md) 和 [`rag02-t1-t5.json`](rag02-t1-t5.json)。未經 HO 在 Colab 實跑的結果維持 `NOT RUN`；命中不等於答案通過，罰則主張仍須人工逐項覆核。

可先執行 `python3 tests/test_rag02_contract.py -v` 做離線合成契約測試（不需語料、模型或 API）。此測試只驗封裝／metadata／routing helper 的 fail-closed 行為，不取代 T1–T5 正式索引檢索、生成答案及人工 claim review。

| 編號 | 題型 | 驗證目的 |
| --- | --- | --- |
| T1 | 數字情境題 | 罰則金額、期限等數字檢索正確 |
| T2 | 查無題 | 語料庫無對應條文時不得產生幻覺 |
| T3 | 生效狀態題 | pending 條文不得混入現行法回答 |
| T4 | 跨條引用連動題 | 如 §35 第 4 項引用第 1 項，context_refs 需連動檢索 |
| T5 | pending 分流題 | 意圖開閘三條件成立時才進入隔離庫 |
