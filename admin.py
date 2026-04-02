from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
 
router = APIRouter()
 
 
class AdminLoginRequest(BaseModel):
    client_id: str
    pin: str
 
 
@router.get("/admin", response_class=HTMLResponse)
def admin_page():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lead Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: sans-serif; background: #f5f5f5; display: flex; justify-content: center; padding: 40px 20px; }
        .container { width: 100%; max-width: 900px; }
        .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); margin-bottom: 20px; }
        h1 { font-size: 24px; margin-bottom: 8px; }
        h3 { font-size: 16px; margin-bottom: 16px; color: #333; }
        p.subtitle { color: #666; margin-bottom: 32px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus { border-color: #007bff; }
        button { width: 100%; padding: 14px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        .error { margin-top: 16px; padding: 12px; background: #fff0f0; border-radius: 8px; border: 1px solid #ffcccc; color: #c00; display: none; font-size: 14px; }
        #dashboard { display: none; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .dashboard-header h2 { font-size: 20px; }
        .logout-btn { background: none; border: 1px solid #ddd; color: #555; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; width: auto; }
        .logout-btn:hover { background: #f5f5f5; }
        .refresh-btn { background: none; border: 1px solid #007bff; color: #007bff; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; width: auto; }
        .refresh-btn:hover { background: #f0f7ff; }
 
        /* Stats */
        .stats-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
        .stat-box { flex: 1; min-width: 120px; background: #f9f9f9; border: 1px solid #eee; border-radius: 10px; padding: 16px; text-align: center; }
        .stat-box .number { font-size: 32px; font-weight: 700; color: #007bff; }
        .stat-box .label { font-size: 13px; color: #888; margin-top: 4px; }
 
        /* Tabs */
        .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 2px solid #eee; }
        .tab { padding: 10px 20px; cursor: pointer; font-size: 14px; font-weight: 600; color: #888; border-bottom: 2px solid transparent; margin-bottom: -2px; }
        .tab.active { color: #007bff; border-bottom-color: #007bff; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
 
        /* Tables */
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { text-align: left; padding: 10px 12px; background: #f5f5f5; border-bottom: 2px solid #eee; font-weight: 600; color: #555; }
        td { padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #fafafa; }
        .empty { text-align: center; padding: 40px; color: #999; font-size: 14px; }
 
        /* FAQ */
        .faq-item { padding: 14px; background: #f9f9f9; border-radius: 8px; margin-bottom: 10px; font-size: 14px; }
        .faq-count { font-size: 12px; color: #888; margin-top: 4px; }
        .loading-text { color: #888; font-size: 14px; padding: 20px 0; }
 
        /* Chart */
        .chart-container { height: 200px; display: flex; align-items: flex-end; gap: 8px; padding: 10px 0; }
        .bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; height: 100%; justify-content: flex-end; }
        .bar { width: 100%; background: #007bff; border-radius: 4px 4px 0 0; min-height: 2px; transition: height 0.3s ease; }
        .bar-label { font-size: 10px; color: #888; text-align: center; }
        .bar-value { font-size: 11px; color: #555; }
 
        /* Pages */
        .page-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
        .page-item:last-child { border-bottom: none; }
        .page-url { color: #333; word-break: break-all; flex: 1; margin-right: 12px; }
        .page-count { background: #007bff; color: white; border-radius: 12px; padding: 2px 10px; font-size: 12px; white-space: nowrap; }
    </style>
</head>
<body>
    <div class="container">
 
        <!-- Login -->
        <div class="card" id="login-card">
            <h1>Lead Dashboard</h1>
            <p class="subtitle">Enter your Client ID and PIN to view your leads and analytics.</p>
            <div class="field">
                <label>Client ID</label>
                <input type="text" id="client_id" placeholder="e.g. client_a1b2c3d4" />
            </div>
            <div class="field">
                <label>PIN</label>
                <input type="password" id="pin" placeholder="4-digit PIN" maxlength="4"
                    onkeydown="if(event.key==='Enter') login()" />
            </div>
            <button onclick="login()" id="login-btn">View My Dashboard</button>
            <div class="error" id="error-box"></div>
        </div>
 
        <!-- Dashboard -->
        <div id="dashboard">
            <div class="card">
                <div class="dashboard-header">
                    <h2 id="business-title">Dashboard</h2>
                    <div style="display:flex; gap:8px;">
                        <button class="refresh-btn" onclick="loadDashboard()">↻ Refresh</button>
                        <button class="logout-btn" onclick="logout()">Log out</button>
                    </div>
                </div>
 
                <!-- Stats -->
                <div class="stats-row">
                    <div class="stat-box">
                        <div class="number" id="total-chats">0</div>
                        <div class="label">Total Chats</div>
                    </div>
                    <div class="stat-box">
                        <div class="number" id="chats-this-week">0</div>
                        <div class="label">Chats This Week</div>
                    </div>
                    <div class="stat-box">
                        <div class="number" id="total-leads">0</div>
                        <div class="label">Total Leads</div>
                    </div>
                    <div class="stat-box">
                        <div class="number" id="leads-this-week">0</div>
                        <div class="label">Leads This Week</div>
                    </div>
                </div>
 
                <!-- Tabs -->
                <div class="tabs">
                    <div class="tab active" onclick="switchTab('leads')">Leads</div>
                    <div class="tab" onclick="switchTab('faqs')">Top Questions</div>
                    <div class="tab" onclick="switchTab('pages')">Top Pages</div>
                    <div class="tab" onclick="switchTab('volume')">Chat Volume</div>
                </div>
 
                <!-- Leads Tab -->
                <div class="tab-content active" id="tab-leads">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Email</th>
                                <th>Date</th>
                            </tr>
                        </thead>
                        <tbody id="leads-table"></tbody>
                    </table>
                    <div class="empty" id="leads-empty" style="display:none;">
                        No leads yet. They'll appear here when users submit their details.
                    </div>
                </div>
 
                <!-- FAQs Tab -->
                <div class="tab-content" id="tab-faqs">
                    <div class="loading-text" id="faqs-loading">Analysing questions with AI...</div>
                    <div id="faqs-list"></div>
                    <div class="empty" id="faqs-empty" style="display:none;">
                        No questions logged yet. Start chatting to see FAQs appear here.
                    </div>
                </div>
 
                <!-- Pages Tab -->
                <div class="tab-content" id="tab-pages">
                    <div id="pages-list"></div>
                    <div class="empty" id="pages-empty" style="display:none;">
                        No page data yet.
                    </div>
                </div>
 
                <!-- Volume Tab -->
                <div class="tab-content" id="tab-volume">
                    <h3>Chats per day (last 7 days)</h3>
                    <div class="chart-container" id="volume-chart"></div>
                </div>
            </div>
        </div>
 
    </div>
 
    <script>
        let currentClientId = null;
        let currentPin = null;
 
        function switchTab(name) {
            document.querySelectorAll(".tab").forEach((t, i) => {
                t.classList.toggle("active", ["leads","faqs","pages","volume"][i] === name);
            });
            document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
            document.getElementById("tab-" + name).classList.add("active");
        }
 
        async function login() {
            const btn = document.getElementById("login-btn");
            const errorBox = document.getElementById("error-box");
            errorBox.style.display = "none";
 
            const client_id = document.getElementById("client_id").value.trim();
            const pin = document.getElementById("pin").value.trim();
 
            if (!client_id || !pin) {
                errorBox.textContent = "Please enter both your Client ID and PIN.";
                errorBox.style.display = "block";
                return;
            }
 
            btn.disabled = true;
            btn.textContent = "Logging in...";
 
            try {
                const res = await fetch("/admin/leads", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id, pin })
                });
 
                if (res.status === 401) {
                    errorBox.textContent = "Incorrect Client ID or PIN.";
                    errorBox.style.display = "block";
                    return;
                }
 
                if (!res.ok) throw new Error("Server error");
 
                const data = await res.json();
                currentClientId = client_id;
                currentPin = pin;
 
                document.getElementById("login-card").style.display = "none";
                document.getElementById("dashboard").style.display = "block";
                document.getElementById("business-title").textContent = data.business_name + " — Dashboard";
 
                renderLeads(data.leads);
                loadAnalytics();
 
            } catch {
                errorBox.textContent = "Something went wrong. Please try again.";
                errorBox.style.display = "block";
            } finally {
                btn.disabled = false;
                btn.textContent = "View My Dashboard";
            }
        }
 
        async function loadDashboard() {
            if (!currentClientId || !currentPin) return;
            try {
                const res = await fetch("/admin/leads", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: currentClientId, pin: currentPin })
                });
                const data = await res.json();
                renderLeads(data.leads);
                loadAnalytics();
            } catch {
                alert("Failed to refresh.");
            }
        }
 
        async function loadAnalytics() {
            try {
                const res = await fetch(`/admin/analytics?client_id=${currentClientId}&pin=${currentPin}`);
                if (!res.ok) return;
                const data = await res.json();
                renderAnalytics(data);
            } catch {}
        }
 
        function renderLeads(leads) {
            const tbody = document.getElementById("leads-table");
            const emptyState = document.getElementById("leads-empty");
            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
 
            document.getElementById("total-leads").textContent = leads.length;
            document.getElementById("leads-this-week").textContent =
                leads.filter(l => new Date(l.timestamp) > sevenDaysAgo).length;
 
            tbody.innerHTML = "";
            if (leads.length === 0) { emptyState.style.display = "block"; return; }
            emptyState.style.display = "none";
 
            [...leads].reverse().forEach(lead => {
                const tr = document.createElement("tr");
                const date = new Date(lead.timestamp).toLocaleDateString("en-NZ", {
                    day: "numeric", month: "short", year: "numeric"
                });
                tr.innerHTML = `<td>${lead.name}</td><td>${lead.email}</td><td>${date}</td>`;
                tbody.appendChild(tr);
            });
        }
 
        function renderAnalytics(data) {
            // Stats
            document.getElementById("total-chats").textContent = data.total_chats;
            document.getElementById("chats-this-week").textContent = data.chats_this_week;
 
            // FAQs
            document.getElementById("faqs-loading").style.display = "none";
            const faqsList = document.getElementById("faqs-list");
            const faqsEmpty = document.getElementById("faqs-empty");
            faqsList.innerHTML = "";
            if (!data.faqs || data.faqs.length === 0) {
                faqsEmpty.style.display = "block";
            } else {
                faqsEmpty.style.display = "none";
                data.faqs.forEach(faq => {
                    const div = document.createElement("div");
                    div.className = "faq-item";
                    div.innerHTML = `<strong>${faq.question}</strong><div class="faq-count">Asked approximately ${faq.count} time${faq.count !== 1 ? "s" : ""}</div>`;
                    faqsList.appendChild(div);
                });
            }
 
            // Pages
            const pagesList = document.getElementById("pages-list");
            const pagesEmpty = document.getElementById("pages-empty");
            pagesList.innerHTML = "";
            if (!data.top_pages || data.top_pages.length === 0) {
                pagesEmpty.style.display = "block";
            } else {
                pagesEmpty.style.display = "none";
                data.top_pages.forEach(page => {
                    const div = document.createElement("div");
                    div.className = "page-item";
                    div.innerHTML = `<span class="page-url">${page.url}</span><span class="page-count">${page.count} chat${page.count !== 1 ? "s" : ""}</span>`;
                    pagesList.appendChild(div);
                });
            }
 
            // Volume chart
            const chart = document.getElementById("volume-chart");
            chart.innerHTML = "";
            if (data.daily_volume && data.daily_volume.length > 0) {
                const max = Math.max(...data.daily_volume.map(d => d.count), 1);
                data.daily_volume.forEach(day => {
                    const heightPct = Math.max((day.count / max) * 100, 2);
                    const wrap = document.createElement("div");
                    wrap.className = "bar-wrap";
                    wrap.innerHTML = `
                        <div class="bar-value">${day.count}</div>
                        <div class="bar" style="height:${heightPct}%"></div>
                        <div class="bar-label">${day.label}</div>
                    `;
                    chart.appendChild(wrap);
                });
            }
        }
 
        function logout() {
            currentClientId = null;
            currentPin = null;
            document.getElementById("dashboard").style.display = "none";
            document.getElementById("login-card").style.display = "block";
            document.getElementById("client_id").value = "";
            document.getElementById("pin").value = "";
        }
    </script>
</body>
</html>
"""
 
 
@router.post("/admin/leads")
async def get_leads(req: AdminLoginRequest):
    from dependencies import sheets_service
    from config import MASTER_SHEET_ID
 
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="clients!A:F"
        ).execute()
        rows = result.get("values", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read clients: {str(e)}")
 
    client_row = None
    for row in rows[1:]:
        if len(row) >= 6 and row[0] == req.client_id and row[5] == req.pin:
            client_row = row
            break
 
    if not client_row:
        raise HTTPException(status_code=401, detail="Invalid client ID or PIN")
 
    business_name = client_row[1]
 
    try:
        leads_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="leads!A:D"
        ).execute()
        leads_rows = leads_result.get("values", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read leads: {str(e)}")
 
    leads = []
    for row in leads_rows[1:]:
        if len(row) >= 4 and row[0] == req.client_id:
            leads.append({
                "name": row[1],
                "email": row[2],
                "timestamp": row[3]
            })
 
    return {"business_name": business_name, "leads": leads}
 
 
@router.get("/admin/analytics")
async def get_analytics(client_id: str, pin: str):
    from dependencies import sheets_service
    from config import MASTER_SHEET_ID
    from dependencies import openai_client
    from database import supabase
    from datetime import datetime, timedelta
 
    # Verify PIN
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="clients!A:F"
        ).execute()
        rows = result.get("values", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to verify client")
 
    verified = any(
        len(row) >= 6 and row[0] == client_id and row[5] == pin
        for row in rows[1:]
    )
    if not verified:
        raise HTTPException(status_code=401, detail="Invalid credentials")
 
    # Fetch sessions
    try:
        sessions_res = supabase.table("sessions")\
            .select("*")\
            .eq("client_id", client_id)\
            .execute()
        sessions = sessions_res.data or []
    except Exception:
        sessions = []
 
    # Fetch user messages only
    try:
        messages_res = supabase.table("messages")\
            .select("*")\
            .eq("client_id", client_id)\
            .eq("role", "user")\
            .execute()
        messages = messages_res.data or []
    except Exception:
        messages = []
 
    # Total chats and chats this week
    total_chats = len(sessions)
    week_ago = datetime.utcnow() - timedelta(days=7)
    chats_this_week = sum(
        1 for s in sessions
        if s.get("created_at") and datetime.fromisoformat(s["created_at"].replace("Z", "")) > week_ago
    )
 
    # Daily volume for last 7 days
    daily_volume = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        count = sum(
            1 for s in sessions
            if s.get("created_at") and
            datetime.fromisoformat(s["created_at"].replace("Z", "")).date() == day.date()
        )
        daily_volume.append({
            "label": day.strftime("%a"),
            "count": count
        })
 
    # Top pages
    page_counts = {}
    for s in sessions:
        url = s.get("page_url", "")
        if url:
            page_counts[url] = page_counts.get(url, 0) + 1
    top_pages = [
        {"url": url, "count": count}
        for url, count in sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
 
    # FAQ analysis using GPT
    faqs = []
    user_messages = [m["content"] for m in messages if m.get("content")]
    if len(user_messages) >= 3:
        try:
            sample = user_messages[-50:]  # use last 50 messages
            faq_prompt = f"""
Here are recent questions users asked a business chatbot:
 
{chr(10).join(f'- {m}' for m in sample)}
 
Identify the top 5 most common topics or questions being asked.
For each, write a clear, concise question that summarises the topic, and estimate how many times it was asked.
Respond ONLY with a JSON array like this:
[
  {{"question": "What are your opening hours?", "count": 8}},
  {{"question": "How much does it cost?", "count": 5}}
]
No other text, just the JSON array.
"""
            faq_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": faq_prompt}],
                temperature=0.3
            )
            import json
            raw = faq_response.choices[0].message.content.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            faqs = json.loads(raw)
        except Exception:
            faqs = []
 
    return {
        "total_chats": total_chats,
        "chats_this_week": chats_this_week,
        "daily_volume": daily_volume,
        "top_pages": top_pages,
        "faqs": faqs
    }
