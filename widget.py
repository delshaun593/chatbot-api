from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
 
router = APIRouter()
 
 
@router.get("/widget.js")
def serve_widget(
    client_id: str,
    primary_color: str = "007bff",
    bot_name: str = "Assistant",
    greeting: str = "Hi there 👋 How can I help you?"
):
    widget_code = f"""
(function() {{
  const CLIENT_ID = "{client_id}";
  const API_URL = "https://chatbot-api-4ssr.onrender.com/chat";
  const LEAD_URL = "https://chatbot-api-4ssr.onrender.com/lead";
  const PRIMARY_COLOR = "#{primary_color}";
  const BOT_NAME = "{bot_name}";
  const GREETING = "{greeting}";
 
  let leadState = {{ collecting: false, name: null, email: null }};
  let expanded = false;
  let messageCount = 0;
  let conversationHistory = [];
  let sessionId = "";
 
  // Create session on load
  fetch(API_URL.replace("/chat", "/session"), {{
    method: "POST",
    headers: {{ "Content-Type": "application/json" }},
    body: JSON.stringify({{
      client_id: CLIENT_ID,
      page_url: window.location.href
    }})
  }})
  .then(r => r.json())
  .then(data => {{ sessionId = data.session_id; }})
  .catch(() => {{}});
 
  // Inject styles
  const style = document.createElement("style");
  style.textContent = `
    #chat-widget-container {{
      position: fixed;
      bottom: 20px;
      right: 20px;
      width: 48px;
      height: 48px;
      background: #111;
      border-radius: 50%;
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s ease;
      overflow: hidden;
    }}
    #chat-widget-container.expanded {{
      width: 320px;
      height: 400px;
      border-radius: 12px;
      background: #fff;
      flex-direction: column;
      cursor: auto;
    }}
    #chat-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 14px;
      background: #111;
      color: white;
      font-weight: 600;
      font-size: 14px;
      flex-shrink: 0;
    }}
    #chat-header .toggle-btn {{
      background: transparent;
      border: none;
      color: white;
      font-size: 18px;
      cursor: pointer;
    }}
    #chat-messages {{
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }}
    .chat-bubble {{
      max-width: 75%;
      padding: 10px 12px;
      border-radius: 16px;
      line-height: 1.4;
      font-size: 14px;
    }}
    .chat-user {{
      background: ${{PRIMARY_COLOR}};
      color: white;
      align-self: flex-end;
    }}
    .chat-bot {{
      background: #eee;
      border: 1px solid #ddd;
      align-self: flex-start;
    }}
    #chat-input-area {{
      display: flex;
      padding: 8px;
      border-top: 1px solid #ddd;
      gap: 6px;
      flex-shrink: 0;
    }}
    #chat-input {{
      flex: 1;
      border-radius: 10px;
      border: 1px solid #ccc;
      padding: 8px 10px;
      outline: none;
      font-size: 14px;
    }}
    #chat-input:focus {{
      border-color: ${{PRIMARY_COLOR}};
    }}
    #chat-send {{
      border: none;
      padding: 8px 12px;
      background: ${{PRIMARY_COLOR}};
      color: white;
      border-radius: 10px;
      cursor: pointer;
      font-size: 14px;
    }}
    #chat-messages::-webkit-scrollbar {{ width: 6px; }}
    #chat-messages::-webkit-scrollbar-thumb {{ background: #ccc; border-radius: 4px; }}
    #chat-icon {{ color: white; font-size: 22px; }}
  `;
  document.head.appendChild(style);
 
  // Create container
  const container = document.createElement("div");
  container.id = "chat-widget-container";
  container.innerHTML = '<span id="chat-icon">💬</span>';
  document.body.appendChild(container);
 
  function buildExpandedContent() {{
    container.innerHTML = `
      <div id="chat-header">
        <span>${{BOT_NAME}}</span>
        <button class="toggle-btn">−</button>
      </div>
      <div id="chat-messages"></div>
      <div id="chat-input-area">
        <input id="chat-input" placeholder="Type a message..." autocomplete="off"/>
        <button id="chat-send">Send</button>
      </div>
    `;
 
    const messagesDiv = container.querySelector("#chat-messages");
    const input = container.querySelector("#chat-input");
    const sendBtn = container.querySelector("#chat-send");
    const toggleBtn = container.querySelector(".toggle-btn");
 
    toggleBtn.addEventListener("click", (e) => {{
      e.stopPropagation();
      minimizeChat();
    }});
 
    sendBtn.addEventListener("click", () => sendMessage(input, messagesDiv));
    input.addEventListener("keydown", (e) => {{
      if (e.key === "Enter") sendMessage(input, messagesDiv);
    }});
 
    return {{ messagesDiv, input }};
  }}
 
  function expandChat() {{
    if (expanded) return;
    expanded = true;
    container.classList.add("expanded");
    const {{ messagesDiv, input }} = buildExpandedContent();
    addMessage(messagesDiv, "Bot", GREETING);
  }}
 
  function minimizeChat() {{
    expanded = false;
    container.classList.remove("expanded");
    container.innerHTML = '<span id="chat-icon">💬</span>';
    conversationHistory = [];
  }}
 
  container.addEventListener("click", () => {{
    if (!expanded) expandChat();
  }});
 
  async function addMessage(messagesDiv, sender, text) {{
    const msg = document.createElement("div");
    msg.className = "chat-bubble " + (sender === "You" ? "chat-user" : "chat-bot");
    messagesDiv.appendChild(msg);
    messageCount++;
    if (messageCount > 5) messagesDiv.style.overflowY = "auto";
 
    if (sender === "Bot") {{
      const words = text.split(" ");
      for (const word of words) {{
        msg.textContent += word + " ";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        await new Promise(resolve => setTimeout(resolve, 30));
      }}
    }} else {{
      msg.textContent = text;
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }}
  }}
 
  function shouldTriggerLeadCapture(userMessage) {{
    const text = userMessage.toLowerCase();
    const highIntentKeywords = [
      "price", "cost", "quote", "booking", "book",
      "appointment", "contact", "help", "support",
      "sign up", "join", "register"
    ];
    return highIntentKeywords.some(keyword => text.includes(keyword));
  }}
 
  async function sendMessage(input, messagesDiv) {{
    const text = input.value.trim();
    if (!text) return;
 
    if (leadState.collecting) {{
      await addMessage(messagesDiv, "You", text);
      input.value = "";
 
      if (!leadState.name) {{
        leadState.name = text;
        await addMessage(messagesDiv, "Bot", "Thanks! Could I also get your email?");
        return;
      }}
 
      if (!leadState.email) {{
        const emailValid = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(text);
        if (!emailValid) {{
          await addMessage(messagesDiv, "Bot", "That doesn't look like a valid email, could you double check it?");
          return;
        }}
 
        leadState.email = text;
        try {{
          await fetch(LEAD_URL, {{
            method: "POST",
            headers: {{ "Content-Type": "application/json" }},
            body: JSON.stringify({{ client_id: CLIENT_ID, name: leadState.name, email: leadState.email }})
          }});
          await addMessage(messagesDiv, "Bot", "Thanks! Your details have been sent to the team. Someone will be in touch shortly 😊");
          leadState = {{ collecting: false, name: null, email: null }};
        }} catch {{
          await addMessage(messagesDiv, "Bot", "Sorry, something went wrong saving your details. Please try again.");
          leadState.email = null;
        }}
        return;
      }}
    }}
 
    await addMessage(messagesDiv, "You", text);
    input.value = "";
    showLoading(messagesDiv, true);
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
 
      showLoading(messagesDiv, false);
 
      if (!res.ok) {{
        await addMessage(messagesDiv, "Bot", `Error: ${{res.status}}`);
        return;
      }}
 
      if (shouldTriggerLeadCapture(text) && !leadState.collecting) {{
        leadState.collecting = true;
        await addMessage(messagesDiv, "Bot", "I can help with that! Before we continue, could I grab your name?");
        return;
      }}
 
      const botBubble = document.createElement("div");
      botBubble.className = "chat-bubble chat-bot";
      messagesDiv.appendChild(botBubble);
 
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
          await new Promise(resolve => setTimeout(resolve, 30));
        }}
      }}
 
      conversationHistory.push({{ role: "assistant", content: fullReply }});
 
    }} catch {{
      showLoading(messagesDiv, false);
      await addMessage(messagesDiv, "Bot", "Connection error.");
    }}
  }}
 
  function showLoading(messagesDiv, show) {{
    let loading = container.querySelector("#loading-indicator");
    if (show) {{
      if (!loading) {{
        loading = document.createElement("div");
        loading.id = "loading-indicator";
        loading.textContent = "Bot is typing...";
        loading.style.cssText = "font-size:12px; color:#888; padding: 4px 8px;";
        messagesDiv.appendChild(loading);
      }}
    }} else if (loading) {{
      loading.remove();
    }}
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }}
 
}})();
"""
    return PlainTextResponse(widget_code, media_type="application/javascript")
