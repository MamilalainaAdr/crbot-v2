# build_project_overview.py
from pathlib import Path
from typing import Iterable
from code_scanner import list_code_files
from llm_client import generate

SUMMARY_DIR = Path("file_summaries")
OVERVIEW_PATH = Path("project_overview.md")

def normalize_filename(path: Path) -> str:
    safe = str(path).replace("/", "_").replace("\\", "_").replace(".", "_")
    return safe + ".md"

def make_summary_prompt(rel_path: str, code: str) -> str:
    return f"""Tu es un assistant expert en architecture logicielle et revue de code.

On te donne le contenu complet d'un fichier de code. Tu dois produire un résumé concis.

Fichier : {rel_path}

Code :
```text
{code}
Tâche :
1- Résumer en 5 phrases maximum :
- rôle principal du fichier,
- principales fonctions / classes,
- interactions importantes avec d'autres modules (imports, appels externes),
- éventuels risques évidents (sécurité, robustesse).
2- Ajouter à la fin :
- une ligne "Zone_sensible: OUI" si le fichier touche à l'authentification, à la base de données, au réseau, aux secrets, ou à la sécurité,
- sinon "Zone_sensible: NON".

Réponds uniquement en français.
"""

def summarize_file(root: Path, path: Path) -> str:
    rel_path = str(path.relative_to(root))
    try:
        code = path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"[ERREUR] Impossible de lire le fichier {rel_path} : {e}"
    prompt = make_summary_prompt(rel_path, code)
    summary = generate(prompt, temperature=0.1, max_tokens=512)
    return summary

def build_overview(root: str = ".") -> None:
    base = Path(root)
    SUMMARY_DIR.mkdir(exist_ok=True)
    overview_lines: list[str] = []
    overview_lines.append("# Vue globale du projet\n")
    overview_lines.append(f"Dossier racine : `{base}`\n")

    for file in list_code_files(root, language="any"):
        rel_path = str(file.relative_to(base))
        print(f"[overview] Résumé de {rel_path}...")

        summary = summarize_file(base, file)

        summary_filename = normalize_filename(file)
        summary_path = SUMMARY_DIR / summary_filename
        summary_path.write_text(summary, encoding="utf-8")

        overview_lines.append(f"## {rel_path}\n")
        overview_lines.append(summary)
        overview_lines.append("\n---\n")

    OVERVIEW_PATH.write_text("\n".join(overview_lines), encoding="utf-8")
    print(f"[overview] Vue globale écrite dans {OVERVIEW_PATH}")
    print(f"[overview] Résumés individuels dans {SUMMARY_DIR}/")

if __name__ == "__main__":
    build_overview(".")