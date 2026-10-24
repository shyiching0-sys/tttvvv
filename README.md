# 📺 TVBox 配置快速驗證與過濾匯出工具 (群暉 NAS 專用離線版)

本項目採用 **Python + Flask + Gunicorn** 實現，專為私有雲及群暉 NAS (DSM) 內網隔離環境進行了深度高容錯優化。採用**「零外部網頁依賴、純內存直讀」**架構，專門適配 TVBox 影視爬蟲 JSON 的 `api_site` 結構，100% 免疫任何大檔案卡死與 Docker 快取衝突。

---

## 📸 運作畫面預覽 (Project Preview)

以下為群暉 NAS 實機部署成功後的網頁控制台界面：

![TVBox Checker 運行畫面預覽](images/preview.png)

---

## ✨ 功能模組說明

### 🔵 方案 A：讀取 NAS data/ 目錄檔案 (原廠硬碟直讀)
* **控制核心**：自動掃描群暉掛載的實體本地 `./data` 資料夾。
* **運作方式**：網頁加載時自動抓取該目錄下的 `.json`、`.txt` 檔案並生成下拉選單。選中後點擊「載入」，後端會直接從 NAS 硬碟直讀內容並填入預覽區。

### 🟢 方案 B：從本機電腦匯入檔案 (瀏覽器背景直傳)
* **控制核心**：採用標準行內 Event 與修正後的 `FileReader(input.files[0])` 異步指標。
* **運作方式**：點擊綠色按鈕可直接調用您當前電腦的檔案瀏覽器，選取本地的 `.json` 配置。內容會瞬間 100% 完整灌入預覽框中，完全不經由網絡傳輸，零延遲。

### 📥 共同核心功能 (一鍵打包導出)
* **運作方式**：不論使用方案 A 還是方案 B，點擊開始批量驗證後，背景將開啟多線程對所有影視站點 API 進行 1.5 秒硬超時測速。驗證完成後自動解鎖藍色按鈕，點擊即可秒級下載已自動剔除全部失效線路、只保留 100% 滿分可用線路的全新配置檔案。

---

## 🚀 部署指南 (Deployment Guides)

本項目提供 **單純部署方案 A**、**單純部署方案 B** 以及 **A+B 同時部署(完全體)** 的完整 Docker 建立方式。請根據您的需求，在群暉 **File Station** 的 `/docker/tvbox-checker/` 目錄下建立對應的 `app.py` 檔案。

### 👑 👑 A + B 同時部署（雙源相容匯出完全體 - 推薦）

#### 1. 撰寫 `app.py` 原始碼
請直接使用我們最終調試成功、100% 完好無截斷的完全體代碼寫入 `/volume1/docker/tvbox-checker/app.py`。

#### 2. 群暉 SSH 終端機一鍵極速部署：
```bash
cd /volume1/docker/tvbox-checker && mkdir -p data && docker rm -f tvbox-checker 2>/dev/null
docker run -d \
  --name tvbox-checker \
  --network host \
  --restart always \
  -v /volume1/docker/tvbox-checker/app.py:/app/app.py \
  -v /volume1/docker/tvbox-checker/data:/app/data \
  -w /app \
  python:3.11-slim \
  sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

### 📌 模組二：單純部署 A（只保留本機電腦匯入功能）

#### 1. 撰寫 `app.py` 原始碼
*(此版本移除了 /list_files 與 /load_file 後端路由及前端的藍色方案 A HTML 區塊)*

#### 2. 群暉 SSH 終端機一鍵極速部署：
```bash
cd /volume1/docker/tvbox-checker && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

### 📌 模組三：單純部署 B（只保留 NAS data/ 目錄讀取功能）

#### 1. 撰寫 `app.py` 原始碼
*(此版本移除了前端的綠色方案 B 按鈕與本機 FileReader 的 JavaScript 腳本)*

#### 2. 群暉 SSH 終端機一鍵極速部署：
```bash
cd /volume1/docker/tvbox-checker && mkdir -p data && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -v /volume1/docker/tvbox-checker/data:/app/data -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

## 💡 使用與驗證

1. **打開網頁**：強烈建議開啟電腦瀏覽器的 **「無痕分頁（隱私模式）」**，訪問 `http://[您的群暉NAS內網IP]:5000`。
2. **導入配置**：
   * **使用方案 A**：在網頁藍色下拉選單中選中並點擊「載入」（需先將檔案放入 NAS 的 `data/` 資料夾中）。
   * **使用方案 B**：點擊綠色按鈕選取本機 `.json` 檔案。
3. **批量驗證**：點擊紅色的 **「🚀 開始批量驗證」**。右側列表會實時跳動並對 78 個（或更多）影視線路進行 1.5 秒硬超時篩選。
4. **一鍵導出**：驗證完成後自動解鎖藍色按鈕，點擊即可秒級下載過濾後的乾淨 JSON 檔案。

## 📄 開源協議 (License)

本項目基於 **MIT License** 協議開源。
