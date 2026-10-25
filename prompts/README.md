# prompts

Cue 維護。RAG 02 Colab 的 prompt 版本化存放：

- system 人設（罰則問答助理，回答必附條號）
- B 版（現行法單庫）回答格式
- A 版（分流：意圖開閘三條件成立 → 進 pending 隔離庫）

## 命名慣例

`v<編號>-<版本>-<用途>.md`，例如 `v1-b-answer-format.md`、`v1-a-pending-gate.md`

## 為什麼進 repo

- 繳交**註三**要求 Prompt 留痕（Prompt 與生成結果截圖）：每版入 repo 即為證據鏈
- 分流 prompt（A 版）是本專案最高風險工件，版本化才能對照 T5 題組驗收
