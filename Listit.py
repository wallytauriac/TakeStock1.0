import ast
import os

def get_lines_by_node_type(file_path, node_types):
    lines = []
    with open(file_path, 'r') as file:
        source = file.readlines()
        tree = ast.parse(''.join(source), filename=file_path)
        for node in ast.walk(tree):
            if isinstance(node, tuple(node_types)):
                line_number = node.lineno - 1  # Line numbers in `ast` start at 1
                lines.append(source[line_number].strip())
    return lines

def analyze_file(file_path):
    function_lines = get_lines_by_node_type(file_path, (ast.FunctionDef,))
    class_lines = get_lines_by_node_type(file_path, (ast.ClassDef,))
    call_lines = get_lines_by_node_type(file_path, (ast.Call,))

    return {
        'functions': function_lines,
        'classes': class_lines,
        'function_calls': call_lines
    }

def analyze_directory(directory_path):
    analysis = {}
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                analysis[file_path] = analyze_file(file_path)
    return analysis

def write_analysis_to_file(output_path, analysis):
    with open(output_path, 'w') as file:
        for file_path, data in analysis.items():
            file.write(f'File: {file_path}\n')
            file.write('Functions:\n')
            for line in data['functions']:
                file.write(f'  {line}\n')
            file.write('Classes:\n')
            for line in data['classes']:
                file.write(f'  {line}\n')
            file.write('Function Calls:\n')
            for line in data['function_calls']:
                file.write(f'  {line}\n')
            file.write('\n')

# Define paths
project_path = 'C:/Users/wally/Documents/Python/Demo/Takestock1.0'
output_path = 'C:/Users/wally/Documents/Python/Demo/Takestock1.0/files/file.txt'

# Perform analysis and write to file
analysis = analyze_directory(project_path)
write_analysis_to_file(output_path, analysis)

