import os
import re

def search_files(directory, search_text):
    report = {}
    for root, _, files in os.walk(directory):
        if not root.startswith(directory):
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if not file.endswith(".py"):
                continue  # Process only Python files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                current_function = None
                current_class = None
                function_content = []
                for line in lines:
                    class_match = re.match(r'^\s*class\s+([\w_]+)\s*\(.*?\):', line)
                    if class_match:
                        current_class = class_match.group(1)
                        if search_text in line:
                            print(f"Found class: {current_class}")  # Debug
                    function_match = re.match(r'^\s*def\s+([\w_]+)\s*\(.*?\):', line)
                    if function_match:
                        if current_function and search_text in '\n'.join(function_content):
                            if search_text not in report:
                                report[search_text] = {}
                            if root not in report[search_text]:
                                report[search_text][root] = []
                            report[search_text][root].append((file, current_class, current_function))
                            print(f"Appending function: {current_function} in class {current_class}")  # Debug
                        current_function = function_match.group(1)
                        function_content = []
                        if search_text in line:
                            print(f"Found function: {current_function} in class {current_class}")  # Debug
                    function_content.append(line)
                if current_function and search_text in '\n'.join(function_content):
                    if search_text not in report:
                        report[search_text] = {}
                    if root not in report[search_text]:
                        report[search_text][root] = []
                    report[search_text][root].append((file, current_class, current_function))
                    print(f"Finalizing function: {current_function} in class {current_class}")  # Debug
    return report

def generate_report(report, output_file, directory):
    with open(output_file, 'w') as f:
        for criteria, paths in report.items():
            f.write(f"Search Criteria: {criteria}\n")
            for path, files in paths.items():
                if path == directory:
                    f.write(f"Directory Path: {path}\n")
                    for file, class_name, function in files:
                        class_info = f", Class: {class_name}" if class_name else ""
                        f.write(f" - {file}{class_info}, Function: {function}\n")
                    f.write("\n")

def generate_list(report, search_text, directory):
    i = 0
    print(f"Search Criteria: {search_text}")
    print("\n")
    print(f"Directory Path: {directory}")
    for criteria, paths in report.items():
        for path, files in paths.items():
            if path == directory:
                for file, class_name, function in files:
                    class_info = f", Class: {class_name}" if class_name else ""
                    i += 1
                    print(f"{file}{class_info}, Function: {function}")
    return i

def main():
    directory = "C:/Users/wally/Documents/Python/Demo/Takestock1.0"
    search_text = "get_table_data"
    output_file = "C:/Users/wally/Documents/Python/Demo/Takestock1.0/files/whereused.txt"
    output_target = "P"
    report = search_files(directory, search_text)
    if output_target == "F":
        generate_report(report, output_file, directory)
        print(f"Report generated: {output_file}")
    else:
        cnt = generate_list(report, search_text, directory)
        print(f"Search generated: {cnt} items.")

if __name__ == "__main__":
    main()
