import subprocess
from typing import Tuple

def get_full_diff():
    result = subprocess.run(
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

    return result.stdout + staged.stdout


def has_changes():
    return len(get_full_diff().strip()) > 0