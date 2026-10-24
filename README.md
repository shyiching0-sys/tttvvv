# TVBox-Checker-Synology

專為群暉 NAS (DSM) 內網環境優化的 TVBox 站點配置驗證與過濾匯出工具。採用內存網頁整合架構，支援大檔案背景解析與二進位檔案流導出，具備極高的抗卡死性能。

---

## 📸 運作畫面預覽

![TVBox Checker 運行畫面](images/preview.png)

---

## 📂 檔案目錄結構

```text
tvbox-checker-synology/
├── app.py          # 完全體核心代碼 (免外置網頁)
├── README.md       # 本項目說明文件
└── images/
    └── preview.png # 實機成功運作截圖
```

---

## ✨ 功能模組

### 🟢 方案 A：從本機電腦匯入檔案 (綠色功能項目)
* **特點**：採用純前端 `FileReader` 異步控制。
* **運作**：點擊綠色按鈕直接選取本機 `.json` 配置，內容瞬間導入編輯預覽區，0 網絡傳輸延遲。

### 🔵 方案 B：讀取 NAS data/ 目錄檔案 (藍色功能項目)
* **特點**：實體硬碟直讀。
* **運作**：自動掃描 `./data` 目錄下的配置檔案並生成下拉選單。選中點擊「載入」即可直接讀取數據。

### 📥 共同核心功能 (一鍵打包導出)
* **運作**：點擊開始驗證後，背景啟動多線程對所有影視站點進行 1.5 秒硬超時測速。驗證完成後自動解鎖藍色按鈕，點擊即可秒級下載已自動剔除全部失效線路、只保留 100% 滿分可用線路的全新 JSON 檔案。

---

## 🚀 部署指南

請在群暉 **File Station** 的 `/volume1/docker/tvbox-checker/` 目麗下準備好您的 `app.py`，並新建一個 `data` 資料夾。

根據實際需求，在群暉 SSH 終端機中選擇對應的指令執行部署：

### 👑 方案 1：A + B 同時部署 (完全體 - 推薦)
```bash
cd /volume1/docker/tvbox-checker && mkdir -p data && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -v /volume1/docker/tvbox-checker/app.py:/app/app.py -v /volume1/docker/tvbox-checker/data:/app/data -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

### 📌 方案 2：單純部署 A（只保留綠色功能：本機電腦匯入）
```bash
cd /volume1/docker/tvbox-checker && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -v /volume1/docker/tvbox-checker/app.py:/app/app.py -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

### 📌 方案 3：單純部署 B（只保留藍色功能：NAS data/ 目錄讀取）
```bash
cd /volume1/docker/tvbox-checker && mkdir -p data && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -v /volume1/docker/tvbox-checker/app.py:/app/app.py -v /volume1/docker/tvbox-checker/data:/app/data -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

## 💡 使用指南

1. **訪問網頁**：建議開啟瀏覽器 **「無痕分頁」**，訪問 `http://[群暉IP]:5000`。
2. **數據載入**：點擊綠色按鈕匯入本地檔案（方案 A）或通過藍色選單載入 NAS 檔案（方案 B）。
3. **批量驗證**：點擊紅色按鈕開始測速，右側列表將實時刷新延遲與評分。
4. **一鍵導出**：全部分析完成後，點擊右上角自動解凍的藍色按鈕即可打包下載全新 JSON 配置。

## 📄 開源協議

MIT License
