#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把线上机会卡全量导出成静态快照，供没有后端的静态托管（Cloudflare Pages）使用。

产物：
  frontend/data/cards-index.json   全量清单（轻字段，供清单页与图书馆列表）
  frontend/data/cards/<id>.json    每张卡的完整详情（供详情弹层）
  frontend/data/today.json         今日卡（含完整详情）
  frontend/data/sources.json       信号源列表（供信号带）

用法：python3 scripts/build_cards_snapshot.py [API_BASE]
默认 API_BASE = http://150.158.136.55
"""
import json, os, sys, time, urllib.request, urllib.error

API = (sys.argv[1] if len(sys.argv) > 1 else 'http://150.158.136.55').rstrip('/')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'frontend', 'data')
DETAIL_DIR = os.path.join(OUT, 'cards')


def get(path, timeout=30):
    req = urllib.request.Request(API + path, headers={'User-Agent': 'lingling-snapshot/1.0'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = r.read()
    try:
        return json.loads(body)
    except Exception:
        raise RuntimeError('返回的不是 JSON（前 80 字节）：%r' % body[:80])


def main():
    os.makedirs(DETAIL_DIR, exist_ok=True)

    # 1) 全量清单
    cards, page, total = [], 1, None
    while True:
        d = get('/api/cards?page=%d&page_size=100' % page)
        total = d.get('total', 0)
        got = d.get('cards', [])
        cards.extend(got)
        if not got or len(cards) >= total:
            break
        page += 1
    if not cards:
        raise RuntimeError('清单为空，拒绝覆盖快照')

    index = {
        'updated_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
        'total': len(cards),
        'cards': cards,
    }
    with open(os.path.join(OUT, 'cards-index.json'), 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    # 2) 每张卡的完整详情
    ok, fail = 0, []
    for c in cards:
        cid = c.get('id')
        if cid is None:
            continue
        try:
            det = get('/api/cards/%s' % cid)
            with open(os.path.join(DETAIL_DIR, '%s.json' % cid), 'w', encoding='utf-8') as f:
                json.dump(det, f, ensure_ascii=False, separators=(',', ':'))
            ok += 1
        except Exception as e:
            fail.append((cid, str(e)))
        if ok % 50 == 0 and ok:
            print('  …已导出 %d 张详情' % ok, flush=True)

    # 3) 今日卡
    today = {}
    try:
        t = get('/api/cards/today')
        tcards = t.get('cards', t if isinstance(t, list) else [])
        full = []
        for c in tcards:
            cid = c.get('id')
            p = os.path.join(DETAIL_DIR, '%s.json' % cid)
            full.append(json.load(open(p, encoding='utf-8')) if os.path.exists(p) else c)
        today = {'updated_at': index['updated_at'], 'date': time.strftime('%Y-%m-%d'), 'cards': full}
    except Exception as e:
        print('  ⚠ 今日卡导出失败:', e)
    with open(os.path.join(OUT, 'today.json'), 'w', encoding='utf-8') as f:
        json.dump(today, f, ensure_ascii=False, separators=(',', ':'))

    # 4) 信号源
    try:
        src = get('/api/sources?limit=50')
        if isinstance(src, list):
            src = {'items': src}
        src['updated_at'] = index['updated_at']
        with open(os.path.join(OUT, 'sources.json'), 'w', encoding='utf-8') as f:
            json.dump(src, f, ensure_ascii=False, separators=(',', ':'))
    except Exception as e:
        print('  ⚠ 信号源导出失败:', e)

    size_idx = os.path.getsize(os.path.join(OUT, 'cards-index.json'))
    size_det = sum(os.path.getsize(os.path.join(DETAIL_DIR, f)) for f in os.listdir(DETAIL_DIR))
    size_all = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.endswith('.json'))
    print('快照完成：%s' % OUT)
    print('  清单 %d 张（%.1f KB）｜ 详情 %d 张（%.1f KB）｜ 顶层文件合计 %.1f KB'
          % (len(cards), size_idx / 1024, ok, size_det / 1024, size_all / 1024))
    print('  日期跨度: %s → %s' % (min(c['created_at'] for c in cards), max(c['created_at'] for c in cards)))
    if fail:
        print('  ⚠ 详情失败 %d 张：%s' % (len(fail), fail[:5]))
    print('  更新时间: %s' % index['updated_at'])


if __name__ == '__main__':
    main()
