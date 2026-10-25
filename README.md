# traffic-rag

TAICA 生成式 AI 課程・第六週作業「打造你的 RAG 系統」實作 repo。

**主題（案 A）**：交通規則罰則問答系統——以《道路交通管理處罰條例》為語料，採雙庫物理隔離架構：

- `core`：現行有效法規庫（固定基準日）
- `pending`：未生效法規隔離庫（另跑、不混入主庫）

## 目錄結構

| 路徑 | 用途 |
| --- | --- |
| `rag-data/core/` | 現行法語料（五份小樣本起步，驗收通過後擴全量） |
| `rag-data/pending/` | 未生效法規隔離區（三份樣本） |
| `rag-data/metadata-schema.md` | metadata 欄位單一真相（manifest 相容性驗收依據） |
| `prompts/` | RAG 02 prompt 版本化（Cue 維護；繳交註三證據鏈） |
| `tests/` | 驗證題組 T1–T5（數字題、查無題、生效狀態題等） |
| `docs/ai-trace/` | AI 使用留痕與 D4 修正紀錄（繳交註三必備） |
| `handoff/` | 編號交接檔（當前狀態／未完成／已知問題／交接對象） |
| `AGENTS.md` | 角色→權限邊界矩陣、流程、分支紀律 |
| `.github/` | issue／PR templates（issue 即任務市場） |

## 資料流

1. 語料切塊（一條一檔、長條按項），放入 `rag-data/`
2. 打包 `rag-data.zip`
3. RAG 01 Colab（yenlung.me/rag01colab）建向量資料庫，匯出 `vector_embedding.zip`
4. RAG 02 Colab（yenlung.me/rag02colab）讀取向量庫，完成罰則問答機器人

## 切塊與命名慣例

- 一條一檔：`art35.txt`；長條按項：`art35_para6.txt`
- 增訂條文用連字號：`art35-2.txt`
- metadata 必含：條號、章、修正日期、生效狀態（schema 見 `rag-data/metadata-schema.md`）
- 回答必附條號

## Embedding

沿用課程指定：google/embeddinggemma-2

## 設計文件

SDD v1.0（A/B 解耦六規則 D1–D6、分流三條件、題組 T1–T5）定稿存於 Vibe Canvas（traffic-rag-sdd）。
