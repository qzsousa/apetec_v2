import os
import uuid
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://givhqyiighixtwsgzujo.supabase.co").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "apetec-itens")


def _headers():
    return {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "apikey": SUPABASE_SERVICE_KEY,
    }


def ensure_bucket():
    if not SUPABASE_SERVICE_KEY:
        raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY nao configurada")
    url = f"{SUPABASE_URL}/storage/v1/bucket"
    try:
        requests.post(
            url,
            json={"id": SUPABASE_BUCKET, "name": SUPABASE_BUCKET, "public": True},
            headers=_headers(),
            timeout=20,
        )
    except Exception:
        pass


def upload_file(file_bytes: bytes, content_type: str, path: str) -> str:
    ensure_bucket()
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{path}"
    headers = _headers()
    headers["Content-Type"] = content_type or "application/octet-stream"
    r = requests.post(url, data=file_bytes, headers=headers, timeout=120)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Falha no upload: {r.status_code} {r.text}")
    return f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{path}"


def delete_file(path: str) -> None:
    if not SUPABASE_SERVICE_KEY:
        return
    url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{path}"
    requests.delete(url, headers=_headers(), timeout=20)
