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
    <title>NXTIER Lead Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root { 
            --primary: #4f46e5; --primary-hover: #4338ca; 
            --bg: #0f172a; --card: rgba(30, 41, 59, 0.7); 
            --text: #f8fafc; --text-muted: #94a3b8; 
            --border: rgba(255, 255, 255, 0.1); 
            --radius: 16px; --shadow: 0 10px 30px -10px rgba(0,0,0,0.5); 
            --glass-border: 1px solid rgba(255,255,255,0.05);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        @keyframes gradientBG { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        body { 
            background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a); background-size: 400% 400%; animation: gradientBG 15s ease infinite;
            display: flex; justify-content: center; padding: 40px 20px; color: var(--text); min-height: 100vh;
        }
        .container { width: 100%; max-width: 1000px; }
        .card { 
            background: var(--card); backdrop-filter: blur(16px); padding: 40px; border-radius: var(--radius); 
            box-shadow: var(--shadow); margin-bottom: 24px; border: var(--glass-border); 
            animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        .logo { font-size: 32px; font-weight: 800; letter-spacing: -1px; color: #fff; display: inline-flex; align-items: center; margin-bottom: 12px; justify-content: center; width: 100%; text-shadow: 0 0 15px rgba(79,70,229,0.5); }
        .logo span { color: #fff; background: linear-gradient(135deg, var(--primary), #818cf8); padding: 4px 12px; border-radius: 8px; margin-right: 6px; box-shadow: 0 4px 15px rgba(79,70,229,0.4); }
        
        h1 { font-size: 28px; margin-bottom: 8px; text-align: center; font-weight: 800; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p.subtitle { color: var(--text-muted); margin-bottom: 32px; text-align: center; }
        .field { margin-bottom: 24px; }
        label { display: block; font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #cbd5e1; }
        input, select, textarea { width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; font-size: 15px; outline: none; transition: all 0.3s; background: rgba(15,23,42,0.6); color: #fff; }
        input:focus, select:focus, textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79,70,229,0.3); transform: translateY(-1px); background: rgba(15,23,42,0.9); }
        button { 
            width: 100%; padding: 16px; background: linear-gradient(135deg, var(--primary), #6366f1); 
            color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; cursor: pointer; 
            transition: all 0.3s ease; box-shadow: 0 8px 15px rgba(79,70,229,0.4); 
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 12px 20px rgba(79,70,229,0.6); }
        button:disabled { background: #475569; cursor: not-allowed; transform: none; box-shadow: none; color: #94a3b8; }
        .error { margin-top: 16px; padding: 16px; background: rgba(239, 68, 68, 0.1); border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; display: none; font-size: 14px; font-weight: 500; }
        
        #dashboard { display: none; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; padding-bottom: 20px; border-bottom: 1px solid var(--border); }
        .dashboard-header h2 { font-size: 20px; font-weight: 700; margin: 0; color: var(--text); }
        .header-logo { font-size: 24px; font-weight: 800; letter-spacing: -1px; color: #fff; display: inline-flex; align-items: center; margin: 0; }
        .header-logo span { color: #fff; background: linear-gradient(135deg, var(--primary), #818cf8); padding: 4px 8px; border-radius: 6px; margin-right: 6px; }
        .header-actions { display: flex; gap: 12px; }
        .logout-btn, .refresh-btn { background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: #e2e8f0; padding: 10px 16px; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600; transition: all 0.2s; width: auto; box-shadow: none; }
        .logout-btn:hover { background: rgba(255,255,255,0.1); color: #fff; transform: none; }
        .refresh-btn { color: #818cf8; border-color: rgba(129, 140, 248, 0.3); background: rgba(129, 140, 248, 0.1); }
        .refresh-btn:hover { background: rgba(129, 140, 248, 0.2); transform: none; box-shadow: none; }
        
        .stats-row { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
        .stat-box { flex: 1; min-width: 140px; background: rgba(15,23,42,0.6); border: 1px solid var(--border); border-radius: 16px; padding: 24px; text-align: center; transition: transform 0.3s, box-shadow 0.3s; }
        .stat-box:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); border-color: rgba(255,255,255,0.2); }
        .stat-box .number { font-size: 40px; font-weight: 800; color: #818cf8; letter-spacing: -1px; margin-bottom: 8px; line-height: 1; text-shadow: 0 0 10px rgba(129,140,248,0.3); }
        .stat-box .label { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        
        .tabs { display: flex; gap: 12px; margin-bottom: 24px; border-bottom: 1px solid var(--border); overflow-x: auto; padding-bottom: 4px; scrollbar-width: none; -ms-overflow-style: none; }
        .tabs::-webkit-scrollbar { display: none; }
        .tab { padding: 12px 20px; cursor: pointer; font-size: 15px; font-weight: 600; color: var(--text-muted); border-bottom: 2px solid transparent; white-space: nowrap; transition: all 0.2s; border-radius: 8px 8px 0 0; }
        .tab:hover { color: #fff; background: rgba(255,255,255,0.05); }
        .tab.active { color: #818cf8; border-bottom-color: #818cf8; background: rgba(129,140,248,0.05); }
        .tab-content { display: none; animation: fadeIn 0.4s ease; }
        .tab-content.active { display: block; }
        
        table { width: 100%; border-collapse: separate; border-spacing: 0; font-size: 14px; }
        th { text-align: left; padding: 16px; background: rgba(15,23,42,0.6); font-weight: 600; color: var(--text-muted); text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }
        th:first-child { border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
        th:last-child { border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
        td { padding: 16px; border-bottom: 1px solid var(--border); color: var(--text); }
        tr:last-child td { border-bottom: none; }
        tr { transition: background 0.2s; }
        tr:hover td { background: rgba(255,255,255,0.03); }
        
        .empty { text-align: center; padding: 48px; color: var(--text-muted); font-size: 15px; background: rgba(15,23,42,0.3); border-radius: 12px; border: 1px dashed var(--border); }
        .faq-item { padding: 16px; background: rgba(15,23,42,0.6); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 12px; font-size: 15px; transition: transform 0.2s; }
        .faq-item:hover { transform: translateX(4px); border-color: rgba(255,255,255,0.2); }
        .faq-count { font-size: 13px; font-weight: 600; color: #818cf8; margin-top: 8px; display: inline-block; background: rgba(129,140,248,0.1); padding: 4px 10px; border-radius: 8px; }
        
        .chart-container { height: 260px; display: flex; align-items: flex-end; gap: 16px; padding: 32px 24px; border: 1px solid var(--border); border-radius: 16px; margin-top: 16px; background: rgba(15,23,42,0.6); }
        .bar-wrap { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 10px; height: 100%; justify-content: flex-end; }
        .bar { width: 100%; max-width: 40px; background: linear-gradient(0deg, var(--primary), #818cf8); border-radius: 6px 6px 0 0; min-height: 4px; transition: height 1s cubic-bezier(0.4, 0, 0.2, 1); opacity: 0.8; box-shadow: 0 -4px 15px rgba(79,70,229,0.3); }
        .bar:hover { opacity: 1; transform: scaleY(1.02); }
        .bar-label { font-size: 12px; font-weight: 600; color: var(--text-muted); text-align: center; text-transform: uppercase; }
        .bar-value { font-size: 14px; font-weight: 700; color: #fff; }
        
        .page-item { display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; border-bottom: 1px solid var(--border); font-size: 14px; background: rgba(15,23,42,0.4); transition: background 0.2s; }
        .page-item:first-child { border-top-left-radius: 12px; border-top-right-radius: 12px; }
        .page-item:last-child { border-bottom: none; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px; }
        .page-item:hover { background: rgba(255,255,255,0.05); }
        .page-url { color: var(--text); font-weight: 500; word-break: break-all; flex: 1; margin-right: 16px; }
        .page-count { background: rgba(129,140,248,0.1); color: #818cf8; border-radius: 12px; padding: 6px 14px; font-size: 13px; font-weight: 600; white-space: nowrap; border: 1px solid rgba(129,140,248,0.2); }
        
        .tk-form-field { margin-bottom: 24px; }
        .tk-form-field label { display: block; font-size: 14px; font-weight: 600; color: #cbd5e1; margin-bottom: 8px; }
        .tk-form-field input[type="text"], .tk-form-field input[type="url"] { width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; font-size: 15px; outline: none; background: rgba(15,23,42,0.6); color: #fff; transition: all 0.3s; }
        .tk-form-field input:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79,70,229,0.3); background: rgba(15,23,42,0.9); }
        .tk-color-row { display: flex; gap: 12px; align-items: center; }
        .tk-color-row input[type="color"] { width: 48px; height: 48px; padding: 2px; border-radius: 12px; cursor: pointer; flex-shrink: 0; border: 1px solid var(--border); background: rgba(15,23,42,0.6); }
        .tk-color-row input[type="text"] { flex: 1; font-family: monospace; }
        .tk-toggle-row { display: flex; align-items: center; gap: 12px; background: rgba(15,23,42,0.4); padding: 12px 16px; border-radius: 12px; border: 1px solid var(--border); }
        .tk-toggle-row input[type="checkbox"] { width: 20px; height: 20px; cursor: pointer; accent-color: var(--primary); }
        .tk-toggle-row label { margin: 0; font-size: 15px; cursor: pointer; color: #fff; }
        
        .tk-save-btn { padding: 14px 28px; background: linear-gradient(135deg, var(--primary), #6366f1); color: white; border: none; border-radius: 12px; font-size: 15px; font-weight: 600; cursor: pointer; width: auto; transition: all 0.2s; box-shadow: 0 4px 15px rgba(79,70,229,0.4); }
        .tk-save-btn:hover { box-shadow: 0 8px 20px rgba(79,70,229,0.6); transform: translateY(-2px); }
        .tk-save-btn:disabled { background: #475569; cursor: not-allowed; box-shadow: none; transform: none; }
        
        .tk-success { color: #34d399; font-size: 14px; font-weight: 500; margin-top: 16px; display: none; background: rgba(16,185,129,0.1); padding: 16px; border-radius: 12px; border: 1px solid rgba(16,185,129,0.3); }
        .tk-error { color: #fca5a5; font-size: 14px; font-weight: 500; margin-top: 16px; display: none; background: rgba(239,68,68,0.1); padding: 16px; border-radius: 12px; border: 1px solid rgba(239,68,68,0.3); }
        
        .tk-section-desc { font-size: 15px; color: var(--text-muted); margin-bottom: 24px; line-height: 1.6; }
        .tk-add-form { background: rgba(15,23,42,0.6); border-radius: 16px; padding: 32px; margin-bottom: 32px; border: 1px solid var(--border); box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .tk-add-form h4 { font-size: 18px; font-weight: 700; margin-bottom: 20px; color: #fff; }
        .tk-add-form input, .tk-add-form textarea, .tk-add-form select { margin-bottom: 16px; width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; font-size: 15px; outline: none; transition: all 0.3s; background: rgba(15,23,42,0.6); color: #fff; }
        .tk-add-form input:focus, .tk-add-form textarea:focus, .tk-add-form select:focus { border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79,70,229,0.3); background: rgba(15,23,42,0.9); }
        .tk-add-form textarea { resize: vertical; min-height: 100px; }
        
        .tk-rev-card-admin { display: flex; justify-content: space-between; align-items: flex-start; padding: 20px 24px; border: 1px solid var(--border); border-radius: 16px; margin-bottom: 16px; background: rgba(15,23,42,0.4); gap: 16px; transition: transform 0.2s, box-shadow 0.2s; }
        .tk-rev-card-admin:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); border-color: rgba(255,255,255,0.2); }
        .tk-rev-info { flex: 1; }
        .tk-rev-meta { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .tk-rev-admin-name { font-weight: 700; font-size: 16px; color: #fff; }
        .tk-rev-admin-stars { color: #fbbf24; font-size: 16px; letter-spacing: 2px; }
        .tk-rev-admin-text { font-size: 15px; color: #cbd5e1; line-height: 1.6; }
        .tk-rev-hidden-tag { font-size: 11px; color: #fcd34d; font-weight: 700; background: rgba(251,191,36,0.1); padding: 4px 10px; border-radius: 12px; text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid rgba(251,191,36,0.2); }
        
        .tk-rev-actions { display: flex; gap: 10px; flex-shrink: 0; }
        .tk-rev-act-btn { padding: 10px 16px; border-radius: 10px; font-size: 13px; font-weight: 600; cursor: pointer; border: 1px solid var(--border); background: rgba(255,255,255,0.05); color: #fff; transition: all 0.2s; box-shadow: none; width: auto; }
        .tk-rev-act-btn:hover { background: rgba(255,255,255,0.1); transform: translateY(-1px); }
        .tk-rev-act-btn.danger { color: #fca5a5; border-color: rgba(239,68,68,0.3); background: rgba(239,68,68,0.05); }
        .tk-rev-act-btn.danger:hover { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.5); }
    </style>
</head>
<body>
    <div class="container">
 
        <!-- Login -->
        <div class="card" id="login-card">
            <div class="logo"><span>{NXT}</span>TIER</div>
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
                    <div class="header-logo"><span>{NXT}</span>TIER</div>
                    <div class="header-actions">
                        <button class="refresh-btn" onclick="loadDashboard()">↻ Refresh</button>
                        <button class="logout-btn" onclick="logout()">Log out</button>
                    </div>
                </div>
                <h2 id="business-title" style="font-size: 20px; font-weight: 700; margin-bottom: 24px; color: var(--text);">Dashboard</h2>
 
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
                    <div class="tab" onclick="switchTab('bot')">🤖 Bot Design</div>
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

                <!-- Bot Tab -->
                <div class="tab-content" id="tab-bot">
                    <p class="tk-section-desc">Customize the appearance and initial greeting message of your chatbot widget.</p>
                    <div class="tk-form-field">
                        <label>Bot Name</label>
                        <input type="text" id="bot-name" placeholder="e.g. Assistant" />
                    </div>
                    <div class="tk-form-field">
                        <label>Greeting Message</label>
                        <input type="text" id="bot-greeting" placeholder="e.g. Hi there 👋 How can I help you?" />
                    </div>
                    <div class="tk-form-field">
                        <label>Primary Colour</label>
                        <div class="tk-color-row">
                            <input type="color" id="bot-primary-picker" value="#007bff" oninput="document.getElementById('bot-primary-hex').value=this.value.replace('#','')" />
                            <input type="text" id="bot-primary-hex" value="007bff" maxlength="6" oninput="if(/^[0-9A-Fa-f]{6}$/.test(this.value)) document.getElementById('bot-primary-picker').value='#'+this.value" />
                        </div>
                    </div>
                    <div class="tk-form-field">
                        <label>Header Colour</label>
                        <div class="tk-color-row">
                            <input type="color" id="bot-header-picker" value="#007bff" oninput="document.getElementById('bot-header-hex').value=this.value.replace('#','')" />
                            <input type="text" id="bot-header-hex" value="007bff" maxlength="6" oninput="if(/^[0-9A-Fa-f]{6}$/.test(this.value)) document.getElementById('bot-header-picker').value='#'+this.value" />
                        </div>
                    </div>
                    <button class="tk-save-btn" id="bot-save-btn" onclick="saveBotConfig()">Save Bot Design</button>
                    <div class="tk-success" id="bot-success">&#x2705; Bot design saved!</div>
                    <div class="tk-error"   id="bot-error"></div>
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
                t.classList.toggle("active", ["leads","faqs","pages","volume","bot","banner","reviews"][i] === name);
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
                loadBotConfig();
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
                loadBotConfig();
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

        // ── Bot Config ─────────────────────────────────────────────────────
        async function loadBotConfig() {
            if (!currentClientId) return;
            try {
                const res = await fetch(`/widget/config?client_id=${currentClientId}`);
                if (!res.ok) return;
                const d = await res.json();
                if (!d || !d.bot_name) return;
                document.getElementById("bot-name").value = d.bot_name || "";
                document.getElementById("bot-greeting").value = d.greeting || "";
                
                const pColor = (d.primary_color || "007bff").replace("#", "");
                const hColor = (d.header_color || "007bff").replace("#", "");
                
                document.getElementById("bot-primary-hex").value = pColor;
                document.getElementById("bot-primary-picker").value = "#" + pColor;
                document.getElementById("bot-header-hex").value = hColor;
                document.getElementById("bot-header-picker").value = "#" + hColor;
            } catch {}
        }

        async function saveBotConfig() {
            const btn = document.getElementById("bot-save-btn");
            const success = document.getElementById("bot-success");
            const error = document.getElementById("bot-error");
            success.style.display = "none";
            error.style.display = "none";
            
            const bot_name = document.getElementById("bot-name").value.trim();
            const greeting = document.getElementById("bot-greeting").value.trim();
            if (!bot_name || !greeting) {
                error.textContent = "Please fill out bot name and greeting.";
                error.style.display = "block";
                return;
            }
            
            btn.disabled = true; btn.textContent = "Saving...";
            try {
                const res = await fetch("/widget/update", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        client_id: currentClientId,
                        pin: currentPin,
                        bot_name: bot_name,
                        greeting: greeting,
                        primary_color: document.getElementById("bot-primary-hex").value.trim(),
                        header_color: document.getElementById("bot-header-hex").value.trim()
                    })
                });
                if (!res.ok) throw new Error();
                success.style.display = "block";
                setTimeout(() => success.style.display = "none", 3000);
            } catch {
                error.textContent = "Something went wrong. Please try again.";
                error.style.display = "block";
            } finally {
                btn.disabled = false; btn.textContent = "Save Bot Design";
            }
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
    from auth import get_client, verify_pin
    from database import supabase

    # Verify credentials via Supabase + bcrypt
    client = get_client(req.client_id)
    if not client or not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid client ID or PIN")

    business_name = client["business_name"]

    # Fetch leads from Supabase
    try:
        leads_res = (
            supabase.table("leads")
            .select("name, email, created_at")
            .eq("client_id", req.client_id)
            .order("created_at")
            .execute()
        )
        leads = [
            {"name": row["name"], "email": row["email"], "timestamp": row["created_at"]}
            for row in (leads_res.data or [])
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read leads: {str(e)}")

    return {"business_name": business_name, "leads": leads}

 
 
@router.get("/admin/analytics")
async def get_analytics(client_id: str, pin: str):
    from auth import verify_pin
    from dependencies import openai_client
    from database import supabase
    from datetime import datetime, timedelta

    # Verify PIN via Supabase + bcrypt
    if not verify_pin(client_id, pin):
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
