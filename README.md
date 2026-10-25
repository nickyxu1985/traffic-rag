# traffic-rag

TAICA 生成式 AI 課程・**第七週作業「打造自己的 RAG 對話機器人」**實作 repo（正式公告「第七週作業1020」）。

**主題（案 A）**：交通規則罰則問答系統——以《道路交通管理處罰條例》為語料，採雙庫物理隔離架構：

- `core`：現行有效法規庫（固定基準日）
- `pending`：未生效法規隔離庫（另跑、不混入主庫）

## 目錄結構

| 路徑 | 用途 |
| --- | --- |
| `rag-data/core/` | 現行法語料（五份小樣本起步，驗收通過後擴全量） |
| `rag-data/pending/` | 未生效法規隔離區（三份樣本） |
| `rag-data/metadata-schema.md` | metadata 欄位單一真相（manifest 相容性驗收依據） |
| `colab/` | 兩份 notebook 版控（rag01＝Muse、rag02＝Cue；executed/ 執行版留痕） |
| `prompts/` | RAG 02 prompt 版本化（Cue 維護；繳交註三證據鏈） |
| `tests/` | 驗證題組 T1–T5（數字題、查無題、生效狀態題等） |
| `docs/ai-trace/` | AI 使用留痕與 D4 修正紀錄（繳交註三必備） |
| `handoff/` | 編號交接檔 |
| `AGENTS.md` | 角色→權限邊界矩陣、流程、分支紀律 |
| `.github/` | issue／PR templates（issue 即任務市場） |

## 資料流

1. 語料切塊（一條一檔、長條按項），放入 `rag-data/`
2. 打包語料 zip 供 RAG 01 讀取
3. `colab/rag01-build-vector-db.ipynb` 於 Colab 執行建向量庫，**依作業規定匯出為 `rag-data.zip`**（＋pending 隔離包 `rag-data-pending.zip`），上傳雲端取得可下載網址
4. `colab/rag02-chatbot.ipynb` **從雲端網址載入 rag-data.zip**，搭配 LLM 完成罰則問答機器人

## 繳交要點（作業七正式規定，2026-10-25 核對）

- **截止 11/02（一）23:59**；遲交至 11/03 16:00；系統自 10/20 18:00 起接受繳交
- 繳交標題：學號 系級 姓名 主題（主題可不打，系級打簡稱）
- 內容必含：**RAG02 Colab 連結（共用權限打開、重點處 Markdown 註明）**、重點截圖、**說明所使用的資料為何**、人設／背景設定、Gradio 對話結果
- **程式須內含讀取 zip 雲端可下載網址的 cell（助教才能執行）**；repo 為 private，勿用 GitHub raw link，zip 上傳雲端（如雲端硬碟）轉直鏈
- 註一：未引入老師固定套件總分 -1；註二：權限未開／非 Colab 連結／無法完整執行＝0–4 分級；註三：AI 協作須特別說明＋理解後說明＋Prompt 與生成結果截圖，否則當抄襲 AI；註四：抄襲＝該次 0 分＋總成績 -10
- 評分：7–9＝有趣主題完成對話機器人、10＝完美、主題有趣 +1；與老師範例（校園社團資料）相似僅 6 分

## 切塊與命名慣例

- 一條一檔：`art35.txt`；長條按項：`art35_para6.txt`
- 增訂條文用連字號：`art35-2.txt`
- metadata 必含：條號、章、修正日期、生效狀態（schema 見 `rag-data/metadata-schema.md`）
- 回答必附條號

## Embedding

沿用課程指定：google/embeddinggemma-2

## 設計文件

SDD v1.0（A/B 解耦六規則 D1–D6、分流三條件、題組 T1–T5）定稿存於 Vibe Canvas（traffic-rag-sdd）。
