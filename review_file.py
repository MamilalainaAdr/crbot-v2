from pathlib import Path
from typing import List, Optional

import chromadb
from llm_client import generate
from code_scanner import Language

CHROMA_PATH = "chroma_index"
COLLECTION_NAME = "crbot_knowledge"
PROJECT_OVERVIEW_PATH = Path("project_overview.md")
SUMMARY_DIR = Path("file_summaries")

def guess_language_from_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".py":
        return "Python"
    if suffix in (".js", ".ts"):
        return "JavaScript/TypeScript"
    if suffix in (".jsx", ".tsx"):
        return "JavaScriptXML/TypeScriptXML"
    if suffix in (".yml", ".yaml"):
        return "yaml/yml"
    if suffix == ".md":
        return "markdown"
    if suffix == ".sh":
        return "bash"
    if suffix == ".java":
        return "Java"
    return "code"

def load_file_summary(path: Path) -> Optional[str]:
    safe = str(path).replace("/", "_").replace("\\", "_").replace(".", "_") + ".md"
    summary_path = SUMMARY_DIR / safe
    if summary_path.exists():
        return summary_path.read_text(encoding="utf-8", errors="ignore")
    return None

def get_neighbor_files(path: Path, max_neighbors: int = 3) -> List[Path]:
    parent = path.parent
    neighbors: List[Path] = []
    for p in parent.iterdir():
        if p.is_file() and p != path and p.suffix.lower() == path.suffix.lower():
            neighbors.append(p)
        if len(neighbors) >= max_neighbors:
            break
    return neighbors

def make_file_prompt(
    filename: str,
    language: str,
    code: str,
    contexts: List[str],
    project_overview: Optional[str],
    self_summary: Optional[str],
    neighbor_summaries: List[str],
) -> str:
    rag_context = "\n\n---\n\n".join(contexts)
    neighbors_text = "\n\n".join(neighbor_summaries) if neighbor_summaries else "(aucun résumé de fichiers voisins disponible)"
    self_text = self_summary or "(pas de résumé spécifique pour ce fichier)"
    overview_text = project_overview or "(pas de vue globale du projet disponible)"

    return f"""Tu es un outil de revue de code automatisée, expert en qualité et en sécurité.

On te donne :
- une vue globale du projet,
- un résumé du fichier à analyser,
- les résumés de quelques fichiers voisins,
- des extraits de bonnes pratiques,
- le code complet du fichier.

Utilise tout ce contexte pour raisonner sur les PROBLÈMES LOCAUX dans le fichier,
mais aussi sur les PROBLÈMES D'INTERACTION avec le reste du projet.

=== Vue globale du projet ===
{overview_text}

=== Résumé de ce fichier ===
{self_text}

=== Résumés de fichiers voisins ===
{neighbors_text}

=== Contexte de bonnes pratiques (RAG) ===
{rag_context}

=== Fichier à analyser ===
Nom : {filename}
Langage : {language}

Code :
```{language}
{code}
Tâche :
1- Identifier les problèmes potentiels dans ce fichier (bugs, sécurité, qualité, style).
2- Identifier les problèmes liés aux interactions avec d'autres fichiers (mauvaise gestion de données partagées, incohérences, duplications, etc.).
3- Indiquer les lignes ou les portions de code concernées (approximation acceptable).
4- Proposer des corrections concrètes (extraits de code corrigé ou pseudo-code).
5- Donner un score global de qualité pour ce fichier entre 0 et 10, avec une phrase d'explication.

Format de sortie (Markdown) :
- [GRAVITY] Description du problème (fichier:ligneapprox)
- - Type: (BUG | SECURITY | STYLE | DESIGN | INTERACTION)
- - Détail / justification
- - Suggestion de correction
À la fin, ajoute une section :
Score global

Score: X/10
Commentaire: ...

GRAVITY peut être : LOW, MEDIUM, HIGH.
Réponds uniquement en français.
"""

def review_file(path: Path) -> str:
    language = guess_language_from_suffix(path)
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)

    question = f"Bonnes pratiques de revue de code et de sécurité pour du code {language}."
    results = collection.query(
        query_texts=[question],
        n_results=4,
    )
    contexts = results["documents"][0]

    code = path.read_text(encoding="utf-8", errors="ignore")

    project_overview = None
    if PROJECT_OVERVIEW_PATH.exists():
        project_overview = PROJECT_OVERVIEW_PATH.read_text(encoding="utf-8", errors="ignore")

    self_summary = load_file_summary(path)

    neighbor_summaries: List[str] = []
    for neigh in get_neighbor_files(path, max_neighbors=3):
        s = load_file_summary(neigh)
        if s:
            neighbor_summaries.append(f"### {neigh}\n{s}")

    prompt = make_file_prompt(
        filename=str(path),
        language=language,
        code=code,
        contexts=contexts,
        project_overview=project_overview,
        self_summary=self_summary,
        neighbor_summaries=neighbor_summaries,
    )

    report = generate(prompt, temperature=0.1, max_tokens=1024)
    return report

if __name__ == "__main__":
    example = Path("example_code/exemple.py")
    print(review_file(example))