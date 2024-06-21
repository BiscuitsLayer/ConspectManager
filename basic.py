import json
import shutil
import time
import git
import logging

from prettier import make_prettier

CONFIG_FILENAME = "config.json"
MAX_ATTEMPTS_COUNT = 3

def commit_and_push(repo, branch, commit_prefix = "DEFAULT") -> bool:
    try:
        # Add all files
        repo.git.add(all=True)

        # Try to get reference
        has_reference = True
        try:
            _ = repo.head.commit
        except ValueError as e:
            has_reference = False

        # Check if there are changes
        diff_list = []
        if has_reference:
            diff_list = repo.head.commit.diff()

        # Commit and push
        if diff_list or not has_reference:
            if diff_list:
                logging.info(f"{commit_prefix}: updates since last commit: {diff_list}")
            else:
                logging.info(f"{commit_prefix}: no previous commits found, creating initial commit")

            commit_msg = f"[{commit_prefix}] Update for {time.strftime('%x %X')}"
            repo.index.commit(commit_msg)
            logging.info(f"{commit_prefix}: commit done")
        
        else:
            logging.warning(f"{commit_prefix}: no changes found since previous commit")
        
        repo.git.push('--set-upstream', repo.remote().name, branch["name"])
        logging.info(f"{commit_prefix}: push done")
        return True

    except git.exc.GitCommandError as e:
        logging.error(f"{commit_msg}: commit failed {e}")
        return False


if __name__ == "__main__":
    # Setup logger handlers
    file_log = logging.FileHandler("basic.log")
    console_out = logging.StreamHandler()

    # Initialize loggers
    logging.basicConfig(handlers=(file_log, console_out), level=logging.INFO)

    # Parse configs
    with open(CONFIG_FILENAME, "r", encoding="utf8") as f:
        config = json.load(f)
        logging.info(f"{config = }")

    my_repo_url = config["repo"]

    for branch in config["branches"]:
        # Setup formatters
        formatter = logging.Formatter(f"%(asctime)s; {branch['name']}; %(levelname)s; %(message)s", "%Y-%m-%d %H:%M:%S")
        file_log.setFormatter(formatter)
        console_out.setFormatter(formatter)

        # Initialize repository
        repo = git.Repo.init(branch["path"], initial_branch=branch["name"])
        logging.info("Git repo initialized")

        # Add remote
        if repo.remotes:
            repo.delete_remote('origin')
            logging.info("Remote origin deleted")

        if not repo.remotes:
            origin = repo.create_remote('origin', my_repo_url)
            logging.info(f"Remote origin added with url {my_repo_url}")

        # Push default update
        attempts_count = 0
        while not commit_and_push(repo, branch) and attempts_count < MAX_ATTEMPTS_COUNT:
            attempts_count += 1

        # Push prettier update
        attempts_count = 0
        make_prettier(branch["path"])
        while not commit_and_push(repo, branch, commit_prefix="PRETTIER") and attempts_count < MAX_ATTEMPTS_COUNT:
            attempts_count += 1
