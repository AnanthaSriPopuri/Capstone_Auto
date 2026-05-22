/* ═══════════════════════════════════════════════════════════
   powerbi.js  —  Power BI Dashboard Module
   All interactive charts for Capstone Studio
   Uses Chart.js loaded from CDN in index.html
═══════════════════════════════════════════════════════════ */

/* ── DATA ENGINE ─────────────────────────────────────────── */
let PBI = {
  sector: null,
  entities: [],
  rawData: {},        // { entityName: [{...}, ...] }
  charts: {},         // Chart.js instances
  activePage: 'overview',
  activeEntity: 0,
  daxResults: {},
};

const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const REGIONS = ['North','South','East','West','Central','Northeast'];
const STATUSES = ['ACTIVE','INACTIVE','PENDING','ERROR','ARCHIVED'];
const CATEGORIES = ['Premium','Standard','Basic','Enterprise','Pro','Lite'];

function randInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
function randF(a,b){ return +(Math.random()*(b-a)+a).toFixed(2); }
function rand(arr){ return arr[Math.floor(Math.random()*arr.length)]; }

/* ── GENERATE SYNTHETIC DATASET ──────────────────────────── */
function generatePBIData(sector, entities) {
  PBI.sector = sector;
  PBI.entities = entities;
  PBI.rawData = {};

  entities.forEach((entity, idx) => {
    const rows = [];
    const n = 120; // enough for charts

    // Monthly buckets
    const monthlyTotals = MONTHS.map(m => ({ month: m, value: 0, count: 0 }));
    const regionMap = {};
    const statusMap = {};
    const categoryMap = {};

    REGIONS.forEach(r => regionMap[r] = { total: 0, count: 0, avg: 0 });
    STATUSES.forEach(s => statusMap[s] = 0);
    CATEGORIES.forEach(c => categoryMap[c] = { total: 0, count: 0 });

    for (let i = 0; i < n; i++) {
      const month = MONTHS[i % 12];
      const region = rand(REGIONS);
      const status = rand(STATUSES);
      const category = rand(CATEGORIES);
      const value = randF(500, 50000);
      const score = randF(20, 100);

      monthlyTotals[i % 12].value += value;
      monthlyTotals[i % 12].count++;
      regionMap[region].total += value;
      regionMap[region].count++;
      statusMap[status]++;
      categoryMap[category].total += value;
      categoryMap[category].count++;

      rows.push({ id: i+1, month, region, status, category, value, score });
    }

    // Averages
    REGIONS.forEach(r => {
      if (regionMap[r].count > 0)
        regionMap[r].avg = +(regionMap[r].total / regionMap[r].count).toFixed(2);
    });
    CATEGORIES.forEach(c => {
      if (categoryMap[c].count > 0)
        categoryMap[c].avg = +(categoryMap[c].total / categoryMap[c].count).toFixed(2);
    });

    PBI.rawData[entity] = {
      rows,
      monthly: monthlyTotals,
      region: regionMap,
      status: statusMap,
      category: categoryMap,
    };
  });

  computeDAX();
}

/* ── DAX MEASURES COMPUTATION ────────────────────────────── */
function computeDAX() {
  const entity = PBI.entities[PBI.activeEntity];
  const d = PBI.rawData[entity];
  if (!d) return;

  const allValues = d.rows.map(r => r.value);
  const allScores = d.rows.map(r => r.score);
  const totalRecords = d.rows.length;
  const totalValue = allValues.reduce((a,b)=>a+b,0);
  const avgScore = allScores.reduce((a,b)=>a+b,0) / allScores.length;
  const activeCount = d.status['ACTIVE'] || 0;

  // Running total (monthly cumulative)
  let runningTotal = 0;
  const runningTotals = d.monthly.map(m => {
    runningTotal += m.value;
    return +runningTotal.toFixed(2);
  });

  // MoM growth % (last 2 months)
  const lastMonth = d.monthly[d.monthly.length-1].value || 1;
  const prevMonth = d.monthly[d.monthly.length-2].value || 1;
  const momGrowth = +((lastMonth - prevMonth) / prevMonth * 100).toFixed(1);

  // YTD Value (sum of all months)
  const ytdValue = d.monthly.reduce((a,m)=>a+m.value,0);

  // Rank by region
  const regionRanked = Object.entries(d.region)
    .sort((a,b) => b[1].total - a[1].total)
    .map(([r,v],i) => ({ region:r, total:v.total, rank:i+1 }));

  // Pct share by status
  const pctShare = {};
  STATUSES.forEach(s => {
    pctShare[s] = +((d.status[s]||0)/totalRecords*100).toFixed(1);
  });

  // Rolling 30d avg (last 3 months simulated)
  const last3 = d.monthly.slice(-3).reduce((a,m)=>a+m.value,0)/3;
  const rolling30d = +last3.toFixed(2);

  // KPI Status
  const kpiStatus = avgScore >= 80 ? 'EXCELLENT' : avgScore >= 60 ? 'GOOD' :
                    avgScore >= 40 ? 'AVERAGE' : 'NEEDS ATTENTION';

  // Top N (top 5 categories by value)
  const topN = Object.entries(d.category)
    .sort((a,b) => b[1].total - a[1].total)
    .slice(0,5)
    .map(([cat,v]) => ({ category:cat, total:v.total }));

  PBI.daxResults = {
    totalRecords,
    totalValue: +totalValue.toFixed(2),
    avgScore: +avgScore.toFixed(2),
    activeCount,
    runningTotals,
    momGrowth,
    ytdValue: +ytdValue.toFixed(2),
    regionRanked,
    pctShare,
    rolling30d,
    kpiStatus,
    topN,
  };

  updateKPICards();
}

/* ── SHOW POWER BI SECTION ───────────────────────────────── */
function showPowerBI(sector, entities) {
  generatePBIData(sector, entities);
  document.getElementById('pbi-section').style.display = 'block';
  document.getElementById('pbi-sector-label').textContent = sector;

  // Build entity tabs
  const tabs = document.getElementById('pbi-entity-tabs');
  tabs.innerHTML = entities.map((e,i) =>
    `<button class="pbi-entity-tab${i===0?' pbi-tab-active':''}"
      onclick="switchPBIEntity(${i})">${e}</button>`
  ).join('');

  switchPBIPage('overview');
  setTimeout(() => {
    document.getElementById('pbi-section').scrollIntoView({ behavior:'smooth', block:'start' });
  }, 200);
}

/* ── ENTITY SWITCH ───────────────────────────────────────── */
function switchPBIEntity(idx) {
  PBI.activeEntity = idx;
  document.querySelectorAll('.pbi-entity-tab').forEach((t,i) => {
    t.classList.toggle('pbi-tab-active', i === idx);
  });
  destroyAllCharts();
  computeDAX();
  switchPBIPage(PBI.activePage);
}

/* ── PAGE NAVIGATION ─────────────────────────────────────── */
function switchPBIPage(page) {
  PBI.activePage = page;
  document.querySelectorAll('.pbi-nav-btn').forEach(b => {
    b.classList.toggle('pbi-nav-active', b.dataset.page === page);
  });
  document.querySelectorAll('.pbi-page').forEach(p => {
    p.style.display = p.id === `pbi-page-${page}` ? 'block' : 'none';
  });
  destroyAllCharts();
  setTimeout(() => renderPage(page), 60);
}

function renderPage(page) {
  if (page === 'overview')    renderOverview();
  if (page === 'regional')    renderRegional();
  if (page === 'trends')      renderTrends();
  if (page === 'categories')  renderCategories();
  if (page === 'dax')         renderDAXPage();
}

/* ── CHART HELPERS ───────────────────────────────────────── */
function destroyAllCharts() {
  Object.values(PBI.charts).forEach(c => { try { c.destroy(); } catch(e){} });
  PBI.charts = {};
}

function isDark() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function getColors(n) {
  const palette = [
    '#3d8ef0','#9b71f5','#2dcc8f','#f0a840','#e85c6e',
    '#06b6d4','#a855f7','#10b981','#f97316','#ec4899'
  ];
  return Array.from({length:n}, (_,i) => palette[i % palette.length]);
}

function chartDefaults() {
  const dark = isDark();
  return {
    textColor: dark ? '#9ca3af' : '#6b7280',
    gridColor: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
    bgColor: dark ? '#1a2535' : '#ffffff',
  };
}

function makeChart(id, config) {
  const canvas = document.getElementById(id);
  if (!canvas) return null;
  if (PBI.charts[id]) { try { PBI.charts[id].destroy(); } catch(e){} }
  const ctx = canvas.getContext('2d');
  const chart = new Chart(ctx, config);
  PBI.charts[id] = chart;
  return chart;
}

/* ── KPI CARDS ───────────────────────────────────────────── */
function updateKPICards() {
  const d = PBI.daxResults;
  if (!d) return;

  const fmt = (n) => n >= 1000000 ? (n/1000000).toFixed(1)+'M' : n >= 1000 ? (n/1000).toFixed(1)+'K' : String(n);

  const cards = [
    { id:'kpi-total-records', label:'Total Records',  value: fmt(d.totalRecords),  sub:'All entities',           color:'#3d8ef0' },
    { id:'kpi-total-value',   label:'Total Value',    value: '$'+fmt(d.totalValue), sub:'Sum across period',      color:'#2dcc8f' },
    { id:'kpi-avg-score',     label:'Avg Score',      value: d.avgScore+'%',        sub:d.kpiStatus,              color:'#f0a840' },
    { id:'kpi-active',        label:'Active Records', value: fmt(d.activeCount),    sub: d.pctShare['ACTIVE']+'% of total', color:'#9b71f5' },
    { id:'kpi-ytd',           label:'YTD Value',      value: '$'+fmt(d.ytdValue),   sub:'Year to date',           color:'#e85c6e' },
    { id:'kpi-mom',           label:'MoM Growth',     value: (d.momGrowth>=0?'+':'')+d.momGrowth+'%', sub:'vs last month', color: d.momGrowth>=0 ? '#2dcc8f' : '#e85c6e' },
  ];

  const container = document.getElementById('pbi-kpi-cards');
  if (!container) return;
  container.innerHTML = cards.map(c => `
    <div class="pbi-kpi-card">
      <div class="pbi-kpi-label">${c.label}</div>
      <div class="pbi-kpi-value" style="color:${c.color}">${c.value}</div>
      <div class="pbi-kpi-sub">${c.sub}</div>
    </div>
  `).join('');
}

/* ══════════════════════════════════════════════════════════
   PAGE 1 — OVERVIEW
══════════════════════════════════════════════════════════ */
function renderOverview() {
  const entity = PBI.entities[PBI.activeEntity];
  const d = PBI.rawData[entity];
  const { textColor, gridColor } = chartDefaults();

  // Chart 1: Monthly revenue line
  makeChart('chart-monthly-line', {
    type: 'line',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'Monthly Value',
        data: d.monthly.map(m => +m.value.toFixed(0)),
        borderColor: '#3d8ef0',
        backgroundColor: 'rgba(61,142,240,0.08)',
        borderWidth: 2,
        pointBackgroundColor: '#3d8ef0',
        pointRadius: 4,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend:{ display:false }, tooltip:{ mode:'index' } },
      scales: {
        x: { ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } },
        y: { ticks:{ color:textColor, font:{size:11}, callback: v => '$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 2: Status donut
  const statusLabels = STATUSES;
  const statusValues = STATUSES.map(s => d.status[s]||0);
  makeChart('chart-status-donut', {
    type: 'doughnut',
    data: {
      labels: statusLabels,
      datasets: [{ data: statusValues, backgroundColor: getColors(5), borderWidth: 2, borderColor: isDark()?'#0d1117':'#ffffff' }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins: {
        legend:{ position:'right', labels:{ color:textColor, font:{size:11}, padding:10 } }
      },
      cutout: '62%'
    }
  });

  // Chart 3: Record count by month bar
  makeChart('chart-count-bar', {
    type: 'bar',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'Record Count',
        data: d.monthly.map(m => m.count),
        backgroundColor: getColors(12),
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 4: Running total area
  makeChart('chart-running-total', {
    type: 'line',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'Running Total',
        data: PBI.daxResults.runningTotals,
        borderColor: '#2dcc8f',
        backgroundColor: 'rgba(45,204,143,0.1)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.3,
        pointRadius: 3,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v => '$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });
}

/* ══════════════════════════════════════════════════════════
   PAGE 2 — REGIONAL ANALYSIS
══════════════════════════════════════════════════════════ */
function renderRegional() {
  const entity = PBI.entities[PBI.activeEntity];
  const d = PBI.rawData[entity];
  const { textColor, gridColor } = chartDefaults();
  const regions = REGIONS;
  const colors = getColors(6);

  // Chart 1: Region bar horizontal
  makeChart('chart-region-bar', {
    type: 'bar',
    data: {
      labels: regions,
      datasets: [{
        label: 'Total Value',
        data: regions.map(r => +d.region[r].total.toFixed(0)),
        backgroundColor: colors,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      indexAxis: 'y',
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11}, callback: v => '$'+v.toLocaleString() }, grid:{ color:gridColor } },
        y:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } }
      }
    }
  });

  // Chart 2: Avg score by region radar
  makeChart('chart-region-radar', {
    type: 'radar',
    data: {
      labels: regions,
      datasets: [{
        label: 'Avg Score',
        data: regions.map(r => d.region[r].avg ? +(d.region[r].avg/500).toFixed(1) : randF(20,90)),
        borderColor: '#9b71f5',
        backgroundColor: 'rgba(155,113,245,0.15)',
        borderWidth: 2,
        pointBackgroundColor: '#9b71f5',
        pointRadius: 4,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        r:{
          ticks:{ display:false },
          grid:{ color:gridColor },
          pointLabels:{ color:textColor, font:{size:11} }
        }
      }
    }
  });

  // Chart 3: Region polar area
  makeChart('chart-region-polar', {
    type: 'polarArea',
    data: {
      labels: regions,
      datasets: [{
        data: regions.map(r => d.region[r].count || 0),
        backgroundColor: colors.map(c => c+'aa'),
        borderColor: colors,
        borderWidth: 1.5,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ position:'right', labels:{ color:textColor, font:{size:11} } }
      },
      scales:{ r:{ ticks:{ display:false }, grid:{ color:gridColor } } }
    }
  });

  // Chart 4: Region grouped bar (value + count)
  makeChart('chart-region-grouped', {
    type: 'bar',
    data: {
      labels: regions,
      datasets: [
        {
          label: 'Total Value (÷1000)',
          data: regions.map(r => +(d.region[r].total/1000).toFixed(1)),
          backgroundColor: '#3d8ef0',
          borderRadius: 4,
        },
        {
          label: 'Record Count',
          data: regions.map(r => d.region[r].count || 0),
          backgroundColor: '#f0a840',
          borderRadius: 4,
        }
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ labels:{ color:textColor, font:{size:11} } } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } }
      }
    }
  });
}

/* ══════════════════════════════════════════════════════════
   PAGE 3 — TRENDS
══════════════════════════════════════════════════════════ */
function renderTrends() {
  const entity = PBI.entities[PBI.activeEntity];
  const d = PBI.rawData[entity];
  const { textColor, gridColor } = chartDefaults();

  // Chart 1: Multi-line (value + rolling avg)
  const rolling = d.monthly.map((m,i,arr) => {
    const slice = arr.slice(Math.max(0,i-2),i+1);
    return +(slice.reduce((a,x)=>a+x.value,0)/slice.length).toFixed(0);
  });

  makeChart('chart-trend-multi', {
    type: 'line',
    data: {
      labels: MONTHS,
      datasets: [
        {
          label: 'Monthly Value',
          data: d.monthly.map(m => +m.value.toFixed(0)),
          borderColor: '#3d8ef0',
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 3,
          tension: 0.3,
        },
        {
          label: 'Rolling 3-Month Avg',
          data: rolling,
          borderColor: '#f0a840',
          borderDash: [6,3],
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.4,
        }
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ labels:{ color:textColor, font:{size:11} } } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 2: MoM Growth waterfall (bar with positive/negative)
  const momData = MONTHS.map((m,i,arr) => {
    if (i===0) return 0;
    const prev = d.monthly[i-1].value || 1;
    return +((d.monthly[i].value - prev)/prev*100).toFixed(1);
  });

  makeChart('chart-mom-growth', {
    type: 'bar',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'MoM Growth %',
        data: momData,
        backgroundColor: momData.map(v => v>=0 ? '#2dcc8f' : '#e85c6e'),
        borderRadius: 4,
        borderSkipped: false,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v=>v+'%' }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 3: Cumulative area (YTD)
  makeChart('chart-ytd-area', {
    type: 'line',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'YTD Cumulative Value',
        data: PBI.daxResults.runningTotals,
        borderColor: '#9b71f5',
        backgroundColor: 'rgba(155,113,245,0.12)',
        fill:true,
        borderWidth:2.5,
        tension:0.3,
        pointRadius:3,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 4: Scatter (score vs value)
  const scatterData = d.rows.slice(0,80).map(r=>({ x:r.score, y:r.value }));
  makeChart('chart-scatter', {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Score vs Value',
        data: scatterData,
        backgroundColor: '#3d8ef055',
        borderColor: '#3d8ef0',
        borderWidth: 1,
        pointRadius: 4,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ title:{ display:true, text:'Score', color:textColor, font:{size:11} }, ticks:{ color:textColor, font:{size:11} }, grid:{ color:gridColor } },
        y:{ title:{ display:true, text:'Value ($)', color:textColor, font:{size:11} }, ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });
}

/* ══════════════════════════════════════════════════════════
   PAGE 4 — CATEGORIES
══════════════════════════════════════════════════════════ */
function renderCategories() {
  const entity = PBI.entities[PBI.activeEntity];
  const d = PBI.rawData[entity];
  const { textColor, gridColor } = chartDefaults();
  const cats = CATEGORIES;
  const colors = getColors(6);

  // Chart 1: Category bar
  makeChart('chart-cat-bar', {
    type: 'bar',
    data: {
      labels: cats,
      datasets: [{
        label: 'Total Value',
        data: cats.map(c => +d.category[c].total.toFixed(0)),
        backgroundColor: colors,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 2: Category pie
  makeChart('chart-cat-pie', {
    type: 'pie',
    data: {
      labels: cats,
      datasets: [{
        data: cats.map(c => d.category[c].count||0),
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: isDark()?'#0d1117':'#fff',
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:'right', labels:{ color:textColor, font:{size:11} } } }
    }
  });

  // Chart 3: Category avg score bar (simulated)
  makeChart('chart-cat-avg', {
    type: 'bar',
    data: {
      labels: cats,
      datasets: [{
        label: 'Avg Score',
        data: cats.map(() => randF(40,95)),
        backgroundColor: cats.map((_,i) => colors[i]+'bb'),
        borderColor: colors,
        borderWidth:1.5,
        borderRadius:4,
        borderSkipped:false,
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ min:0, max:100, ticks:{ color:textColor, font:{size:11}, callback: v=>v+'%' }, grid:{ color:gridColor } }
      }
    }
  });

  // Chart 4: Top N table (rendered as bar)
  const topN = PBI.daxResults.topN;
  makeChart('chart-topn', {
    type: 'bar',
    data: {
      labels: topN.map(t=>t.category),
      datasets: [{
        label: 'Top 5 by Value',
        data: topN.map(t=> +t.total.toFixed(0)),
        backgroundColor: ['#3d8ef0','#9b71f5','#2dcc8f','#f0a840','#e85c6e'],
        borderRadius:5,
        borderSkipped:false,
      }]
    },
    options: {
      indexAxis:'y',
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ display:false } },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } },
        y:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } }
      }
    }
  });
}

/* ══════════════════════════════════════════════════════════
   PAGE 5 — DAX MEASURES
══════════════════════════════════════════════════════════ */
function renderDAXPage() {
  const d = PBI.daxResults;
  const entity = PBI.entities[PBI.activeEntity];
  const { textColor, gridColor } = chartDefaults();

  // Show DAX table
  const tableBody = document.getElementById('dax-table-body');
  if (tableBody) {
    const fmt = n => typeof n === 'number' ? (n >= 1000 ? '$'+n.toLocaleString() : n) : n;
    const measures = [
      { name:'Total_Records',    formula:'COUNTROWS(\''+entity+'\')',         result: d.totalRecords.toLocaleString(),              type:'COUNT' },
      { name:'Total_Value',      formula:'SUM(\''+entity+'\'[value])',         result:'$'+d.totalValue.toLocaleString(),             type:'SUM' },
      { name:'Avg_Score',        formula:'AVERAGE(\''+entity+'\'[score])',     result:d.avgScore+'%',                                type:'AVG' },
      { name:'Active_Count',     formula:'CALCULATE([Total_Records],status="ACTIVE")', result:d.activeCount.toLocaleString(),        type:'FILTER' },
      { name:'YTD_Value',        formula:'TOTALYTD(SUM([value]),\'Calendar\'[Date])', result:'$'+d.ytdValue.toLocaleString(),        type:'TIME' },
      { name:'MoM_Growth_Pct',   formula:'DIVIDE([Cur]-[Prev],[Prev],0)',     result:(d.momGrowth>=0?'+':'')+d.momGrowth+'%',      type:'TIME' },
      { name:'Rolling_30d_Avg',  formula:'CALCULATE(AVERAGE([value]),DATESINPERIOD(...))', result:'$'+d.rolling30d.toLocaleString(), type:'TIME' },
      { name:'Rank_By_Region',   formula:'RANKX(ALL([region]),[Total_Records],,DESC)', result: d.regionRanked[0]?.region+' = #1',   type:'RANK' },
      { name:'Pct_Share_Active', formula:'DIVIDE([Active_Count],[Total_Records])',  result:d.pctShare['ACTIVE']+'%',               type:'RATIO' },
      { name:'KPI_Status',       formula:'SWITCH(TRUE(),[Avg_Score]>=80,"EXCELLENT",...)', result:d.kpiStatus,                      type:'SWITCH' },
    ];
    tableBody.innerHTML = measures.map(m => `
      <tr>
        <td><span class="dax-name">${m.name}</span></td>
        <td><code class="dax-formula">${m.formula}</code></td>
        <td><span class="dax-result">${m.result}</span></td>
        <td><span class="dax-type dax-type-${m.type.toLowerCase()}">${m.type}</span></td>
      </tr>
    `).join('');
  }

  // Chart: Pct share by status
  makeChart('chart-dax-pct', {
    type: 'doughnut',
    data: {
      labels: STATUSES,
      datasets: [{
        data: STATUSES.map(s => d.pctShare[s]||0),
        backgroundColor: getColors(5),
        borderWidth:2,
        borderColor: isDark()?'#0d1117':'#fff',
      }]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ position:'bottom', labels:{ color:textColor, font:{size:11}, padding:8 } },
        tooltip:{ callbacks:{ label: ctx => ctx.label+': '+ctx.parsed+'%' } }
      },
      cutout:'55%'
    }
  });

  // Chart: Region rank bar
  makeChart('chart-dax-rank', {
    type:'bar',
    data:{
      labels: d.regionRanked.map(r=>r.region),
      datasets:[{
        label:'Rank by Value',
        data: d.regionRanked.map(r=>+r.total.toFixed(0)),
        backgroundColor: d.regionRanked.map((_,i)=>getColors(6)[i]),
        borderRadius:4,
        borderSkipped:false,
      }]
    },
    options:{
      responsive:true, maintainAspectRatio:false,
      plugins:{
        legend:{ display:false },
        tooltip:{ callbacks:{ label: ctx=>'$'+ctx.parsed.y.toLocaleString()+' (Rank #'+(ctx.dataIndex+1)+')' } }
      },
      scales:{
        x:{ ticks:{ color:textColor, font:{size:11} }, grid:{ display:false } },
        y:{ ticks:{ color:textColor, font:{size:11}, callback: v=>'$'+v.toLocaleString() }, grid:{ color:gridColor } }
      }
    }
  });
}

/* ── EXPORT POWER QUERY STEPS ────────────────────────────── */
function exportPowerQuerySteps() {
  const entity = PBI.entities[PBI.activeEntity];
  const steps = `POWER QUERY — 15 Transformation Steps for ${entity}
Sector: ${PBI.sector}
Generated: ${new Date().toLocaleString()}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STEP 1:  Source — Connect to CSV/JSON/Excel file
STEP 2:  Promote Headers — Use first row as column names
STEP 3:  Remove Duplicates — Remove rows with duplicate IDs
STEP 4:  Filter Rows — Remove rows where status is null or empty
STEP 5:  Replace Values — Replace "N/A", "null", "--" with null
STEP 6:  Change Type — Cast amount/value columns to Decimal Number
STEP 7:  Change Type — Cast date columns to Date type
STEP 8:  Remove Errors — Remove rows with type-conversion errors
STEP 9:  Add Column — Add source_entity column with entity name
STEP 10: Trim — Remove leading/trailing whitespace from text columns
STEP 11: Capitalize Each Word — Normalize status field casing
STEP 12: Merge Queries — Left join with reference/lookup table
STEP 13: Expand Merged Column — Expand joined columns into flat table
STEP 14: Remove Columns — Drop staging columns not needed in model
STEP 15: Rename Columns — Apply business-friendly column names

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DAX MEASURES (10)

Total_Records   = COUNTROWS('${entity}')
Total_Value     = SUM('${entity}'[value])
Avg_Score       = AVERAGE('${entity}'[score])
Active_Count    = CALCULATE([Total_Records], '${entity}'[status]="ACTIVE")
YTD_Value       = TOTALYTD(SUM('${entity}'[value]),'Calendar'[Date])
MoM_Growth_Pct  = DIVIDE(
                    [Total_Records]
                      - CALCULATE([Total_Records], DATEADD('Calendar'[Date],-1,MONTH)),
                    CALCULATE([Total_Records], DATEADD('Calendar'[Date],-1,MONTH)), 0)
Rolling_30d_Avg = CALCULATE(AVERAGE('${entity}'[value]),
                    DATESINPERIOD('Calendar'[Date],LASTDATE('Calendar'[Date]),-30,DAY))
Rank_By_Region  = RANKX(ALL('${entity}'[region]),[Total_Records],,DESC,DENSE)
Pct_Share       = DIVIDE([Total_Records],
                    CALCULATE([Total_Records], ALL('${entity}')))
KPI_Status      = SWITCH(TRUE(),
                    [Avg_Score]>=80,"EXCELLENT",
                    [Avg_Score]>=60,"GOOD",
                    [Avg_Score]>=40,"AVERAGE","NEEDS ATTENTION")
`;
  const blob = new Blob([steps], {type:'text/plain;charset=utf-8'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `${PBI.sector}_PowerBI_Steps.txt`;
  a.click();
  URL.revokeObjectURL(a.href);
}