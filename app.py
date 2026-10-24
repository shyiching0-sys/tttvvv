import os, json, time, concurrent.futures, requests, threading
from flask import Flask, jsonify, request, Response
app = Flask(__name__)
test_status = {"is_running": False, "total": 0, "current": 0, "results": []}
original_json_data = {}
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
def verify_single_url(name, url, key_id):
    start_time = time.time()
    try:
        res = requests.head(url, timeout=1.5, allow_redirects=True)
        if res.status_code >= 400: res = requests.get(url, timeout=1.5, stream=True)
        elapsed = (time.time() - start_time) * 1000
        if res.status_code == 200:
            score = max(50, 100 - int(elapsed / 50))
            return {"name": name, "url": url, "key_id": key_id, "status": "可用", "code": res.status_code, "delay": f"{elapsed:.0f}ms", "score": score, "style": "bg-ok"}
    except: pass
    return {"name": name, "url": url, "key_id": key_id, "status": "失效", "code": "Timeout", "delay": "-", "score": 0, "style": "bg-fail"}
def parse_source_text(raw_data):
    global original_json_data
    source_list = []
    raw_data = raw_data.strip()
    if not raw_data: return []
    if raw_data.startswith('{') or raw_data.startswith('['):
        try:
            parsed = json.loads(raw_data)
            original_json_data = parsed
            if isinstance(parsed, dict) and "api_site" in parsed:
                for k, item in parsed["api_site"].items():
                    if isinstance(item, dict) and "api" in item:
                        source_list.append({"name": item.get("name", k), "url": item.get("api", ""), "key_id": k})
                return [s for s in source_list if s["url"]]
        except: pass
    return []
@app.route('/')
def index():
    return """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>TVBox 驗證工具</title><style>body{background:#f4f6f9;font-family:sans-serif;padding:20px;color:#333;margin:0;}.container{max-width:1200px;margin:0 auto;}header{border-bottom:2px solid #dee2e6;padding-bottom:15px;margin-bottom:20px;}h1{margin:0;font-size:24px;color:#212529;}.badge-nas{background:#0d6efd;color:white;padding:3px 8px;font-size:14px;border-radius:4px;margin-left:10px;}.row{display:flex;gap:20px;flex-wrap:wrap;}.col-left{flex:5;min-width:320px;}.col-right{flex:7;min-width:450px;}.card{background:white;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.05);padding:20px;margin-bottom:20px;}.card-title{margin-top:0;margin-bottom:15px;font-size:18px;color:#495057;border-bottom:1px solid #eee;padding-bottom:10px;}.form-group{margin-bottom:15px;}.form-label{display:block;font-weight:bold;margin-bottom:5px;font-size:14px;}.form-select,.form-control{width:100%;padding:8px;border:1px solid #ced4da;border-radius:4px;box-sizing:border-box;font-size:14px;}.btn{display:inline-block;padding:8px 16px;font-size:14px;font-weight:bold;text-align:center;border:none;border-radius:4px;cursor:pointer;}.btn-primary{background:#0d6efd;color:white;}.btn-success{background:#198754;color:white;margin-bottom:10px;}.btn-danger{background:#dc3545;color:white;font-size:16px;width:100%;padding:12px;}.btn:disabled{background:#6c757d;cursor:not-allowed;}.input-group{display:flex;gap:10px;}.import-box{border:2px dashed #198754;border-radius:6px;padding:20px;text-align:center;background:#f8fff9;}.text-muted{color:#6c757d;font-size:13px;}.d-none{display:none!important;}.progress-wrapper{background:#e9ecef;border-radius:6px;overflow:hidden;height:25px;margin-top:10px;}.progress-bar{background:#198754;height:100%;width:0%;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;}.report-grid{display:flex;gap:15px;text-align:center;margin-top:10px;}.report-item{flex:1;border:1px solid #dee2e6;border-radius:6px;padding:10px;background:#f8f9fa;}.report-item h3 {margin:5px 0;font-size:24px;}.table-container{max-height:500px;overflow-y:auto;border:1px solid #dee2e6;border-radius:6px;}table{width:100%;border-collapse:collapse;text-align:left;font-size:14px;}th,td{padding:12px;border-bottom:1px solid #dee2e6;}th{background:#f8f9fa;position:sticky;top:0;z-index:1;}.bg-ok{background:#d1e7dd!important;color:#0f5132;}.bg-fail{background:#f8d7da!important;color:#842029;}.badge-status{padding:3px 6px;border-radius:4px;font-size:12px;font-weight:bold;color:white;}.bg-success-badge{background:#198754;}.bg-danger-badge{background:#dc3545;}.badge-score{background:#6c757d;color:white;padding:3px 6px;border-radius:4px;font-weight:bold;}</style></head><body><div class="container"><header><h1>📺 TVBox 訂閱源與流媒體快速驗證工具 <span class="badge-nas">群暉專用獨立安全版-內存完全體</span></h1></header><div class="row"><div class="col-left"><div class="card"><h3 class="card-title">📂 1. 導入數據源</h3><div class="form-group" style="background:#f1f3f5;padding:12px;border-radius:6px;border:1px solid #e9ecef;margin-bottom:15px;"><label class="form-label" style="color:#0d6efd;">【方案 A】讀取 NAS data/ 目錄檔案</label><div class="input-group"><select id="nasSel" class="form-select"><option value="">-- 正在掃描 NAS 目錄 --</option></select><button class="btn btn-primary" type="button" onclick="loadNasFile()">載入</button></div></div><div class="form-group" style="background:#f1f3f5;padding:12px;border-radius:6px;border:1px solid #e9ecef;margin-bottom:15px;"><label class="form-label" style="color:#198754;">【方案 B】從本機電腦匯入檔案</label><div class="import-box"><div class="text-muted mb-2 fw-bold" id="st" style="color:#dc3545;font-size:14px;">❌ 尚未選擇任何本機檔案</div><button type="button" class="btn btn-success" onclick="document.getElementById('fi').click()">📁 點擊選取電腦內的 .json 檔案</button><input type="file" id="fi" style="display:none;" accept=".json" onchange="loadFile(this)"></div></div><div class="form-group"><label class="form-label text-muted">📝 數據手動輸入/編輯區 (大檔案不需填入此框)</label><textarea id="tx" class="form-control" rows="5" style="font-family:monospace;" placeholder="請在此處貼上或透過方案A/B載入您的 api_site 配置 JSON..."></textarea></div><div class="row" style="gap:10px;align-items:flex-end;"><div style="flex:1;"><label class="form-label text-muted" style="font-size:12px;">並發線程數 (1-50)</label><input type="number" id="threads" class="form-control" value="16" min="1" max="50"></div><div style="flex:1;"><button id="btn" class="btn btn-danger" onclick="run()">🚀 開始批量驗證</button></div></div></div></div><div class="col-right"><div class="card d-none" id="progressCard"><div style="display:flex;justify-content:space-between;align-items:center;font-weight:bold;"><span>⏳ 正在測試中...</span><span id="pgText" style="background:#333;color:white;padding:2px 8px;border-radius:4px;">0 / 0</span></div><div class="progress-wrapper"><div id="pBar" class="progress-bar">0%</div></div></div><div class="card d-none" id="reportCard"><h3 class="card-title" style="color:#0d6efd;border:none;margin-bottom:5px;">📊 檢測報告摘要</h3><div class="report-grid"><div class="report-item"><h3 style="color:#198754;" id="okCount">0</h3><small class="text-muted">可用源</small></div><div class="report-item"><h3 style="color:#dc3545;" id="failCount">0</h3><small class="text-muted">失效源</small></div><div class="report-item"><h3 style="color:#ffc107;" id="avgScore">0</h3><small class="text-muted">綜合平均分</small></div></div><div style="margin-top:15px;text-align:right;"><button class="btn btn-primary" id="exBtn" style="display:none;" onclick="exportCleanJson()">📥 一鍵打包下載乾淨的 JSON 檔案</button></div></div><div class="card"><h3 class="card-title">📋 驗證結果清單</h3><div class="table-container"><table><thead><tr><th style="width:55%;">名稱與網址</th><th style="width:15%;">狀態</th><th style="width:15%;">響應延遲</th><th style="width:15%;">評分</th></tr></thead><tbody id="tb"><tr><td colspan="4" class="text-muted" style="text-align:center;padding:30px 0;">暫無數據，請先加載/匯入源清單並開始測試。</td></tr></tbody></table></div></div></div></div></div><script>let tm=null;window.onload=function(){fetchNasList();};function fetchNasList(){fetch("/list_files?t="+new Date().getTime()).then(res=>res.json()).then(data=>{if(data.status==="success"&&data.files){const sel=document.getElementById("nasSel");sel.innerHTML="<option value=''>-- 請選擇 NAS data/ 中的檔案 --</option>";data.files.forEach(f=>{let opt=document.createElement("option");opt.value=f;opt.innerText=f;sel.appendChild(opt);});}});}function loadNasFile(){const fn=document.getElementById("nasSel").value;if(!fn){alert("請先選擇一個 NAS 檔案！");return;}fetch("/load_file",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({filename:fn})}).then(res=>res.json()).then(data=>{if(data.status==="success"){document.getElementById("tx").value=data.content;document.getElementById("st").style.color="#0d6efd";document.getElementById("st").innerText="已加載 NAS 檔案："+fn;}});}function loadFile(input){if(!input.files||input.files.length===0)return;let fileObj=input.files[0];let reader=new FileReader();reader.onload=function(e){document.getElementById("tx").value=e.target.result;document.getElementById("st").style.color="#198754";document.getElementById("st").innerText="📄 已成功載入本機："+fileObj.name+" ("+(fileObj.size/1024).toFixed(1)+" KB)";};reader.readAsText(fileObj);}function run(){const th=document.getElementById("threads").value;const txt=document.getElementById("tx").value;if(!txt.trim()){alert("請先選擇本機檔案、NAS檔案或直接在下方框中輸入數據！");return;}document.getElementById("btn").disabled=true;document.getElementById("exBtn").style.display="none";document.getElementById("progressCard").classList.remove("d-none");document.getElementById("reportCard").classList.add("d-none");let fd=new FormData();fd.append("threads",th);fd.append("sources",txt);fetch("/upload_and_test",{method:"POST",body:fd}).then(res=>res.json()).then(data => {if(data.status==="success"){alert(data.message);if(tm)clearInterval(tm);tm=setInterval(chk,1000);}else{alert(data.message);document.getElementById("btn").disabled=false;}});}function chk(){fetch("/progress?t="+new Date().getTime()).then(res=>res.json()).then(data=>{const tot=data.total;const cur=data.current;const pct=tot>0?Math.round((cur/tot)*100):0;document.getElementById("pgText").innerText=cur+" / "+tot;document.getElementById("pBar").style.width=pct+"%";document.getElementById("pBar").innerText=pct+"%";if(data.results.length>0){document.getElementById("tb").innerHTML=data.results.sort((a,b)=>b.score-a.score).map(i=>`<tr class="${i.style==='table-success'?'bg-ok':'bg-fail'}"><td><b>${i.name}</b><br><small style="color:#6c757d;word-break:break-all;">${i.url}</small></td><td><span class="badge-status ${i.status==='可用'?'bg-success-badge':'bg-danger-badge'}">${i.status} (${i.code})</span></td><td><code>${i.delay}</code></td><td><span class="badge-score">${i.score}</span></td></tr>`).join("");}if(!data.is_running&&cur===tot&&tot>0){clearInterval(tm);document.getElementById("btn").disabled=false;document.getElementById("reportCard").classList.remove("d-none");document.getElementById("exBtn").style.display="inline-block";const ok=data.results.filter(r=>r.status==="可用").length;const fa=tot-ok;const sc=data.results.reduce((s,r)=>s+r.score,0);const av=tot>0?Math.round(sc/tot):0;document.getElementById("okCount").innerText=ok;document.getElementById("failCount").innerText=fa;document.getElementById("avgScore").innerText=av;alert("驗證完成！已為您解鎖一鍵導出乾淨 JSON 功能。");}});}function exportCleanJson(){window.location.href="/export_clean_json";}
</script></body></html>"""

@app.route('/list_files', methods=['GET'])
def list_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith(('.json', '.m3u', '.m3u8', '.txt'))]
        return jsonify({"status": "success", "files": files})
    except Exception as e: return jsonify({"status": "error", "message": str(e)})

@app.route('/load_file', methods=['POST'])
def load_file():
    filename = request.json.get("filename", "")
    safe_path = os.path.abspath(os.path.join(DATA_DIR, filename))
    if not safe_path.startswith(os.path.abspath(DATA_DIR)) or not os.path.exists(safe_path):
        return jsonify({"status": "error", "message": "檔案不存在"})
    try:
        with open(safe_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
        return jsonify({"status": "success", "content": content})
    except Exception as e: return jsonify({"status": "error", "message": str(e)})

@app.route('/upload_and_test', methods=['POST'])
def upload_and_test():
    global test_status
    if test_status["is_running"]: return jsonify({"status": "error", "message": "已有任務運行中"})
    raw_content = request.form.get("sources", "")
    s_list = parse_source_text(raw_content)
    if not s_list: return jsonify({"status": "error", "message": "未能成功抓取到有效 api_site 站點配置！"})
    test_status.update({"is_running": True, "total": len(s_list), "current": 0, "results": []})
    def run_pool():
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as exec:
            futures = {exec.submit(verify_single_url, item['name'], item['url'], item['key_id']): item for item in s_list}
            for f in concurrent.futures.as_completed(futures):
                test_status["results"].append(f.result())
                test_status["current"] += 1
        test_status["is_running"] = False
    threading.Thread(target=run_pool).start()
    return jsonify({"status": "success", "message": f"成功載入 {len(s_list)} 個影視站點，開始同步測速！"})

@app.route('/progress')
def progress(): return jsonify(test_status)

@app.route('/export_clean_json')
def export_clean_json():
    global test_status, original_json_data
    if not test_status["results"]: return "暫無檢測數據", 400
    available_keys = {item["key_id"] for item in test_status["results"] if item["status"] == "可用"}
    clean_json = {}
    if isinstance(original_json_data, dict):
        for k, v in original_json_data.items():
            if k != "api_site": clean_json[k] = v
        if "api_site" in original_json_data:
            clean_json["api_site"] = {}
            for site_key, site_val in original_json_data["api_site"].items():
                if site_key in available_keys: clean_json["api_site"][site_key] = site_val
    else:
        clean_json["api_site"] = {}
        for item in test_status["results"]:
            if item["status"] == "可用": clean_json["api_site"][item["key_id"]] = {"name": item["name"], "api": item["url"]}
    output_json_str = json.dumps(clean_json, ensure_ascii=False, indent=2)
    return Response(output_json_str, mimetype="application/json", headers={"Content-disposition": "attachment; filename=tvbox_clean_site.json"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
