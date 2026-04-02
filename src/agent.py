import json
import os
import sys

import resend
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from groq import Groq

from email_template import render_html
from prompts import SYSTEM_PROMPT, build_search_queries, build_user_prompt

load_dotenv()


def get_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        print(f"[ERROR] Variable de entorno faltante: {key}", file=sys.stderr)
        sys.exit(1)
    return value


def search_trends() -> str:
    queries = build_search_queries()
    all_results = []

    print("[INFO] Buscando tendencias con DuckDuckGo...")
    with DDGS() as ddgs:
        for query in queries:
            try:
                results = list(ddgs.text(query, max_results=5))
                for r in results:
                    all_results.append(f"- {r.get('title', '')}: {r.get('body', '')}")
            except Exception as e:
                print(f"[WARN] Error en búsqueda '{query}': {e}", file=sys.stderr)

    if not all_results:
        print("[ERROR] No se obtuvieron resultados de búsqueda.", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] {len(all_results)} resultados obtenidos.")
    return "\n".join(all_results[:15])  # Máximo 15 resultados para no exceder tokens


def call_groq(client: Groq, search_results: str) -> list[dict]:
    user_prompt = build_user_prompt(search_results)

    print("[INFO] Generando ideas con Groq...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )

    raw_text = response.choices[0].message.content.strip()

    # Extraer JSON si viene envuelto en markdown code block
    if "```json" in raw_text:
        start = raw_text.find("```json") + 7
        end = raw_text.find("```", start)
        raw_text = raw_text[start:end].strip()
    elif "```" in raw_text:
        start = raw_text.find("```") + 3
        end = raw_text.find("```", start)
        raw_text = raw_text[start:end].strip()

    # Extraer JSON si hay texto antes o después
    if not raw_text.startswith("{"):
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start == -1:
            print("[ERROR] Groq no retornó un JSON válido.", file=sys.stderr)
            print(f"[DEBUG] Respuesta: {raw_text}", file=sys.stderr)
            sys.exit(1)
        raw_text = raw_text[start:end]

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo parsear el JSON: {e}", file=sys.stderr)
        print(f"[DEBUG] Raw text: {raw_text}", file=sys.stderr)
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

    print("[INFO] 3 ideas generadas correctamente.")
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
        print(f"[ERROR] Resend no retornó un ID. Respuesta: {response}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] ✓ Email enviado. ID: {response['id']}")


def main() -> None:
    groq_key = get_env("GROQ_API_KEY")
    resend_key = get_env("RESEND_API_KEY")
    email_to = get_env("EMAIL_TO")

    resend.api_key = resend_key
    groq_client = Groq(api_key=groq_key)

    search_results = search_trends()
    ideas = call_groq(groq_client, search_results)
    send_email(ideas, email_to)

    print("[INFO] ✓ Agente completado exitosamente.")


if __name__ == "__main__":
    main()
