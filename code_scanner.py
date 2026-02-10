from pathlib import Path
from typing import Iterable, Literal

Language = Literal["python", "javascript", "typescript", "java", "markdown", "shell", "javascript xml", "typescript xml", "yaml", "yml", "configurations", "variables", "any"]

CODE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js"],
    "typescript": [".ts"],
    "java": [".java"],
    "markdown": [".md"],
    "bash": [".sh"],
    "javascript xml": [".jsx"],
    "typescript xml": [".tsx"],
    "javascript xml": [".jsx"],
    "yaml": [".yaml"],
    "yml": [".yml"],
    "configurations": [".conf"],
    "variables": [".env"],
}

def list_code_files(root: str, language: Language = "any") -> Iterable[Path]:
    """
    Parcourt récursivement root et renvoie les fichiers de code.
    - language="any" => tous les langages connus
    - sinon filtre sur un langage particulier
    """
    base = Path(root)
    if language == "any":
        exts = [ext for lst in CODE_EXTENSIONS.values() for ext in lst]
    else:
        exts = CODE_EXTENSIONS.get(language, [])

    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            yield path

if __name__ == "__main__":
    for f in list_code_files(".", language="any"):
        print(f)
