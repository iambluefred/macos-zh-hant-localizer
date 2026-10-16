# macOS 繁體中文化工具

幫**有簡體中文、但沒有繁體中文**的 Mac App 產生台灣繁體翻譯（`zh-Hant.lproj`）。

- 使用 [OpenCC](https://github.com/BYVoid/OpenCC) 的 `s2twp`（簡體 → 台灣繁體＋常用詞彙，例如 文件→檔案、视频→影片、设置→設定）
- 再用 `convert_lproj.py` 裡的修正表處理 OpenCC 轉得不自然的詞（釋出→發布、選中→選取、幫助→說明…）
- 只轉翻譯後的文字，`.strings` 的 key、格式符號（`%@`、`%d`）與檔案格式（UTF-16／UTF-8／二進位 plist）都保持不變
- **不會修改 App 本身**；產生的翻譯放在 `output/`

## 用法

```bash
./localize.sh /Applications/某某.app
```

第一次執行會自動建立 Python 環境並安裝 OpenCC。完成後：

1. 先備份 App
2. 在 Finder 對 App 按右鍵 →「顯示套件內容」→ `Contents` → `Resources`
3. 把 `output/<App 名稱>/zh-Hant.lproj` 拖進 `Resources`（macOS 會要求確認）
4. 結束並重新開啟 App；系統語言第一順位是繁體中文時就會顯示繁體

注意：

- 放進 App 的是**資料夾本身**，不能用替身或符號連結（沙盒 App 讀不到 App 外面的檔案）
- App 更新後會被覆蓋，需要重新放一次
- 原本簡體版沒翻譯的部分，繁體版也會維持英文
- 修改他人的 App 只供個人使用；轉出來的翻譯屬於原作者，請勿公開散布（`output/` 已排除在 git 之外）

## 修正詞彙

發現轉得不好的詞，加到 `convert_lproj.py` 的 `FIXES`（部分取代）或 `EXACT`（整段相同才取代）。
