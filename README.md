# 📺 TVBox 配置快速驗證與過濾匯出工具 (群暉 NAS 專用離線版)

本項目採用 **Python + Flask** 實現，專為私有雲及群暉 NAS (DSM) 內網隔離環境進行了深度高容錯優化。採用**「零外部網頁依賴、純內存直讀」**架構，專門適配 TVBox 影視爬蟲 JSON 的 `api_site` 結構，100% 免疫任何大檔案卡死與 Docker 快取衝突。

---

## ✨ 功能模組說明

### 🟢 方案 A：綠色功能項目 (本機電腦匯入)
* **控制核心**：採用標準行內 Event 與修正後的 `FileReader(input.files[0])` 指標。
* **運作方式**：點擊綠色按鈕可直接調用您當前電腦的檔案瀏覽器，選取本地的 `.json` 配置。內容會瞬間 100% 完整灌入預覽框中，完全不經由網絡傳輸，零延遲。

### 🔵 方案 B：藍色功能項目 (NAS 目錄讀取)
* **控制核心**：自動掃描群暉掛載的實體本地 `./data` 資料夾。
* **運作方式**：網頁加載時自動抓取該目錄下的 `.json`、`.txt` 檔案並生成下拉選單。選中後點擊「載入」，後端會直接從 NAS 硬碟直讀內容並填入預覽區。

### 📥 共同核心功能 (一鍵打包導出)
* **運作方式**：不論使用方案 A 還是方案 B，點擊開始批量驗證後，背景將開啟多線程對所有影視站點 API 進行 1.5 秒硬超時測速。驗證完成後自動解鎖藍色按鈕，點擊即可秒級下載已自動剔除全部失效線路、只保留 100% 滿分可用線路的全新配置檔案。

---

## 🚀 部署指南 (Deployment Guides)

本項目提供 **單獨部署方案 A**、**單獨部署方案 B** 以及 **A+B 同時部署(完全體)** 的完整 Docker 建立方式。請根據您的需求，在群暉 **File Station** 的 `/docker/tvbox-checker/` 目錄下建立對應的 `app.py` 檔案。

### 📌 模組一：單純部署 A（只保留綠色功能：本機電腦匯入）

#### 1. 撰寫 `app.py` 程式碼
```python
# (此處放置僅包含方案 A 綠色按鈕前端 HTML、parse_source_text、upload_and_test、progress、export_clean_json 路由的 Python 代碼)
# 註：此版本移除了 /list_files 與 /load_file 後端路由及前端的藍色方案 A HTML 區塊。
```
#### 2. 群暉 SSH 終端機一鍵極速部署：
```bash
cd /volume1/docker/tvbox-checker && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

### 📌 模組二：單純部署 B（只保留藍色功能：NAS data/ 目錄讀取）

#### 1. 撰寫 `app.py` 程式碼
```python
# (此處放置僅包含方案 B 藍色下拉選單、/list_files、/load_file 後端路由及對應驗證、過濾導出路由的 Python 代碼)
# 註：此版本移除了前端的綠色方案 B 按鈕與本機 FileReader 的 JavaScript 腳本。
```
#### 2. 群暉 SSH 終端機一鍵極速部署：
```bash
cd /volume1/docker/tvbox-checker && mkdir -p data && docker rm -f tvbox-checker 2>/dev/null
docker run -d --name tvbox-checker --network host --restart always -v /volume1/docker/tvbox-checker/data:/app/data -w /app python:3.11-slim sh -c "pip install --no-cache-dir Flask==3.0.2 requests==2.31.0 gunicorn==21.2.0 && python app.py"
```

---

### 📌 模組三：A + B 同時部署（雙源相容匯出完全體）—— 👑 推薦

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

## 💡 使用與驗證

1. **打開網頁**：強烈建議開啟電腦瀏覽器的 **「無痕分頁（隱私模式）」**，訪問 `http://[您的群暉NAS內網IP]:5000`。
2. **導入配置**：
   * **使用方案 A**：點擊綠色按鈕選取本機 `.json` 檔案。
   * **使用方案 B**：將 `.json` 檔案丟進群暉的 `data/` 資料夾中，在網頁藍色下拉選單中選中並點擊「載入」。
3. **批量驗證**：點擊紅色的 **「🚀 開始批量驗證」**。右側列表會實時跳動並對 78 個（或更多）影視線路進行 1.5 秒硬超時篩選。
4. **一鍵導出**：驗證完成後自動解鎖藍色按鈕，點擊即可秒級下載過濾後的乾淨 JSON 檔案。

## 📄 開源協議 (License)

本項目基於 **MIT License** 協議開源。
