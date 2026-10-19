"""导出待审查的 GitHub 源码展示副本，不调用 git、不联网、不发布。"""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.metadata import PROJECT_SLUG, VERSION

FILES = (
    '.gitignore', 'README.md', 'RIGHTS.md', 'main.py',
    'LateNightProgrammerSimulator.spec', 'LateNightProgrammerSimulator-public.spec',
    'requirements.txt', 'requirements-build.txt',
    'SPRITE_RULES.md', 'data/events.json', 'data/ambient.json',
    'tools/check_assets.py', 'tools/simulate_sessions.py', 'tools/prepare_github.py',
    'docs/PROJECT.md', 'docs/ASSET_SETUP.md', 'docs/GITHUB_RELEASE.md',
    'docs/PLATFORM_COOPERATION.md',
    'docs/RELEASE_NOTES_v0.1.0-preview.md',
)
PATTERNS = ('src/*.py', 'tests/*.py', 'docs/screenshots/*.png', 'docs/screenshots/*.md',
            '.github/workflows/*.yml', 'licenses/*.txt')


def prepare():
    paths = {ROOT / name for name in FILES}
    for pattern in PATTERNS:
        paths.update(ROOT.glob(pattern))
    for path in paths:
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f'Invalid source path: {path}')
    relatives = sorted(path.relative_to(ROOT).as_posix() for path in paths)
    parent = ROOT / 'dist' / 'github-prep'
    destination = parent / PROJECT_SLUG
    if destination.is_symlink() or not destination.resolve().is_relative_to(ROOT / 'dist'):
        raise ValueError('Export path must stay within project dist/')
    expected = set(relatives) | {'PACKAGE_CONTENTS.json'}
    if destination.exists():
        if any(path.is_symlink() for path in destination.rglob('*')):
            raise ValueError('Export contains a symlink; inspect it before regenerating')
        extras = {p.relative_to(destination).as_posix() for p in destination.rglob('*') if p.is_file()} - expected
        if extras:
            raise ValueError(f'Unexpected files in export; inspect before regenerating: {sorted(extras)}')
    destination.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name in relatives:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / name, target)
        manifest.append({'path': name, 'bytes': target.stat().st_size,
                         'sha256': sha256(target.read_bytes()).hexdigest()})
    contents = {
        'project': PROJECT_SLUG, 'version': VERSION,
        'scope': 'source showcase; original runtime assets are excluded',
        'game_assets_included': False, 'runnable_without_assets': False,
        'executable_included': False, 'original_git_history_included': False,
        'code_license_selected': False, 'exporter_performs_upload': False,
        'files': manifest,
    }
    (destination / 'PACKAGE_CONTENTS.json').write_text(
        json.dumps(contents, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    archive = parent / f'{PROJECT_SLUG}-source-{VERSION}.zip'
    if archive.is_symlink():
        raise ValueError('Archive destination must not be a symlink')
    with ZipFile(archive, 'w', compression=ZIP_DEFLATED) as output:
        for name in sorted(expected):
            output.write(destination / name, f'{PROJECT_SLUG}/{name}')
    with ZipFile(archive) as output:
        if output.testzip() is not None:
            raise ValueError('ZIP integrity check failed')
        names = output.namelist()
        forbidden = ('.git/', '.idea/', '.claude/', '__pycache__/', '/assets/')
        if any(any(part in name for part in forbidden) or name.endswith(('.exe', '.mp3', '.ttf', '.pyc'))
               for name in names):
            raise ValueError('Unexpected private or runtime resource in showcase archive')
    print(f'Prepared {len(manifest)} files: {destination}')
    print(f'Archive: {archive}')
    print('No Git history, runtime assets or EXE included. Nothing uploaded.')


if __name__ == '__main__':
    prepare()
