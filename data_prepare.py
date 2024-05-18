import os
import re
import pandas as pd

# Path to the downloaded repository
REPO_PATH = './stm32_gtest_c_code'
def get_files_in_directory(directory_path, extensions):
    file_data = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    file_data.append({'path': file_path, 'content': file_content})
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return file_data


def extract_function_names(c_code):
    # Regex to extract C function names
    function_pattern = re.compile(r'^\s*[\w\[\]\s\*]+\s+([\w_]+)\s*\(.*\)\s*\{', re.MULTILINE)
    function_names = function_pattern.findall(c_code)
    return function_names


def find_test_cases_for_functions(function_names, test_files):
    matched_tests = []
    for test_file in test_files:
        for function_name in function_names:
            if function_name in test_file['content']:
                test_cases = extract_individual_test_cases(test_file['content'])
                matched_tests.extend(test_cases)
                break
    return matched_tests


def extract_individual_test_cases(test_content):
    # Split the test cases by identifying the start of each test case
    test_case_pattern = re.compile(r'^\s*TEST(_F|_P)?\(([^,]+),\s*([^)]+)\)', re.MULTILINE)
    test_cases = []

    current_test_case = None
    for line in test_content.splitlines():
        if test_case_pattern.match(line):
            if current_test_case:
                test_cases.append(current_test_case)
            current_test_case = line
        elif current_test_case:
            current_test_case += "\n" + line

    if current_test_case:
        test_cases.append(current_test_case)

    return test_cases


# Collect source and test files
source_files = get_files_in_directory(os.path.join(REPO_PATH, 'source'), ('.c', '.h'))
test_files = get_files_in_directory(os.path.join(REPO_PATH, 'tests'), ('.cpp', '.hpp'))

print(f"Collected {len(source_files)} source files.")
print(f"Collected {len(test_files)} test files.")

# Prepare data pairs
data_pairs = []

for source_file in source_files:
    source_content = source_file['content']
    function_names = extract_function_names(source_content)

    if function_names:
        matched_tests = find_test_cases_for_functions(function_names, test_files)
        for test_case in matched_tests:
            data_pairs.append({
                'code_snippet': source_content,
                'test_case': test_case
            })

print(f"Prepared {len(data_pairs)} data pairs.")

# Create a DataFrame
df = pd.DataFrame(data_pairs)

# Output to CSV
output_path = 'test_case_generation_data.csv'
df.to_csv(output_path, index=False)

print(f"Data has been successfully saved to {output_path}")
