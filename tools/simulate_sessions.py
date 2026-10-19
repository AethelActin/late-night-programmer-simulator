"""无交互数值抽样。只模拟动画时长，不加载图像/音频，不能代替试玩。"""
import argparse
from collections import Counter
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.session import GameSession


class AnimationTimeline:
    counts = {p.name: len(list(p.glob('*.png')))
              for p in (ROOT / 'assets/images/sprites').glob('*') if p.is_dir()}

    def play(self, name, transition=None):
        self.remaining = self.counts[name] / 8 + (1.5 if transition == 'fade' else 0)
        self.loop = False

    def update(self, dt):
        self.remaining -= dt

    def is_finished(self):
        return not self.loop and self.remaining <= 0


def simulate(seeds):
    results = []
    for mode in range(3):
        endings = Counter()
        lengths = []
        for seed in range(seeds):
            random.seed(seed)
            session = GameSession(AnimationTimeline())
            session.start(mode)
            for tick in range(72000):
                session.update(0.1)
                if session.state.domain == 'done':
                    endings[session.stats['_done_reason']] += 1
                    lengths.append((tick + 1) / 10)
                    break
            else:
                endings['timeout_2h'] += 1
        results.append({'mode': mode, 'seeds': seeds, 'endings': dict(endings),
                        'min_seconds': min(lengths) if lengths else None,
                        'max_seconds': max(lengths) if lengths else None})
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seeds', type=int, default=20)
    args = parser.parse_args()
    if args.seeds <= 0:
        parser.error('--seeds must be positive')
    if len(AnimationTimeline.counts) < 16:
        parser.error('Animation assets are required to measure durations; see docs/ASSET_SETUP.md')
    print(json.dumps(simulate(args.seeds), ensure_ascii=False, indent=2))
