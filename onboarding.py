from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uuid
import random

router = APIRouter()


class OnboardingRequest(BaseModel):
    business_name: str
    industry: str
    services: str
    hours: str
    contact: str
    email: str
    website_url: str = ""
    extra_info: str = ""
    bot_name: str = "Assistant"
    primary_color: str = "007bff"
    header_color: str = ""


def generate_client_id():
    return "client_" + str(uuid.uuid4())[:8]


def generate_pin():
    return str(random.randint(1000, 9999))


@router.get("/onboarding", response_class=HTMLResponse)
def onboarding_form():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NXTIER Chatbot Onboarding</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #4f46e5;
            --primary-hover: #4338ca;
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --border: rgba(255, 255, 255, 0.1);
            --ring: rgba(79, 70, 229, 0.5);
            --radius: 16px;
            --shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            --glass-border: 1px solid rgba(255,255,255,0.05);
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes glowPulse {
            0% { text-shadow: 0 0 10px rgba(79,70,229,0.5); }
            50% { text-shadow: 0 0 20px rgba(79,70,229,0.8), 0 0 30px rgba(79,70,229,0.6); }
            100% { text-shadow: 0 0 10px rgba(79,70,229,0.5); }
        }
        body { 
            background: linear-gradient(-45deg, #0f172a, #1e1b4b, #312e81, #0f172a);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            display: flex; justify-content: center; padding: 40px 20px; color: var(--text-main); 
            min-height: 100vh;
        }
        .form-container { 
            background: var(--card-bg); 
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 48px; border-radius: var(--radius); width: 100%; max-width: 640px; 
            box-shadow: var(--shadow); 
            border: var(--glass-border);
            animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .logo-container { text-align: center; margin-bottom: 32px; }
        .logo { font-size: 36px; font-weight: 800; letter-spacing: -1px; color: #fff; display: inline-flex; align-items: center; justify-content: center; animation: glowPulse 3s infinite; }
        .logo span { color: #fff; background: linear-gradient(135deg, var(--primary), #818cf8); padding: 4px 12px; border-radius: 8px; margin-right: 4px; box-shadow: 0 4px 15px rgba(79,70,229,0.4); }
        h1 { margin-bottom: 12px; font-size: 28px; font-weight: 800; letter-spacing: -0.5px; text-align: center; background: linear-gradient(to right, #fff, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        p.subtitle { color: var(--text-muted); margin-bottom: 40px; text-align: center; font-size: 15px; line-height: 1.5; }
        .section-title { font-size: 13px; font-weight: 700; text-transform: uppercase; color: var(--primary); margin: 36px 0 20px; letter-spacing: 1px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
        .field { margin-bottom: 24px; animation: fadeInUp 0.5s ease backwards; }
        .field:nth-child(n) { animation-delay: 0.1s; }
        label { display: block; font-weight: 600; margin-bottom: 8px; font-size: 14px; color: #cbd5e1; }
        .hint { font-size: 13px; color: var(--text-muted); margin-top: 6px; }
        input[type="text"], input[type="email"], textarea { 
            width: 100%; padding: 14px 16px; border: 1px solid var(--border); border-radius: 12px; 
            font-size: 15px; outline: none; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
            background: rgba(15, 23, 42, 0.6); color: #fff; 
        }
        input:focus, textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 4px var(--ring); transform: translateY(-1px); background: rgba(15, 23, 42, 0.9); }
        textarea { resize: vertical; min-height: 100px; }
        .color-row { display: flex; gap: 12px; align-items: center; }
        .color-row input[type="color"] { width: 48px; height: 48px; padding: 2px; border-radius: 12px; border: 1px solid var(--border); cursor: pointer; flex-shrink: 0; background: rgba(15,23,42,0.6); transition: transform 0.2s; }
        .color-row input[type="color"]:hover { transform: scale(1.05); }
        .color-row input[type="text"] { flex: 1; font-family: ui-monospace, monospace; }
        button[type="button"] { 
            width: 100%; padding: 16px; background: linear-gradient(135deg, var(--primary), #6366f1); 
            color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 700; 
            cursor: pointer; margin-top: 24px; transition: all 0.3s ease; 
            box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.5); 
            position: relative; overflow: hidden;
        }
        button[type="button"]:hover { transform: translateY(-2px); box-shadow: 0 15px 25px -5px rgba(79, 70, 229, 0.6); }
        button[type="button"]:active { transform: translateY(1px); }
        button[type="button"]:disabled { background: #475569; color: #94a3b8; cursor: not-allowed; box-shadow: none; transform: none; }
        .result { margin-top: 40px; padding: 32px; background: rgba(16, 185, 129, 0.1); border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.3); display: none; animation: fadeInUp 0.6s ease; }
        .result h2 { color: #34d399; margin-bottom: 20px; font-size: 22px; }
        .result p { font-size: 15px; color: #cbd5e1; margin-bottom: 12px; line-height: 1.5; }
        .code-box { background: rgba(0,0,0,0.5); color: #a7f3d0; padding: 20px; border-radius: 12px; font-family: ui-monospace, monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; margin: 16px 0; border: 1px solid rgba(255,255,255,0.1); }
        .copy-btn { width: auto !important; padding: 10px 20px !important; font-size: 14px !important; margin-top: 0 !important; background: rgba(255,255,255,0.1) !important; box-shadow: none !important; border: 1px solid rgba(255,255,255,0.2) !important; }
        .copy-btn:hover { background: rgba(255,255,255,0.2) !important; }
        .info-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
        .info-box { background: rgba(15,23,42,0.8); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .info-box .info-label { font-size: 12px; font-weight: 600; color: #34d399; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px; }
        .info-box .info-value { font-size: 18px; font-weight: 700; color: #fff; font-family: ui-monospace, monospace; }
        .warning { font-size: 14px; color: #fcd34d; margin-top: 16px; font-weight: 500; background: rgba(251, 191, 36, 0.1); padding: 12px; border-radius: 12px; border: 1px solid rgba(251, 191, 36, 0.3); }
        .error { margin-top: 20px; padding: 16px; background: rgba(239, 68, 68, 0.1); border-radius: 12px; border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; display: none; font-size: 14px; font-weight: 500; }
        .progress { display: none; margin-top: 20px; padding: 16px; background: rgba(56, 189, 248, 0.1); border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3); color: #7dd3fc; font-size: 14px; font-weight: 500; text-align: center; }
        details { background: rgba(15,23,42,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px; margin-top: 24px; }
        summary { font-weight: 600; cursor: pointer; color: #e2e8f0; font-size: 14px; user-select: none; }
        a { color: #818cf8; text-decoration: none; font-weight: 500; }
        a:hover { text-decoration: underline; color: #a5b4fc; }
    </style>
</head>
<body>
    <div class="form-container">
        <div class="logo-container">
            <div class="logo"><span>{NXT}</span>TIER</div>
        </div>
        <h1>Set Up Your Chatbot</h1>
        <p class="subtitle">Fill in your business details and we'll generate a custom chatbot for your website in seconds.</p>
        
        <div class="section-title">Business Details</div>

        <div class="field">
            <label>Business Name *</label>
            <input type="text" id="business_name" placeholder="e.g. Auckland Plumbing Co." />
        </div>
        <div class="field">
            <label>Industry *</label>
            <input type="text" id="industry" placeholder="e.g. Plumbing, Fitness, Legal" />
        </div>
        <div class="field">
            <label>Website URL <span style="font-weight:400;color:var(--text-muted)">(recommended)</span></label>
            <input type="text" id="website_url" placeholder="e.g. https://yourbusiness.co.nz" />
            <p class="hint">We'll automatically scan your website to make the chatbot smarter.</p>
        </div>
        <div class="field">
            <label>Services Offered *</label>
            <textarea id="services" placeholder="e.g. Emergency plumbing, pipe repairs, bathroom installations..."></textarea>
        </div>
        <div class="field">
            <label>Opening Hours *</label>
            <input type="text" id="hours" placeholder="e.g. Mon–Fri 8am–6pm, Sat 9am–2pm" />
        </div>
        <div class="field">
            <label>Contact Information *</label>
            <input type="text" id="contact" placeholder="e.g. Phone: 09 123 4567, Email: hello@business.co.nz" />
        </div>
        <div class="field">
            <label>Your Email Address * <span style="font-weight:400;color:var(--text-muted)">(for receiving leads)</span></label>
            <input type="email" id="email" placeholder="you@yourbusiness.com" />
        </div>
        <div class="field">
            <label>Anything else the chatbot should know? <span style="font-weight:400;color:var(--text-muted)">(optional)</span></label>
            <textarea id="extra_info" placeholder="e.g. We offer a free first consultation. We only service the Auckland region."></textarea>
        </div>

        <div class="section-title">Chatbot Branding</div>

        <div class="field">
            <label>Bot Name</label>
            <input type="text" id="bot_name" placeholder="e.g. Aria, Max, Assistant" />
            <p class="hint">This name appears in the chat header.</p>
        </div>
        <div class="field">
            <label>Primary Colour</label>
            <div class="color-row">
                <input type="color" id="color_picker" value="#007bff" oninput="syncColor(this.value)" />
                <input type="text" id="primary_color" placeholder="007bff" value="007bff" oninput="syncPicker(this.value)" />
            </div>
            <p class="hint">Used for the send button and user message bubbles.</p>
        </div>
        <div class="field">
            <label>Header Colour <span style="font-weight:400;color:var(--text-muted)">(optional)</span></label>
            <div class="color-row">
                <input type="color" id="header_picker" value="#007bff" oninput="syncHeaderColor(this.value)" />
                <input type="text" id="header_color" placeholder="Leave blank to match primary" oninput="syncHeaderPicker(this.value)" />
            </div>
            <p class="hint">The colour of the chat window header bar.</p>
        </div>
        <button type="button" id="submit-btn" onclick="submitForm()">Generate My Chatbot →</button>
        <div class="progress" id="progress-box">⏳ Scanning your website and generating your chatbot — this may take 20–30 seconds...</div>
        <div class="error" id="error-box"></div>

        <div class="result" id="result-box">
            <h2>✅ Your chatbot is ready!</h2>

            <p style="margin-bottom:20px;">Save these details — you'll need them to access your lead dashboard.</p>
            <div class="info-row">
                <div class="info-box">
                    <div class="info-label">Client ID</div>
                    <div class="info-value" id="client-id-display"></div>
                </div>
                <div class="info-box">
                    <div class="info-label">Dashboard PIN</div>
                    <div class="info-value" id="pin-display"></div>
                </div>
            </div>
            <p class="warning">⚠️ Save your Client ID and PIN now — they won't be shown again.</p>

            <p style="margin-top:24px; margin-bottom:8px; font-weight: 600;">Paste this code before the <code>&lt;/body&gt;</code> tag on every page of your website:</p>
            <div class="code-box" id="embed-code"></div>
            <button type="button" class="copy-btn" onclick="copyCode()">Copy Code</button>

            <details style="margin-top:24px;">
                <summary>Chatbot only (without banner &amp; reviews)</summary>
                <div class="code-box" id="widget-only-code" style="margin-top:16px;"></div>
                <button type="button" class="copy-btn" onclick="copySingleCode()">Copy</button>
            </details>

            <p style="margin-top:24px; font-size:14px; text-align: center;">
                View your leads at:<br>
                <a id="admin-link" href="#" target="_blank" style="display:inline-block; margin-top:8px;"></a>
            </p>
        </div>
    </div>

    <script>
        function syncColor(hex) {
            document.getElementById("primary_color").value = hex.replace("#", "");
        }

        function syncPicker(val) {
            if (/^[0-9A-Fa-f]{6}$/.test(val)) {
                document.getElementById("color_picker").value = "#" + val;
            }
        }

        function syncHeaderColor(hex) {
            document.getElementById("header_color").value = hex.replace("#", "");
        }

        function syncHeaderPicker(val) {
            if (/^[0-9A-Fa-f]{6}$/.test(val)) {
                document.getElementById("header_picker").value = "#" + val;
            }
        }

        async function submitForm() {
            const btn = document.getElementById("submit-btn");
            const errorBox = document.getElementById("error-box");
            const progressBox = document.getElementById("progress-box");
            errorBox.style.display = "none";

            const fields = {
                business_name: document.getElementById("business_name").value.trim(),
                industry: document.getElementById("industry").value.trim(),
                services: document.getElementById("services").value.trim(),
                hours: document.getElementById("hours").value.trim(),
                contact: document.getElementById("contact").value.trim(),
                email: document.getElementById("email").value.trim(),
                website_url: document.getElementById("website_url").value.trim(),
                extra_info: document.getElementById("extra_info").value.trim(),
                bot_name: document.getElementById("bot_name").value.trim() || "Assistant",
                primary_color: document.getElementById("primary_color").value.trim().replace("#", "") || "007bff",
                header_color: document.getElementById("header_color").value.trim().replace("#", "")
            };

            const required = ["business_name", "industry", "services", "hours", "contact", "email"];
            for (const key of required) {
                if (!fields[key]) {
                    errorBox.textContent = "Please fill in all required fields.";
                    errorBox.style.display = "block";
                    return;
                }
            }

            btn.disabled = true;
            btn.textContent = "Generating your chatbot...";
            if (fields.website_url) {
                progressBox.style.display = "block";
            }

            try {
                const res = await fetch("/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(fields)
                });

                if (!res.ok) throw new Error("Server error");

                const data = await res.json();

                document.getElementById("embed-code").textContent = data.embed_code;
                document.getElementById("widget-only-code").textContent = data.widget_only_code || "";
                document.getElementById("client-id-display").textContent = data.client_id;
                document.getElementById("pin-display").textContent = data.pin;

                const adminUrl = window.location.origin + "/admin";
                const adminLink = document.getElementById("admin-link");
                adminLink.href = adminUrl;
                adminLink.textContent = adminUrl;

                progressBox.style.display = "none";
                document.getElementById("result-box").style.display = "block";
                document.getElementById("result-box").scrollIntoView({ behavior: "smooth" });

            } catch {
                errorBox.textContent = "Something went wrong. Please try again.";
                errorBox.style.display = "block";
                progressBox.style.display = "none";
            } finally {
                btn.disabled = false;
                btn.textContent = "Generate My Chatbot →";
            }
        }

        function copyCode() {
            const code = document.getElementById("embed-code").textContent;
            navigator.clipboard.writeText(code).then(() => {
                const btn = document.querySelector(".copy-btn");
                btn.textContent = "Copied!";
                setTimeout(() => btn.textContent = "Copy Code", 2000);
            });
        }

        function copySingleCode() {
            const code = document.getElementById("widget-only-code").textContent;
            navigator.clipboard.writeText(code).then(() => {
                const btns = document.querySelectorAll(".copy-btn");
                btns[1].textContent = "Copied!";
                setTimeout(() => btns[1].textContent = "Copy", 2000);
            });
        }
    </script>
</body>
</html>
"""


@router.post("/register")
async def register_client(req: OnboardingRequest):
    from dependencies import openai_client, sheets_service
    from config import CLIENT_PROMPTS, MASTER_SHEET_ID
    from crawler import crawl_website
    import json
    import urllib.parse

    # Crawl website if URL provided
    website_content = ""
    if req.website_url:
        try:
            website_content = crawl_website(req.website_url)
            print(f"✅ Crawled {req.website_url} — {len(website_content)} chars")
        except Exception as e:
            print(f"⚠️ Failed to crawl {req.website_url}: {e}")

    prompt_instructions = f"""
Create a helpful chatbot system prompt for the following business:

Business Name: {req.business_name}
Industry: {req.industry}
Services: {req.services}
Opening Hours: {req.hours}
Contact Info: {req.contact}
Extra Info: {req.extra_info}

{"Website Content (scraped from their site):" + website_content if website_content else ""}

The system prompt should:
- Give the bot a friendly, professional personality
- Include all the business details above
- If website content is provided, use it to answer questions accurately
- Instruct the bot to answer clearly and concisely
- Instruct the bot to encourage users to get in touch when appropriate
- Include lead capture rules: collect name and email when users ask about pricing, booking, or availability
- Ask for one detail at a time and not be pushy
- If the user declines to share details, continue helping normally

Output your response as JSON with exactly two fields:
1. "system_prompt": The system prompt string.
2. "greeting": A short, friendly, and highly relevant 1-2 sentence welcoming greeting message.
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_instructions}],
        temperature=0.4,
        response_format={"type": "json_object"}
    )

    try:
        content = json.loads(response.choices[0].message.content)
        system_prompt = content.get("system_prompt", "You are a helpful assistant.")
        greeting = content.get("greeting", "Hi there 👋 How can I help you today?")
    except Exception:
        system_prompt = response.choices[0].message.content
        greeting = "Hi there 👋 How can I help you today?"
        
    encoded_greeting = urllib.parse.quote(greeting)
    client_id = generate_client_id()
    pin = generate_pin()

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=MASTER_SHEET_ID,
            range="clients!A:F",
            valueInputOption="USER_ENTERED",
            body={"values": [[
                client_id,
                req.business_name,
                req.email,
                system_prompt,
                str(datetime.now()),
                pin
            ]]}
        ).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save client: {str(e)}")

    CLIENT_PROMPTS[client_id] = system_prompt

    embed_code = (
        f'<script>'
        f'fetch("https://chatbot-api-4ssr.onrender.com/widget.js'
        f'?client_id={client_id}'
        f'&bot_name={req.bot_name}'
        f'&primary_color={req.primary_color}'
        f'&header_color={req.header_color}'
        f'&greeting={encoded_greeting}")'
        f'.then(r => r.text())'
        f'.then(code => eval(code));'
        f'</script>'
    )

    toolkit_embed_code = (
        f'<script>'
        f'fetch("https://chatbot-api-4ssr.onrender.com/toolkit.js'
        f'?client_id={client_id}'
        f'&bot_name={req.bot_name}'
        f'&primary_color={req.primary_color}'
        f'&header_color={req.header_color}'
        f'&greeting={encoded_greeting}")'
        f'.then(r => r.text())'
        f'.then(code => eval(code));'
        f'</script>'
    )

    return {
        "client_id": client_id,
        "pin": pin,
        "embed_code": toolkit_embed_code,
        "widget_only_code": embed_code,
    }
