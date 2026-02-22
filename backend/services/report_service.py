from datetime import datetime
from typing import Dict


class ReportService:
    def generate_html_report(self, repository_name: str, gate_result: Dict) -> str:
        passed = gate_result.get("passed", False)
        status_color = "#22c55e" if passed else "#ef4444"
        status_text = "PASSED" if passed else "FAILED"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        rows = ""
        for c in gate_result.get("checks", []):
            icon = "✅" if c["passed"] else "❌"
            bg = "#f0fdf4" if c["passed"] else "#fef2f2"
            rows += (
                f'<tr style="background:{bg}">'
                f'<td style="padding:8px 12px">{icon} {c["name"]}</td>'
                f'<td style="padding:8px 12px;text-align:center">{c["value"]}</td>'
                f'<td style="padding:8px 12px;text-align:center">{c["threshold"]}</td>'
                f'<td style="padding:8px 12px">{c["message"]}</td>'
                f"</tr>"
            )

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Code Intelligence — {repository_name}</title>
  <style>
    body {{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;margin:0;padding:24px;background:#f8fafc;color:#1e293b}}
    .card {{background:white;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,.1)}}
    .badge {{display:inline-block;padding:8px 20px;border-radius:9999px;color:white;font-weight:700;font-size:18px;background:{status_color}}}
    table {{width:100%;border-collapse:collapse}}
    th {{background:#f1f5f9;padding:10px 12px;text-align:left;font-weight:600}}
    td {{border-bottom:1px solid #e2e8f0}}
    h1 {{margin:0 0 4px;font-size:24px}}
    h2 {{margin:0 0 16px;font-size:18px;color:#475569}}
  </style>
</head>
<body>
  <div class="card">
    <h1>🔍 Code Intelligence Report</h1>
    <h2>{repository_name}</h2>
    <p style="color:#64748b">Generated: {timestamp}</p>
    <div class="badge">{status_text}</div>
    <p style="margin-top:12px;color:#64748b">{gate_result.get("summary", "")}</p>
  </div>
  <div class="card">
    <h2>Quality Gate Results</h2>
    <table>
      <thead><tr><th>Check</th><th>Value</th><th>Threshold</th><th>Details</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </div>
</body>
</html>"""

    def generate_text_report(self, repository_name: str, gate_result: Dict) -> str:
        lines = [
            f"Code Intelligence Report — {repository_name}",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            "=" * 60,
            f"Status: {'PASSED ✅' if gate_result['passed'] else 'FAILED ❌'}",
            gate_result.get("summary", ""),
            "",
            "Checks:",
            "-" * 40,
        ]
        for c in gate_result.get("checks", []):
            icon = "✅" if c["passed"] else "❌"
            lines.append(f"{icon} {c['name']}: {c['message']}")
        return "\n".join(lines)
