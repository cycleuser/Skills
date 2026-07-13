# -*- coding: utf-8 -*-
"""Refine knowledge base: merge image-label fragments into structured captions"""
import re, json

JSON = '/Users/fred/Documents/GitHub/cycleuser/GangDan/knowledge/drone_handbook_final.json'

with open(JSON, encoding='utf-8') as f:
    chapters = json.load(f)

def refine_html(html):
    """Smart rewrite: merge short <p> fragments after images into caption-lists"""
    result = []
    buffer = []  # accumulating short fragments
    in_caption_zone = False
    
    # Tokenize: split into paragraphs, images, figures, lists
    tokens = re.split(r'(<(?:p|img|figure|li|h4|div)[^>]*>.*?</(?:p|img|figure|li|h4|div)>)', html, flags=re.DOTALL)
    # Actually, regex split eats the delimiters. Let's use finditer instead.
    
    # Simpler approach: split on newline-before-<, process line by line
    lines = html.split('\n')
    out_lines = []
    label_buf = []  # short label texts to merge
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        # Skip empty
        if not line:
            out_lines.append(line)
            i += 1
            continue
        
        # If line is <img> or <figure>...
        is_img = '<img' in line or '<figure>' in line
        if is_img:
            # Look ahead: collect consecutive short <p> fragments
            label_buf = []
            j = i + 1
            while j < len(lines):
                nl = lines[j].strip()
                m = re.match(r'<p>(.*?)</p>', nl)
                if not m:
                    if not nl:
                        j += 1
                        continue
                    break
                text = m.group(1).strip()
                # A label fragment: short, no sentence structure (no 。)
                if len(text) < 25 and '。' not in text and '图' not in text and '表' not in text:
                    label_buf.append(text)
                    j += 1
                else:
                    break
            # Output
            if label_buf and len(label_buf) >= 3:
                # Replace with: image + caption-list
                out_lines.append(line)  # the img/figure
                cap_text = '  ·  '.join(label_buf)
                out_lines.append(f'<p class="img-legend" style="font-size:12px;color:var(--muted);text-align:center;margin:4px 0 10px;line-height:1.8">{cap_text}</p>')
                i = j
                continue
            else:
                out_lines.append(line)
                i += 1
                continue
        
        out_lines.append(line)
        i += 1
    
    return '\n'.join(out_lines)

# Apply to all sections
fixed_count = 0
for ch in chapters:
    for sec in ch['sections']:
        old = sec['html']
        new = refine_html(old)
        if old != new:
            sec['html'] = new
            fixed_count += 1

print(f"Fixed {fixed_count} sections with label-fragment merging")

# Also add CSS class for img-legend
# Save
with open(JSON, 'w', encoding='utf-8') as f:
    json.dump(chapters, f, ensure_ascii=False, indent=2)
print(f"Saved: {JSON}")

    # Verify a specific case
for ch in chapters:
    for sec in ch['sections']:
        if '图2.6' in sec['html'] or '2 . 6' in sec['html']:
            idx = sec['html'].find('2.6')
            if idx < 0: idx = sec['html'].find('2 . 6')
            print("\n=== 图2.6 area (refined) ===")
            print(sec['html'][max(0,idx-200):idx+400])
            break