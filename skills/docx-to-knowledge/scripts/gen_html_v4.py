# -*- coding: utf-8 -*-
"""从扁平 JSON 生成优雅 HTML（章节级 HTML，图片内联）"""
import json, os, re

JSON = '/Users/fred/Documents/GitHub/cycleuser/GangDan/knowledge/drone_handbook_final.json'
for path in ['/Users/fred/Documents/GitHub/cycleuser/GangDan/knowledge/drone_handbook_full.json',
             JSON]:
    # copy final to full for gen_html compat
    with open(JSON, encoding='utf-8') as f:
        chapters = json.load(f)

# Symlink final -> full
import shutil
shutil.copy(JSON, '/Users/fred/Documents/GitHub/cycleuser/GangDan/knowledge/drone_handbook_full.json')

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# Build flat HTML: each chapter is a block
content_html = ''
for ch in chapters:
    content_html += f'<div class="chapter" id="ch{ch["id"]}"><h2>{esc(ch["title"])}</h2>\n'
    content_html += ch['html'] + '\n'
    content_html += '</div>\n'

# Build nav
nav_html = f'<h3>目录（{len(chapters)}章）</h3>\n'
section_count = 0
for ch in chapters:
    h3_count = ch['html'].count('<h3>')
    nav_html += f'<a href="#" data-target="ch{ch["id"]}" style="font-weight:600">{esc(ch["title"])} ({ch.get("images",h3_count)}图)</a>\n'
    # Extract h3 titles for sub-nav
    for m in re.finditer(r'<h3>(.*?)</h3>', ch['html']):
        sec_title = m.group(1).strip()
        sec_id = f's{ch["id"]}_{section_count}'
        nav_html += f'<a href="#" data-target="{sec_id}" style="padding-left:22px;font-size:12px">{esc(sec_title)}</a>\n'
        section_count += 1

# Add IDs to h3 elements in content
for ch in chapters:
    sc = [0]  # mutable counter
    def add_id(m):
        title = m.group(1)
        id_str = f's{ch["id"]}_{sc[0]}'
        sc[0] += 1
        return f'<h3 id="{id_str}">{title}</h3>'
    ch['html'] = re.sub(r'<h3>(.*?)</h3>', add_id, ch['html'])

KB = json.dumps(chapters, ensure_ascii=False)

# Write KB.js
kb_js = 'var DRONE_KB=' + KB + ';'
for p in ['/Users/fred/Documents/GitHub/cycleuser/blog/content/static/drone_kb.js',
          '/Users/fred/Documents/GitHub/cycleuser/GangDan/drone_kb.js']:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(kb_js)

# HTML template
html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>无人机驾驶员航空知识手册</title>
<style>
:root{{--bg:#fafbfc;--card:#fff;--text:#22262a;--muted:#6a737d;--border:#e4e8ec;--link:#1a6fc4;--accent:#f0f4ff;--hi:#fff3a1}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0d1117;--card:#151b24;--text:#c9d1d9;--muted:#8b949e;--border:#21262d;--link:#58a6ff;--accent:#162140;--hi:#5a4a00}}}}
*{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
body{{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;background:var(--bg);color:var(--text);font-size:15px;line-height:1.75;-webkit-text-size-adjust:none}}
.top{{position:sticky;top:0;z-index:100;background:var(--bg);border-bottom:1px solid var(--border);padding:8px 12px;display:flex;gap:8px;align-items:center;backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px)}}
.top input{{flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:20px;font-size:15px;background:var(--card);color:var(--text);outline:none;-webkit-appearance:none}}
.top input:focus{{border-color:var(--link)}}
.top .btn{{padding:8px 14px;border:1px solid var(--border);border-radius:20px;background:var(--card);color:var(--text);font-size:13px;cursor:pointer;white-space:nowrap}}
.top .btn:hover{{background:var(--accent);color:var(--link)}}
.nav{{position:fixed;top:58px;left:0;bottom:0;width:260px;border-right:1px solid var(--border);overflow-y:auto;background:var(--card);z-index:99;transition:transform .22s;padding:12px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.nav.hidden{{transform:translateX(-100%)}}
@media(max-width:700px){{.nav{{width:100%;max-width:280px}}}}
.nav h3{{font-size:14px;margin:12px 0 6px;color:var(--muted);border-bottom:1px solid var(--border);padding-bottom:4px}}
.nav a{{display:block;padding:5px 10px;font-size:13px;color:var(--text);text-decoration:none;border-radius:6px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.nav a:hover{{background:var(--accent);color:var(--link)}}
.content{{margin-left:260px;padding:20px 24px;max-width:900px}}
@media(max-width:700px){{.content{{margin-left:0;padding:12px 14px}}}}
.chapter{{margin-bottom:36px}}
.chapter h2{{font-size:1.35em;border-bottom:2px solid var(--link);padding-bottom:6px;margin:24px 0 16px;color:var(--link)}}
.chapter h3{{font-size:1.1em;margin:18px 0 10px;color:var(--text);border-bottom:1px solid var(--border);padding-bottom:4px}}
.chapter h4{{font-size:1em;font-weight:700;margin:12px 0 6px;color:var(--text)}}
.chapter p{{margin:6px 0}}
.chapter img{{max-width:100%;height:auto;display:block;margin:10px auto;border-radius:4px}}
.chapter .fig-cap{{text-align:center;font-size:13px;color:var(--muted);margin:4px 0 14px}}
.diagram-labels{{font-size:12px;color:var(--muted);background:var(--elev-1);border-radius:6px;padding:8px 14px;margin:8px 0;line-height:1.8}}
.res-card{{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px 18px;margin-bottom:14px;cursor:pointer}}
.res-card:hover{{border-color:var(--link)}}
.res-card h3{{font-size:1em;margin:0 0 6px;color:var(--text)}}
mark.hl{{background:var(--hi);border-radius:3px;padding:0 1px}}
.no-results{{text-align:center;padding:40px;color:var(--muted)}}
.res-count{{padding-bottom:8px;color:var(--muted);font-size:13px}}
.overlay{{position:fixed;inset:0;background:rgba(0,0,0,.35);z-index:98;display:none}}
.overlay.show{{display:block}}
@media(min-width:701px){{.overlay.show{{display:none}}}}
.content-hidden{{display:none}}
</style>
</head>
<body>
<div class="top"><button class="btn" onclick="toggleNav()">☰</button><input id="search" type="search" placeholder="搜索全文…" autocomplete="off" oninput="doSearch()"><button class="btn" onclick="clearSearch()">✕</button></div>
<div class="overlay" id="overlay" onclick="toggleNav()"></div>
<nav class="nav" id="nav">{nav_html}</nav>
<div class="content" id="content">{content_html}</div>
<script src="drone_kb.js"></script>
<script>
var DRONE_KB=DRONE_KB||[];
function toggleNav(){{document.getElementById('nav').classList.toggle('hidden');document.getElementById('overlay').classList.toggle('show')}}
function clearSearch(){{document.getElementById('search').value='';doSearch()}}
function escRe(s){{return s.replace(/[.*+?\^${{}}()|[\\\\]\\\\\\\\]/g,'\\\\\\\\$&')}}
function esc(s){{return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}}

function doSearch(){{
  var q=document.getElementById('search').value.trim();
  if(!q){{location.reload();return}}
  var results=[],ql=q.toLowerCase();
  DRONE_KB.forEach(function(ch){{
    var plain=ch.html.replace(/<[^>]+>/g,'').toLowerCase();
    var ci=plain.indexOf(ql);
    if(ci>=0)results.push({{ch:ch,ci:ci,plain:plain}})
  }});
  var ct=document.getElementById('content');
  if(!results.length){{ct.innerHTML='<div class="no-results">没有找到「'+esc(q)+'」</div>';return}}
  var o='<div class="res-count">找到 '+results.length+' 个结果</div>';
  results.forEach(function(r){{
    var ch=r.ch,pl=r.plain,ci=r.ci,s=Math.max(0,ci-40),e=Math.min(pl.length,ci+q.length+60);
    var ex=pl.slice(s,e);if(s>0)ex='\u2026'+ex;if(e<pl.length)ex+='\u2026';
    ex=ex.replace(new RegExp('('+escRe(q)+')','gi'),'<mark class="hl">$1</mark>');
    o+='<div class="res-card" onclick="navToChapter('+ch.id+')"><h3>'+esc(ch.title)+'</h3><div>'+ex+'</div></div>';
  }});
  ct.innerHTML=o;
}}
function navToChapter(id){{location.reload();setTimeout(function(){{var el=document.getElementById('ch'+id);if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});if(window.innerWidth<701)toggleNav()}},200)}}
document.getElementById('nav').addEventListener('click',function(ev){{
  var a=ev.target.closest('a');if(!a)return;ev.preventDefault();
  var id=a.getAttribute('data-target');if(!id)return;
  var el=document.getElementById(id);if(el)el.scrollIntoView({{behavior:'smooth',block:'start'}});if(window.innerWidth<701)toggleNav()
}});
</script>
</body>
</html>'''

for out in ['/Users/fred/Documents/GitHub/cycleuser/GangDan/drone_handbook.html',
            '/Users/fred/Documents/GitHub/cycleuser/blog/content/static/无人机知识手册.html']:
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

print(f"HTML: {os.path.getsize('/Users/fred/Documents/GitHub/cycleuser/GangDan/drone_handbook.html')/1024:.0f} KB")
print(f"Chapters: {len(chapters)}, Sections: {section_count}")
print(f"Total images: {sum(c.get('images',0) for c in chapters)}")
