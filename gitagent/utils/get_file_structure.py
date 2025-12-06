from pathlib import Path


class FileStructure():
    EXCLUDE_PREFIXES = {
        ".git/",
        "__pycache__/",
        ".venv/",
        "venv/",
        "env/",
        "build/",
        "dist/",
        ".tox/"
    }
    
    def __init__(self):
        self.files = {}
        self._load_files()

    
    def _load_files(self):
        root = Path(".").resolve()
        entries = []
        
        for py_file in root.rglob("*.py"):
            path = py_file.relative_to(root).as_posix()
            if (any(path.startswith(prefix) for prefix in self.EXCLUDE_PREFIXES)):
                continue

            try:
                self.files[path] = py_file.read_text()            
            except Exception:
                pass
    

    def get_paths(self):
        return sorted(self.files.keys())
    
    def get_contents(self, paths):
        result = {}

        for path in paths:
            if path in self.files:
                result[path] = self.files[path]
            
            else:
                print("Not found in repo")
            
        return result