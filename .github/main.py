import os
import subprocess
import sys
import yaml
import requests

# Constants and Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
EXTERNAL_REPO = "DeepaErappa/git-config-files"
EXTERNAL_BRANCH = "main"
API_YAML = os.path.join(REPO_ROOT, "api-definitions", "tmf-manage.yaml")
CONFIG_DIR = os.path.join(REPO_ROOT, "deployment-config")
GITHUB_TOKEN = os.getenv("GH_TOKEN")

# Branch to config mapping
MERGE_MAP = {
    ("dev", "reference"): "ref.yaml",
    ("reference", "staging"): "staging.yaml",
    ("staging", "main"): "prod.yaml",
    ("staging", "master"): "prod.yaml"
}

def get_current_branch():
    return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()

def get_last_merged_branch():
    log = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
    if 'from' in log and 'into' in log:
        parts = log.split()
        from_index = parts.index('from')
        return parts[from_index + 1]
    return None

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def write_yaml(path, data):
    with open(path, 'w') as f:
        yaml.dump(data, f, sort_keys=False, default_flow_style=False)
def fetch_external_yaml_file(repo, path, branch):
    if not GITHUB_TOKEN:
        raise EnvironmentError("GH_TOKEN not set in environment")

    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.raw"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch {path} from {repo}@{branch}: {response.status_code} - {response.text}")

    return yaml.safe_load(response.text)

def replace_properties(api_yaml_path, new_properties_yaml_path):
    # Load full API YAML
    api_data = load_yaml(api_yaml_path)
    
    # Load new properties
    new_props_data = load_yaml(new_properties_yaml_path)

    if 'properties' not in new_props_data:
        raise KeyError("New properties YAML must contain top-level 'properties' key")

    # Debug prints (optional)
    print("Keys before replacement:", list(api_data.keys()))
    print("Existing properties keys:", list(api_data.get('properties', {}).keys()))
    print("New properties keys:", list(new_props_data['properties'].keys()))

    # Replace the existing 'properties' section completely
    api_data['properties'] = new_props_data['properties']

    # Write full updated YAML back
    write_yaml(api_yaml_path, api_data)

    print(f"Successfully replaced 'properties' section in {api_yaml_path}")

# Usage example:
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

# import os
# import subprocess
# import yaml
# import requests


# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# # Go one level up to reach repo root
# REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
# EXTERNAL_REPO = "DeepaErappa/git-config-files"  # e.g., "DeepaErappa/config-repo"
# EXTERNAL_BRANCH = "main"  # or whatever branch holds the staging/prod.yaml

# # Absolute paths to API and config directories
# API_YAML = os.path.join(REPO_ROOT, "api-definitions", "tmf-manage.yaml")
# CONFIG_DIR = os.path.join(REPO_ROOT, "deployment-config")
# GITHUB_TOKEN = os.getenv("GH_TOKEN")

# # Define merge paths and their corresponding config files
# MERGE_MAP = {
#     ("dev", "reference"): "ref.yaml",
#     ("reference", "staging"): "staging.yaml",
#     ("staging", "main"): "prod.yaml",
#     ("staging", "master"): "prod.yaml"
# }

# def get_current_branch():
#     return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode().strip()

# def get_last_merged_branch():
#     # Uses git log to parse last merged commit message
#     log = subprocess.check_output(['git', 'log', '-1', '--pretty=%B']).decode().strip()
#     if 'from' in log and 'into' in log:
#         parts = log.split()
#         from_index = parts.index('from')
#         return parts[from_index + 1]
#     return None

# def load_yaml(path):
#     with open(path, 'r') as file:
#         return yaml.safe_load(file)

# def write_yaml(path, data):
#     with open(path, 'w') as file:
#         yaml.dump(data, file, sort_keys=False)

# import base64
# import requests

# def fetch_external_yaml_file(repo, path, branch):
#     if not GITHUB_TOKEN:
#         raise EnvironmentError("GH_TOKEN not set in environment")

#     url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
#     headers = {
#         "Authorization": f"token {GITHUB_TOKEN}",
#         "Accept": "application/vnd.github.v3.raw"
#     }

#     response = requests.get(url, headers=headers)
#     if response.status_code != 200:
#         raise RuntimeError(f"Failed to fetch {path} from {repo}@{branch}: {response.status_code} - {response.text}")

#     return yaml.safe_load(response.text)


# def replace_properties(env_yaml_file):
#     api_data = load_yaml(API_YAML)
#     if env_yaml_file in ["staging.yaml", "prod.yaml"]:
#         print(f"[i] Fetching {env_yaml_file} from external repository")
#         env_data = fetch_external_yaml_file(EXTERNAL_REPO, f"deployment-config/{env_yaml_file}", EXTERNAL_BRANCH)
#         print(env_data)
#     else:
#         env_data = load_yaml(os.path.join(CONFIG_DIR, env_yaml_file))


#     if 'properties' not in env_data:
#         raise KeyError(f"'properties' not found in {env_yaml_file}")
#     # Update version if present
#     if 'version' in env_data:
#         api_data['version'] = env_data['version']
#         print(f"[✓] Updated 'version' in {API_YAML} to {env_data['version']}")
#     else:
#         print(f"[i] 'version' not found in {env_yaml_file}, skipping version update.")


#     api_data['properties'] = env_data['properties']
#     write_yaml(API_YAML, api_data)
#     print(f"[✓] Updated 'properties' in {API_YAML} using {env_yaml_file}")

# # def main():
# #     current_branch = get_current_branch()
# #     source_branch = get_last_merged_branch()

# #     print(f"Detected merge from: {source_branch} → {current_branch}")

# #     key = (source_branch, current_branch)
# #     if key in MERGE_MAP:
# #         replace_properties(MERGE_MAP[key])
# #     else:
# #         print(f"No config found for {source_branch} → {current_branch}. Skipping replacement.")

# import sys

# def main():
#     if len(sys.argv) == 3:
#         source_branch = sys.argv[1]
#         current_branch = sys.argv[2]
#     else:
#         current_branch = get_current_branch()
#         source_branch = get_last_merged_branch()

#     print(f"Detected merge from: {source_branch} → {current_branch}")

#     key = (source_branch, current_branch)
#     if key in MERGE_MAP:
#         replace_properties(MERGE_MAP[key])
#     else:
#         print(f"No config found for {source_branch} → {current_branch}. Skipping replacement.")


# if __name__ == "__main__":
#     main()
