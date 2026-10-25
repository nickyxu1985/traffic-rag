# colab — 兩份 notebook 的版本控制

| 檔案 | 用途 | 負責人 |
| --- | --- | --- |
| `rag01-build-vector-db.ipynb` | RAG 01 建向量庫（core 主庫＋pending 隔離庫） | Muse（issue #3） |
| `rag02-chatbot.ipynb` | RAG 02 RAG 對話機器人（檢索＋prompt＋Gradio） | Cue（issue #1） |
| `executed/` | 執行版留痕（帶 output，檔名帶日期） | HO 每次跑完存入 |

## 版控規則

1. **主檔案 commit 前清空所有 output**——保持 diff 可讀、避免 cell 計數數字亂跳產生假衝突（Colab → 編輯 → 清除所有輸出 → 下載 .ipynb → commit）。
2. 帶 output 的執行版以 `rag01-YYYYMMDD.ipynb` 命名存 `executed/`：繳交**註三**的 AI 留痕證據；最終繳交仍以 Colab 連結（權限打開）＋重點處 Markdown 註明為準。
3. **一份 notebook 一個 owner**：rag01＝Muse、rag02＝Cue；不跨改，merge 衝突以 owner 版本為準。
4. Colab 同步循環：agent 改 repo → HO 用 Colab 開 GitHub 檔案（colab.research.google.com/github/nickyxu1985/traffic-rag/blob/main/colab/…）或直接上傳 → 執行 → 下載 .ipynb、清 output → commit 回 `agent/<name>-*` 分支。
5. **老師模板為基底**：yenlung.me/rag01colab／rag02colab；固定套件清單以老師版為準（未引入總分 -1）；改編處在 notebook 內以 Markdown 註明。
