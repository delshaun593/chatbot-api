from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

router = APIRouter()

BASE_URL = "https://chatbot-api-4ssr.onrender.com"


@router.get("/toolkit.js")
def serve_toolkit(
    client_id: str,
    bot_name: str = "Assistant",
    primary_color: str = "007bff",
    header_color: str = "",
    greeting: str = "Hi there 👋 How can I help you?",
):
    """
    Unified loader that initialises all three toolkit widgets in parallel:
      1. Announcement Banner   (/banner.js)
      2. Social Proof Reviews  (/reviews.js)
      3. AI Chatbot            (/widget.js)
    Only widgets with active data render; the others silently skip.
    """
    widget_url = (
        f"{BASE_URL}/widget.js"
        f"?client_id={client_id}"
        f"&bot_name={bot_name}"
        f"&primary_color={primary_color}"
        f"&header_color={header_color}"
        f"&greeting={greeting}"
    )

    js = f"""
/* ── Website Toolkit v1.0 ──────────────────────────────────────────────────── */
(function() {{
  var BASE_URL   = "{BASE_URL}";
  var CLIENT_ID  = "{client_id}";
  var WIDGET_URL = "{widget_url}";

  function load(url) {{
    return fetch(url)
      .then(function(r) {{ return r.text(); }})
      .then(function(code) {{
        try {{ (0, eval)(code); }} catch (e) {{}}
      }})
      .catch(function() {{}});
  }}

  // Fire all three widgets in parallel — each silently no-ops if no data found
  load(BASE_URL + "/banner.js?client_id="  + CLIENT_ID);
  load(BASE_URL + "/reviews.js?client_id=" + CLIENT_ID);
  load(WIDGET_URL);
}})();
/* ─────────────────────────────────────────────────────────────────────────── */
"""
    return PlainTextResponse(js, media_type="application/javascript")
