# -*- coding: utf-8 -*-


import re
import json

# Constants for file paths
USER_AGENTS_FILE = 'files/user_agents.json'
OS_VERSIONS_FILE = 'files/os_versions.json'

# Regex patterns
CHROME_PATTERN = r'Chrome/\d[\d\.]*'
EDGE_PATTERN = r'Edge/\d[\d\.]*'
MACOS_PATTERN = r'Mac OS X \d[\d_]*'

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content, mode='w'):
    with open(file_path, mode, encoding='utf-8') as file:
        file.write(content)

def load_versions(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def replace_versions(file_path, new_version, pattern):
    content = read_file(file_path)
    updated_content = re.sub(pattern, new_version, content)
    write_file(file_path, updated_content)

def main():
    # Load version numbers from JSON file
    versions = load_versions(OS_VERSIONS_FILE)

    # Construct new version strings
    new_chrome_version = f'Chrome/{versions.get("Chrome", "latest")}'
    new_edge_version = f'Edge/{versions.get("Edge", "latest")}'
    new_macos_version = f'Mac OS X {versions.get("macOS", "latest")}'

    # Update the user agents file with new versions
    replace_versions(USER_AGENTS_FILE, new_chrome_version, CHROME_PATTERN)
    replace_versions(USER_AGENTS_FILE, new_edge_version, EDGE_PATTERN)
    replace_versions(USER_AGENTS_FILE, new_macos_version, MACOS_PATTERN)

if __name__ == "__main__":
    main()
