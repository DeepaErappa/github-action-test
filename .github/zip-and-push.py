import os
import shutil
import subprocess
import sys
import zipfile

TMP_OUTPUT_FILE = ".tmp-output/tmf-manage.yaml"
DEPLOY_DESCRIPTOR = "deployment-config/deployment-descriptor.txt"
ZIP_FILENAME = "collected_output.zip"
DEST_REPO = "DeepaErappa/zip-files"
DEST_BRANCH = "main"
DEST_REPO_DIR = "zip-target"

GIT_USER_NAME = "github-actions[bot]"
GIT_USER_EMAIL = "github-actions[bot]@users.noreply.github.com"
GH_TOKEN = os.environ.get("GH_TOKEN")

if not GH_TOKEN:
    sys.exit("GH_TOKEN environment variable is required")

def run(cmd, cwd=None):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)

def create_zip():
    with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add the single deployment-descriptor file
        if os.path.exists(DEPLOY_DESCRIPTOR):
            zipf.write(DEPLOY_DESCRIPTOR, os.path.join("deployment-config", "deployment-descriptor.txt"))
        else:
            print(f"[!] {DEPLOY_DESCRIPTOR} not found")

        # Add the tmf-manage.yaml from .tmp-output into api-definitions/
        if os.path.exists(TMP_OUTPUT_FILE):
            zipf.write(TMP_OUTPUT_FILE, os.path.join("api-definitions", "tmf-manage.yaml"))
        else:
            print(f"[!] {TMP_OUTPUT_FILE} not found")

    print(f"[✓] Created {ZIP_FILENAME}")

def clone_dest_repo():
    repo_url = f"https://x-access-token:{GH_TOKEN}@github.com/{DEST_REPO}.git"
    if os.path.exists(DEST_REPO_DIR):
        shutil.rmtree(DEST_REPO_DIR)
    run(f"git clone --depth 1 --branch {DEST_BRANCH} {repo_url} {DEST_REPO_DIR}")

def copy_zip_to_repo():
    shutil.copy(ZIP_FILENAME, os.path.join(DEST_REPO_DIR, ZIP_FILENAME))

def commit_and_push():
    run(f"git config user.name \"{GIT_USER_NAME}\"", cwd=DEST_REPO_DIR)
    run(f"git config user.email \"{GIT_USER_EMAIL}\"", cwd=DEST_REPO_DIR)
    run(f"git add {ZIP_FILENAME}", cwd=DEST_REPO_DIR)
    try:
        run(f"git commit -m \"[Auto] Add/update {ZIP_FILENAME}\"", cwd=DEST_REPO_DIR)
    except subprocess.CalledProcessError:
        print("No changes to commit")
    run("git push", cwd=DEST_REPO_DIR)

def cleanup_tmp_folder():
    if os.path.exists(".tmp-output"):
        shutil.rmtree(".tmp-output")
        print("[✓] Removed .tmp-output folder")

def main():
    create_zip()
    clone_dest_repo()
    copy_zip_to_repo()
    commit_and_push()
    cleanup_tmp_folder()
    print("[✓] Zip pushed to target repo and cleaned up.")

if __name__ == "__main__":
    main()


# import os
# import shutil
# import subprocess
# import sys
# import zipfile

# SRC_DIRS = ["api-definitions", "deployment-config"]
# ZIP_FILENAME = "collected_output.zip"
# DEST_REPO = "DeepaErappa/zip-files"   # <-- replace with your target repo, e.g. "org/repo"
# DEST_BRANCH = "main"                 # <-- target branch name in destination repo
# DEST_REPO_DIR = "zip-target"

# GIT_USER_NAME = "github-actions[bot]"
# GIT_USER_EMAIL = "github-actions[bot]@users.noreply.github.com"
# GH_TOKEN = os.environ.get("GH_TOKEN")

# if not GH_TOKEN:
#     sys.exit("GH_TOKEN environment variable is required")

# def run(cmd, cwd=None):
#     print(f"Running: {cmd}")
#     subprocess.run(cmd, shell=True, check=True, cwd=cwd)

# def create_zip():
#     with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
#         for src_dir in SRC_DIRS:
#             for root, dirs, files in os.walk(src_dir):
#                 for file in files:
#                     abs_path = os.path.join(root, file)
#                     rel_path = os.path.relpath(abs_path, '.')  # keep folder structure
#                     zipf.write(abs_path, rel_path)
#     print(f"Created {ZIP_FILENAME}")

# def clone_dest_repo():
#     repo_url = f"https://x-access-token:{GH_TOKEN}@github.com/{DEST_REPO}.git"
#     if os.path.exists(DEST_REPO_DIR):
#         shutil.rmtree(DEST_REPO_DIR)
#     run(f"git clone --depth 1 --branch {DEST_BRANCH} {repo_url} {DEST_REPO_DIR}")

# def copy_zip_to_repo():
#     shutil.copy(ZIP_FILENAME, os.path.join(DEST_REPO_DIR, ZIP_FILENAME))

# def commit_and_push():
#     run(f"git config user.name \"{GIT_USER_NAME}\"", cwd=DEST_REPO_DIR)
#     run(f"git config user.email \"{GIT_USER_EMAIL}\"", cwd=DEST_REPO_DIR)
#     run(f"git add {ZIP_FILENAME}", cwd=DEST_REPO_DIR)
#     # Commit if changes exist, otherwise ignore error
#     try:
#         run(f"git commit -m \"[Auto] Add/update {ZIP_FILENAME}\"", cwd=DEST_REPO_DIR)
#     except subprocess.CalledProcessError:
#         print("No changes to commit")
#     run("git push", cwd=DEST_REPO_DIR)
# def main():
#     create_zip()
#     clone_dest_repo()
#     copy_zip_to_repo()
#     commit_and_push()
#     print("Zip pushed to target repo successfully.")

# if __name__ == "__main__":
#     main()
