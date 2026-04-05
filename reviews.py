from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from database import supabase

router = APIRouter()

BASE_URL = "https://chatbot-api-4ssr.onrender.com"


# ── Models ─────────────────────────────────────────────────────────────────────
class ReviewAddRequest(BaseModel):
    client_id: str
    pin: str
    reviewer_name: str
    rating: int = 5
    text: str


class ReviewActionRequest(BaseModel):
    client_id: str
    pin: str
    review_id: str


class ReviewToggleRequest(BaseModel):
    client_id: str
    pin: str
    review_id: str
    approved: bool


from auth import verify_pin


# ── Routes ─────────────────────────────────────────────────────────────────────
@router.get("/reviews/list")
async def list_reviews(client_id: str):
    """Returns all approved reviews for a client (public)."""
    try:
        res = (
            supabase.table("reviews")
            .select("id, reviewer_name, rating, text, created_at")
            .eq("client_id", client_id)
            .eq("approved", True)
            .order("created_at")
            .execute()
        )
        return res.data or []
    except Exception:
        return []


@router.get("/reviews/all")
async def list_all_reviews(client_id: str, pin: str):
    """Returns all reviews including hidden ones — for the admin dashboard."""
    if not verify_pin(client_id, pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        res = (
            supabase.table("reviews")
            .select("*")
            .eq("client_id", client_id)
            .order("created_at", desc=True)
            .execute()
        )
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/add")
async def add_review(req: ReviewAddRequest):
    """Add a new review for a client (PIN-authenticated)."""
    if not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    rating = max(1, min(5, req.rating))
    try:
        supabase.table("reviews").insert({
            "client_id": req.client_id,
            "reviewer_name": req.reviewer_name,
            "rating": rating,
            "text": req.text,
            "approved": True,
        }).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/delete")
async def delete_review(req: ReviewActionRequest):
    """Permanently delete a review (PIN-authenticated)."""
    if not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        supabase.table("reviews").delete()\
            .eq("id", req.review_id)\
            .eq("client_id", req.client_id)\
            .execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reviews/toggle")
async def toggle_review(req: ReviewToggleRequest):
    """Show or hide a review on the widget (PIN-authenticated)."""
    if not verify_pin(req.client_id, req.pin):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        supabase.table("reviews").update({"approved": req.approved})\
            .eq("id", req.review_id)\
            .eq("client_id", req.client_id)\
            .execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviews.js")
def serve_reviews(client_id: str):
    """Serves the self-contained social proof reviews widget JS."""
    js = f"""
(function() {{
  var CLIENT_ID = "{client_id}";
  var BASE_URL   = "{BASE_URL}";

  fetch(BASE_URL + "/reviews/list?client_id=" + CLIENT_ID)
    .then(function(r) {{ return r.json(); }})
    .then(function(reviews) {{
      if (!reviews || reviews.length === 0) return;

      // ── Styles ─────────────────────────────────────────────────────────────
      var style = document.createElement("style");
      style.textContent = [
        "#tk-rev-btn {{",
        "  position:fixed;bottom:20px;left:20px;",
        "  background:#fff;border-radius:28px;",
        "  box-shadow:0 4px 20px rgba(0,0,0,0.13);",
        "  padding:10px 18px 10px 14px;",
        "  display:flex;align-items:center;gap:10px;",
        "  cursor:pointer;z-index:999998;",
        "  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;",
        "  font-size:13px;font-weight:600;color:#111;",
        "  border:1px solid rgba(0,0,0,0.07);",
        "  transition:transform 0.2s ease,box-shadow 0.2s ease;",
        "  user-select:none;",
        "}}",
        "#tk-rev-btn:hover {{ transform:translateY(-2px); box-shadow:0 6px 28px rgba(0,0,0,0.18); }}",
        ".tk-r-stars {{ color:#f59e0b;font-size:14px;letter-spacing:1px; }}",
        "#tk-rev-panel {{",
        "  position:fixed;bottom:80px;left:20px;width:300px;",
        "  background:#fff;border-radius:16px;",
        "  box-shadow:0 8px 36px rgba(0,0,0,0.18);",
        "  z-index:999997;overflow:hidden;",
        "  opacity:0;transform:translateY(14px) scale(0.97);",
        "  transition:opacity 0.3s ease,transform 0.3s ease;",
        "  pointer-events:none;",
        "}}",
        "#tk-rev-panel.tk-open {{ opacity:1;transform:translateY(0) scale(1);pointer-events:auto; }}",
        "#tk-rev-header {{",
        "  padding:14px 16px;background:#111;color:#fff;",
        "  font-weight:700;font-size:14px;",
        "  display:flex;align-items:center;justify-content:space-between;",
        "}}",
        "#tk-rev-close {{",
        "  background:none;border:none;color:#fff;",
        "  font-size:20px;cursor:pointer;line-height:1;padding:0;",
        "}}",
        "#tk-rev-scroll {{",
        "  overflow-y:auto;max-height:320px;padding:12px;",
        "  display:flex;flex-direction:column;gap:10px;",
        "}}",
        "#tk-rev-scroll::-webkit-scrollbar {{ width:5px; }}",
        "#tk-rev-scroll::-webkit-scrollbar-thumb {{ background:#e0e0e0;border-radius:4px; }}",
        ".tk-rev-card {{",
        "  background:#f9fafb;border-radius:10px;",
        "  padding:12px 14px;border:1px solid #eee;",
        "  animation:tkRevFade 0.35s ease;",
        "}}",
        "@keyframes tkRevFade {{ from{{opacity:0;transform:translateY(6px);}} to{{opacity:1;transform:none;}} }}",
        ".tk-rev-top {{ display:flex;align-items:center;justify-content:space-between;margin-bottom:6px; }}",
        ".tk-rev-name {{ font-weight:700;font-size:13px;color:#111; }}",
        ".tk-rev-r {{ color:#f59e0b;font-size:12px;letter-spacing:1px; }}",
        ".tk-rev-text {{ font-size:13px;color:#444;line-height:1.55; }}"
      ].join("");
      document.head.appendChild(style);

      // ── Stats ──────────────────────────────────────────────────────────────
      var total = reviews.reduce(function(s, r) {{ return s + (r.rating || 5); }}, 0);
      var avg   = (total / reviews.length).toFixed(1);
      var count = reviews.length;
      var label = avg + " \u00b7 " + count + " review" + (count !== 1 ? "s" : "");

      // ── Floating button ────────────────────────────────────────────────────
      var btn = document.createElement("div");
      btn.id = "tk-rev-btn";
      btn.setAttribute("role", "button");
      btn.setAttribute("aria-label", "Show customer reviews");
      btn.innerHTML = '<span class="tk-r-stars">\u2605\u2605\u2605\u2605\u2605</span>' +
                      '<span id="tk-rev-label">' + label + '</span>';
      document.body.appendChild(btn);

      // ── Panel ──────────────────────────────────────────────────────────────
      var cardsHTML = reviews.map(function(r) {{
        var filled = Math.round(r.rating || 5);
        var stars  = "\u2605".repeat(filled) + "\u2606".repeat(5 - filled);
        return '<div class="tk-rev-card">' +
               '  <div class="tk-rev-top">' +
               '    <span class="tk-rev-name">' + r.reviewer_name + '</span>' +
               '    <span class="tk-rev-r">' + stars + '</span>' +
               '  </div>' +
               '  <div class="tk-rev-text">' + r.text + '</div>' +
               '</div>';
      }}).join("");

      var panel = document.createElement("div");
      panel.id = "tk-rev-panel";
      panel.innerHTML =
        '<div id="tk-rev-header">' +
        '  <span>\u2b50 Customer Reviews</span>' +
        '  <button id="tk-rev-close" aria-label="Close">\u00d7</button>' +
        '</div>' +
        '<div id="tk-rev-scroll">' + cardsHTML + '</div>';
      document.body.appendChild(panel);

      // ── Cycle reviewer names in collapsed button ────────────────────────────
      var idx = 0;
      setInterval(function() {{
        idx = (idx + 1) % reviews.length;
        var lbl = document.getElementById("tk-rev-label");
        if (!lbl) return;
        lbl.textContent = "\u201c" + reviews[idx].reviewer_name + "\u201d \u00b7 " + count + " review" + (count !== 1 ? "s" : "");
        setTimeout(function() {{
          if (lbl) lbl.textContent = label;
        }}, 3000);
      }}, 5000);

      // ── Toggle open / close ────────────────────────────────────────────────
      btn.addEventListener("click", function() {{
        panel.classList.toggle("tk-open");
      }});
      document.getElementById("tk-rev-close").addEventListener("click", function(e) {{
        e.stopPropagation();
        panel.classList.remove("tk-open");
      }});
      document.addEventListener("click", function(e) {{
        if (!panel.contains(e.target) && !btn.contains(e.target)) {{
          panel.classList.remove("tk-open");
        }}
      }});
    }})
    .catch(function() {{}});
}})();
"""
    return PlainTextResponse(js, media_type="application/javascript")
