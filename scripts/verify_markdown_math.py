import os
import re

repo_root = r"C:\Users\manit\Documents\College\Himshikhar-NILM-ESP32"

def check_file(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []
    
    # 1. Check for broken math syntax
    if re.search(r"\\hat\{y\}t", content):
        issues.append(("syntax error", "Found \\hat{y}t without subscript underscore"))
    if re.search(r"\\sum\{[t=1|n=1|k=1]", content):
        issues.append(("syntax error", "Found \\sum{ without subscript underscore"))

    # 2. Check $$ display math
    for m in re.finditer(r"\$\$(.+?)\$\$", content, re.DOTALL):
        blk = m.group(1)
        if blk.count("{") != blk.count("}"):
            issues.append(("unbalanced braces in display math", blk[:60]))
        text_matches = re.findall(r"\\text\{([^}]*)\}", blk)
        for tm in text_matches:
            if re.search(r"(?<!\\)_", tm):
                issues.append(("display \\text unescaped underscore", tm, m.group(0)[:60]))

    # 3. Check $ inline math (excluding $$)
    no_display = re.sub(r"\$\$.+?\$\$", "", content, flags=re.DOTALL)
    dollar_spans = re.findall(r"(?<!\\)\$(.*?)(?<!\\)\$", no_display)
    for blk in dollar_spans:
        if blk.count("{") != blk.count("}"):
            issues.append(("unbalanced braces in inline math", blk))
        text_matches = re.findall(r"\\text\{([^}]*)\}", blk)
        for tm in text_matches:
            if re.search(r"(?<!\\)_", tm):
                issues.append(("inline \\text unescaped underscore", tm, blk))
        unescaped = [m.start() for m in re.finditer(r"(?<!\\)_", blk)]
        if len(unescaped) >= 2:
            if re.search(r"[a-zA-Z]_[a-zA-Z]+_[a-zA-Z]", blk):
                issues.append(("multiple raw underscores", blk))

    # 4. Check image links exist
    img_refs = re.findall(r"!\[.*?\]\((.*?)\)", content)
    file_dir = os.path.dirname(fpath)
    for img in img_refs:
        # Ignore external URLs
        if img.startswith("http://") or img.startswith("https://"):
            continue
        # Check relative path from file location
        target = os.path.normpath(os.path.join(file_dir, img))
        if not os.path.exists(target):
            issues.append(("missing image file", img, target))

    return issues

has_any_issue = False
for root, dirs, files in os.walk(repo_root):
    if ".git" in root or ".gemini" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            fpath = os.path.join(root, f)
            iss = check_file(fpath)
            if iss:
                has_any_issue = True
                print(f"File {fpath} has {len(iss)} issues:")
                for item in iss:
                    print("  ", item)

if not has_any_issue:
    print("SUCCESS: All Markdown files passed math, syntax, and image verification with 0 issues!")
