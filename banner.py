from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from database import supabase

router = APIRouter()

BASE_URL = "https://chatbot-api-4ssr.onrender.com"


# ── Models ─────────────────────────────────────────────────────────────────────
class BannerUpdateRequest(BaseModel):
    client_id: str
    pin: str
    message: str
    cta_text: str = ""
    cta_url: str = ""
    bg_color: str = "1a1a2e"
    text_color: str = "ffffff"
    active: bool = True


from auth import verify_pin


@router.get("/banner/config")
async def get_banner_config(client_id: str):
    """Returns the active banner config for a client (public)."""
    try:
        res = (
            supabase.table("banners")
            .select("*")
            .eq("client_id", client_id)
            .execute()
        )
        data = res.data
        if not data:
            return {}
        return data[0]
    except Exception:
        return {}


@router.post("/banner/update")
async def update_banner(req: BannerUpdateRequest):
    """Create or update a client's banner (PIN-authenticated)."""
    if not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "client_id": req.client_id,
        "message": req.message,
        "cta_text": req.cta_text,
        "cta_url": req.cta_url,
        "bg_color": req.bg_color.lstrip("#"),
        "text_color": req.text_color.lstrip("#"),
        "active": req.active,
    }
    try:
        existing = (
            supabase.table("banners")
            .select("id")
            .eq("client_id", req.client_id)
            .execute()
        )
        if existing.data:
            supabase.table("banners").update(payload).eq("client_id", req.client_id).execute()
        else:
            supabase.table("banners").insert(payload).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/banner.js")
def serve_banner(client_id: str):
    """Serves the self-contained announcement banner widget JS."""
    js = f"""
(function() {{
  var CLIENT_ID = "{client_id}";
  var BASE_URL  = "{BASE_URL}";
  var DISMISSED_KEY = "tk_banner_" + CLIENT_ID;

  if (sessionStorage.getItem(DISMISSED_KEY)) return;

  fetch(BASE_URL + "/banner/config?client_id=" + CLIENT_ID)
    .then(function(r) {{ return r.json(); }})
    .then(function(cfg) {{
      if (!cfg || !cfg.active || !cfg.message) return;

      var bgColor  = cfg.bg_color  || "1a1a2e";
      var txtColor = cfg.text_color || "ffffff";

      var style = document.createElement("style");
      style.textContent = [
        "#tk-banner {{",
        "  position:fixed;top:0;left:0;right:0;",
        "  background:#" + bgColor + ";",
        "  color:#" + txtColor + ";",
        "  padding:13px 52px 13px 24px;",
        "  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
        "  font-size:14px;font-weight:500;line-height:1.4;",
        "  z-index:1000000;",
        "  display:flex;align-items:center;justify-content:center;gap:14px;",
        "  transform:translateY(-100%);",
        "  transition:transform 0.4s cubic-bezier(0.4,0,0.2,1);",
        "  box-shadow:0 2px 16px rgba(0,0,0,0.28);",
        "}}",
        "#tk-banner.tk-visible {{ transform:translateY(0); }}",
        "body.tk-banner-open {{ padding-top:48px; transition:padding-top 0.4s cubic-bezier(0.4,0,0.2,1); }}",
        "#tk-banner-cta {{",
        "  background:rgba(255,255,255,0.18);",
        "  border:1px solid rgba(255,255,255,0.4);",
        "  color:inherit;padding:5px 18px;border-radius:20px;",
        "  cursor:pointer;font-size:13px;font-weight:700;",
        "  text-decoration:none;white-space:nowrap;flex-shrink:0;",
        "  transition:background 0.2s;",
        "}}",
        "#tk-banner-cta:hover {{ background:rgba(255,255,255,0.3); }}",
        "#tk-banner-close {{",
        "  position:absolute;right:16px;background:none;border:none;",
        "  color:inherit;font-size:22px;cursor:pointer;opacity:0.7;",
        "  line-height:1;padding:0;font-family:inherit;",
        "}}",
        "#tk-banner-close:hover {{ opacity:1; }}"
      ].join("");
      document.head.appendChild(style);

      var ctaHTML = (cfg.cta_text && cfg.cta_url)
        ? '<a id="tk-banner-cta" href="' + cfg.cta_url + '" target="_blank" rel="noopener">' + cfg.cta_text + '</a>'
        : "";

      var el = document.createElement("div");
      el.id = "tk-banner";
      el.innerHTML = '<span id="tk-banner-msg">' + cfg.message + '</span>' +
                     ctaHTML +
                     '<button id="tk-banner-close" aria-label="Close banner">\u00d7</button>';
      document.body.insertBefore(el, document.body.firstChild);

      setTimeout(function() {{
        el.classList.add("tk-visible");
        document.body.classList.add("tk-banner-open");
      }}, 150);

      document.getElementById("tk-banner-close").addEventListener("click", function() {{
        el.classList.remove("tk-visible");
        document.body.classList.remove("tk-banner-open");
        setTimeout(function() {{ el.remove(); }}, 420);
        sessionStorage.setItem(DISMISSED_KEY, "1");
      }});
    }})
    .catch(function() {{}});
}})();
"""
    return PlainTextResponse(js, media_type="application/javascript")
