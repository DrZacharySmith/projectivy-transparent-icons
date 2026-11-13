const styleFilter = document.querySelector("#style-filter");
const search = document.querySelector('#search');
const clear = document.querySelector('#clear');
const count = document.querySelector('#count');
const empty = document.querySelector('#empty');
const viewport = document.querySelector('.viewport');
const cards = [...document.querySelectorAll('#icons li')];

function filterIcons() {
  const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
  let matches = 0;
  for (const card of cards) {
    const label = card.querySelector('span').textContent.toLowerCase();
    const matchesStyle = styleFilter.value === "all" || card.dataset.style === styleFilter.value;
    card.hidden = !matchesStyle || !terms.every(term => label.includes(term));
    if (!card.hidden) matches++;
  }
  count.textContent = terms.length || styleFilter.value !== "all"
    ? `${matches} of ${cards.length} icons`
    : `${cards.length} icons`;
  empty.hidden = matches > 0;
  clear.hidden = search.value.length === 0;
  viewport.scrollTop = 0;
}

styleFilter.addEventListener("change", filterIcons);
search.addEventListener('input', filterIcons);
clear.addEventListener('click', () => {
  search.value = '';
  filterIcons();
  search.focus();
});
filterIcons();

const zipButton = document.querySelector('#download-zip');
const selectionCount = document.querySelector('#selection-count');
const checkboxes = [...document.querySelectorAll('.icon-select input')];

function updateSelection() {
  const selected = checkboxes.filter(box => box.checked).length;
  selectionCount.textContent = `${selected} ${selected === 1 ? 'icon' : 'icons'} selected`;
  zipButton.disabled = selected === 0 || zipButton.hasAttribute("aria-busy");
}

for (const box of checkboxes) {
  box.addEventListener('change', updateSelection);
}
updateSelection();

zipButton.addEventListener('click', async () => {
  const selected = checkboxes.filter(box => box.checked);
  if (!selected.length) return;

  zipButton.disabled = true;
  zipButton.textContent = 'Preparing ZIP…';
  zipButton.setAttribute('aria-busy', 'true');

  try {
    const zip = new JSZip();

    for (const box of selected) {
      const card = box.closest('li');
      const link = card.querySelector('a.card');
      const response = await fetch(link.href);
      if (!response.ok) throw new Error(`Could not download ${link.download}`);

      const folder = card.dataset.style === 'steampunk' ? 'Steampunk' : 'Glossy Cartoon';
      zip.folder(folder).file(link.download, await response.arrayBuffer());
    }

    const blob = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(blob);
    const download = document.createElement('a');
    download.href = url;
    download.download = 'projectivy-selected-icons.zip';
    document.body.append(download);
    download.click();
    download.remove();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  } catch (error) {
    console.error(error);
    alert('Could not create the ZIP. Your selections are still checked. Please try again.');
  } finally {
    zipButton.removeAttribute('aria-busy');
    zipButton.textContent = 'Download selected ZIP';
    updateSelection();
  }
});
