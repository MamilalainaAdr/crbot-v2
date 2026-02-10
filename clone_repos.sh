#!/bin/bash

# Créer le dossier data_sources
mkdir -p data_repos
cd data_repos

echo "[clone_repos] Clonage des repos GitHub..."

# Liste des repos
repos=(
    "https://github.com/OWASP/ASVS"
    "https://github.com/joho/awesome-code-review"
    "https://github.com/matiassingers/awesome-readme"
    "https://github.com/microsoft/code-with-engineering-playbook"
    "https://github.com/google/eng-practices"
    "https://github.com/airbnb/javascript"
    "https://github.com/realpython/python-guide"
    "https://github.com/reviewdog/reviewdog"
    "https://github.com/SonarSource/sonar-java"
    "https://github.com/google/styleguide"
)

# Cloner chaque repo
for repo in "${repos[@]}"; do
    repo_name=$(basename "$repo" .git)
    
    if [ -d "$repo_name" ]; then
        echo "[clone_repos] $repo_name déjà cloné"
    else
        echo "[clone_repos] Clonage de $repo_name..."
        git clone --depth 1 "$repo" "$repo_name"
    fi
done

cd ..
echo "[clone_repos] Tous les repos sont clonés dans data_repos/"