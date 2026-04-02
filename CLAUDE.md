# Travel Ideas Agent

Script Python que cada mañana investiga tendencias de travel content y envía 3 ideas por email vía GitHub Actions.

## Comandos

- `python src/agent.py` — Ejecutar el agente localmente (requiere `.env`)
- `pip install -r requirements.txt` — Instalar dependencias

## Tech Stack

Python 3.12 + Anthropic API (claude-sonnet-4-6 + web_search_20250305) + Resend + GitHub Actions

## Arquitectura

### Flujo de ejecución
1. `agent.py` carga env vars y construye prompts desde `prompts.py`
2. Llama a Claude con el tool `web_search_20250305` activado
3. Claude investiga tendencias y retorna JSON con 3 ideas
4. `email_template.py` convierte el JSON a HTML con estilos inline
5. Resend envía el email al destinatario configurado en `EMAIL_TO`

### Archivos clave
- `src/agent.py` — Orquestador principal
- `src/prompts.py` — SYSTEM_PROMPT y `build_user_prompt()`
- `src/email_template.py` — `render_html(ideas) -> (subject, html_body)`
- `.github/workflows/daily-ideas.yml` — Cron job: 12:00 UTC todos los días

### Parseo de respuesta de Claude
Claude retorna múltiples bloques de contenido (tool_use + text).
`agent.py` itera `response.content` buscando el bloque `type == "text"` que contiene el JSON.
Si el JSON no empieza con `{`, busca la primera `{` y última `}` para extraerlo.

## Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key de Anthropic (console.anthropic.com) |
| `RESEND_API_KEY` | API key de Resend (resend.com/api-keys) |
| `EMAIL_TO` | Email destinatario |

Para desarrollo local: copiar `.env.example` a `.env` y completar con claves reales.
Para producción: configurar como GitHub Actions Secrets.

## Reglas No Negociables

1. Nunca hardcodear API keys. Siempre desde variables de entorno.
2. El script sale con `sys.exit(1)` ante cualquier error — GitHub Actions lo marca como fallido.
3. El JSON de Claude se valida antes de pasar a email_template (3 ideas, 5 campos cada una).
4. El `from` del email en producción debe ser un dominio verificado en Resend.
5. No modificar el SYSTEM_PROMPT sin actualizar también el parser en agent.py.
