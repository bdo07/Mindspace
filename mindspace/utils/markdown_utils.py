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

    is_dark = theme == "dark"
    bg_color = "#202B1D" if is_dark else "#FFFFFF"
    text_color = "#F2F5ED" if is_dark else "#20251E"
    secondary_color = "#A7B29F" if is_dark else "#777E73"
    border_color = "#354331" if is_dark else "#E4E8DF"
    code_bg = "#182116" if is_dark else "#F0F2EB"
    quote_border = "#F1A344" if is_dark else "#15370D"
    link_color = "#97D7FF" if is_dark else "#15370D"
    checkbox_bg = "#6C9B59" if is_dark else "#15370D"
    checkbox_border = "#6C9B59" if is_dark else "#15370D"
    check_text_color = "#11170F" if is_dark else "#FFFFFF"

    # Turn checklist markdown syntax `[ ]` and `[x]` into visual styled boxes
    body_html = re.sub(
        r"\[ \]\s*",
        f"<span style='display:inline-block;width:14px;height:14px;border:1.5px solid {secondary_color};border-radius:3px;margin-right:6px;vertical-align:middle;'></span>",
        body_html,
    )
    body_html = re.sub(
        r"\[[xX]\]\s*",
        f"<span style='display:inline-block;width:14px;height:14px;background:{checkbox_bg};border:1.5px solid {checkbox_border};border-radius:3px;margin-right:6px;vertical-align:middle;text-align:center;color:{check_text_color};font-size:10px;line-height:14px;font-weight:700;'>✓</span>",
        body_html,
    )

    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
        body {{
            background-color: {bg_color};
            color: {text_color};
            font-family: ".AppleSystemUIFont", "Segoe UI", Roboto, "Helvetica Neue", Inter, Arial;
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
