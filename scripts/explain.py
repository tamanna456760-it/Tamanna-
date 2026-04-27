def explain_error(line):
    if "SyntaxError" in line:
        return "Syntax Error → কোডের structure ভুল"
    elif "IndentationError" in line:
        return "Indentation Error → space/tab সমস্যা"
    elif "NameError" in line:
        return "Name Error → variable define করা নাই"
    elif "no output" in line.lower():
        return "JS Warning → output নেই"
    else:
        return "Unknown Error → manually check করো"

report = []

try:
    with open("errors.txt", "r") as f:
        lines = f.readlines()

    for line in lines:
        explanation = explain_error(line)
        report.append(f"{line.strip()} => {explanation}")

except:
    report.append("No errors found ✅")

with open("final_report.txt", "w") as f:
    f.write("\n".join(report))

print("Final Report Generated")