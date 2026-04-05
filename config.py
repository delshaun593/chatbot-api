# In-memory cache for client system prompts.
# Seeded from Supabase at startup (see main.py load_clients_from_supabase).
# Key: client_id (str)  →  Value: system_prompt (str)
CLIENT_PROMPTS: dict[str, str] = {}
