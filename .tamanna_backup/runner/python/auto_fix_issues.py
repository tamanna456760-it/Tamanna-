import json


def read_issues_from_file(issues_file):
    with open(issues_file, "r") as f:
        issues = json.load(f)
    return issues


def fix_issues(issues):
    for issue in issues:
        file_path = issue["file"]
        issue_type = issue["type"]
        language = issue["language"]
        details = issue["details"]

        if issue_type == "Unexpected console.log":
            print(
                f"File: {file_path} (Language: {language}) - Remove console.log manually: {details}"
            )
            # এখানে তুমি চাইলে সরাসরি console.log লাইন মুছে ফেলার কোড লিখতে পারো

        elif issue_type == "Read error":
            print(
                f"File: {file_path} (Language: {language}) - Error reading file: {details}"
            )
            # এই ধরনের ইস্যুতে হয়তো তুমি কিছু ফাইল বাদ দিয়েই রাখবে, বা আলাদা ভাবে ম্যানেজ করবে

        elif issue_type == "Missing main function":
            print(
                f"File: {file_path} (Language: {language}) - Inserting main function template."
            )
            with open(file_path, "a") as f:
                f.write("\n\nif __name__ == '__main__':\n    main()\n")

        # অন্যান্য লজিক: ভাষা অনুযায়ী ফিক্সিং টেমপ্লেট, উদাহরণস্বরূপ, Java-তে "public static void main(String[] args)" ইনজেক্ট করা, বা অন্য ভাষার জন্য আলাদা লজিক


if __name__ == "__main__":
    issues_file = "issues.json"
    issues = read_issues_from_file(issues_file)
    fix_issues(issues)
