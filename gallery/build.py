from html import escape, unescape
from pathlib import Path
import re
import shutil
import subprocess
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


def added_dates():
    # Walk the published branch history so merges use the date icons reached main.
    result = subprocess.run(
        ['git', 'log', '--first-parent', '--reverse',
         '--format=%x00COMMIT%x00%ct', '--name-status', '-z',
         '--find-renames=100%', '-l0'],
        cwd=ROOT, check=True, capture_output=True,
    )
    tokens = iter(result.stdout.decode('utf-8').split('\0'))
    dates = {}
    timestamp = 0
    for token in tokens:
        status = token.strip()
        if not status:
            continue
        if status == 'COMMIT':
            timestamp = int(next(tokens))
            continue
        path = next(tokens)
        if status.startswith('R'):
            destination = next(tokens)
            dates[destination] = dates.pop(path, timestamp)
        elif status == 'A' or status.startswith('C'):
            if status.startswith('C'):
                path = next(tokens)
            dates[path] = timestamp
        elif status == 'D':
            dates.pop(path, None)
    return dates


def main():
    glossy_readme = ROOT / 'styles/glossy-cartoon/README.md'
    collections = (
        ('Glossy Cartoon', ROOT / 'icons/styles/glossy-cartoon', glossy_readme if glossy_readme.exists() else ROOT / 'README.md'),
        ('Steampunk', ROOT / 'icons/styles/steampunk', ROOT / 'styles/steampunk/README.md'),
    )
    icons = []
    for style, folder, readme in collections:
        labels = display_names(readme)
        for path in folder.glob('*'):
            if path.is_file() and path.suffix.lower() == '.png' and not path.name.startswith('.'):
                suffix = r'(?:16x9|Glossy)' if style == 'Glossy Cartoon' else '16x9'
                name = re.sub(rf'\s*-\s*{suffix}$', '', path.stem, flags=re.I).strip()
                icons.append((labels.get(path.name, escape(name)), style, path))
    if not icons:
        raise SystemExit('No icon PNGs found.')
    icons.sort(key=lambda item: (item[0].casefold(), item[1], item[2].name))
    show_styles = len({style for _, style, _ in icons}) > 1
    OUTPUT.mkdir(exist_ok=True)
    if (OUTPUT / 'images').exists():
        shutil.rmtree(OUTPUT / 'images')
    dates = added_dates()
    cards = []
    for name, style, path in icons:
        relative = Path('images') / path.relative_to(ROOT)
        destination = OUTPUT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        url = quote(relative.as_posix(), safe='/')
        caption = f'{name}<small>{style}</small>' if show_styles else name
        filename = escape(path.name, quote=True)
        added = dates.get(path.relative_to(ROOT).as_posix(), 0)
        cards.append(f'<li data-style="{path.parent.name}" data-added="{added}"><a class="card" href="{url}" download="{filename}">'
                     f'<img src="{url}" alt="" loading="lazy"><span>{caption}</span>'
                     '<span class="download-label">Download PNG</span></a>'
                     '<div class="icon-actions">'
                     f'<label class="icon-select"><input type="checkbox" aria-label="Select {name} ({style})"> '
                     'Select</label>'
                     f'<button class="preview-button" type="button" '
                     f'aria-label="Preview {name} ({style})">Preview</button>'
                     '</div></li>')
    template = (SOURCE / 'index.html').read_text(encoding='utf-8')
    (OUTPUT / 'index.html').write_text(template.replace('{{COUNT}}', str(len(icons)))
                                       .replace('{{ICONS}}', '\n'.join(cards)), encoding='utf-8')
    for asset in ('gallery.css', 'gallery.js', 'jszip.min.js'):
        shutil.copyfile(SOURCE / asset, OUTPUT / asset)
    print(f'Built searchable gallery with {len(icons)} icons.')


if __name__ == '__main__':
    main()
