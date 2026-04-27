import os

errors = []

for root, dirs, files in os.walk("."):
    for file in files:
        path = os.path.join(root, file)

        if file.endswith(".py"):
            try:
                with open(path, "r") as f:
                    code = f.read()
                compile(code, path, 'exec')
            except Exception as e:
                errors.append(f"{path} :: {str(e)}")

        elif file.endswith(".js"):
            # basic JS check
            try:
                with open(path, "r") as f:
                    code = f.read()
                if "console.log(" not in code:
                    errors.append(f"{path} :: Possible issue (no output found)")
            except Exception as e:
                errors.append(f"{path} :: {str(e)}")

with open("errors.txt", "w") as f:
    f.write("\n".join(errors))

print("Errors saved in errors.txt")