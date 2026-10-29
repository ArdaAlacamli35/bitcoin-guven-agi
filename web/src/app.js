// Etkileşimli güven ağı: arama, düğüme tıklayınca detay paneli, topluluk filtresi, TR/EN.
import Graph from 'graphology';
import Sigma from 'sigma';

const T = {
  tr: {
    title: 'Bitcoin OTC güven ağı',
    sub: (n, e, t) => `${t.toLocaleString('tr-TR')} kullanıcıdan seçilen ${n} düğüm ve ${e} bağlantı. Turuncu çizgiler güvensizlik (negatif puan).`,
    search: 'Kullanıcı ara (ör. K1a2b3c)',
    community: 'Topluluk',
    all: 'Tüm topluluklar',
    negOnly: 'Yalnızca güvensizlik kenarlarını göster',
    reset: 'Görünümü sıfırla',
    pick: 'Ayrıntı görmek için bir düğüme tıklayın veya arayın.',
    notFound: 'Bu kimlikte gösterilen bir düğüm yok.',
    degree: 'Derece (verdiği + aldığı puan)',
    inPos: 'Aldığı güven puanı',
    inNeg: 'Aldığı güvensizlik puanı',
    negShare: 'Aldığı puanlarda negatif payı',
    pr: 'PageRank (×1000)',
    prPos: 'İtibar: pozitif ağda PageRank',
    prNeg: 'Toplanan güvensizlik: negatif ağda PageRank',
    members: 'üye',
    innerNeg: 'iç negatif oranı',
    conflict: 'Güvensizlik kümesi: negatif oranı rastlantıyla açıklanamayacak kadar yüksek',
    neighbors: (p, n) => `Gösterilen komşular: ${p} güven, ${n} güvensizlik bağlantısı`,
    filterNote: 'Filtre: derece ≥ 20 ya da güvensizlik kümesinde derece ≥ 8. Kimlikler anonimdir.',
    lang: 'English',
  },
  en: {
    title: 'Bitcoin OTC trust network',
    sub: (n, e, t) => `${n} nodes and ${e} links selected from ${t.toLocaleString('en-US')} users. Orange lines are distrust (negative ratings).`,
    search: 'Search user (e.g. K1a2b3c)',
    community: 'Community',
    all: 'All communities',
    negOnly: 'Show distrust edges only',
    reset: 'Reset view',
    pick: 'Click a node or search to see details.',
    notFound: 'No displayed node with this ID.',
    degree: 'Degree (ratings given + received)',
    inPos: 'Trust ratings received',
    inNeg: 'Distrust ratings received',
    negShare: 'Negative share of received ratings',
    pr: 'PageRank (×1000)',
    prPos: 'Reputation: PageRank on positive network',
    prNeg: 'Accumulated distrust: PageRank on negative network',
    members: 'members',
    innerNeg: 'internal negative share',
    conflict: 'Distrust cluster: negative share too high to be explained by chance',
    neighbors: (p, n) => `Displayed neighbours: ${p} trust, ${n} distrust links`,
    filterNote: 'Filter: degree ≥ 20, or degree ≥ 8 inside distrust clusters. IDs are anonymised.',
    lang: 'Türkçe',
  },
};
const NAME_EN = [
  ['Kurucu çekirdek', 'Founding core'], ['Ana pazar', 'Main market'], ['dalgası', 'wave'],
  ['Sessiz güven halkası', 'Quiet trust ring'], ['Toplu işaretleme kümesi', 'Mass-flagging cluster'],
  ['Karşılıklı −10 çatışma kümesi', 'Mutual −10 conflict cluster'], ['Erken dönem küçük halka', 'Early small ring'],
  ['Diğer küçük topluluklar', 'Other small communities'],
];

let lang = (() => { try { return localStorage.getItem('ag-dil') || 'tr'; } catch { return 'tr'; } })();
if (new URLSearchParams(location.search).get('lang') === 'en') lang = 'en';
const t = (k, ...a) => (typeof T[lang][k] === 'function' ? T[lang][k](...a) : T[lang][k]);
const cname = (s) => (lang === 'tr' ? s : NAME_EN.reduce((acc, [a, b]) => acc.replace(a, b), s));
const fmt = (n, d = 0) => Number(n).toLocaleString(lang === 'tr' ? 'tr-TR' : 'en-US', { maximumFractionDigits: d, minimumFractionDigits: d });
const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };

const data = await (await fetch('./ag.json')).json();
const comm = new Map(data.communities.map((c) => [c.id, c]));
const graph = new Graph({ type: 'undirected', multi: false });
data.nodes.forEach((n) => {
  graph.addNode(n.id, {
    x: n.x, y: n.y, size: 2 + Math.sqrt(n.d) * 0.55, color: comm.get(n.c)?.renk ?? '#5c6068', label: n.id, raw: n,
  });
});
data.edges.forEach(([a, b, s], i) => {
  graph.addEdgeWithKey(`e${i}`, data.nodes[a].id, data.nodes[b].id, {
    color: s > 0 ? 'rgba(127,142,163,0.16)' : 'rgba(255,122,26,0.55)', size: s > 0 ? 0.4 : 0.9, sign: s,
  });
});

const state = { selected: null, community: 'all', negOnly: false, hovered: null };
const renderer = new Sigma(graph, $('#ag'), {
  labelColor: { color: '#ededee' }, labelSize: 12, labelRenderedSizeThreshold: 9, defaultEdgeType: 'line',
  zIndex: true,
  nodeReducer(node, attr) {
    const r = { ...attr };
    const n = attr.raw;
    const inComm = state.community === 'all' || String(n.c) === state.community;
    if (!inComm) { r.color = '#2a2c31'; r.label = ''; r.zIndex = 0; }
    if (state.selected) {
      if (node === state.selected) { r.zIndex = 3; r.size = attr.size * 1.8; r.forceLabel = true; }
      else if (graph.hasEdge(node, state.selected)) { r.zIndex = 2; }
      else { r.color = '#2a2c31'; r.label = ''; r.zIndex = 0; }
    }
    return r;
  },
  edgeReducer(edge, attr) {
    const r = { ...attr };
    if (state.negOnly && attr.sign > 0) r.hidden = true;
    const [a, b] = graph.extremities(edge);
    if (state.community !== 'all') {
      const ca = String(graph.getNodeAttribute(a, 'raw').c), cb = String(graph.getNodeAttribute(b, 'raw').c);
      if (ca !== state.community && cb !== state.community) r.hidden = true;
    }
    if (state.selected && a !== state.selected && b !== state.selected) r.hidden = true;
    else if (state.selected) r.size = attr.size * 2;
    return r;
  },
});

function select(id) {
  state.selected = id;
  renderPanel();
  renderer.refresh();
  if (id) {
    const p = renderer.getNodeDisplayData(id);
    renderer.getCamera().animate({ x: p.x, y: p.y, ratio: 0.35 }, { duration: 500 });
  }
}

function renderPanel() {
  const box = $('#detay');
  box.replaceChildren();
  if (!state.selected) {
    if (state.community !== 'all') {
      const c = comm.get(Number(state.community));
      box.append(el('h2', null, cname(c.ad)));
      if (c.uye != null) {
        box.append(el('p', null, `${fmt(c.uye)} ${t('members')} · ${t('innerNeg')} %${fmt(c.ic_neg * 100, 1)} · z = ${fmt(c.neg_z, 1)}`));
        if (c.catisma) box.append(el('p', 'uyari', t('conflict')));
      }
    } else box.append(el('p', 'soluk', t('pick')));
    return;
  }
  const n = graph.getNodeAttribute(state.selected, 'raw');
  const c = comm.get(n.c);
  box.append(el('h2', 'mono', n.id));
  const chip = el('p', 'chip', cname(c.ad));
  chip.style.setProperty('--c', c.renk);
  box.append(chip);
  if (c.catisma) box.append(el('p', 'uyari', t('conflict')));
  const dl = el('dl');
  const negShare = n.gp + n.gn ? (n.gn / (n.gp + n.gn)) * 100 : 0;
  [[t('degree'), fmt(n.d)], [t('inPos'), fmt(n.gp)], [t('inNeg'), fmt(n.gn)], [t('negShare'), `%${fmt(negShare, 1)}`],
    [t('pr'), fmt(n.pr, 3)], [t('prPos'), fmt(n.prp, 3)], [t('prNeg'), fmt(n.prn, 3)]].forEach(([k, v]) => {
    dl.append(el('dt', null, k), el('dd', 'mono', v));
  });
  box.append(dl);
  let p = 0, q = 0;
  graph.forEachEdge(state.selected, (_, a) => (a.sign > 0 ? p++ : q++));
  box.append(el('p', 'soluk', t('neighbors', p, q)));
}

function applyLang() {
  document.documentElement.lang = lang;
  $('#baslik').textContent = t('title');
  $('#alt').textContent = t('sub', data.meta.gosterilen_dugum, data.meta.gosterilen_kenar, data.meta.toplam_dugum);
  $('#ara').placeholder = t('search');
  $('#ara-label').textContent = t('search');
  $('#topluluk-label').textContent = t('community');
  $('#neg-label').textContent = t('negOnly');
  $('#sifirla').textContent = t('reset');
  $('#dil').textContent = t('lang');
  $('#not').textContent = t('filterNote');
  const sel = $('#topluluk');
  const cur = sel.value || 'all';
  sel.replaceChildren(new Option(t('all'), 'all'), ...data.communities.map((c) => new Option(`T${c.id < 0 ? '–' : c.id} · ${cname(c.ad.replace(/^T\d+ · /, ''))}`, String(c.id))));
  sel.value = cur;
  const leg = $('#lejant');
  leg.replaceChildren(...data.communities.map((c) => {
    const b = el('button', 'leg', `T${c.id < 0 ? '–' : c.id}`);
    b.type = 'button';
    b.title = cname(c.ad);
    b.style.setProperty('--c', c.renk);
    b.setAttribute('aria-pressed', String(state.community === String(c.id)));
    b.addEventListener('click', () => { sel.value = state.community === String(c.id) ? 'all' : String(c.id); sel.dispatchEvent(new Event('change')); });
    return b;
  }));
  renderPanel();
}

renderer.on('clickNode', ({ node }) => select(node));
renderer.on('clickStage', () => select(null));
renderer.on('enterNode', () => { $('#ag').style.cursor = 'pointer'; });
renderer.on('leaveNode', () => { $('#ag').style.cursor = 'default'; });

const ids = data.nodes.map((n) => n.id);
const dl = $('#kimlikler');
ids.slice().sort((a, b) => graph.getNodeAttribute(b, 'raw').pr - graph.getNodeAttribute(a, 'raw').pr).slice(0, 200)
  .forEach((id) => dl.append(new Option(id)));
$('#ara-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const q = $('#ara').value.trim();
  const hit = ids.find((id) => id.toLowerCase() === q.toLowerCase()) ?? ids.find((id) => id.toLowerCase().startsWith(q.toLowerCase()));
  if (q && hit) { $('#durum').textContent = ''; select(hit); }
  else $('#durum').textContent = t('notFound');
});
$('#topluluk').addEventListener('change', (e) => {
  state.community = e.target.value;
  state.selected = null;
  applyLang();
  renderer.refresh();
});
$('#neg').addEventListener('change', (e) => { state.negOnly = e.target.checked; renderer.refresh(); });
$('#sifirla').addEventListener('click', () => {
  state.selected = null; state.community = 'all'; state.negOnly = false;
  $('#topluluk').value = 'all'; $('#neg').checked = false; $('#ara').value = '';
  applyLang(); renderer.refresh(); renderer.getCamera().animatedReset();
});
$('#dil').addEventListener('click', () => {
  lang = lang === 'tr' ? 'en' : 'tr';
  try { localStorage.setItem('ag-dil', lang); } catch { /* yok say */ }
  applyLang();
});
applyLang();
window.__ag = { select, graph };
