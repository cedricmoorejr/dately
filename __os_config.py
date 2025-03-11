# -*- coding: utf-8 -*-


import requests
import re
import json
import concurrent.futures

## HTTP Configuration
##=========================================================
def fetch_chrome_version(url = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json'):
    """ Fetch and process Google Chrome version data from a URL."""
    response = requests.get(url)
    data = response.json()
    chrome_version = data['channels']['Stable']['version']
    return chrome_version

def fetch_edge_version(url='https://learn.microsoft.com/en-us/deployedge/microsoft-edge-release-schedule'):
    """ Fetch and process Microsoft Edge version data from a URL."""
    response = requests.get(url)
    html_content = response.text

    table_pattern = r'<table[^>]*>(.*?)</table>'
    header_pattern = r'<th[^>]*>(.*?)</th>'
    row_pattern = r'<tr[^>]*>(.*?)</tr>'
    cell_pattern = r'<td[^>]*>(.*?)</td>'
    table_match = re.search(table_pattern, html_content, re.DOTALL)
    if not table_match:
        return None

    table_html = table_match.group(1)
    headers = re.findall(header_pattern, table_html, re.DOTALL)
    headers = [re.sub(r'<.*?>', '', header).strip() for header in headers]  # Clean header tags
    rows = re.findall(row_pattern, table_html, re.DOTALL)
    table_data = []
    for row in rows:
        cells = re.findall(cell_pattern, row, re.DOTALL)
        cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]  # Clean cell tags
        if cells:  # Skip empty rows
            table_data.append(cells)
    final_headers, final_rows = headers, table_data
    filtered_rows =  [row for row in final_rows if 'ReleaseVersion' in row[1].replace(" ", "")]
    version = filtered_rows[0][2]
    date_match = re.search(r'\d{1,2}-[A-Za-z]{3}-\d{4}', version)
    if date_match:
        version_part = version[date_match.end():].strip()
        version_match = re.search(r'\d+\.\d+\.\d+\.\d+', version_part)
        if version_match:
            cleaned_version = version_match.group(0)
    return cleaned_version

def fetch_macOS_version(url='https://support.apple.com/en-us/109033', least_version=12):
    """ Fetch and process macOS version data from a URL."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve the webpage, status code: {response.status_code}")
    html_content = response.text
    table_pattern = re.compile(r'<tr>(.*?)</tr>', re.DOTALL)
    cell_pattern = re.compile(r'<t[dh].*?>(.*?)</t[dh]>', re.DOTALL)
    rows = table_pattern.findall(html_content)
    table_data = []
    for row in rows:
        cells = cell_pattern.findall(row)
        cleaned_cells = [re.sub(r'<.*?>', '', cell).strip() for cell in cells]
        table_data.append(cleaned_cells)
    filtered_table_data = [row for row in table_data if len(row) > 1 and any(char.isdigit() for char in row[1])] # Step 1: Remove lists where the second item doesn't contain any digits
    updated_table_data = [[row[0], row[1].replace('.', '_')] for row in filtered_table_data] # Step 2: Replace "." with "_" in the second item (version)
    filtered_table_data = [row for row in updated_table_data if int(row[1].split('_')[0]) >= least_version] # Step 3: Remove lists where the first number in the version is less than least_version
    
    # Create a list of acceptable versions in the specified format
    acceptable_versions = ([row[1] for row in filtered_table_data][1]
             if len(filtered_table_data) > 1 and [row[1] for row in filtered_table_data][1]
             else [row[1] for row in filtered_table_data][0]) # Get Second Largest Version
    return acceptable_versions


def main_parallel():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        os_results = {}  
        os_tasks = {}
        os_tasks = {
            'Chrome': executor.submit(fetch_chrome_version),
            'Edge': executor.submit(fetch_edge_version),
            'macOS': executor.submit(fetch_macOS_version)
        }

        for os_name, future in os_tasks.items():
            try:
                os_version = future.result()
                os_results[os_name] = os_version
                print(f"OS version for {os_name} completed with result: {os_version}")
            except Exception as e:
                print(f"OS version task for {os_name} raised an exception: {e}")
                
        return os_results



# Call main_parallel and use its results
os_versions = main_parallel()


file_path = "files/os_versions.json"        
with open(file_path, 'w') as file:
    json.dump(os_versions, file, indent=4)
