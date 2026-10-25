# 語料 metadata schema（單一真相，v0.2）

> v0.1→v0.2（2026-10-25）：新增 `source_ref` 溯源欄（PM 定調：語料切分以 `raw/` 官方 PDF 原檔為準）。
> 待與 Instinct 的 manifest-bundle 逐項對齊後升版；衝突以 SDD v1.0＋manifest 為準，HO 拍板。

Muse 的 manifest 相容性驗收、Cue 的引用／分流驗收，以本表為欄位依據。

| 欄位 | 型別 | 必填 | 說明 |
| --- | --- | --- | --- |
| id | string | ✓ | 檔名主鍵，如 `art35`、`art35_para6`、`art35-2` |
| 條號 | string | ✓ | 如「第 35 條第 6 項」 |
| 章 | string | ✓ | 所屬章名 |
| 修正日期 | date | ✓ | 官方發布日 |
| 生效狀態 | enum | ✓ | `current`／`pending`（§92-2 依官方資訊屬 pending，作負面測例不進現行庫） |
| 預定施行日期 | date | pending 必填 | **條件式**：effective_date 有值即顯示該日期，不得寫死「施行日期未定」 |
| source_ref | string | ✓ | **溯源定位**：`raw/` 原檔檔名＋頁碼/條號定位；切塊文字以 `raw/` 官方 PDF 為準（端到端溯源） |
| context_refs | string[] | 引用他條時 | 如 §35 第 4 項引用第 1 項；需同包連動實測（T4 題組） |
