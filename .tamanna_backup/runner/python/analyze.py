import os

errors = []

for root, dirs, files in os.walk("."):
    for file in files:
        path = os.path.join(root, file)

        try:
            if file.endswith(".py"):
                with open(path, "r") as f:
                    code = f.read()
                compile(code, path, "exec")

        except Exception as e:
            errors.append({
                "file": path,
                "error": str(e)
            })

with open("errors.txt", "w") as f:
    for e in errors:
        f.write(f"{e['file']} || {e['error']}\n")

print("Scan Done")