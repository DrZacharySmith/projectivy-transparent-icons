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
    const label = card.textContent.toLowerCase();
    card.hidden = !terms.every(term => label.includes(term));
    if (!card.hidden) matches++;
  }
  count.textContent = terms.length
    ? `${matches} of ${cards.length} icons`
    : `${cards.length} icons`;
  empty.hidden = matches > 0;
  clear.hidden = search.value.length === 0;
  viewport.scrollTop = 0;
}

search.addEventListener('input', filterIcons);
clear.addEventListener('click', () => {
  search.value = '';
  filterIcons();
  search.focus();
});
filterIcons();
