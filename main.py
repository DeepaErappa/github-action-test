import os
import subprocess
import sys
import yaml
import tempfile
import shutil
from pathlib import Path

# File paths
API_YAML = "api-definitions/api.yaml"
CONFIG_DIR = "deployment-config"

# Define merge paths and their corresponding config files
MERGE_MAP = {
    ("dev", "reference"): "ref.yaml",
    ("reference", "staging"): {
        "type": "external",
        "repo": "https://github.com/DeepaErappa/git-config-files.git",
        "file": "deployment-config/staging.yaml"
    },
    ("staging", "main"): {
        "type": "external",
        "repo": "https://github.com/DeepaErappa/git-config-files.git",
        "file": "deployment-config/prod.yaml"
    },
    ("staging", "master"): {
        "type": "external",
        "repo": "https://github.com/DeepaErappa/git-config-files.git",
        "file": "deployment-config/prod.yaml"
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

def replace_properties(env_yaml_file):
    print(f"[•] Using local config file: {env_yaml_file}")
    env_path = os.path.join(CONFIG_DIR, env_yaml_file)
    update_properties(API_YAML, env_path)

def fetch_external_yaml(repo_url, target_file):
    print(f"[•] Cloning repo: {repo_url}")
    temp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(['git', 'clone', '--depth=1', repo_url, temp_dir], check=True)
        file_path = os.path.join(temp_dir, target_file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{target_file} not found in {repo_url}")
        return file_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to clone repository: {e}")
    finally:
        shutil.rmtree(temp_dir)

def update_properties(api_yaml_path, env_yaml_path):
    api_data = load_yaml(api_yaml_path)
    env_data = load_yaml(env_yaml_path)

    if 'properties' not in env_data:
        raise KeyError(f"'properties' section not found in {env_yaml_path}")

    api_data['properties'] = env_data['properties']
    write_yaml(api_yaml_path, api_data)
    print(f"[✓] Updated '{api_yaml_path}' using properties from '{env_yaml_path}'")

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
        repo_url = config["repo"]
        remote_file = config["file"]
        try:
            external_yaml_path = fetch_external_yaml(repo_url, remote_file)
            update_properties(API_YAML, external_yaml_path)
        except Exception as e:
            print(f"[✗] Error: {e}")
    else:
        print(f"[!] Unknown config format for {key}: {config}")

if __name__ == "__main__":
    main()
