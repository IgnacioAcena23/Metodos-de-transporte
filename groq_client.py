"""
groq_client.py
Módulo compartido para llamadas a la API de Groq.
Usa únicamente la librería estándar de Python (urllib, json, os).
"""
import json
import os
import urllib.request
import urllib.error

# ── Carga automática del .env ────────────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

_GROQ_URL    = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL  = "llama-3.1-8b-instant"
_TIMEOUT     = 20   # segundos


def consultar_groq(prompt: str, max_tokens: int = 600) -> str:
    """
    Envía *prompt* a Groq y devuelve el texto de la respuesta.
    Lanza RuntimeError con el mensaje de error si algo falla.
    """
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "No se encontró GROQ_API_KEY.\n"
            "Asegúrate de que el archivo .env esté en la misma carpeta."
        )

    payload = {
        "model": _GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type":  "application/json",
        "User-Agent":    "Mozilla/5.0",
    }
    req = urllib.request.Request(
        _GROQ_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code} – {e.reason}\n{body}")
    except Exception as exc:
        raise RuntimeError(str(exc))
