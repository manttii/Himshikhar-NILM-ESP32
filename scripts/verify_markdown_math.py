import os
import re

repo_root = r"C:\Users\manit\Documents\College\Himshikhar-NILM-ESP32"

def check_file(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    issues = []
    # Check $$ display math
    for m in re.finditer(r"\$\$(.+?)\$\$", content, re.DOTALL):
        blk = m.group(1)
        text_matches = re.findall(r"\\text\{([^}]*)\}", blk)
        for tm in text_matches:
            if re.search(r"(?<!\\)_", tm):
                issues.append(("display \\text unescaped underscore", tm, m.group(0)[:60]))

    # Check $ inline math (excluding $$)
    no_display = re.sub(r"\$\$.+?\$\$", "", content, flags=re.DOTALL)
    dollar_spans = re.findall(r"(?<!\\)\$(.*?)(?<!\\)\$", no_display)
    for blk in dollar_spans:
        text_matches = re.findall(r"\\text\{([^}]*)\}", blk)
        for tm in text_matches:
            if re.search(r"(?<!\\)_", tm):
                issues.append(("inline \\text unescaped underscore", tm, blk))
        # Check for multiple underscores in a single span that might trigger markdown italics or LaTeX error
        unescaped = [m.start() for m in re.finditer(r"(?<!\\)_", blk)]
        if len(unescaped) >= 2:
            # check if they look like V_pin_RMS
            if re.search(r"[a-zA-Z]_[a-zA-Z]+_[a-zA-Z]", blk):
                issues.append(("multiple raw underscores", blk))
    return issues

for root, dirs, files in os.walk(repo_root):
    if ".git" in root or ".gemini" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            fpath = os.path.join(root, f)
            iss = check_file(fpath)
            if iss:
                print(f"File {fpath} has {len(iss)} issues:")
                for item in iss:
                    print("  ", item)
print("Finished markdown math scan.")
