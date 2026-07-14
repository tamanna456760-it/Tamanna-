import os

# তোমার repo folder
REPO_PATH = "./tamanna-"

# কোন কোন extension merge করবে
CODE_EXT = {".py", ".js", ".php", ".java", ".c", ".cpp", ".html"}

# Output file
OUTPUT_FILE = "TAMANNA_SYSTEM_ALL_CODE.txt"


def is_code_file(filename):
    _, ext = os.path.splitext(filename)
    return ext.lower() in CODE_EXT


def collect_all_code(repo_path):
    combined = []

    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if is_code_file(file):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    combined.append(
                        f"\n\n==============================\n"
                        f" FILE: {full_path}\n"
                        f"==============================\n\n"
                        f"{content}\n"
                    )

                except Exception as e:
                    print(f"Error reading {full_path}: {e}")

    return combined


def save_output(data):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(data))

    print(f"\n✔ All code merged successfully into: {OUTPUT_FILE}")


if __name__ == "__main__":
    all_code = collect_all_code(REPO_PATH)
    save_output(all_code)
