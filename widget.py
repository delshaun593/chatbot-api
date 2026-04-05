from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from database import supabase

router = APIRouter()

class WidgetConfigRequest(BaseModel):
    client_id: str
    pin: str
    bot_name: str
    primary_color: str
    header_color: str
    greeting: str

from auth import verify_pin

@router.get("/widget/config")
async def get_widget_config(client_id: str):
    """Returns the dynamic widget config for a client."""
    try:
        res = supabase.table("widget_config").select("*").eq("client_id", client_id).execute()
        data = res.data
        if not data:
            return {}
        return data[0]
    except Exception:
        return {}

@router.post("/widget/update")
async def update_widget_config(req: WidgetConfigRequest):
    """Update a client's widget configuration."""
    if not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "client_id": req.client_id,
        "bot_name": req.bot_name,
        "primary_color": req.primary_color.lstrip("#"),
        "header_color": req.header_color.lstrip("#"),
        "greeting": req.greeting
    }
    try:
        existing = supabase.table("widget_config").select("id").eq("client_id", req.client_id).execute()
        if existing.data:
            supabase.table("widget_config").update(payload).eq("client_id", req.client_id).execute()
        else:
            supabase.table("widget_config").insert(payload).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/widget.js")
def serve_widget(
    client_id: str,
    primary_color: str = "007bff",
    header_color: str = "",
    bot_name: str = "Assistant",
    greeting: str = "Hi there 👋 How can I help you?"
):
    # Generate JS handling fetch
    widget_code = f"""
(function() {{
  const CLIENT_ID = "{client_id}";
  const BASE_URL = "https://chatbot-api-4ssr.onrender.com";

  let _primary_color = "{primary_color}";
  let _header_color = "{header_color}";
  let _bot_name = "{bot_name}".replace(/"/g, '\\"');
  let _greeting = "{greeting}".replace(/"/g, '\\"');

  fetch(BASE_URL + "/widget/config?client_id=" + CLIENT_ID)
    .then(r => r.json())
    .then(cfg => {{
      if (cfg && cfg.primary_color) {{
        _primary_color = cfg.primary_color;
        _header_color = cfg.header_color || cfg.primary_color;
        _bot_name = cfg.bot_name || _bot_name;
        _greeting = cfg.greeting || _greeting;
      }}
      if (!_header_color) _header_color = _primary_color;
      initWidget(_primary_color, _header_color, _bot_name, _greeting);
    }})
    .catch(() => {{
      if (!_header_color) _header_color = _primary_color;
      initWidget(_primary_color, _header_color, _bot_name, _greeting);
    }});

  function initWidget(PRIMARY_COLOR_HEX, HEADER_COLOR_HEX, BOT_NAME, GREETING) {{
    const PRIMARY_COLOR = "#" + PRIMARY_COLOR_HEX;
    const HEADER_COLOR = "#" + HEADER_COLOR_HEX;
    const AVATAR_INITIAL = BOT_NAME ? BOT_NAME.charAt(0).toUpperCase() : "A";
    
    const API_URL = BASE_URL + "/chat";
    const LEAD_URL = BASE_URL + "/lead";
    const SESSION_URL = BASE_URL + "/session";

    let leadState = {{ collecting: false, name: null, email: null }};
    let expanded = false;
    let messageCount = 0;
    let conversationHistory = [];
    let sessionId = "";

    // Create session on load
    fetch(SESSION_URL, {{
      method: "POST",
      headers: {{ "Content-Type": "application/json" }},
      body: JSON.stringify({{ client_id: CLIENT_ID, page_url: window.location.href }})
    }})
    .then(r => r.json())
    .then(data => {{ sessionId = data.session_id; }})
    .catch(() => {{}});

    // ── Styles ──────────────────────────────────────────────────────────────────
    const style = document.createElement("style");
    style.textContent = `
    @keyframes cwPulse {{
      0% {{ box-shadow: 0 0 0 0 ${{PRIMARY_COLOR}}55; }}
      70% {{ box-shadow: 0 0 0 12px ${{PRIMARY_COLOR}}00; }}
      100% {{ box-shadow: 0 0 0 0 ${{PRIMARY_COLOR}}00; }}
    }}
    @keyframes cwFadeSlideIn {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes cwBounceIn {{
      0% {{ opacity: 0; transform: scale(0.7) translateY(20px); }}
      60% {{ opacity: 1; transform: scale(1.04) translateY(-4px); }}
      100% {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}
    @keyframes cwDot {{
      0%, 80%, 100% {{ transform: scale(0.6); opacity: 0.4; }}
      40% {{ transform: scale(1); opacity: 1; }}
    }}
    @keyframes cwSpin {{
      to {{ transform: rotate(360deg); }}
    }}

    #cw-btn {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      width: 56px;
      height: 56px;
      background: ${{PRIMARY_COLOR}};
      border-radius: 50%;
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      box-shadow: 0 4px 20px ${{PRIMARY_COLOR}}66;
      animation: cwPulse 2.5s infinite;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    #cw-btn:hover {{
      transform: scale(1.08);
      box-shadow: 0 6px 28px ${{PRIMARY_COLOR}}88;
    }}
    #cw-btn svg {{
      width: 26px;
      height: 26px;
      fill: white;
      transition: transform 0.3s ease, opacity 0.2s ease;
    }}
    #cw-btn.open svg.icon-chat {{ opacity: 0; transform: rotate(90deg) scale(0.5); position: absolute; }}
    #cw-btn.open svg.icon-close {{ opacity: 1; transform: rotate(0deg) scale(1); }}
    #cw-btn svg.icon-close {{ opacity: 0; transform: rotate(-90deg) scale(0.5); position: absolute; }}

    #cw-bubble {{
      position: fixed;
      bottom: 92px;
      right: 24px;
      background: white;
      color: #111;
      padding: 9px 16px;
      border-radius: 24px;
      font-size: 13px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-weight: 500;
      box-shadow: 0 4px 20px rgba(0,0,0,0.12);
      cursor: pointer;
      z-index: 999998;
      white-space: nowrap;
      transition: opacity 0.3s ease, transform 0.3s ease;
      animation: cwFadeSlideIn 0.4s ease forwards;
    }}
    #cw-bubble:hover {{ transform: translateY(-2px); }}
    #cw-bubble.hidden {{ opacity: 0 !important; pointer-events: none !important; transform: translateY(6px) !important; }}

    #cw-window {{
      position: fixed;
      bottom: 92px;
      right: 24px;
      width: 360px;
      max-width: calc(100vw - 48px);
      height: 520px;
      max-height: calc(100vh - 120px);
      background: #fff;
      border-radius: 20px;
      box-shadow: 0 12px 48px rgba(0,0,0,0.18), 0 2px 8px rgba(0,0,0,0.08);
      z-index: 999997;
      display: none;
      flex-direction: column;
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    #cw-window.visible {{
      display: flex;
      animation: cwBounceIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
    }}

    #cw-header {{
      background: ${{HEADER_COLOR}};
      padding: 16px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
      flex-shrink: 0;
    }}
    #cw-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: rgba(255,255,255,0.25);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 15px;
      color: white;
      flex-shrink: 0;
    }}
    #cw-header-info {{ flex: 1; }}
    #cw-header-name {{
      color: white;
      font-weight: 700;
      font-size: 15px;
      line-height: 1.2;
    }}
    #cw-header-status {{
      color: rgba(255,255,255,0.75);
      font-size: 12px;
      margin-top: 2px;
    }}
    #cw-close {{
      background: rgba(255,255,255,0.15);
      border: none;
      color: white;
      width: 30px;
      height: 30px;
      border-radius: 50%;
      font-size: 18px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.2s;
      flex-shrink: 0;
      line-height: 1;
    }}
    #cw-close:hover {{ background: rgba(255,255,255,0.25); }}

    #cw-messages {{
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 10px;
      background: #f8f9fb;
    }}
    #cw-messages::-webkit-scrollbar {{ width: 4px; }}
    #cw-messages::-webkit-scrollbar-thumb {{ background: #ddd; border-radius: 4px; }}

    .cw-msg {{
      display: flex;
      gap: 8px;
      align-items: flex-end;
      animation: cwFadeSlideIn 0.25s ease forwards;
    }}
    .cw-msg.user {{ flex-direction: row-reverse; }}
    .cw-msg-avatar {{
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: ${{HEADER_COLOR}};
      color: white;
      font-size: 12px;
      font-weight: 700;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
    }}
    .cw-bubble {{
      max-width: 78%;
      padding: 10px 14px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.5;
      word-break: break-word;
    }}
    .cw-bubble.bot {{
      background: white;
      color: #1a1a1a;
      border-radius: 18px 18px 18px 4px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
    .cw-bubble.user {{
      background: ${{PRIMARY_COLOR}};
      color: white;
      border-radius: 18px 18px 4px 18px;
    }}

    #cw-typing {{
      display: none;
      align-items: flex-end;
      gap: 8px;
      animation: cwFadeSlideIn 0.25s ease forwards;
    }}
    #cw-typing.visible {{ display: flex; }}
    .cw-typing-bubble {{
      background: white;
      border-radius: 18px 18px 18px 4px;
      padding: 12px 16px;
      display: flex;
      gap: 4px;
      align-items: center;
      box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }}
    .cw-dot {{
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #bbb;
      animation: cwDot 1.2s infinite ease-in-out;
    }}
    .cw-dot:nth-child(2) {{ animation-delay: 0.2s; }}
    .cw-dot:nth-child(3) {{ animation-delay: 0.4s; }}

    #cw-input-area {{
      padding: 12px 14px;
      background: white;
      border-top: 1px solid #f0f0f0;
      display: flex;
      gap: 8px;
      align-items: center;
      flex-shrink: 0;
    }}
    #cw-input {{
      flex: 1;
      border: 1.5px solid #e8e8e8;
      border-radius: 12px;
      padding: 10px 14px;
      font-size: 14px;
      outline: none;
      font-family: inherit;
      background: #fafafa;
      transition: border-color 0.2s, background 0.2s;
      color: #1a1a1a;
    }}
    #cw-input:focus {{
      border-color: ${{PRIMARY_COLOR}};
      background: white;
    }}
    #cw-input::placeholder {{ color: #aaa; }}
    #cw-send {{
      width: 38px;
      height: 38px;
      border: none;
      border-radius: 10px;
      background: ${{PRIMARY_COLOR}};
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: transform 0.15s ease, opacity 0.15s ease;
    }}
    #cw-send:hover {{ transform: scale(1.08); }}
    #cw-send:active {{ transform: scale(0.95); }}
    #cw-send svg {{ width: 18px; height: 18px; fill: white; }}

    #cw-footer {{
      text-align: center;
      font-size: 11px;
      color: #ccc;
      padding: 6px 0 10px;
      background: white;
      font-family: inherit;
    }}
  `;
  document.head.appendChild(style);

  // ── DOM ──────────────────────────────────────────────────────────────────────

  // Chat button
  const btn = document.createElement("div");
  btn.id = "cw-btn";
  btn.innerHTML = `
    <svg class="icon-chat" viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/></svg>
    <svg class="icon-close" viewBox="0 0 24 24"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>
  `;
  document.body.appendChild(btn);

  // Bubble label
  const bubble = document.createElement("div");
  bubble.id = "cw-bubble";
  bubble.textContent = "Ask " + BOT_NAME;
  bubble.addEventListener("click", () => openChat());
  document.body.appendChild(bubble);

  // Chat window
  const win = document.createElement("div");
  win.id = "cw-window";
  win.innerHTML = `
    <div id="cw-header">
      <div id="cw-avatar">${{AVATAR_INITIAL}}</div>
      <div id="cw-header-info">
        <div id="cw-header-name">${{BOT_NAME}}</div>
        <div id="cw-header-status">● Online</div>
      </div>
      <button id="cw-close">×</button>
    </div>
    <div id="cw-messages">
      <div id="cw-typing">
        <div class="cw-msg-avatar">${{AVATAR_INITIAL}}</div>
        <div class="cw-typing-bubble">
          <div class="cw-dot"></div>
          <div class="cw-dot"></div>
          <div class="cw-dot"></div>
        </div>
      </div>
    </div>
    <div id="cw-input-area">
      <input id="cw-input" placeholder="Type a message..." autocomplete="off" />
      <button id="cw-send">
        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
      </button>
    </div>
    <div id="cw-footer">Powered by AI</div>
  `;
  document.body.appendChild(win);

  const messagesDiv = win.querySelector("#cw-messages");
  const input = win.querySelector("#cw-input");
  const typingIndicator = win.querySelector("#cw-typing");

  // ── Events ───────────────────────────────────────────────────────────────────
  btn.addEventListener("click", () => {{
    if (expanded) closeChat(); else openChat();
  }});
  win.querySelector("#cw-close").addEventListener("click", closeChat);
  win.querySelector("#cw-send").addEventListener("click", () => sendMessage());
  input.addEventListener("keydown", (e) => {{ if (e.key === "Enter") sendMessage(); }});

  function openChat() {{
    if (expanded) return;
    expanded = true;
    btn.classList.add("open");
    bubble.classList.add("hidden");
    win.classList.add("visible");
    if (messageCount === 0) addMessage("Bot", GREETING);
    setTimeout(() => input.focus(), 400);
  }}

  function closeChat() {{
    expanded = false;
    btn.classList.remove("open");
    bubble.classList.remove("hidden");
    win.classList.remove("visible");
  }}

  // ── Messages ─────────────────────────────────────────────────────────────────
  function showTyping(show) {{
    typingIndicator.classList.toggle("visible", show);
    if (show) messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }}

  async function addMessage(sender, text) {{
    const isBot = sender === "Bot";
    const row = document.createElement("div");
    row.className = "cw-msg" + (isBot ? "" : " user");

    if (isBot) {{
      row.innerHTML = `
        <div class="cw-msg-avatar">${{AVATAR_INITIAL}}</div>
        <div class="cw-bubble bot"></div>
      `;
    }} else {{
      row.innerHTML = `<div class="cw-bubble user"></div>`;
    }}

    // Insert before typing indicator
    messagesDiv.insertBefore(row, typingIndicator);
    messageCount++;

    const bubbleEl = row.querySelector(".cw-bubble");

    if (isBot) {{
      const words = text.split(" ");
      for (const word of words) {{
        bubbleEl.textContent += word + " ";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        await new Promise(r => setTimeout(r, 28));
      }}
    }} else {{
      bubbleEl.textContent = text;
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }}
  }}

  // ── Lead capture ─────────────────────────────────────────────────────────────
  function shouldTriggerLeadCapture(msg) {{
    const t = msg.toLowerCase();
    return ["price","cost","quote","booking","book","appointment",
            "contact","help","support","sign up","join","register"]
      .some(k => t.includes(k));
  }}

  // ── Send ─────────────────────────────────────────────────────────────────────
  async function sendMessage() {{
    const text = input.value.trim();
    if (!text) return;

    if (leadState.collecting) {{
      await addMessage("You", text);
      input.value = "";

      if (!leadState.name) {{
        leadState.name = text;
        await addMessage("Bot", "Thanks! Could I also get your email?");
        return;
      }}

      if (!leadState.email) {{
        const emailValid = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(text);
        if (!emailValid) {{
          await addMessage("Bot", "That doesn't look like a valid email — could you double check it?");
          return;
        }}
        leadState.email = text;
        try {{
          await fetch(LEAD_URL, {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ client_id: CLIENT_ID, name: leadState.name, email: leadState.email }})
          }});
          await addMessage("Bot", "Thanks! Your details have been sent to the team. Someone will be in touch shortly 😊");
          leadState = {{ collecting: false, name: null, email: null }};
        }} catch {{
          await addMessage("Bot", "Sorry, something went wrong saving your details. Please try again.");
          leadState.email = null;
        }}
        return;
      }}
    }}

    await addMessage("You", text);
    input.value = "";
    showTyping(true);

    const pageText = document.body.innerText.replace(/\\s+/g, " ").slice(0, 8000);

    try {{
      conversationHistory.push({{ role: "user", content: text }});

      const res = await fetch(API_URL, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: JSON.stringify({{
          client_id: CLIENT_ID,
          message: text,
          page_content: pageText,
          page_url: window.location.href,
          history: conversationHistory,
          session_id: sessionId
        }})
      }});

      showTyping(false);

      if (!res.ok) {{
        await addMessage("Bot", "Something went wrong. Please try again.");
        return;
      }}

      if (shouldTriggerLeadCapture(text) && !leadState.collecting) {{
        leadState.collecting = true;
        await addMessage("Bot", "I can help with that! Before we continue, could I grab your name?");
        return;
      }}

      // Streaming response
      const row = document.createElement("div");
      row.className = "cw-msg";
      row.innerHTML = `
        <div class="cw-msg-avatar">${{AVATAR_INITIAL}}</div>
        <div class="cw-bubble bot"></div>
      `;
      messagesDiv.insertBefore(row, typingIndicator);
      const botBubble = row.querySelector(".cw-bubble");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullReply = "";

      while (true) {{
        const {{ done, value }} = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        fullReply += chunk;
        const words = chunk.split(" ");
        for (const word of words) {{
          botBubble.textContent += word + " ";
          messagesDiv.scrollTop = messagesDiv.scrollHeight;
          await new Promise(r => setTimeout(r, 28));
        }}
      }}

      conversationHistory.push({{ role: "assistant", content: fullReply }});

    }} catch {{
      showTyping(false);
      await addMessage("Bot", "Connection error. Please try again.");
    }}
  }}

  }}
}})();
"""
    return PlainTextResponse(widget_code, media_type="application/javascript")
