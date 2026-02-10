from pathlib import Path
from typing import Tuple, Optional

from code_scanner import list_code_files, Language
from review_file import review_file

def review_directory(root: str, max_files: Optional[int] = None, language: Language = "any") -> Tuple[str, int]:
    """
    Analyse tous les fichiers de code d'un dossier.
    Retourne (rapport_markdown, nombre_de_problèmes_HIGH).
    """
    base = Path(root)

    report_lines: list[str] = []
    high_issues = 0
    count = 0

    for file in list_code_files(root, language=language):
        count += 1
        if max_files is not None and count > max_files:
            break

        print(f"[crbot] Analyse du fichier {file}...")
        report = review_file(file)

        report_lines.append(f"# Fichier : {file}\n\n{report}\n\n---\n")

        if "[HIGH]" in report or "HIGH]" in report:
            high_issues += 1

    full_report = "\n".join(report_lines)
    return full_report, high_issues

if __name__ == "__main__":
    rep, high = review_directory("example_code", max_files=5)
    Path("crbot_report.md").write_text(rep, encoding="utf-8")
    print("[crbot] Rapports générés, HIGH issues:", high)