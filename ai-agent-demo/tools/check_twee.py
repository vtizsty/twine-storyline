"""检查一个 Twee 故事（Harlowe 3）里的常见问题，对应第三讲的四类问题。
用法：python3 check_twee.py 故事.twee
检查：断链（跑不通）、死路（跑不通）、走不到的片段、全角符号写进代码、写了却从不读取的记录。
看不懂、对不上这两类要靠人玩，脚本查不出来。"""
import sys, re, json

def parse(text):
    ps = {}; order = []
    for block in re.split(r'^:: ', text, flags=re.M)[1:]:
        head, _, body = block.partition('\n')
        m = re.match(r'(.+?)(?:\s+\[(.*?)\])?(?:\s+\{.*\})?\s*$', head)
        name, tags = m.group(1).strip(), (m.group(2) or '').split()
        ps[name] = {'tags': tags, 'body': body}; order.append(name)
    return ps, order

def links(body):
    out = []
    for m in re.finditer(r'\[\[(.+?)\]\]', body):
        s = m.group(1)
        if '->' in s: out.append(s.split('->')[-1])
        elif '<-' in s: out.append(s.split('<-')[0])
        elif '|' in s: out.append(s.split('|')[-1])
        else: out.append(s)
    out += re.findall(r'\((?:link-goto|goto|click-goto):[^)]*?"([^"]+)"\s*\)', body)
    return [l.strip() for l in out]

def main(path):
    text = open(path, encoding='utf-8').read(); ps, order = parse(text)
    meta = {k: v for k, v in ps.items() if k in ('StoryTitle', 'StoryData')}
    story = {k: v for k, v in ps.items() if k not in meta}
    start = json.loads(ps['StoryData']['body']).get('start') if 'StoryData' in ps else order[0]
    problems = []
    # 1 断链
    for n, p in story.items():
        for l in links(p['body']):
            if l not in story: problems.append(('跑不通', f'“{n}”里的链接指向不存在的片段“{l}”'))
    # 2 死路
    for n, p in story.items():
        if 'startup' in p['tags']: continue
        b = p['body']
        if not links(b) and '(restart:' not in b and '(reload:' not in b:
            problems.append(('跑不通', f'“{n}”没有任何出口，也没有“重新开始”'))
    # 3 走不到
    seen, todo = set(), [start]
    while todo:
        n = todo.pop()
        if n in seen or n not in story: continue
        seen.add(n); todo += links(story[n]['body'])
    for n, p in story.items():
        if n not in seen and 'startup' not in p['tags']:
            problems.append(('走不到', f'从“{start}”出发走不到“{n}”'))
    # 4 全角符号写进代码
    for n, p in story.items():
        for line in p['body'].split('\n'):
            if re.search(r'（\s*[a-z-]+[:：]', line) or re.search(r'\([a-z-]+:[^()\[\]]*?[“”‘’]', line):
                problems.append(('全角符号', f'“{n}”：{line.strip()[:40]}'))
    # 5 写了却从不读取的记录
    allbody = '\n'.join(p['body'] for p in story.values())
    names = set(re.findall(r'\(set:\s*\$([\w]+)', allbody)) | set(re.findall(r'\(put:[^)]*into\s+\$([\w]+)', allbody))
    for v in sorted(names):
        reads = re.findall(r'\$' + v + r'\b', re.sub(r'\(set:\s*\$' + v + r"\b(?:'s\s+\w+)?\s+to", '(set: _ to', allbody))
        if not reads: problems.append(('闲置记录', f'记录 ${v} 写了，但没有任何地方读它'))
    print(f'检查：{path}')
    print(f'片段 {len(story)} 个，起点“{start}”，记录 {len(names)} 个：' + '、'.join('$' + v for v in sorted(names)))
    if not problems: print('通过：没有发现断链、死路、走不到的片段、全角符号或闲置记录。'); return 0
    for k, m in problems: print(f'【{k}】{m}')
    print(f'共 {len(problems)} 处问题。“看不懂”“对不上”还要请人来玩。'); return 1

if __name__ == '__main__':
    sys.exit(main(sys.argv[1]))
