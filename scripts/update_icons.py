from pathlib import Path
from urllib.parse import quote, unquote
import hashlib, html, math, re
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / 'icons/styles/glossy-cartoon'
README = ROOT / 'README.md'
PROOF = ROOT / 'Projectivy-Icons-Proof-Sheet.png'
text = README.read_text(encoding='utf-8')
# Retain existing friendly names, including alternate versions.
labels = {}
for src, label in re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]+)"', text):
    labels[Path(unquote(src.split('?')[0])).name] = html.unescape(label)
files = [p for p in ICON_DIR.iterdir() if p.is_file() and p.suffix.lower() == '.png' and not p.name.startswith('.')]
if not files:
    raise SystemExit('No PNG icons found; refusing to replace gallery.')
def name(p):
    return labels.get(p.name) or re.sub(r'\s*-\s*16x9$', '', p.stem, flags=re.I).strip()
files.sort(key=lambda p: (name(p).casefold(), p.name.casefold()))
count = len(files)
# Validate all inputs before writing outputs.
for p in files:
    with Image.open(p) as im:
        im.verify()
def url(p):
    return 'icons/styles/glossy-cartoon/' + quote(p.name, safe='')
def version(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:12]
gallery = """## Gallery

[Browse and search all icons →](https://drzacharysmith.github.io/projectivy-transparent-icons/)

| Glossy Cartoon | Steampunk |
| :---: | :---: |
| <img src="icons/styles/glossy-cartoon/TiviMate-16x9.png" width="140" alt="TiviMate"> | <img src="icons/styles/steampunk/TiviMate-Metal.png" width="140" alt="TiviMate Steampunk"> |
| <img src="icons/styles/glossy-cartoon/Stremio-16x9.png" width="140" alt="Stremio"> | <img src="icons/styles/steampunk/Stremio-Metal.png" width="140" alt="Stremio Steampunk"> |
| <img src="icons/styles/glossy-cartoon/TiviDeck-16x9.png" width="140" alt="TiviDeck"> | <img src="icons/styles/steampunk/TiviDeck-Metal.png" width="140" alt="TiviDeck Steampunk"> |

"""
pattern = r'^## Gallery\s*\n.*?(?=^## |\Z)'
text, replaced = re.subn(pattern, lambda _: gallery, text, count=1, flags=re.M|re.S)
if replaced != 1:
    raise SystemExit('README must contain a ## Gallery section.')
text = re.sub(r'\*\*\d+ transparent PNG icons\*\*', f'**{count} transparent PNG icons**', text)
# Deterministic six-column proof sheet. Original PNGs are never modified.
W=2400; margin=72; gap=24; cols=6; cw=(W-2*margin-(cols-1)*gap)//cols; ch=260; top=230
rows=math.ceil(count/cols); H=top+rows*ch+(rows-1)*gap+110
sheet=Image.new('RGB',(W,H),'#0e1420'); d=ImageDraw.Draw(sheet)
def font(size, bold=False):
    f=Path('/usr/share/fonts/truetype/dejavu')/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')
    return ImageFont.truetype(str(f),size) if f.exists() else ImageFont.load_default(size=size)
d.text((margin,60),'PROJECTIVY',font=font(62,True),fill='white')
d.text((margin,140),f'TRANSPARENT ICONS  /  PROOF SHEET  /  {count} ICONS',font=font(27),fill='#a8b9d0')
for i,p in enumerate(files):
    x=margin+i%cols*(cw+gap); y=top+i//cols*(ch+gap)
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=18,fill='#1a2433',outline='#2a394c',width=2)
    with Image.open(p) as source:
        icon=source.convert('RGBA'); icon.thumbnail((cw-36,ch-65),Image.Resampling.LANCZOS)
        sheet.paste(icon,(x+(cw-icon.width)//2,y+15+(ch-65-icon.height)//2),icon)
    label=name(p); size=21
    while d.textbbox((0,0),label,font=font(size,True))[2]>cw-20 and size>12:
        size-=1
    d.text((x+cw/2,y+ch-38),label,font=font(size,True),fill='#edf3fc',anchor='mt')
d.text((margin,H-66),'AI-generated artwork • Unofficial app icons • Names and logos belong to their respective owners',font=font(23),fill='#a8b9d0')
sheet.save(PROOF,optimize=True)
proof_url = f'https://raw.githubusercontent.com/DrZacharySmith/projectivy-transparent-icons/main/Projectivy-Icons-Proof-Sheet.png?v={version(PROOF)}'
text = re.sub(
    r'!\[Projectivy Transparent Icons\]\([^)]*\)',
    lambda _: f'![Projectivy Transparent Icons]({proof_url})',
    text,
)
README.write_text(text, encoding='utf-8')
print(f'Updated {count} icons, gallery, count, and proof sheet.')
