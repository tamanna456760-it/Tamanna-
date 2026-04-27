import os

report = []

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r") as f:
                    code = f.read()
                
                compile(code, path, 'exec')
                report.append(f"[OK] {path}")

            except Exception as e:
                report.append(f"[ERROR] {path} -> {str(e)}")

with open("report.txt", "w") as f:
    f.write("\n".join(report))

print("Report Generated: report.txt")