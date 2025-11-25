import subprocess

def get_difference():
    unstaged = subprocess.run(
        ["git", "diff", "HEAD"],
        capture_output=True,
        text=True,
        check=False
    )

    staged = subprocess.run(
        ["git", "diff", "--staged", "HEAD"],
        capture_output=True,
        text=True,
        check=False
    )

    return unstaged.stdout + staged.stdout

def has_changes():
    return len(get_difference().strip()) > 0