import os
from datetime import datetime


_REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'reports')
os.makedirs(_REPORTS_DIR, exist_ok=True)


def generate_html_report(title, sections):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    parts = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='UTF-8'><title>", title, "</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;background:#0f0f0f;color:#e0e0e0;padding:20px;}",
        "h1{color:#00ff41;}table{border-collapse:collapse;width:100%;margin-top:10px;}",
        "th,td{border:1px solid #333;padding:8px;text-align:left;}th{background:#111;}",
        ".section{margin-top:30px;}.meta{color:#888;font-size:12px;}",
        "</style></head><body>",
        f"<h1>{title}</h1><p class='meta'>Generated: {now}</p>",
    ]
    for sec in sections:
        parts.append("<div class='section'><h2>" + sec.get('heading', '') + "</h2>")
        rows = sec.get('rows', [])
        if rows:
            parts.append("<table><tr>")
            for h in sec.get('headers', []):
                parts.append(f"<th>{h}</th>")
            parts.append("</tr>")
            for row in rows:
                parts.append("<tr>")
                for cell in row:
                    parts.append(f"<td>{cell}</td>")
                parts.append("</tr>")
            parts.append("</table>")
        else:
            parts.append("<p>No data.</p>")
        parts.append("</div>")
    parts.append("</body></html>")
    return "\n".join(parts)


def save_html_report(title, sections, filename=None):
    if filename is None:
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    path = os.path.join(_REPORTS_DIR, filename)
    try:
        html = generate_html_report(title, sections)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return path
    except Exception:
        return None
