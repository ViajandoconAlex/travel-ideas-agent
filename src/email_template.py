from datetime import datetime

PLATFORM_ICONS = {
    "Instagram Reel": "📱",
    "TikTok": "🎵",
    "YouTube Short": "▶️",
}

PLATFORM_COLORS = {
    "Instagram Reel": "#E1306C",
    "TikTok": "#010101",
    "YouTube Short": "#FF0000",
}


def render_html(ideas: list[dict]) -> tuple[str, str]:
    fecha = datetime.now().strftime("%d/%m/%Y")
    subject = f"💡 3 ideas de contenido para hoy — {fecha}"

    ideas_html = ""
    for i, idea in enumerate(ideas):
        plataforma = idea.get("plataforma", "")
        icon = PLATFORM_ICONS.get(plataforma, "🎬")
        color = PLATFORM_COLORS.get(plataforma, "#2563eb")
        separator = '<hr style="border:none;border-top:1px solid #e5e7eb;margin:32px 0;">' if i < len(ideas) - 1 else ""

        ideas_html += f"""
        <div>
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;">
            <span style="font-size:22px;">{icon}</span>
            <span style="font-size:18px;font-weight:700;color:{color};letter-spacing:-0.3px;">{plataforma.upper()}</span>
          </div>

          <div style="background:#f8fafc;border-left:4px solid {color};padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:16px;">
            <span style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">Tendencia</span>
            <p style="margin:4px 0 0;font-size:14px;color:#374151;">{idea.get('tendencia_base', '')}</p>
          </div>

          <div style="margin-bottom:14px;">
            <span style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">🎬 Gancho de apertura</span>
            <p style="margin:6px 0 0;font-size:16px;font-weight:600;color:#111827;font-style:italic;">"{idea.get('gancho', '')}"</p>
          </div>

          <div style="margin-bottom:14px;">
            <span style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">📝 Desarrollo</span>
            <p style="margin:6px 0 0;font-size:14px;color:#374151;line-height:1.6;">{idea.get('desarrollo', '')}</p>
          </div>

          <div>
            <span style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:0.5px;">📣 CTA</span>
            <p style="margin:6px 0 0;font-size:14px;color:#374151;">{idea.get('cta', '')}</p>
          </div>
        </div>
        {separator}
        """

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <div style="max-width:600px;margin:32px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#1e3a5f 0%,#2563eb 100%);padding:32px 40px;">
      <p style="margin:0;font-size:12px;font-weight:600;color:#93c5fd;text-transform:uppercase;letter-spacing:1px;">Viajando con Alex</p>
      <h1 style="margin:8px 0 0;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">Ideas de contenido</h1>
      <p style="margin:6px 0 0;font-size:14px;color:#93c5fd;">{fecha} · 3 ideas basadas en tendencias</p>
    </div>

    <!-- Content -->
    <div style="padding:40px;">
      {ideas_html}
    </div>

    <!-- Footer -->
    <div style="background:#f8fafc;padding:20px 40px;border-top:1px solid #e5e7eb;">
      <p style="margin:0;font-size:12px;color:#9ca3af;text-align:center;">
        Generado automáticamente cada mañana · Travel Ideas Agent
      </p>
    </div>

  </div>
</body>
</html>
""".strip()

    return subject, html
