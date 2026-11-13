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
