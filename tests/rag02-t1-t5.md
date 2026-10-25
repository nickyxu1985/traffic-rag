# RAG 02 驗收題組 T1–T5

本測試按 SDD v1.0 驗證 retrieval 與 generation 兩層。每筆都要記錄實際 package、chunk_id、條號／項次、生效狀態、`context_refs`、回答引用及人工 claim review。Repo 目前沒有已版控語料樣本；下列「預期命中」是依官方法規版本及 SDD 定義的驗收目標，不代表已在向量庫命中。未經 HO 在 Colab 實跑一律為 `NOT RUN`。

## 固定規則與來源

- **core 基準**：採截至本題組基準日仍生效的條文版本；不可把 2026-08-17 修正而官方頁面標示尚待施行的 §35 新版數字放進 core。官方現行全文與施行狀態：[全國法規資料庫《道路交通管理處罰條例》](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=K0040012)。官方沿革列明 2026-08-17 修正 §35 的施行日期由行政院另定：[法規沿革](https://law.moj.gov.tw/LawClass/LawHistory.aspx?pcode=K0040012)。
- **§35 core 對照文本**：官方歷史版本（修正日期 2026-01-14）[《道路交通管理處罰條例》歷史法規全文](https://law.moj.gov.tw/LawClass/LawOldVer.aspx?pcode=K0040012)。此版本第35條第1項原文包含：「機車駕駛人處新臺幣一萬五千元以上九萬元以下罰鍰，汽車駕駛人處新臺幣三萬元以上十二萬元以下罰鍰，並均當場移置保管該汽機車及吊扣其駕駛執照一年至二年；附載未滿十二歲兒童或因而肇事致人受傷者，並吊扣其駕駛執照二年至四年；致人重傷或死亡者，吊銷其駕駛執照，並不得再考領：一、酒精濃度超過規定標準。二、吸食毒品、迷幻藥、麻醉藥品或其相類似之管制藥品。」
- **點數對照文本**：[全國法規資料庫第63條](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=K0040012&flno=63)第1項原文：「經當場舉發者，並得依對行車秩序及交通安全危害程度記違規點數一點至三點。」第2項原文：「前項情形，已受吊扣或吊銷駕駛執照處分者，不予記違規點數。」T1 必須同時檢索兩項，區分一般記點範圍及 §35 第1項已受吊扣／吊銷時的不記點條件。
- **pending 對照**：官方現行全文載明 2026-08-17 修正第35條，施行日期由行政院另定；該版第35條第1項列機車新臺幣 18,000 元以上 120,000 元以下、汽車 36,000 元以上 150,000 元以下。此段只可作為 pending 測試證據，不能混入 core 回答。官方全文對第92-2條亦標示尚未生效資訊：[第92-2條](https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=K0040012&flno=92-2)。是否顯示具體施行日期，以各 chunk metadata 的 `effective_date`／`預定施行日期` 為準；不能把日期寫死。

> 官方資料庫可能同時展示現行與尚未生效修正文字。RAG 回答以封裝內版本與 metadata 為準；本節外部來源只用於測試預期及人工核對，不得繞過檢索直接回答。

## 測試案例

### T1 — 精確金額、車種、條件、點數與吊扣

**問題**：機車與汽車駕駛經測試檢定符合第35條第1項第1款或第2款時，罰鍰範圍和吊扣期限各是多少？附載未滿12歲兒童、肇事致人受傷，或致人重傷／死亡時如何變化？一般違規點數何時記1至3點，而第35條這些情形如何判斷？

**模式／預期檢索**：B；core。須命中 `core:` namespace 的第35條第1項（含第1項第1、2款）、第63條第1項及第63條第2項；metadata 均為 `current`。期望 article/item：`35 / 1`、`63 / 1`、`63 / 2`。若 chunk 的 `context_refs` 指向上述配套條文，需記錄其連動結果。

**通過條件**：回答精確引用機車 15,000–90,000 元、汽車 30,000–120,000 元；一般吊扣 1–2 年；附載未滿12歲兒童或肇事致人受傷為 2–4 年；致人重傷或死亡為吊銷且不得再考領。一般點數須說明第63條第1項「經當場舉發」及依危害程度記1–3點；就已受吊扣／吊銷的 §35 情形，依第63條第2項不予記點。不得把官方 pending 新版金額 18,000–120,000／36,000–150,000 混入。金額與處分須附可追溯到命中 chunk 的原文引句及 citation。

**實測紀錄**：檢索 package／chunk_id／條號項次／status：`NOT RUN`；生成引用檢查：`NOT RUN`；主張人工覆核：`PENDING`；整體：`NOT RUN`。

### T2 — 範圍外條文與 §92-2 的 B 版拒答

**問題**：請依本資料庫告訴我第92-2條修正後，哪些失智症或體格變化情形會影響駕駛資格、會如何註銷駕照？

**模式／預期檢索**：B；只能檢索 core。不得載入或查詢 pending；對應 `第92-2條` 的 core 命中應為零，禁止任何 `pending:` chunk。

**通過條件**：答「本資料庫查不到相關條文，因此無法依本資料庫回答。」或等義的資料庫範圍拒答。不得說「法律沒有規定」、不得回答該條內容、施行日期、適用條件或法律效果，也不得用模型記憶補充。

**實測紀錄**：實際 core 命中／是否呼叫 pending：`NOT RUN`；拒答文字與法律效果 claim review：`PENDING`；整體：`NOT RUN`。

### T3 — 同一 §92-2：B 拒答、A 條件式 pending 警告

**T3-B 問題**：同 T2，並問「第92-2條目前生效了嗎？」

**預期**：B 只查 core，不能看到 `pending:92-2`；若 core 無對應資料，按 T2 拒答，不回答生效狀態。

**T3-A 問題**：請問 2025-11-19 增訂的《道路交通管理處罰條例》第92-2條何時施行？請依資料庫中的對應條文與 metadata 回答。

**模式／預期檢索**：A；先通過明確修正／施行狀態意圖，再從 pending 命中對應第92-2條，且 metadata 明確標記 `not_yet_effective`（或 schema `生效狀態: pending`）。期望 namespace `pending:`、article `92-2`；只因 core miss 不得開閘。

**通過條件**：A 答案第一句須是尚未生效警告；只依命中 pending chunk 作答。若 metadata 有 `effective_date`／`預定施行日期` 值，顯示該值；只有 absent/null/unknown 才寫「本資料庫 metadata 未提供可確認的施行日期（施行日期未定）。」不得固定寫「未定」，也不得從外部頁面補值。引用須對應實際 pending chunk。A 的 pending 命中不改變 B 的拒答結果。

**實測紀錄**：B 檢索／回答：`NOT RUN`；A 意圖閘／pending hit/status/date／引用：`NOT RUN`；主張人工覆核：`PENDING`；整體：`NOT RUN`。

### T4 — §35 第4項引用第1項的同包連動與版本隔離

**T4-core 問題**：第35條第4項說的「拒絕接受第一項測試檢定」是指哪些測試情形？拒測罰鍰及駕照處分為何？

**預期檢索**：B/core 命中 `第35條第4項`，並依該 chunk 的 `context_refs` 在**同一 core package**連動命中 `第35條第1項`；不得跨到 pending。metadata status 均為 current，且屬同一 core 封裝／manifest baseline。個別項次的 `修正日期` 可不同，須如實記錄，不可把日期相異誤判成版本混用。

**T4-pending 問題**：請問 2026-08-17 修正公布的第35條第1項，汽車與機車的新罰鍰範圍及施行日期是什麼？

**預期檢索**：A；明確修正與施行日期意圖後，pending package 命中第35條第1項，status 為尚未生效。若 pending package 沒有對應命中或 metadata 不能證明 pending，必須拒絕作答而不得用 core 舊版代答。

**通過條件**：core 子案例須記錄第4項 → 第1項 `context_refs` 關係；不得漏掉被引用條文。版本比較子案例如有 pending 證據，引用 pending 版數字（機車 18,000–120,000 元、汽車 36,000–150,000 元），並先顯示警告與 metadata 日期；不得在同一答案把 core 舊版與 pending 新版拼成單一適用金額。答案只可引用實際命中的同版本 chunks。

**實測紀錄**：core 子案例實際兩項 hit／context_refs／版本：`NOT RUN`；pending 子案例 hit/status/date／引用：`NOT RUN`；人工版本混用覆核：`PENDING`；整體：`NOT RUN`。

### T5 — 模糊路由先澄清，且只問必要條件

**T5-A 問題**：新法會怎麼影響交通罰則？

**預期**：A 判定意圖不明（沒有明確說要查修正內容或施行狀態），先問使用者是要查 core 現行資料，還是某一修正案／施行狀態；不得先搜尋 pending，也不得只因 core miss 進 pending。澄清問題不可先透露任何未檢索的條文內容。

**T5-B 問題**：我是汽車駕駛，酒測超過標準；想知道第35條的罰鍰，近十年是否有相同違規我不確定。需要補充什麼？

**預期**：B/core；車種和酒測超標事實已給定。若要判斷個人精確金額，唯一優先補問的是近十年內第35條相關違規次數／是否為再犯；不應再問車種、酒測數值、乘客年齡、事故細節或身份資料。若資料只支持條文範圍，先列出分支並說明限制，不得裝作已知再犯次數。

**通過條件**：人工確認澄清只涵蓋會改變所問答案的缺失資訊；T5-A 沒有 pending 檢索；T5-B 沒有不必要追問或法律效果推論。若實際條文要求其他必要條件，須在人工 review 記錄其命中來源與原因，不可機械套用預設問題。

**實測紀錄**：A classifier／pending search flag：`NOT RUN`；B 追問文字／命中證據：`NOT RUN`；必要性人工覆核：`PENDING`；整體：`NOT RUN`。

## 逐項結果模板

| Case | Mode | Expected package/article/item/status | Actual chunk_id/article/item/status/context_refs | Retrieval PASS/FAIL | Answer citations/quotes | Penalty/version claim review | Unneeded questions/legal-effect claims | Overall |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | B | core / §35(1), §63(2) / current | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T2 | B | core / §92-2 no relevant hit / — | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T3-B | B | core / §92-2 no relevant hit / — | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T3-A | A | pending / §92-2 / not_yet_effective | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T4-core | B | core / §35(4) + §35(1) / same current version | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T4-pending | A | pending / §35(1) / not_yet_effective | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T5-A | A | no pending search until clarified | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |
| T5-B | B | core / §35 relevant item(s) / current | NOT RUN | NOT RUN | NOT RUN | PENDING | PENDING | NOT RUN |

檢索 PASS 只代表命中 package、chunk、條號／項次及生效狀態符合預期。生成 PASS 仍須人工逐項核對每個金額、期限、條件、引用與原文；沒有 Colab 實測證據就維持 `NOT RUN`。
