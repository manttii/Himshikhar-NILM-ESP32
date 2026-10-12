# -*- coding: utf-8 -*-
"""
Script to generate the publication-grade IEEE Transactions formatted PDF:
docs/Manit_Sharma_IEEE_Transactions_NILM_Paper.pdf

Process:
1. Parse docs/NILM_ACADEMIC_RESEARCH_PAPER.md
2. Transform into IEEE Transactions layout HTML with KaTeX and high-DPI figures
3. Compile via Microsoft Edge Headless engine
4. Validate PDF structure, page count, and visual integrity using PyMuPDF
"""

import os
import re
import subprocess
import pymupdf
import markdown

script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
docs_dir = os.path.join(repo_root, "docs")
paper_md = os.path.join(docs_dir, "NILM_ACADEMIC_RESEARCH_PAPER.md")
output_html = os.path.join(docs_dir, "paper_print_preview.html")
output_pdf = os.path.join(docs_dir, "Manit_Sharma_IEEE_Transactions_NILM_Paper.pdf")

with open(paper_md, "r", encoding="utf-8") as f:
    raw_md = f.read()

# Protect math blocks before markdown conversion
display_math = []
def save_display_math(match):
    idx = len(display_math)
    display_math.append(match.group(1).strip())
    return f"<!--DISPLAY_MATH_{idx}-->"

raw_md = re.sub(r"\$\$(.+?)\$\$", save_display_math, raw_md, flags=re.DOTALL)

inline_math = []
def save_inline_math(match):
    idx = len(inline_math)
    inline_math.append(match.group(1).strip())
    return f"<!--INLINE_MATH_{idx}-->"

raw_md = re.sub(r"(?<!\\)\$(.*?)(?<!\\)\$", save_inline_math, raw_md)

html_body = markdown.markdown(raw_md, extensions=['tables', 'fenced_code'])

# Restore math blocks
for idx, m in enumerate(display_math):
    html_body = html_body.replace(f"&lt;!--DISPLAY_MATH_{idx}--&gt;", f'<div class="display-eq">$${m}$$</div>')
    html_body = html_body.replace(f"<!--DISPLAY_MATH_{idx}-->", f'<div class="display-eq">$${m}$$</div>')

for idx, m in enumerate(inline_math):
    html_body = html_body.replace(f"&lt;!--INLINE_MATH_{idx}--&gt;", f'\\({m}\\)')
    html_body = html_body.replace(f"<!--INLINE_MATH_{idx}-->", f'\\({m}\\)')

# Replace image paths with absolute file URIs
def fix_img_src(match):
    src = match.group(1)
    if not src.startswith("http") and not src.startswith("file:"):
        abs_p = os.path.normpath(os.path.join(docs_dir, src)).replace("\\", "/")
        return f'<img src="file:///{abs_p}"'
    return match.group(0)

html_body = re.sub(r'<img src="(.*?)"', fix_img_src, html_body)

# Wrap tables with appropriate container
# Wide tables spanning both columns: Table 1, Table 2, Table 7A, Table 7B
# Normal tables staying in column: Table 2A, Table 3, Table 4, Table 5, Table 6
def wrap_tables(match):
    heading = match.group(1)
    table_html = match.group(2)
    is_wide = any(t in heading for t in ["Table 1:", "Table 2:", "Table 7A:", "Table 7B:"])
    cls_name = "full-width" if is_wide else "normal-block"
    return f'<div class="{cls_name}">{heading}\n{table_html}</div>'

html_body = re.sub(r'(<h4>Table\s+[^<]+</h4>)\s*(<table>.*?</table>)', wrap_tables, html_body, flags=re.DOTALL)

# Wrap wide multi-panel figure 5 in full-width
def wrap_wide_figures(match):
    return f'<div class="full-width">{match.group(0)}</div>'

html_body = re.sub(r'(<p><img[^>]+fig5_multi_panel[^>]+>.*?(?:<em>.*?</em>)?</p>)', wrap_wide_figures, html_body, flags=re.DOTALL)

css_styles = """
@page {
    size: letter;
    margin: 18mm 14mm 18mm 14mm;
    @bottom-right {
        content: counter(page);
        font-family: 'Times New Roman', serif;
        font-size: 9pt;
    }
    @top-left {
        content: "IEEE TRANSACTIONS ON SMART GRID / CONSUMER ELECTRONICS (SPECIAL ISSUE ON EDGE METROLOGY)";
        font-family: 'Times New Roman', serif;
        font-size: 8pt;
        font-style: italic;
        color: #555;
    }
}

body {
    font-family: 'Times New Roman', Times, serif;
    font-size: 9.5pt;
    line-height: 1.28;
    color: #111;
    margin: 0;
    padding: 0;
    text-rendering: optimizeLegibility;
}

/* Two Column Layout */
.ieee-columns {
    column-count: 2;
    column-gap: 18px;
    text-align: justify;
    text-justify: inter-word;
}

/* Full-width elements spanning both columns */
.full-width {
    column-span: all;
    margin: 8px 0;
    break-inside: auto;
}

/* Normal column blocks */
.normal-block {
    margin: 6px 0;
    break-inside: avoid;
}

h1 {
    font-size: 19pt;
    font-weight: bold;
    text-align: center;
    line-height: 1.18;
    margin: 0 0 10px 0;
    column-span: all;
}

/* Top level section */
h2 {
    font-size: 9.5pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: center;
    margin-top: 14px;
    margin-bottom: 6px;
    letter-spacing: 0.5px;
}

/* Subsections */
h3 {
    font-size: 9.5pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 10px;
    margin-bottom: 4px;
    text-align: left;
}

h4 {
    font-size: 9pt;
    font-weight: bold;
    margin-top: 8px;
    margin-bottom: 3px;
}

p {
    margin: 0 0 6px 0;
    text-indent: 1.2em;
}

p:first-of-type, .no-indent {
    text-indent: 0;
}

/* Equations */
.display-eq {
    text-align: center;
    margin: 5px 0;
    font-size: 8.5pt;
    overflow-x: hidden;
}

/* Figures */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 6px auto;
}

em {
    font-size: 8pt;
    line-height: 1.15;
    display: block;
    text-align: justify;
    margin-top: 2px;
    margin-bottom: 8px;
    color: #222;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 6.8pt;
    margin: 6px 0 10px 0;
    line-height: 1.15;
}

table th, table td {
    border-top: 0.5px solid #bbb;
    border-bottom: 0.5px solid #bbb;
    padding: 2.5px 2px;
    text-align: center;
}

table th {
    font-weight: bold;
    background-color: #f7f7f7;
    border-top: 1.5px solid #222;
    border-bottom: 1.5px solid #222;
}

table tr:last-child td {
    border-bottom: 1.5px solid #222;
}

/* References */
ol {
    padding-left: 16px;
    margin: 6px 0;
    font-size: 8pt;
    line-height: 1.2;
}

ol li {
    margin-bottom: 4px;
    text-align: justify;
}

hr {
    display: none;
}
"""

js_script = """
document.addEventListener('DOMContentLoaded', function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '\\\\(', right: '\\\\)', display: false}
        ],
        throwOnError: false
    });
});
"""

ieee_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Non-Intrusive Load Monitoring Under Low-Frequency Constraints</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/katex.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.8/contrib/auto-render.min.js"></script>

<style>
{css_styles}
</style>
</head>
<body>

<div class="ieee-columns">
{html_body}
</div>

<script>
{js_script}
</script>
</body>
</html>
"""

with open(output_html, "w", encoding="utf-8") as f:
    f.write(ieee_html)

print(f"Generated printable HTML preview at: {output_html} ({len(ieee_html)} chars)")

# Execute Edge Headless Compiler
edge_bin = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
edge_cmd = [
    edge_bin,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    "--virtual-time-budget=10000",
    f"--print-to-pdf={output_pdf}",
    os.path.abspath(output_html)
]

print("Executing Microsoft Edge Headless engine to compile IEEE PDF...")
res = subprocess.run(edge_cmd, capture_output=True, text=True)
print(f"Edge process exited with code: {res.returncode}")

if os.path.exists(output_pdf):
    doc = pymupdf.open(output_pdf)
    page_count = len(doc)
    file_size_kb = os.path.getsize(output_pdf) / 1024
    print(f"\nSUCCESS: Generated IEEE Transactions PDF at {output_pdf}")
    print(f"Document Details: {page_count} pages, {file_size_kb:.1f} KB")
    
    # Audit text on first 2 pages and last page
    print("\n--- Document Quality Audit ---")
    first_page_text = doc[0].get_text()[:400].encode('ascii', errors='backslashreplace').decode()
    print("Page 1 Excerpt:\n", first_page_text)
    
    last_page_text = doc[-1].get_text()[-400:].encode('ascii', errors='backslashreplace').decode()
    print(f"Page {page_count} Excerpt:\n", last_page_text)
else:
    print(f"ERROR: PDF was not generated at {output_pdf}")
