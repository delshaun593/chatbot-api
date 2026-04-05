"""
Email notification service for NXTIER using Resend.
Sends a formatted lead alert to the business owner whenever a lead is captured.

Requires env var: RESEND_API_KEY
Optional env var: RESEND_FROM (defaults to onboarding@resend.dev for sandbox testing)
"""
import os
import asyncio
import httpx
from datetime import datetime

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_FROM = os.getenv("RESEND_FROM", "onboarding@resend.dev")
RESEND_URL = "https://api.resend.com/emails"


async def send_lead_notification(
    *,
    owner_email: str,
    business_name: str,
    lead_name: str,
    lead_email: str,
    page_url: str = "",
) -> bool:
    """
    Fire-and-forget: sends a lead alert email to the business owner.
    Returns True on success, False on failure (never raises).
    """
    if not RESEND_API_KEY:
        print("⚠️  RESEND_API_KEY not set — skipping lead email notification")
        return False

    now = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")
    page_line = f"<p><strong>Page:</strong> {page_url}</p>" if page_url else ""

    html_body = f"""
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; max-width: 560px; margin: 0 auto; background: #fafafa; border-radius: 12px; overflow: hidden; border: 1px solid #e5e7eb;">
      <div style="background: linear-gradient(135deg, #4f46e5, #6366f1); padding: 28px 32px;">
        <h1 style="color: #fff; margin: 0; font-size: 22px; font-weight: 800; letter-spacing: -0.5px;">
          🎉 New Lead Captured
        </h1>
        <p style="color: rgba(255,255,255,0.8); margin: 6px 0 0; font-size: 14px;">{now}</p>
      </div>
      <div style="padding: 28px 32px; background: #fff;">
        <p style="color: #374151; font-size: 15px; margin: 0 0 20px;">
          Someone just enquired via your <strong>{business_name}</strong> chatbot:
        </p>
        <div style="background: #f3f4f6; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
          <p style="margin: 0 0 10px; font-size: 15px;"><strong>Name:</strong> {lead_name}</p>
          <p style="margin: 0 0 10px; font-size: 15px;"><strong>Email:</strong> <a href="mailto:{lead_email}" style="color: #4f46e5;">{lead_email}</a></p>
          {page_line}
        </div>
        <a href="mailto:{lead_email}" style="display: inline-block; background: linear-gradient(135deg, #4f46e5, #6366f1); color: #fff; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 700; font-size: 14px;">
          Reply to {lead_name} →
        </a>
      </div>
      <div style="padding: 16px 32px; background: #f9fafb; border-top: 1px solid #e5e7eb;">
        <p style="color: #9ca3af; font-size: 12px; margin: 0;">
          Sent by <strong>NXTIER</strong> · View your dashboard at
          <a href="https://chatbot-api-4ssr.onrender.com/admin" style="color: #6366f1;">nxtier.app/admin</a>
        </p>
      </div>
    </div>
    """

    payload = {
        "from": RESEND_FROM,
        "to": [owner_email],
        "subject": f"🎉 New lead from {lead_name} — {business_name}",
        "html": html_body,
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                RESEND_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code in (200, 201):
                print(f"✅ Lead email sent to {owner_email}")
                return True
            else:
                print(f"⚠️  Resend API error {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        print(f"⚠️  Lead email failed: {e}")
        return False
