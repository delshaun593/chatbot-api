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

        /* Banner tab */
        .tk-form-field { margin-bottom: 18px; }
        .tk-form-field label { display: block; font-size: 13px; font-weight: 600; color: #555; margin-bottom: 6px; }
        .tk-form-field input[type="text"], .tk-form-field input[type="url"] {
            width: 100%; padding: 9px 12px; border: 1px solid #ddd; border-radius: 8px;
            font-size: 14px; outline: none; font-family: inherit; box-sizing: border-box;
        }
        .tk-form-field input:focus { border-color: #007bff; }
        .tk-color-row { display: flex; gap: 8px; align-items: center; }
        .tk-color-row input[type="color"] { width: 40px; height: 36px; padding: 2px; border-radius: 6px; cursor: pointer; flex-shrink: 0; }
        .tk-color-row input[type="text"] { flex: 1; }
        .tk-toggle-row { display: flex; align-items: center; gap: 10px; }
        .tk-toggle-row input[type="checkbox"] { width: auto; margin: 0; cursor: pointer; }
        .tk-toggle-row label { margin: 0; font-size: 14px; cursor: pointer; }
        .tk-save-btn { padding: 10px 28px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; width: auto; transition: background 0.2s; }
        .tk-save-btn:hover { background: #0056b3; }
        .tk-save-btn:disabled { background: #aaa; cursor: not-allowed; }
        .tk-success { color: #2e7d32; font-size: 13px; margin-top: 10px; display: none; }
        .tk-error   { color: #c00;    font-size: 13px; margin-top: 10px; display: none; }
        .tk-hint    { font-size: 12px; color: #999; margin-top: 4px; }
        .tk-section-desc { font-size: 13px; color: #666; margin-bottom: 20px; line-height: 1.5; }

        /* Reviews tab */
        .tk-add-form { background: #f8f9fa; border-radius: 10px; padding: 18px; margin-bottom: 24px; border: 1px solid #eee; }
        .tk-add-form h4 { font-size: 14px; font-weight: 700; margin-bottom: 14px; color: #333; }
        .tk-add-form input, .tk-add-form textarea, .tk-add-form select {
            width: 100%; padding: 9px 12px; border: 1px solid #ddd; border-radius: 8px;
            font-size: 14px; outline: none; margin-bottom: 10px;
            font-family: inherit; box-sizing: border-box;
        }
        .tk-add-form input:focus, .tk-add-form textarea:focus { border-color: #007bff; }
        .tk-add-form textarea { resize: vertical; min-height: 72px; }
        .tk-rev-card-admin {
            display: flex; justify-content: space-between; align-items: flex-start;
            padding: 12px 14px; border: 1px solid #eee; border-radius: 10px;
            margin-bottom: 10px; background: #fff; gap: 12px;
        }
        .tk-rev-info { flex: 1; }
        .tk-rev-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
        .tk-rev-admin-name  { font-weight: 700; font-size: 13px; color: #111; }
        .tk-rev-admin-stars { color: #f59e0b; font-size: 13px; }
        .tk-rev-admin-text  { font-size: 13px; color: #444; line-height: 1.45; }
        .tk-rev-hidden-tag  { font-size: 11px; color: #e65100; font-weight: 700; background: #fff3e0; padding: 2px 8px; border-radius: 10px; }
        .tk-rev-actions { display: flex; gap: 6px; flex-shrink: 0; }
        .tk-rev-act-btn {
            padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 600;
            cursor: pointer; border: 1px solid #ddd; background: #fff; color: #555;
            transition: all 0.15s;
        }
        .tk-rev-act-btn:hover  { background: #f5f5f5; }
        .tk-rev-act-btn.danger { color: #c00; border-color: #fcc; }
        .tk-rev-act-btn.danger:hover { background: #fff5f5; }
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
                    <div class="tab" onclick="switchTab('banner')">📣 Banner</div>
                    <div class="tab" onclick="switchTab('reviews')">⭐ Reviews</div>
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

                <!-- Banner Tab -->
                <div class="tab-content" id="tab-banner">
                    <p class="tk-section-desc">Set a promotional announcement bar that appears at the top of your website. Visitors can dismiss it — it won't reappear for that browser session.</p>
                    <div class="tk-form-field">
                        <label>Banner Message *</label>
                        <input type="text" id="banner-message" placeholder="e.g. &#x1F389; Free consultation this month — book now!" />
                    </div>
                    <div class="tk-form-field">
                        <label>Button Text <span style="font-weight:400;color:#999">(optional)</span></label>
                        <input type="text" id="banner-cta-text" placeholder="e.g. Book Now" />
                    </div>
                    <div class="tk-form-field">
                        <label>Button Link <span style="font-weight:400;color:#999">(optional)</span></label>
                        <input type="text" id="banner-cta-url" placeholder="e.g. https://yourbusiness.com/book" />
                    </div>
                    <div class="tk-form-field">
                        <label>Background Colour</label>
                        <div class="tk-color-row">
                            <input type="color" id="banner-bg-picker" value="#1a1a2e" oninput="document.getElementById('banner-bg-hex').value=this.value.replace('#','')" />
                            <input type="text" id="banner-bg-hex" value="1a1a2e" maxlength="6" oninput="if(/^[0-9A-Fa-f]{6}$/.test(this.value)) document.getElementById('banner-bg-picker').value='#'+this.value" />
                        </div>
                    </div>
                    <div class="tk-form-field">
                        <label>Text Colour</label>
                        <div class="tk-color-row">
                            <input type="color" id="banner-text-picker" value="#ffffff" oninput="document.getElementById('banner-text-hex').value=this.value.replace('#','')" />
                            <input type="text" id="banner-text-hex" value="ffffff" maxlength="6" oninput="if(/^[0-9A-Fa-f]{6}$/.test(this.value)) document.getElementById('banner-text-picker').value='#'+this.value" />
                        </div>
                    </div>
                    <div class="tk-form-field tk-toggle-row">
                        <input type="checkbox" id="banner-active" checked />
                        <label for="banner-active">Banner Active</label>
                    </div>
                    <button class="tk-save-btn" id="banner-save-btn" onclick="saveBanner()">Save Banner</button>
                    <div class="tk-success" id="banner-success">&#x2705; Banner saved!</div>
                    <div class="tk-error"   id="banner-error"></div>
                </div>

                <!-- Reviews Tab -->
                <div class="tab-content" id="tab-reviews">
                    <div class="tk-add-form">
                        <h4>Add a Review</h4>
                        <input type="text" id="rev-name" placeholder="Customer Name *" />
                        <select id="rev-rating">
                            <option value="5">&#x2605;&#x2605;&#x2605;&#x2605;&#x2605; (5 stars)</option>
                            <option value="4">&#x2605;&#x2605;&#x2605;&#x2605;&#x2606; (4 stars)</option>
                            <option value="3">&#x2605;&#x2605;&#x2605;&#x2606;&#x2606; (3 stars)</option>
                            <option value="2">&#x2605;&#x2605;&#x2606;&#x2606;&#x2606; (2 stars)</option>
                            <option value="1">&#x2605;&#x2606;&#x2606;&#x2606;&#x2606; (1 star)</option>
                        </select>
                        <textarea id="rev-text" placeholder="Review text *"></textarea>
                        <button class="tk-save-btn" id="rev-add-btn" onclick="addReview()">Add Review</button>
                        <div class="tk-success" id="rev-add-success">&#x2705; Review added!</div>
                        <div class="tk-error"   id="rev-add-error"></div>
                    </div>
                    <div id="reviews-admin-list"></div>
                    <div class="empty" id="reviews-admin-empty" style="display:none;">No reviews yet. Add your first one above!</div>
                </div>
            </div>
        </div>
 
    </div>
 
    <script>
        let currentClientId = null;
        let currentPin = null;
 
        function switchTab(name) {
            document.querySelectorAll(".tab").forEach((t, i) => {
                t.classList.toggle("active", ["leads","faqs","pages","volume","banner","reviews"][i] === name);
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
                loadBanner();
                loadReviews();
 
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
                loadBanner();
                loadReviews();
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

        // ── Banner ─────────────────────────────────────────────────────────
        async function loadBanner() {
            if (!currentClientId) return;
            try {
                const res = await fetch(`/banner/config?client_id=${currentClientId}`);
                if (!res.ok) return;
                const d = await res.json();
                if (!d || !d.message) return;
                document.getElementById("banner-message").value   = d.message   || "";
                document.getElementById("banner-cta-text").value  = d.cta_text  || "";
                document.getElementById("banner-cta-url").value   = d.cta_url   || "";
                const bg = (d.bg_color   || "1a1a2e").replace("#", "");
                const tc = (d.text_color || "ffffff").replace("#", "");
                document.getElementById("banner-bg-hex").value    = bg;
                document.getElementById("banner-bg-picker").value = "#" + bg;
                document.getElementById("banner-text-hex").value    = tc;
                document.getElementById("banner-text-picker").value = "#" + tc;
                document.getElementById("banner-active").checked  = d.active !== false;
            } catch {}
        }

        async function saveBanner() {
            const btn     = document.getElementById("banner-save-btn");
            const success = document.getElementById("banner-success");
            const error   = document.getElementById("banner-error");
            success.style.display = "none";
            error.style.display   = "none";
            const message = document.getElementById("banner-message").value.trim();
            if (!message) {
                error.textContent = "Please enter a banner message.";
                error.style.display = "block";
                return;
            }
            btn.disabled = true; btn.textContent = "Saving...";
            try {
                const res = await fetch("/banner/update", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        client_id:  currentClientId,
                        pin:        currentPin,
                        message,
                        cta_text:   document.getElementById("banner-cta-text").value.trim(),
                        cta_url:    document.getElementById("banner-cta-url").value.trim(),
                        bg_color:   document.getElementById("banner-bg-hex").value.trim(),
                        text_color: document.getElementById("banner-text-hex").value.trim(),
                        active:     document.getElementById("banner-active").checked,
                    })
                });
                if (!res.ok) throw new Error();
                success.style.display = "block";
                setTimeout(() => success.style.display = "none", 3000);
            } catch {
                error.textContent = "Something went wrong. Please try again.";
                error.style.display = "block";
            } finally {
                btn.disabled = false; btn.textContent = "Save Banner";
            }
        }

        // ── Reviews ────────────────────────────────────────────────────────
        async function loadReviews() {
            if (!currentClientId || !currentPin) return;
            try {
                const res = await fetch(`/reviews/all?client_id=${currentClientId}&pin=${currentPin}`);
                if (!res.ok) return;
                renderAdminReviews(await res.json());
            } catch {}
        }

        function renderAdminReviews(reviews) {
            const list  = document.getElementById("reviews-admin-list");
            const empty = document.getElementById("reviews-admin-empty");
            list.innerHTML = "";
            if (!reviews || reviews.length === 0) { empty.style.display = "block"; return; }
            empty.style.display = "none";
            reviews.forEach(r => {
                const filled = Math.round(r.rating || 5);
                const stars  = "★".repeat(filled) + "☆".repeat(5 - filled);
                const hidden = !r.approved ? '<span class="tk-rev-hidden-tag">Hidden</span>' : "";
                const card   = document.createElement("div");
                card.className = "tk-rev-card-admin";
                card.innerHTML = `
                    <div class="tk-rev-info">
                        <div class="tk-rev-meta">
                            <span class="tk-rev-admin-name">${r.reviewer_name}</span>
                            <span class="tk-rev-admin-stars">${stars}</span>
                            ${hidden}
                        </div>
                        <div class="tk-rev-admin-text">${r.text}</div>
                    </div>
                    <div class="tk-rev-actions">
                        <button class="tk-rev-act-btn" onclick="toggleReview('${r.id}',${!r.approved})">${r.approved ? "Hide" : "Show"}</button>
                        <button class="tk-rev-act-btn danger" onclick="deleteReview('${r.id}')">Delete</button>
                    </div>`;
                list.appendChild(card);
            });
        }

        async function addReview() {
            const btn     = document.getElementById("rev-add-btn");
            const success = document.getElementById("rev-add-success");
            const error   = document.getElementById("rev-add-error");
            success.style.display = "none";
            error.style.display   = "none";
            const name   = document.getElementById("rev-name").value.trim();
            const text   = document.getElementById("rev-text").value.trim();
            const rating = parseInt(document.getElementById("rev-rating").value);
            if (!name || !text) {
                error.textContent = "Please fill in the customer name and review text.";
                error.style.display = "block";
                return;
            }
            btn.disabled = true; btn.textContent = "Adding...";
            try {
                const res = await fetch("/reviews/add", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: currentClientId, pin: currentPin, reviewer_name: name, rating, text })
                });
                if (!res.ok) throw new Error();
                document.getElementById("rev-name").value = "";
                document.getElementById("rev-text").value = "";
                success.style.display = "block";
                setTimeout(() => success.style.display = "none", 3000);
                loadReviews();
            } catch {
                error.textContent = "Something went wrong. Please try again.";
                error.style.display = "block";
            } finally {
                btn.disabled = false; btn.textContent = "Add Review";
            }
        }

        async function deleteReview(id) {
            if (!confirm("Permanently delete this review?")) return;
            try {
                await fetch("/reviews/delete", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: currentClientId, pin: currentPin, review_id: id })
                });
                loadReviews();
            } catch {}
        }

        async function toggleReview(id, approved) {
            try {
                await fetch("/reviews/toggle", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: currentClientId, pin: currentPin, review_id: id, approved })
                });
                loadReviews();
            } catch {}
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
