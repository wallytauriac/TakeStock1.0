import os
import re


def initial_search_references(directory, search_text):
    references = {}

    for root, _, files in os.walk(directory):
        for file in sorted(files):  # Sort files to ensure consistent order
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")  # Debugging info
            if not file.endswith(".py"):
                continue  # Process only Python files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines):
                    if search_text in line:
                        if file_path not in references:
                            references[file_path] = []
                        references[file_path].append(line_num + 1)

    return references


def find_context(directory, references):
    context_info = {}

    for file_path, line_numbers in references.items():
        print(f"Reading file for context: {file_path}")  # Debugging info
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            current_class = None
            for i, line in enumerate(lines):
                class_match = re.match(r'^\s*class\s+([\w_]+)\s*\(.*?\):', line)
                if class_match:
                    current_class = class_match.group(1)
                    print(f"Detected class: {current_class} in file {file_path} at line {i + 1}")  # Debugging info
                method_match = re.match(r'^\s*def\s+([\w_]+)\s*\(.*?\):', line)
                if method_match:
                    current_method = method_match.group(1)
                if i + 1 in line_numbers:
                    context = f"File: {os.path.basename(file_path)}"
                    if current_class:
                        context += f", Class: {current_class}"
                    if current_method:
                        context += f", Method: {current_method}"
                    print(f"Context being added: {context}")  # Debugging info
                    if file_path not in context_info:
                        context_info[file_path] = []
                    context_info[file_path].append(context)

    return context_info


def generate_report(directory, context_info):
    print(f"Search results in: {directory}\n")
    for file_path, contexts in context_info.items():
        print(f"References found in: {os.path.basename(file_path)}")
        unique_contexts = set(contexts)  # Remove duplicates
        for context in unique_contexts:
            print(f" - {context}")
        print("")  # Add a newline for better readability


def main():
    directory = "C:/Users/wally/Documents/Python/Demo/Takestock1.0"
    search_text = "get_table_data"

    references = initial_search_references(directory, search_text)
    context_info = find_context(directory, references)
    generate_report(directory, context_info)


if __name__ == "__main__":
    main()
