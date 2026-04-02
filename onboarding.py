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
    greeting: str = "Hi there 👋 How can I help you?"


def generate_client_id():
    return "client_" + str(uuid.uuid4())[:8]


def generate_pin():
    return str(random.randint(1000, 9999))


@router.get("/onboarding", response_class=HTMLResponse)
def onboarding_form():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Onboarding</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: sans-serif; background: #f5f5f5; display: flex; justify-content: center; padding: 40px 20px; }
        .form-container { background: white; padding: 40px; border-radius: 12px; width: 100%; max-width: 600px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); }
        h1 { margin-bottom: 8px; font-size: 24px; }
        p.subtitle { color: #666; margin-bottom: 32px; }
        .section-title { font-size: 13px; font-weight: 700; text-transform: uppercase; color: #999; margin: 28px 0 16px; letter-spacing: 0.5px; }
        .field { margin-bottom: 20px; }
        label { display: block; font-weight: 600; margin-bottom: 6px; font-size: 14px; }
        input, textarea { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; font-family: sans-serif; }
        input:focus, textarea:focus { border-color: #007bff; }
        textarea { resize: vertical; min-height: 80px; }
        .color-row { display: flex; gap: 10px; align-items: center; }
        .color-row input[type="color"] { width: 48px; height: 40px; padding: 2px; border-radius: 8px; cursor: pointer; flex-shrink: 0; }
        .color-row input[type="text"] { flex: 1; }
        button[type="button"] { width: 100%; padding: 14px; background: #007bff; color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 8px; }
        button[type="button"]:hover { background: #0056b3; }
        button[type="button"]:disabled { background: #aaa; cursor: not-allowed; }
        .result { margin-top: 32px; padding: 24px; background: #f0f9f0; border-radius: 8px; border: 1px solid #b2dfb2; display: none; }
        .result h2 { color: #2e7d32; margin-bottom: 16px; }
        .result p { font-size: 14px; color: #555; margin-bottom: 8px; }
        .code-box { background: #1e1e1e; color: #d4d4d4; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 13px; white-space: pre-wrap; word-break: break-all; margin: 12px 0; }
        .copy-btn { width: auto !important; padding: 8px 16px !important; font-size: 14px !important; margin-top: 0 !important; }
        .info-row { display: flex; gap: 12px; margin-bottom: 20px; }
        .info-box { flex: 1; background: #fff; border: 1px solid #ddd; border-radius: 8px; padding: 14px; }
        .info-box .info-label { font-size: 12px; color: #888; margin-bottom: 4px; }
        .info-box .info-value { font-size: 16px; font-weight: 700; color: #111; font-family: monospace; }
        .warning { font-size: 13px; color: #e65100; margin-top: 12px; }
        .error { margin-top: 16px; padding: 12px; background: #fff0f0; border-radius: 8px; border: 1px solid #ffcccc; color: #c00; display: none; font-size: 14px; }
        .hint { font-size: 12px; color: #999; margin-top: 4px; }
        .progress { display: none; margin-top: 16px; padding: 12px; background: #f0f7ff; border-radius: 8px; border: 1px solid #b3d4ff; color: #0056b3; font-size: 14px; }
    </style>
</head>
<body>
    <div class="form-container">
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
            <label>Website URL <span style="font-weight:400;color:#888">(recommended — lets the chatbot learn your full site)</span></label>
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
            <label>Your Email Address * <span style="font-weight:400;color:#888">(for receiving leads)</span></label>
            <input type="email" id="email" placeholder="you@yourbusiness.com" />
        </div>
        <div class="field">
            <label>Anything else the chatbot should know? <span style="font-weight:400;color:#888">(optional)</span></label>
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
            <label>Greeting Message</label>
            <input type="text" id="greeting" placeholder="e.g. Hi there 👋 How can I help you today?" />
        </div>

        <button type="button" id="submit-btn" onclick="submitForm()">Generate My Chatbot →</button>
        <div class="progress" id="progress-box">⏳ Scanning your website and generating your chatbot — this may take 20–30 seconds...</div>
        <div class="error" id="error-box"></div>

        <div class="result" id="result-box">
            <h2>✅ Your chatbot is ready!</h2>

            <p style="margin-bottom:16px;">Save these details — you'll need them to access your lead dashboard.</p>
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

            <p style="margin-top:20px; margin-bottom:4px;">Paste this code before the <code>&lt;/body&gt;</code> tag on every page of your website:</p>
            <div class="code-box" id="embed-code"></div>
            <button type="button" class="copy-btn" onclick="copyCode()">Copy Code</button>

            <details style="margin-top:20px;">
                <summary style="cursor:pointer;font-size:13px;color:#666;">Chatbot only (without banner &amp; reviews)</summary>
                <div class="code-box" id="widget-only-code" style="margin-top:10px;"></div>
                <button type="button" class="copy-btn" onclick="copySingleCode()">Copy</button>
            </details>

            <p style="margin-top:16px; font-size:13px; color:#555;">
                View your leads at:
                <a id="admin-link" href="#" target="_blank" style="color:#007bff;"></a>
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
                greeting: document.getElementById("greeting").value.trim() || "Hi there 👋 How can I help you?"
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
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_instructions}],
        temperature=0.4
    )

    system_prompt = response.choices[0].message.content
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
        f'&greeting={req.greeting}")'
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
        f'&greeting={req.greeting}")'
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
