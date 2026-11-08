"""Freeze only this presentation delivery and the source files read for it."""
from pathlib import Path
from hashlib import sha256
import json

here = Path(__file__).resolve().parent
repo = here.parents[2]
files = [here.parent / 'RL_DESIGN_GROUP_MEETING_20261108.pptx',
         here.parent / 'RL_DESIGN_NOTES_ZH.md', here.parent / 'README.md']
files += [p for p in here.iterdir() if p.is_file() and p.name != 'SHA256.json']
files += list((here / 'final_previews').glob('*.png'))
sources = [
    'essay/myEssay/tables/formal.tex', 'essay/myEssay/tables/iterations.tex',
    'RL/adaptive_v1/SUMMARY.md', 'RL/adaptive_v1/RESULTS.md',
    'RL/adaptive_v1/LIMITATIONS.md', 'RL/adaptive_v1/DESIGN.md',
    'RL/adaptive_v1/online.py', 'RL/reuse_v1/SUMMARY.md',
    'sub/stage9/balanced_bound.py', 'sub/stage9/cg_balanced.py',
    'sub/stage9/demand_balanced.py', 'sub/agDetail/ALGORITHM_DESIGN_ZH.md',
    'sub/agDetail/evidence_summary.json',
]


def entries(paths):
    return {p.relative_to(repo).as_posix(): sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(paths))}


manifest = {'scope': '2026-11-08 RL design presentation; no solver/training modifications',
            'git_read_baseline': 'fb2b971d', 'deliverables': entries(files),
            'read_only_sources': entries([repo / f for f in sources])}
(here / 'SHA256.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'deliverables': len(manifest['deliverables']),
                  'read_only_sources': len(manifest['read_only_sources'])}))
