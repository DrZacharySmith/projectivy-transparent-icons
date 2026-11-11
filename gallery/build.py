from html import escape, unescape
from pathlib import Path
import re
import shutil
from urllib.parse import quote, unquote


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'gallery'
OUTPUT = ROOT / '_gallery_site'


def display_names(readme):
    if not readme.exists():
        return {}
    return {
        Path(unquote(url.split('?')[0])).name: escape(unescape(label))
        for url, label in re.findall(
            r'<img\s+[^>]*src="([^"]+)"[^>]*alt="([^"]+)"',
            readme.read_text(encoding='utf-8'),
        )
    }


def main():
    glossy_readme = ROOT / 'styles/glossy-cartoon/README.md'
    collections = (
        ('Glossy Cartoon', ROOT / 'icons', glossy_readme if glossy_readme.exists() else ROOT / 'README.md'),
        ('Steampunk', ROOT / 'styles/steampunk/icons', ROOT / 'styles/steampunk/README.md'),
    )
    icons = []
    for style, folder, readme in collections:
        labels = display_names(readme)
        for path in folder.glob('*'):
            if path.is_file() and path.suffix.lower() == '.png' and not path.name.startswith('.'):
                name = re.sub(r'\s*-\s*16x9$', '', path.stem, flags=re.I).strip()
                icons.append((labels.get(path.name, escape(name)), style, path))
    if not icons:
        raise SystemExit('No icon PNGs found.')
    icons.sort(key=lambda item: (item[0].casefold(), item[1], item[2].name))
    show_styles = len({style for _, style, _ in icons}) > 1
    OUTPUT.mkdir(exist_ok=True)
    if (OUTPUT / 'images').exists():
        shutil.rmtree(OUTPUT / 'images')
    cards = []
    for name, style, path in icons:
        relative = Path('images') / path.relative_to(ROOT)
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        url = quote(relative.as_posix(), safe='/')
        caption = f'{name}<small>{style}</small>' if show_styles else name
        filename = escape(path.name, quote=True)
        cards.append(f'<li><a class="card" href="{url}" download="{filename}">'
                     f'<img src="{url}" alt="" loading="lazy"><span>{caption}</span>'
                     '<span class="download-label">Download PNG</span></a></li>')
    template = (SOURCE / 'index.html').read_text(encoding='utf-8')
    (OUTPUT / 'index.html').write_text(template.replace('{{COUNT}}', str(len(icons)))
                                       .replace('{{ICONS}}', '\n'.join(cards)), encoding='utf-8')
    for asset in ('gallery.css', 'gallery.js'):
        shutil.copyfile(SOURCE / asset, OUTPUT / asset)
    print(f'Built searchable gallery with {len(icons)} icons.')


if __name__ == '__main__':
    main()
