import os
import subprocess
import sys
import yaml
import requests

# File paths
API_YAML = "api-definitions/api.yaml"
CONFIG_DIR = "deployment-config"

# Define merge paths and their corresponding config files
MERGE_MAP = {
    ("dev", "reference"): "ref.yaml",
    ("reference", "staging"): {
        "type": "external",
        "repo": "DeepaErappa/git-config-files",
        "file": "deployment-config/staging.yaml",
        "branch": "main"  # You can change this to the actual branch
    },
    ("staging", "main"): {
        "type": "external",
        "repo": "DeepaErappa/git-config-files",
        "file": "deployment-config/prod.yaml",
        "branch": "main"
    },
    ("staging", "master"): {
        "type": "external",
        "repo": "DeepaErappa/git-config-files",
        "file": "deployment-config/prod.yaml",
        "branch": "main"
    },
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
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def write_yaml(path, data):
    with open(path, 'w') as file:
        yaml.dump(data, file, sort_keys=False)

def fetch_external_yaml(repo, path, branch):
    token = os.getenv("GH_TOKEN")
    if not token:
        raise EnvironmentError("GH_TOKEN not set in environment")

    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.raw"
    }

    print(f"[•] Fetching file from GitHub API: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise RuntimeError(f"Failed to fetch file: {response.status_code} - {response.text}")

    return yaml.safe_load(response.text)

def update_properties_from_dict(api_yaml_path, env_data):
    api_data = load_yaml(api_yaml_path)

    if 'properties' not in env_data:
        raise KeyError("'properties' section not found in fetched config")

    api_data['properties'] = env_data['properties']
    write_yaml(api_yaml_path, api_data)
    print(f"[✓] Updated '{api_yaml_path}' using properties from fetched config")

def replace_properties(env_yaml_file):
    print(f"[•] Using local config file: {env_yaml_file}")
    env_path = os.path.join(CONFIG_DIR, env_yaml_file)
    update_properties_from_dict(API_YAML, load_yaml(env_path))

def main():
    if len(sys.argv) == 3:
        source_branch = sys.argv[1]
        current_branch = sys.argv[2]
    else:
        current_branch = get_current_branch()
        source_branch = get_last_merged_branch()

    print(f"Detected merge from: {source_branch} → {current_branch}")

    key = (source_branch, current_branch)
    if key not in MERGE_MAP:
        print(f"[!] No config found for merge path: {key}. Skipping update.")
        return

    config = MERGE_MAP[key]
    if isinstance(config, str):
        replace_properties(config)
    elif isinstance(config, dict) and config.get("type") == "external":
        try:
            env_data = fetch_external_yaml(config["repo"], config["file"], config.get("branch", "main"))
            update_properties_from_dict(API_YAML, env_data)
        except Exception as e:
            print(f"[✗] Error: {e}")
    else:
        print(f"[!] Unknown config format for {key}: {config}")

if __name__ == "__main__":
    main()
