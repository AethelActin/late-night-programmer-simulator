"""检查图形运行需要的资源，不下载或修改素材。"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SEQUENCES = ('idle1', 'idle2', 'idle3', 'cat_wake', 'cat_type_remove', 'cat_down',
             'rain', 'rain_idle', 'rain_cat_wake', 'rain_cat_watch',
             'drink', 'phone', 'scratch', 'drowsy', 'excited', 'done')


def missing_assets(root=ROOT):
    missing = []
    for filename in ('PressStart2P-Regular.ttf', 'FusionPixel10.ttf'):
        path = Path('assets/fonts') / filename
        if not (root / path).is_file():
            missing.append(path.as_posix())
    for sequence in SEQUENCES:
        path = Path('assets/images/sprites') / sequence
        if not any((root / path).glob('*.png')):
            missing.append(path.as_posix() + '/*.png')
    return missing


if __name__ == '__main__':
    missing = missing_assets()
    if missing:
        print('Missing required assets (see docs/ASSET_SETUP.md):')
        for path in missing:
            print(' - ' + path)
        raise SystemExit(1)
    print('Required fonts and 16 animation sequences are present. Audio is optional.')
