"""把 Twine 2 故事库 HTML（可含多个故事）转成 Twee 3 文本，每个故事一个 .twee 文件。
用法：python3 html2twee.py 输入.html 输出文件夹"""
import sys, re, json, html, pathlib

def convert(src, outdir):
    t = pathlib.Path(src).read_text(encoding='utf-8'); out = []
    for sd in re.finditer(r'<tw-storydata(.*?)>(.*?)</tw-storydata>', t, re.S):
        attrs = dict(re.findall(r'([\w-]+)="([^"]*)"', sd.group(1)))
        body = sd.group(2); pids = {}
        passages = []
        for p in re.finditer(r'<tw-passagedata(.*?)>(.*?)</tw-passagedata>', body, re.S):
            a = dict(re.findall(r'([\w-]+)="([^"]*)"', p.group(1)))
            pids[a['pid']] = html.unescape(a['name'])
            passages.append((html.unescape(a['name']), a.get('tags', ''), a.get('position', ''), html.unescape(p.group(2))))
        name = html.unescape(attrs['name'])
        data = {'ifid': attrs.get('ifid'), 'format': attrs.get('format'), 'format-version': attrs.get('format-version'),
                'start': pids.get(attrs.get('startnode'))}
        lines = [':: StoryTitle', name, '', ':: StoryData', json.dumps(data, ensure_ascii=False, indent=2), '']
        for n, tags, pos, txt in passages:
            head = f':: {n}' + (f' [{tags}]' if tags else '') + (f' {{"position":"{pos}","size":"100,100"}}' if pos else '')
            lines += [head, txt.rstrip(), '']
        f = pathlib.Path(outdir) / f'{name}.twee'
        f.write_text('\n'.join(lines), encoding='utf-8'); out.append(f)
    return out

if __name__ == '__main__':
    for f in convert(sys.argv[1], sys.argv[2]): print('写出', f)
