import typer
from pathlib import Path

import build_index
from build_project_overview import build_overview
from review_project import review_directory
from code_scanner import Language

app = typer.Typer(help="crbot : outil local de revue de code (qualité + sécurité) avec RAG.")

@app.command()
def index():
    """
    Reconstruit l'index RAG à partir des fichiers dataset/doc_*.txt.
    """
    typer.echo("[crbot] Reconstruction de l'index RAG...")
    build_index.main()
    typer.echo("[crbot] Index reconstruit.")

@app.command()
def overview(
    path: str = typer.Argument(".", help="Chemin du projet de code à résumer."),
):
    """
    Génère une vue globale du projet (project_overview.md + file_summaries/).
    """
    typer.echo(f"[crbot] Génération de la vue globale pour : {path}")
    build_overview(path)
    typer.echo("[crbot] Vue globale générée.")

@app.command()
def review(
    path: str = typer.Argument(".", help="Chemin du dossier de code à analyser."),
    max_files: int = typer.Option(None, help="Nombre max de fichiers à analyser."),
    language: str = typer.Option("any", help="Filtrer sur un langage (python, javascript, typescript, java, any)."),
    fail_on_high: bool = typer.Option(
        True,
        help="Retourne un code de sortie 1 s'il existe des problèmes HIGH.",
    ),
):
    """
    Analyse un dossier de code et génère un rapport Markdown (crbot_report.md).
    """
    typer.echo(f"[crbot] Analyse du dossier : {path}")
    lang: Language = language if language in ("python", "javascript", "typescript", "java", "any") else "any"

    report, high_issues = review_directory(path, max_files=max_files, language=lang)

    out_path = Path("crbot_report.md")
    out_path.write_text(report, encoding="utf-8")
    typer.echo(f"[crbot] Rapport écrit dans {out_path}")

    if fail_on_high and high_issues > 0:
        typer.echo(f"[crbot] Problèmes HIGH détectés : {high_issues}. Code de sortie 1.")
        raise typer.Exit(code=1)
    else:
        typer.echo("[crbot] Aucun problème HIGH détecté.")
        raise typer.Exit(code=0)

if __name__ == "__main__":
    app()
