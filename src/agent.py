import json
import os
import sys

import anthropic
import resend
from dotenv import load_dotenv

from email_template import render_html
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()


def get_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        print(f"[ERROR] Variable de entorno faltante: {key}", file=sys.stderr)
        sys.exit(1)
    return value


def call_claude(client: anthropic.Anthropic) -> list[dict]:
    user_prompt = build_user_prompt()

    print("[INFO] Llamando a Claude con web_search activado...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_prompt}],
    )

    # Extraer el bloque de texto con el JSON de la respuesta
    raw_json = None
    for block in response.content:
        if block.type == "text" and block.text.strip().startswith("{"):
            raw_json = block.text.strip()
            break

    if not raw_json:
        # Intentar encontrar JSON en cualquier bloque de texto
        for block in response.content:
            if block.type == "text" and "{" in block.text:
                start = block.text.find("{")
                end = block.text.rfind("}") + 1
                raw_json = block.text[start:end]
                break

    if not raw_json:
        print("[ERROR] Claude no retornó un JSON válido.", file=sys.stderr)
        print(f"[DEBUG] Respuesta completa: {response.content}", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo parsear el JSON de Claude: {e}", file=sys.stderr)
        print(f"[DEBUG] Raw JSON: {raw_json}", file=sys.stderr)
        sys.exit(1)

    ideas = data.get("ideas", [])
    if len(ideas) != 3:
        print(f"[ERROR] Se esperaban 3 ideas, se recibieron {len(ideas)}.", file=sys.stderr)
        sys.exit(1)

    # Validar campos requeridos
    required_fields = ["plataforma", "tendencia_base", "gancho", "desarrollo", "cta"]
    for i, idea in enumerate(ideas):
        for field in required_fields:
            if not idea.get(field):
                print(f"[ERROR] Idea {i+1} falta el campo '{field}'.", file=sys.stderr)
                sys.exit(1)

    print(f"[INFO] 3 ideas generadas correctamente.")
    return ideas


def send_email(ideas: list[dict], email_to: str) -> None:
    subject, html_body = render_html(ideas)

    print(f"[INFO] Enviando email a {email_to}...")
    response = resend.Emails.send({
        "from": "Travel Ideas <onboarding@resend.dev>",
        "to": [email_to],
        "subject": subject,
        "html": html_body,
    })

    if not response.get("id"):
        print(f"[ERROR] Resend no retornó un ID de email. Respuesta: {response}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] ✓ Email enviado. ID: {response['id']}")


def main() -> None:
    anthropic_key = get_env("ANTHROPIC_API_KEY")
    resend_key = get_env("RESEND_API_KEY")
    email_to = get_env("EMAIL_TO")

    resend.api_key = resend_key
    claude_client = anthropic.Anthropic(api_key=anthropic_key)

    ideas = call_claude(claude_client)
    send_email(ideas, email_to)

    print(f"[INFO] ✓ Agente completado exitosamente.")


if __name__ == "__main__":
    main()
