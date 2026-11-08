"""Read-only checks of presentation numbers against existing source reports.

This is an artifact/data-provenance check, not a new solver or optimality test.
Run from any directory using Python 3.10+ (standard library only).
"""
from pathlib import Path
from hashlib import sha256
import json
import re
import zipfile
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DECK = HERE.parent / 'RL_DESIGN_GROUP_MEETING_20261108.pptx'
NS = {'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def run():
    iterations = ROOT / 'essay/myEssay/tables/iterations.tex'
    formal = ROOT / 'essay/myEssay/tables/formal.tex'
    results = ROOT / 'RL/adaptive_v1/RESULTS.md'
    pp = []
    total = []
    for line in iterations.read_text(encoding='utf-8').splitlines():
        if re.match(r'\d+/\d+/\d+\s*&', line):
            pp.append(float(line.split('&')[5].strip()))
    for line in formal.read_text(encoding='utf-8').splitlines():
        if re.match(r'\d+/\d+/\d+\s*&', line):
            total.append(float(line.split('&')[7].strip().rstrip('\\')))
    records = {}
    for line in results.read_text(encoding='utf-8').splitlines():
        if line.startswith('|n'):
            x = [v.strip() for v in line.strip('|').split('|')]
            records[(x[0], x[1])] = {'gap': float(x[4]), 'seconds': float(x[5])}
    expected = [
        [pp],
        [[records[(case, policy)]['seconds'] for case in ['n80s32', 'n120tight32']]
         for policy in ['exact', 'fixed']],
        [[records[('n120tight34', policy)]['gap'] for policy in ['exact', 'fixed']]],
    ]
    charts = []
    with zipfile.ZipFile(DECK) as z:
        chart_parts = sorted((n for n in z.namelist() if re.search(r'/chart\d+\.xml$', n)),
                             key=lambda n: int(re.search(r'chart(\d+)\.xml$', n).group(1)))
        assert len(chart_parts) == 3
        for part, wanted in zip(chart_parts, expected):
            root = ET.fromstring(z.read(part))
            observed = [[float(v.text) for v in s.findall('.//c:val//c:pt/c:v', NS)]
                        for s in root.findall('.//c:ser', NS)]
            assert observed == wanted, (part, observed, wanted)
            charts.append({'part': part, 'values': observed, 'source_match': True})
        assert len([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]) == 20
        assert len([n for n in z.namelist() if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]) == 20
        manifest = json.loads((HERE / 'slide_manifest.json').read_text(encoding='utf-8'))
        for m in manifest:
            note = ET.fromstring(z.read(f"ppt/notesSlides/notesSlide{m['slide']}.xml"))
            text = ''.join(t.text or '' for t in note.findall('.//a:t', NS))
            assert m['notes'] in text, m['slide']

    report = {
        'scope': 'Presentation/source-report equality; no new solve, RL training, or optimality replay.',
        'pptx_sha256': digest(DECK), 'slides': 20, 'notes': 20,
        'chart_series_source_match': charts,
        'native_pp_fraction_from_displayed_tables': [a/b for a, b in zip(pp, total)],
        'sources': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p)
                    for p in [iterations, formal, results]},
        'status': 'PASS',
    }
    (HERE / 'SOURCE_CHECK.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    notes = ['# 组会逐页讲稿', '', '对应20页PPT；约18–20分钟。数字是历史实测，RL设计尚未训练。', '']
    for m in manifest:
        notes += [f"## {m['slide']:02d}｜{m['title']}", '', m['notes'], '']
    (HERE / 'SPEAKER_NOTES.md').write_text('\n'.join(notes).rstrip()+'\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'charts': 3, 'slides': 20, 'notes': 20,
                      'pptx_sha256': report['pptx_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    run()
