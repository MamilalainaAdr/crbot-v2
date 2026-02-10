import pathlib

SOURCE_DIRS = [
    "data_repos/ASVS",
    "data_repos/awesome-code-review",
    "data_repos/awesome-readme",
    "data_repos/code-with-engineering-playbook",
    "data_repos/eng-practices",
    "data_repos/javascript",
    "data_repos/python-guide",
    "data_repos/reviewdog",
    "data_repos/sonar-java",
    "data_repos/styleguide",
]

OUTPUT_DIR = pathlib.Path("dataset")
EXTENSIONS = (".md", ".txt")
MAX_FILE_SIZE = 200_000  # 200 Ko

def iter_files():
    for src in SOURCE_DIRS:
        base = pathlib.Path(src)
        if not base.exists():
            print(f"[collect] WARNING: {base} n'existe pas, repo non cloné ?")
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTENSIONS:
                if path.stat().st_size <= MAX_FILE_SIZE:
                    yield path
                else:
                    print(f"[collect] Ignoré (trop gros): {path}")

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for i, path in enumerate(iter_files(), start=1):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[collect] Erreur lecture {path}: {e}")
            continue

        out_path = OUTPUT_DIR / f"doc_{i}.txt"
        out_path.write_text(text, encoding="utf-8")
        print(f"[collect] Sauvegardé {out_path} depuis {path}")

if __name__ == "__main__":
    main()
