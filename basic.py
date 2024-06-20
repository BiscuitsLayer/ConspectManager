import json
import time
import git

from prettier import make_prettier

CONFIG_FILENAME = "config.json"

def commit_and_push(repo, branch, commit_prefix = "DEFAULT"):
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
        commit_msg = f"[{commit_prefix}] Update for {time.strftime('%x %X')}"
        repo.index.commit(commit_msg)
        repo.git.push('--set-upstream', repo.remote().name, branch["name"])


if __name__ == "__main__":
    # Parse configs
    with open(CONFIG_FILENAME, "r") as f:
        config = json.load(f)
    my_repo_url = config["repo"]

    for branch in config["branches"]:
        # Initialize repository
        repo = git.Repo.init(branch["path"], initial_branch=branch["name"])

        # Add remote
        if not repo.remotes:
            origin = repo.create_remote('origin', my_repo_url)

        # Push default update
        commit_and_push(repo, branch)

        # Push prettier update
        make_prettier(branch["path"])
        commit_and_push(repo, branch, commit_prefix="PRETTIER")
