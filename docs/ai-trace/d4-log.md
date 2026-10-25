# D4 修正紀錄

實作期發現的問題與修正，依 SDD v1.0 D4 流程記錄（不重開設計討論）。

| 日期 | 問題 | 修正 | 影響 |
| --- | --- | --- | --- |
| 2026-10-25 | §35 第 6 項舊文不能標為現行有效：憲法法庭 111 年憲判字第 1 號對強制採血規定設有失效期限 | 該項自 B（現行法庫）排除，改以 §16 補足五份樣本 | Muse／Cue 測試前提同步更新；原因留存 manifest audit |
| 2026-10-25 | 官方整編頁同時載有尚未生效的 2026-08-17 §35 修正與 §92-2；若視為單一現行版本會混入 pending 罰額。repo 無版控語料樣本，RAG 01 實際 ZIP／metadata 尚無法在此驗收。 | T1/T4 把 §35 core 舊版與 pending 新版分 package、namespace/status；T3 驗 B 拒答／A 三閘門。RAG02 按老師四檔封裝分開載入並驗 hash、模型、metadata、namespace/status；缺欄或版本不符就 fail closed；未實測均標 `NOT RUN`。 | RAG02 路由與驗收骨架完成；實際 RAG01 封裝相容性、檢索命中及 HO Colab 執行待樣本驗收，不宣稱通過。 |
| 2026-10-25 | 作業七最新公告指定 RAG01 core／pending 匯出檔名為 `rag-data.zip`／`rag-data-pending.zip`；issue 尚無已託管的公開直連 URL，不能沿用 `vector_embedding*.zip` 或捏造連結。 | RAG02 改用正式檔名；開頭設定 HTTPS URL cell，檢查 ZIP、拒絕 GitHub／GitHubusercontent raw 與 URL 帳密；pending URL 僅 A 模式必填並下載，B 不下載／載入。 | URL 是 PM 託管後填入的部署期輸入，未測真實 URL；測試用假網路。PM 後續填值並由 HO 在 Colab 實跑。 |
