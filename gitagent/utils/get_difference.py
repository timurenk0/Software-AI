def get_difference():
    # ... (rest of the file remains the same)

    return unstaged.stdout + staged.stdout

def has_changes():
    return len(get_difference().strip()) > 0