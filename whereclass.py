import os


def build_class_method_mapping(directory):
    class_method_mapping = {}

    for root, _, files in os.walk(directory):
        for file in sorted(files):
            file_path = os.path.join(root, file)
            if not file.endswith(".py"):
                continue  # Process only Python files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                current_class = None
                for i, line in enumerate(lines):
                    stripped_line = line.strip()
                    if stripped_line.startswith('class '):
                        current_class = stripped_line.split(' ')[1].split('(')[0]
                        if file_path not in class_method_mapping:
                            class_method_mapping[file_path] = {}
                        class_method_mapping[file_path][current_class] = []
                    elif stripped_line.startswith('def '):
                        current_method = stripped_line.split(' ')[1].split('(')[0]
                        if current_class:
                            class_method_mapping[file_path][current_class].append(current_method)
                        else:
                            # Handle standalone functions
                            if file_path not in class_method_mapping:
                                class_method_mapping[file_path] = {}
                            if 'Standalone' not in class_method_mapping[file_path]:
                                class_method_mapping[file_path]['Standalone'] = []
                            class_method_mapping[file_path]['Standalone'].append(current_method)

    return class_method_mapping


def detect_references(directory, search_text, class_method_mapping):
    context_info = {}

    for file_path, class_dict in class_method_mapping.items():
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            current_class = None
            current_method = None
            for i, line in enumerate(lines):
                stripped_line = line.strip()
                if stripped_line.startswith('class '):
                    current_class = stripped_line.split(' ')[1].split('(')[0]
                elif stripped_line.startswith('def '):
                    current_method = stripped_line.split(' ')[1].split('(')[0]
                if search_text in line:
                    context = f"File: {os.path.basename(file_path)}"
                    if current_class:
                        context += f", Class: {current_class}, Method: {current_method}"
                    else:
                        context += f", Function: {current_method}"
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
    search_text = "recalculate_value"

    class_method_mapping = build_class_method_mapping(directory)
    context_info = detect_references(directory, search_text, class_method_mapping)
    generate_report(directory, context_info)


if __name__ == "__main__":
    main()
