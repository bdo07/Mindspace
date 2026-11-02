"""Markdown rendering utilities for Mindspace."""

import html
import re

try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def markdown_to_html(md_text: str, theme: str = "light") -> str:
    """Converts markdown text to styled HTML document matching Mindspace visual identity."""
    if HAS_MARKDOWN:
        try:
            body_html = markdown.markdown(
                md_text or "",
                extensions=["fenced_code", "tables", "nl2br", "sane_lists"],
            )
        except Exception:
            body_html = f"<pre>{html.escape(md_text or '')}</pre>"
    else:
        # Fallback simple converter
        escaped = html.escape(md_text or "")
        body_html = f"<div style='white-space: pre-wrap;'>{escaped}</div>"

    # Turn checklist markdown syntax `[ ]` and `[x]` into visual styled boxes
    body_html = re.sub(
        r"\[ \]\s*",
        r"<span style='display:inline-block;width:14px;height:14px;border:1.5px solid #858585;border-radius:3px;margin-right:6px;vertical-align:middle;'></span>",
        body_html,
    )
    body_html = re.sub(
        r"\[[xX]\]\s*",
        r"<span style='display:inline-block;width:14px;height:14px;background:#8B79D9;border:1.5px solid #8B79D9;border-radius:3px;margin-right:6px;vertical-align:middle;text-align:center;color:#fff;font-size:10px;line-height:14px;'>✓</span>",
        body_html,
    )

    is_dark = theme == "dark"
    bg_color = "#1E1E22" if is_dark else "#FFFFFF"
    text_color = "#F0F0F3" if is_dark else "#202020"
    secondary_color = "#A0A0A8" if is_dark else "#6C6C74"
    border_color = "#2E2E36" if is_dark else "#EAE8E2"
    code_bg = "#27272D" if is_dark else "#F4F3EE"
    quote_border = "#9D8DE6" if is_dark else "#8B79D9"
    link_color = "#A899E8" if is_dark else "#7865CD"

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Inter, Arial, sans-serif;
            font-size: 15px;
            line-height: 1.65;
            margin: 0;
            padding: 24px 28px;
            word-wrap: break-word;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: {text_color};
            font-weight: 600;
            margin-top: 1.4em;
            margin-bottom: 0.5em;
            line-height: 1.25;
        }}
        h1 {{ font-size: 1.8em; border-bottom: 1px solid {border_color}; padding-bottom: 8px; }}
        h2 {{ font-size: 1.4em; }}
        h3 {{ font-size: 1.15em; }}
        p {{ margin: 0.8em 0; }}
        a {{ color: {link_color}; text-decoration: none; font-weight: 500; }}
        a:hover {{ text-decoration: underline; }}
        code {{
            background-color: {code_bg};
            padding: 2px 6px;
            border-radius: 4px;
            font-family: "SF Mono", Menlo, Monaco, Consolas, "Courier New", monospace;
            font-size: 0.9em;
        }}
        pre {{
            background-color: {code_bg};
            padding: 14px 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid {border_color};
        }}
        pre code {{
            background: none;
            padding: 0;
            font-size: 0.9em;
        }}
        blockquote {{
            margin: 1.2em 0;
            padding: 6px 18px;
            color: {secondary_color};
            border-left: 3px solid {quote_border};
            font-style: italic;
        }}
        ul, ol {{
            padding-left: 24px;
            margin: 0.8em 0;
        }}
        li {{
            margin: 0.35em 0;
        }}
        hr {{
            border: 0;
            height: 1px;
            background: {border_color};
            margin: 28px 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.2em 0;
        }}
        th, td {{
            border: 1px solid {border_color};
            padding: 8px 12px;
            text-align: left;
        }}
        th {{
            background-color: {code_bg};
            font-weight: 600;
        }}
    </style>
    </head>
    <body>
    {body_html}
    </body>
    </html>
    """
    return template

