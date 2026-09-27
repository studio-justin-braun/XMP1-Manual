"""Stage the HTML and PDF edition for GitHub Pages, with relative URLs intact."""
from pathlib import Path
import shutil
from check_repository import main as validate

ROOT = Path(__file__).resolve().parents[1]


def main():
    validate()
    target = ROOT / 'build/site'
    target.mkdir(parents=True, exist_ok=True)
    for name in ('Handbuch', 'pdf'):
        shutil.copytree(ROOT / name, target / name, dirs_exist_ok=True)
    for name in ('index.html', '.nojekyll'):
        shutil.copy2(ROOT / name, target / name)
    print('GitHub-Pages-Dateien: build/site/')


if __name__ == '__main__':
    main()
