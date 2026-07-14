def fix_suggestion(error):
    error = error.lower()

    if "syntaxerror" in error:
        return "Fix: কোডের bracket বা colon (:) ভুল আছে"
    elif "indentationerror" in error:
        return "Fix: space/tab ঠিক করো"
    elif "nameerror" in error:
        return "Fix: variable আগে define করো"
    elif "eof" in error:
        return "Fix: কোড অসম্পূর্ণ (missing bracket)"
    else:
        return "Fix: manual check দরকার"


report = []

try:
    with open("errors.txt", "r") as f:
        lines = f.readlines()

    for line in lines:
        file, err = line.split("||")
        suggestion = fix_suggestion(err)

        report.append(f"""
FILE: {file}
ERROR: {err}
SUGGESTION: {suggestion}
--------------------------
""")

except:
    report.append("No errors found ✅")

with open("final_report.txt", "w") as f:
    f.write("\n".join(report))

print("AI Fix Report Ready")
