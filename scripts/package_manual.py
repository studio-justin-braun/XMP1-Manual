"""Create an offline download ZIP of the validated repository edition."""
from pathlib import Path
import zipfile
from check_repository import main as validate

ROOT = Path(__file__).resolve().parents[1]


def main():
    validate()
    target = ROOT / 'dist/XMP1_Handbuch_Gesamtpaket.zip'
    target.parent.mkdir(exist_ok=True)
    files = [ROOT / name for name in ('index.html', 'LIESMICH.txt', 'Pruefbericht.md', 'NOTICE.md')]
    for name in ('Handbuch', 'pdf', 'Quellen', 'Pruefung'):
        files.extend(p for p in (ROOT / name).rglob('*') if p.is_file())
    with zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
                raise RuntimeError(f'Unerwarteter Dateiverweis: {path}')
            archive.write(path, path.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as archive:
        if archive.testzip() is not None:
            raise RuntimeError('ZIP-Prüfung fehlgeschlagen.')
    print(f'ZIP: {target.name}, {len(files)} Dateien, {target.stat().st_size:,} Bytes (dist/)')


if __name__ == '__main__':
    main()
