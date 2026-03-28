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
        .container { width: 100%; max-width: 800px; }
        .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
        h1 { font-size: 24px; margin-bottom: 8px; }
        p.subtitle { color: #666; margin-bottom: 32px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
        input:focus { border-color: #007bff; }
        button { width: 100%; padding: 14px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #aaa; cursor: not-allowed; }
        .error { margin-top: 16px; padding: 12px; background: #fff0f0; border-radius: 8px; border: 1px solid #ffcccc; color: #c00; display: none; font-size: 14px; }

        /* Dashboard */
        #dashboard { display: none; }
        .dashboard-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
        .dashboard-header h2 { font-size: 20px; }
        .logout-btn { background: none; border: 1px solid #ddd; color: #555; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; width: auto; }
        .logout-btn:hover { background: #f5f5f5; }
        .stats-row { display: flex; gap: 16px; margin-bottom: 24px; }
        .stat-box { flex: 1; background: #f9f9f9; border: 1px solid #eee; border-radius: 10px; padding: 16px; text-align: center; }
        .stat-box .number { font-size: 32px; font-weight: 700; color: #007bff; }
        .stat-box .label { font-size: 13px; color: #888; margin-top: 4px; }
        table { width: 100%; border-collapse: collapse; font-size: 14px; }
        th { text-align: left; padding: 10px 12px; background: #f5f5f5; border-bottom: 2px solid #eee; font-weight: 600; color: #555; }
        td { padding: 10px 12px; border-bottom: 1px solid #f0f0f0; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #fafafa; }
        .empty { text-align: center; padding: 40px; color: #999; font-size: 14px; }
        .refresh-btn { background: none; border: 1px solid #007bff; color: #007bff; padding: 8px 16px; border-radius: 8px; cursor: pointer; font-size: 14px; width: auto; }
        .refresh-btn:hover { background: #f0f7ff; }
    </style>
</head>
<body>
    <div class="container">

        <!-- Login -->
        <div class="card" id="login-card">
            <h1>Lead Dashboard</h1>
            <p class="subtitle">Enter your Client ID and PIN to view your leads.</p>
            <div class="field">
                <label>Client ID</label>
                <input type="text" id="client_id" placeholder="e.g. client_a1b2c3d4" />
            </div>
            <div class="field">
                <label>PIN</label>
                <input type="password" id="pin" placeholder="4-digit PIN" maxlength="4"
                    onkeydown="if(event.key==='Enter') login()" />
            </div>
            <button onclick="login()" id="login-btn">View My Leads</button>
            <div class="error" id="error-box"></div>
        </div>

        <!-- Dashboard -->
        <div class="card" id="dashboard">
            <div class="dashboard-header">
                <h2 id="business-title">Your Leads</h2>
                <div style="display:flex; gap:8px;">
                    <button class="refresh-btn" onclick="loadLeads()">↻ Refresh</button>
                    <button class="logout-btn" onclick="logout()">Log out</button>
                </div>
            </div>
            <div class="stats-row">
                <div class="stat-box">
                    <div class="number" id="total-leads">0</div>
                    <div class="label">Total Leads</div>
                </div>
                <div class="stat-box">
                    <div class="number" id="recent-leads">0</div>
                    <div class="label">Last 7 Days</div>
                </div>
            </div>
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
            <div class="empty" id="empty-state" style="display:none;">
                No leads yet. They'll appear here when users submit their details.
            </div>
        </div>

    </div>

    <script>
        let currentClientId = null;
        let currentPin = null;

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
                    errorBox.textContent = "Incorrect Client ID or PIN. Please try again.";
                    errorBox.style.display = "block";
                    return;
                }

                if (!res.ok) throw new Error("Server error");

                const data = await res.json();
                currentClientId = client_id;
                currentPin = pin;

                document.getElementById("login-card").style.display = "none";
                document.getElementById("dashboard").style.display = "block";
                document.getElementById("business-title").textContent = data.business_name + " — Leads";

                renderLeads(data.leads);

            } catch {
                errorBox.textContent = "Something went wrong. Please try again.";
                errorBox.style.display = "block";
            } finally {
                btn.disabled = false;
                btn.textContent = "View My Leads";
            }
        }

        async function loadLeads() {
            if (!currentClientId || !currentPin) return;
            try {
                const res = await fetch("/admin/leads", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ client_id: currentClientId, pin: currentPin })
                });
                const data = await res.json();
                renderLeads(data.leads);
            } catch {
                alert("Failed to refresh leads.");
            }
        }

        function renderLeads(leads) {
            const tbody = document.getElementById("leads-table");
            const emptyState = document.getElementById("empty-state");
            const totalEl = document.getElementById("total-leads");
            const recentEl = document.getElementById("recent-leads");

            tbody.innerHTML = "";
            totalEl.textContent = leads.length;

            const sevenDaysAgo = new Date();
            sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
            const recentCount = leads.filter(l => new Date(l.timestamp) > sevenDaysAgo).length;
            recentEl.textContent = recentCount;

            if (leads.length === 0) {
                emptyState.style.display = "block";
                return;
            }

            emptyState.style.display = "none";
            // Show most recent first
            [...leads].reverse().forEach(lead => {
                const tr = document.createElement("tr");
                const date = new Date(lead.timestamp).toLocaleDateString("en-NZ", {
                    day: "numeric", month: "short", year: "numeric"
                });
                tr.innerHTML = `
                    <td>${lead.name}</td>
                    <td>${lead.email}</td>
                    <td>${date}</td>
                `;
                tbody.appendChild(tr);
            });
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

    # Verify client_id and PIN against clients tab
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="clients!A:F"
        ).execute()
        rows = result.get("values", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read clients: {str(e)}")

    # Find matching client row
    client_row = None
    for row in rows[1:]:  # skip header
        if len(row) >= 6 and row[0] == req.client_id and row[5] == req.pin:
            client_row = row
            break

    if not client_row:
        raise HTTPException(status_code=401, detail="Invalid client ID or PIN")

    business_name = client_row[1]

    # Fetch leads for this client from leads tab
    try:
        leads_result = sheets_service.spreadsheets().values().get(
            spreadsheetId=MASTER_SHEET_ID,
            range="leads!A:D"
        ).execute()
        leads_rows = leads_result.get("values", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read leads: {str(e)}")

    leads = []
    for row in leads_rows[1:]:  # skip header
        if len(row) >= 4 and row[0] == req.client_id:
            leads.append({
                "name": row[1],
                "email": row[2],
                "timestamp": row[3]
            })

    return {
        "business_name": business_name,
        "leads": leads
    }
