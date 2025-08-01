import os
import subprocess
import yaml

# File paths 
API_YAML = "api-definitions/api.yaml"
CONFIG_DIR = "deployment-config"

# Define merge paths and their corresponding config files
MERGE_MAP = {
    ("dev", "reference"): "ref.yaml",
    ("reference", "staging"): "staging.yaml",
    ("staging", "main"): "prod.yaml",
    ("staging", "master"): "prod.yaml"
}

def get_current_branch():
    return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()

def get_last_merged_branch():
    # Uses git log to parse last merged commit message
    log = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
    if 'from' in log and 'into' in log:
        parts = log.split()
        from_index = parts.index('from')
        return parts[from_index + 1]
    return None

def load_yaml(path):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def write_yaml(path, data):
    with open(path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def replace_properties(env_yaml_file):
    api_data = load_yaml(API_YAML)
    env_data = load_yaml(os.path.join(CONFIG_DIR, env_yaml_file))

    if 'properties' not in env_data:
        raise KeyError(f"'properties' not found in {env_yaml_file}")

    api_data['properties'] = env_data['properties']
    write_yaml(API_YAML, api_data)
    print(f"[✓] Updated 'properties' in {API_YAML} using {env_yaml_file}")



# def main():
#     current_branch = get_current_branch()
#     source_branch = get_last_merged_branch()

#     print(f"Detected merge from: {source_branch} → {current_branch}")

#     key = (source_branch, current_branch)
#     if key in MERGE_MAP:
#         replace_properties(MERGE_MAP[key])
#     else:
#         print(f"No config found for {source_branch} → {current_branch}. Skipping replacement.")

import sys

def main():
    if len(sys.argv) == 3:
        source_branch = sys.argv[1]
        current_branch = sys.argv[2]
    else:
        current_branch = get_current_branch()
        source_branch = get_last_merged_branch()

    print(f"Detected merge from: {source_branch} → {current_branch}")

    key = (source_branch, current_branch)
    if key in MERGE_MAP:
        replace_properties(MERGE_MAP[key])
    else:
        print(f"No config found for {source_branch} → {current_branch}. Skipping replacement.")


if __name__ == "__main__":
    main()
