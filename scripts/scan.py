import os

errors = []

for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)

            try:
                with open(path, "r") as f:
                    code = f.read()

                compile(code, path, "exec")

            except Exception as e:
                errors.append(f"{path} || {str(e)}")

with open("errors.txt", "w") as f:
    f.write("\n".join(errors))

print("Scan Done")