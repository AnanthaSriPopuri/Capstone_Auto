/* ═══════════════════════════════════════════════════════════
   CapstoneStudio — app.js  Professional Edition
   Auth · Sector · Demo data · Upload · LLM trigger · Download
═══════════════════════════════════════════════════════════ */

/* ── AUTH ────────────────────────────────────────────────── */
const USERS = { admin:'admin123', student:'capstone2024' };

/* ── SECTORS (40) ────────────────────────────────────────── */
const SECTORS = [
  ['Healthcare','🏥','Core Industries'],
  ['Finance & Banking','🏦','Core Industries'],
  ['Education & EdTech','🎓','Core Industries'],
  ['Retail & E-Commerce','🛍️','Core Industries'],
  ['Manufacturing','🏭','Core Industries'],
  ['Transportation & Logistics','🚚','Core Industries'],
  ['Energy & Utilities','⚡','Core Industries'],
  ['Telecom','📡','Core Industries'],
  ['Government & Public Services','🏛️','Public Sector'],
  ['Agriculture','🌾','Public Sector'],
  ['Real Estate','🏘️','Public Sector'],
  ['Insurance','🛡️','Public Sector'],
  ['Travel & Hospitality','✈️','Lifestyle'],
  ['Food & Beverage','🍽️','Lifestyle'],
  ['Sports & Fitness','⚽','Lifestyle'],
  ['Food Delivery & Online Ordering','🍕','Lifestyle'],
  ['Media & Entertainment','🎬','Technology'],
  ['Cybersecurity','🔐','Technology'],
  ['IoT & Smart Devices','📱','Technology'],
  ['Social Media & Analytics','📊','Technology'],
  ['Gaming & Esports','🎮','Technology'],
  ['Music & Streaming','🎵','Technology'],
  ['Digital Marketing','📣','Technology'],
  ['Space Research & Satellites','🛸','Science'],
  ['Healthcare Research & Genomics','🧬','Science'],
  ['Weather & Climate Analytics','🌦️','Science'],
  ['Environmental & Sustainability','🌱','Science'],
  ['Pharmaceuticals','💊','Science'],
  ['Automotive','🚗','Engineering'],
  ['Aviation & Aerospace','🛩️','Engineering'],
  ['Mining & Natural Resources','⛏️','Engineering'],
  ['Construction & Infrastructure','🏗️','Engineering'],
  ['Legal & Compliance','⚖️','Professional'],
  ['Human Resources','👥','Professional'],
  ['Supply Chain & Procurement','📦','Professional'],
  ['Event Management & Ticketing','🎫','Professional'],
  ['Charity & Non-Profit','❤️','Social'],
  ['Education Research','📚','Social'],
  ['Cyber Risk Intelligence','🕵️','Social'],
  ['Waste Management & Recycling','♻️','Social'],
];

const ENTITY_MAP = {
  'Healthcare':['Patients','Admissions','Medical_Staff','Billing_Records'],
  'Finance & Banking':['Customers','Transactions','Loan_Accounts','Branch_Operations'],
  'Education & EdTech':['Students','Courses','Faculty','Enrollment_Records'],
  'Retail & E-Commerce':['Products','Orders','Customers','Inventory'],
  'Manufacturing':['Products','Production_Batches','Suppliers','Quality_Checks'],
  'Transportation & Logistics':['Shipments','Vehicles','Drivers','Routes'],
  'Energy & Utilities':['Meters','Consumption_Records','Grid_Assets','Maintenance_Logs'],
  'Telecom':['Subscribers','Call_Records','Network_Nodes','Service_Plans'],
  'Government & Public Services':['Citizens','Service_Requests','Departments','Budget_Allocations'],
  'Agriculture':['Farms','Crop_Yields','Farmers','Weather_Stations'],
  'Insurance':['Policyholders','Claims','Agents','Premium_Records'],
  'Travel & Hospitality':['Guests','Bookings','Properties','Reviews'],
  'Food & Beverage':['Products','Suppliers','Sales_Transactions','Inventory'],
  'Automotive':['Vehicles','Customers','Service_Records','Dealers'],
  'Cybersecurity':['Incidents','Assets','Users','Threat_Logs'],
  'Gaming & Esports':['Players','Matches','Tournaments','Leaderboards'],
  'Pharmaceuticals':['Drugs','Clinical_Trials','Patients','Regulatory_Records'],
  'Real Estate':['Properties','Agents','Transactions','Listings'],
  'Legal & Compliance':['Cases','Clients','Attorneys','Court_Records'],
  'Human Resources':['Employees','Departments','Payroll','Performance_Reviews'],
};

const FORMATS   = ['csv','json','xlsx','xml'];
const FMT_ICONS = ['📊','📋','📗','🔷'];
const FMT_CLS   = ['fmt-csv','fmt-json','fmt-xlsx','fmt-xml'];

const NON_INDIAN_NAMES = [
  'Marcus Ellsworth','Claire Henderson','Thomas Ridley','Sofia Marchetti',
  'James Whitfield','Emma Larsson','Oliver Brentwood','Laura Fischer',
  'Nathan Calloway','Grace Hartman','Leo Fitzgerald','Anna Svensson',
  'Daniel Forsythe','Victoria Pemberton','Sebastian Mercer','Alice Thornton',
  'William Caldwell','Charlotte Sinclair','Henry Fletcher','Isabelle Moreau',
];
const COMPANIES = [
  'NorthBridge Solutions','Apex DataWorks','Vantage Analytics Group',
  'Meridian Tech Partners','Crestline Digital','Summit DataOps',
  'Horizon Infosystems','Pinnacle Analytics','Redwood Data Labs',
  'Cascade Intelligence','Overture Systems','Broadfield Consulting',
];

/* ── STATE ───────────────────────────────────────────────── */
let currentUser  = null;
let sector       = null;
let emoji        = '';
let sourceMode   = 'demo';
let charLimit    = 8000;
let complexity   = 'medium';
let currentPrompt= '';
let currentReq   = '';
let currentSol   = '';
let generating   = false;
let uploadedFiles= {};
let demoCache    = {};
let progressTimer= null;
let progressStep = 0;

/* ── HELPERS ─────────────────────────────────────────────── */
const $ = id => document.getElementById(id);
function rand(a)    { return a[Math.floor(Math.random()*a.length)]; }
function randInt(a,b){ return Math.floor(Math.random()*(b-a+1))+a; }
function randF(a,b)  { return +(Math.random()*(b-a)+a).toFixed(2); }
function esc(t)      { return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function getEntities(s){ return ENTITY_MAP[s]||['Entity_A','Entity_B','Entity_C','Entity_D']; }
function shuffle(a)  { const b=[...a]; for(let i=b.length-1;i>0;i--){const j=randInt(0,i);[b[i],b[j]]=[b[j],b[i]];} return b; }

/* ── AUTH ────────────────────────────────────────────────── */
function doLogin(){
  const u=$('login-user').value.trim();
  const p=$('login-pass').value;
  const err=$('login-error');
  if(USERS[u]&&USERS[u]===p){
    currentUser=u;
    err.classList.remove('show');
    $('login-screen').classList.remove('active');
    $('app-screen').classList.add('active');
    $('user-label').textContent=u;
    buildSectorList();
  } else {
    err.classList.add('show');
    $('login-pass').value='';
  }
}

function doLogout(){
  currentUser=null; sector=null;
  $('app-screen').classList.remove('active');
  $('login-screen').classList.add('active');
  $('login-user').value='';
  $('login-pass').value='';
}

document.addEventListener('keydown',e=>{
  if(e.key==='Enter'&&$('login-screen').classList.contains('active')) doLogin();
});

/* ── SECTOR LIST ─────────────────────────────────────────── */
function buildSectorList(filter=''){
  const nav=$('sector-list');
  nav.innerHTML='';
  const cats={};
  SECTORS.forEach(([name,em,cat])=>{
    if(filter&&!name.toLowerCase().includes(filter.toLowerCase())) return;
    (cats[cat]=cats[cat]||[]).push([name,em]);
  });
  Object.entries(cats).forEach(([cat,items])=>{
    const lbl=document.createElement('div');
    lbl.className='cat-label'; lbl.textContent=cat;
    nav.appendChild(lbl);
    items.forEach(([name,em])=>{
      const el=document.createElement('div');
      el.className='sector-item'+(sector===name?' active':'');
      el.innerHTML=`<span class="sector-emoji">${em}</span><span>${name}</span>`;
      el.onclick=()=>selectSector(name,em);
      nav.appendChild(el);
    });
  });
}

function filterSectors(){ buildSectorList($('sector-search').value); }

function selectSector(name,em){
  sector=name; emoji=em;
  uploadedFiles={}; demoCache={};
  buildSectorList($('sector-search').value);

  const entities=getEntities(name);

  // Topbar
  $('topbar-sector-info').style.display='flex';
  $('topbar-sector-pill').textContent=`${em} ${name}`;

  // Entity strip
  const strip=$('entity-strip');
  strip.style.display='flex';
  $('entity-chips').innerHTML=entities.map((e,i)=>`
    <div class="e-chip">
      <div class="e-dot" style="background:${['#3d8ef0','#9b71f5','#2dcc8f','#f0a840'][i]}"></div>
      ${e} <span class="e-fmt">.${FORMATS[i]}</span>
    </div>`).join('');

  // Show workflow cards
  $('empty-state').style.display='none';
  ['card-source','card-api','card-prompt','card-gen'].forEach(id=>{
    $(id).style.display='block';
    $(id).classList.add('fadein');
  });

  // Reset downstream state
  $('card-download').style.display='none';
  $('gen-progress').style.display='none';
  $('prompt-result').style.display='none';
  $('btn-gen-prompt').disabled=false;
  $('btn-run').disabled=true;
  $('snum-prompt').className='step-num s-active';
  $('snum-gen').className='step-num';
  $('badge-prompt').textContent='';
  $('badge-gen').textContent='';
  currentPrompt='';

  if(sourceMode==='demo') buildDemoGrid();
  else buildUploadGrid();

  toast('info',`${em} ${name} selected`);
}

/* ── SOURCE MODE ─────────────────────────────────────────── */
function setSourceMode(mode){
  sourceMode=mode;
  $('tab-demo').classList.toggle('active',mode==='demo');
  $('tab-upload').classList.toggle('active',mode==='upload');
  $('panel-demo').style.display   =mode==='demo'?'block':'none';
  $('panel-upload').style.display =mode==='upload'?'block':'none';
  if(sector){ mode==='demo'?buildDemoGrid():buildUploadGrid(); }
  $('badge-source').textContent=mode==='demo'?'Random data':'Upload files';
  toast('info',mode==='demo'?'Demo mode — synthetic data generated':'Upload mode — add your data files');
}

/* ── DEMO DATA ───────────────────────────────────────────── */
const STATUSES=['ACTIVE','INACTIVE','PENDING','ERROR','ARCHIVED'];
const REGIONS =['North','South','East','West','Central','Northeast'];
const CATS    =['Premium','Standard','Basic','Enterprise','Pro','Lite'];
const PRIS    =['LOW','MED','HIGH'];
const EVTS    =['STATUS_CHANGE','UPDATE','DELETE','CREATE','AUDIT','ALERT'];
const SEVE    =['LOW','MED','HIGH','CRITICAL'];

function rName(){ return rand(NON_INDIAN_NAMES); }

function genCSV(name,n=25){
  const hdr='id,name,status,created_date,region,score,is_active';
  const nullAt=shuffle([...Array(n).keys()]).slice(0,4);
  const rows=[hdr];
  for(let i=0;i<n;i++){
    const bad=nullAt.includes(i);
    const dt=`2024-${String(randInt(1,12)).padStart(2,'0')}-${String(randInt(1,28)).padStart(2,'0')}`;
    rows.push([
      1000+i,
      bad&&i%4===0?'':rName(),
      bad&&i%4===1?'null':rand(STATUSES),
      bad&&i%4===2?'2099-99-99':dt,
      rand(REGIONS),
      bad&&i%4===3?'N/A':randF(0,100),
      Math.random()>0.3?'true':'false',
    ].join(','));
  }
  return rows.join('\n');
}

function genJSON(name,n=25){
  const nullAt=shuffle([...Array(n).keys()]).slice(0,4);
  return JSON.stringify([...Array(n)].map((_,i)=>{
    const bad=nullAt.includes(i);
    return{
      record_id:5000+i,
      entity_ref:1000+randInt(0,n-1),
      category:bad?null:rand(CATS),
      value:bad?'':randF(100,50000),
      last_updated:`2024-${String(randInt(1,12)).padStart(2,'0')}-${String(randInt(1,28)).padStart(2,'0')}T${String(randInt(0,23)).padStart(2,'0')}:00:00`,
      notes:Math.random()>0.6?'Sample note':'',
    };
  }),null,2);
}

function genXLSX(name,n=25){
  const hdr='seq_id,description,assigned_to,priority,completion_pct';
  const nullAt=shuffle([...Array(n).keys()]).slice(0,4);
  return [hdr,...[...Array(n)].map((_,i)=>{
    const bad=nullAt.includes(i);
    return[200+i,`"Task ${i+1}: ${rand(['Review','Update','Analyse','Validate'])} ${name}"`,
      bad?'':rName(), bad?'':rand(PRIS), bad?'N/A':randF(0,100)].join(',');
  })].join('\n');
}

function genXML(name,n=25){
  const nullAt=shuffle([...Array(n).keys()]).slice(0,4);
  let xml=`<?xml version="1.0" encoding="UTF-8"?>\n<records>\n`;
  for(let i=0;i<n;i++){
    const bad=nullAt.includes(i);
    const ts=`2024-${String(randInt(1,12)).padStart(2,'0')}-${String(randInt(1,28)).padStart(2,'0')} ${String(randInt(0,23)).padStart(2,'0')}:${String(randInt(0,59)).padStart(2,'0')}:00`;
    xml+=`  <record>\n    <log_id>${9000+i}</log_id>\n    <source_ref>${1000+randInt(0,n-1)}</source_ref>\n    <event_type>${bad?'':rand(EVTS)}</event_type>\n    <timestamp>${ts}</timestamp>\n    <severity>${bad?'':rand(SEVE)}</severity>\n  </record>\n`;
  }
  return xml+'</records>';
}

const GEN_FNS=[genCSV,genJSON,genXLSX,genXML];

function buildDemoGrid(){
  if(!sector) return;
  const entities=getEntities(sector);
  demoCache={};
  const grid=$('demo-grid');
  grid.style.display='grid';
  grid.innerHTML=entities.map((e,i)=>{
    const content=GEN_FNS[i](e);
    const ext=i===3?'xml':FORMATS[i]==='xlsx'?'csv':FORMATS[i];
    demoCache[e]={content,ext};
    const safeName=e.toLowerCase().replace(/_/g,'-');
    const preview=content.split('\n').slice(0,3).join('\n');
    const recs=content.split('\n').length-1;
    return `<div class="demo-card fadein">
      <div class="demo-card-head">
        <span class="demo-card-icon">${FMT_ICONS[i]}</span>
        <span class="demo-card-name">${safeName}.${ext}</span>
        <span class="fmt-tag ${FMT_CLS[i]}">${FORMATS[i].toUpperCase()}</span>
      </div>
      <div class="demo-card-meta">~${recs} sample records · ${content.length.toLocaleString()} chars</div>
      <div class="demo-preview">${esc(preview)}</div>
      <button class="btn-dl-demo" onclick="downloadDemoFile('${e}')">⬇ Download ${ext.toUpperCase()}</button>
    </div>`;
  }).join('');
}

function downloadDemoFile(entityName){
  const d=demoCache[entityName];
  if(!d){toast('error','Generate demo files first');return;}
  const safeName=entityName.toLowerCase().replace(/_/g,'-');
  const blob=new Blob([d.content],{type:'text/plain;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=`${safeName}_sample.${d.ext}`;
  a.click(); URL.revokeObjectURL(a.href);
  toast('success',`⬇ ${safeName}_sample.${d.ext}`);
}

/* ── UPLOAD GRID ─────────────────────────────────────────── */
function buildUploadGrid(){
  if(!sector) return;
  const entities=getEntities(sector);
  $('upload-grid').innerHTML=entities.map((e,i)=>{
    const accept=i===0?'.csv':i===1?'.json':i===2?'.xlsx,.xls,.csv':'.xml,.csv';
    return `<div class="upload-slot" id="slot-${e}">
      <div class="upload-slot-head">
        <div class="e-dot" style="background:${['#3d8ef0','#9b71f5','#2dcc8f','#f0a840'][i]};width:7px;height:7px;border-radius:50%;"></div>
        <span class="upload-slot-entity">${e}</span>
        <span class="fmt-tag ${FMT_CLS[i]}">${FORMATS[i].toUpperCase()}</span>
      </div>
      <div class="upload-drop" onclick="$('fi-${e}').click()">
        <input type="file" id="fi-${e}" accept="${accept}" onchange="handleUpload('${e}',this)"/>
        📁 Browse or drop · accepts ${accept}
      </div>
      <div class="upload-file-info" id="uinfo-${e}">
        <span class="upload-fname" id="ufname-${e}"></span>
        <button class="btn-rm" onclick="removeUpload('${e}')">✕</button>
      </div>
    </div>`;
  }).join('');
}

function handleUpload(entityName,input){
  const file=input.files[0]; if(!file) return;
  uploadedFiles[entityName]=file;
  $(`slot-${entityName}`).classList.add('has-file');
  $(`ufname-${entityName}`).textContent=file.name;
  toast('success',`✓ ${file.name} uploaded`);
}

function removeUpload(entityName){
  delete uploadedFiles[entityName];
  $(`slot-${entityName}`).classList.remove('has-file');
  const inp=$(`fi-${entityName}`); if(inp) inp.value='';
  toast('info',`Removed file for ${entityName}`);
}

/* ── API KEY TOGGLE ──────────────────────────────────────── */
function toggleApiVis(){
  const inp=$('api-key-input');
  const show=inp.type==='password';
  inp.type=show?'text':'password';
  $('api-toggle-btn').textContent=show?'Hide':'Show';
}

/* ── CHAR LIMIT ──────────────────────────────────────────── */
function setCharLimit(n,el){
  charLimit=n;
  document.querySelectorAll('.pill-btn').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  if(currentPrompt) buildAndShowPrompt();
}

/* ── COMPLEXITY ──────────────────────────────────────────── */
function setCX(level,el){
  complexity=level;
  document.querySelectorAll('.cx-card').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  if(currentPrompt) buildAndShowPrompt();
}

/* ── COMPLEXITY CONFIG ───────────────────────────────────── */
const CX={
  easy:{
    label:'Easy', cls:'pill-easy', icon:'🟢',
    desc:'Basic CRUD, simple queries, single-file scripts.',
    modifier:`
COMPLEXITY DIRECTIVE: EASY
Generate ONLY introductory-level stories:
• Simple SELECT/INSERT/UPDATE/DELETE — no subqueries or joins
• Single-file Python scripts with basic read/write
• Bash scripts under 15 lines doing one task
• MongoDB: insertOne, findOne, simple find() — no aggregation
• PySpark: load CSV, show schema, basic filter only
• Power BI: simple bar/pie charts, 2-3 DAX measures (COUNT, SUM, AVERAGE)
Label every story: [EASY]
`,
  },
  medium:{
    label:'Medium', cls:'pill-medium', icon:'🟡',
    desc:'Joins, window functions, PySpark cleaning, DAX.',
    modifier:`
COMPLEXITY DIRECTIVE: MEDIUM
Standard capstone level:
• SQL: 2-3 table JOINs, GROUP BY, HAVING, subqueries
• Stored procedures with parameters and error handling
• PySpark: groupBy, agg, window functions
• MongoDB: $group, $match, $sort, $lookup pipeline
• Power BI: 5-8 DAX measures including CALCULATE, RANKX, DATEADD
Label every story: [MEDIUM]
`,
  },
  hard:{
    label:'Hard', cls:'pill-hard', icon:'🔴',
    desc:'CTEs, ML pipelines, complex aggregations, RLS.',
    modifier:`
COMPLEXITY DIRECTIVE: HARD
Advanced production-grade:
• SQL: Recursive CTEs, PIVOT, dynamic SQL, window functions (NTILE, CUME_DIST)
• PySpark: ML pipelines, broadcast joins, UDFs, partitioned writes
• MongoDB: $facet, $graphLookup, $merge, Atlas Search
• Python: async processing, schema validation, concurrent.futures
• Power BI: row-level security, calculation groups, composite models
Label every story: [HARD]
`,
  },
  mixed:{
    label:'Mixed', cls:'pill-mixed', icon:'🔵',
    desc:'Progressive Easy → Medium → Hard.',
    modifier:`
COMPLEXITY DIRECTIVE: MIXED
Progressive difficulty curve:
• Unix: first 5 [EASY], next 5 [MEDIUM], last 5 [HARD]
• Shell: first 3 [EASY], next 4 [MEDIUM], last 3 [HARD]
• Python: US-PY-01/02 [EASY], US-PY-03/04 [MEDIUM], US-PY-05 [HARD]
• MongoDB: US-MG-01/02 [EASY], US-MG-03–07 [MEDIUM], US-MG-08–11 [HARD]
• SQL: first 8 [MEDIUM], last 7 [HARD]
Label every story with its level.
`,
  },
};

/* ── PROMPT BUILDER ──────────────────────────────────────── */
function buildPrompt(s,entities,limit){
  const cx=CX[complexity];
  const [e0,e1,e2,e3]=entities;
  const company=rand(COMPANIES);
  const names=shuffle(NON_INDIAN_NAMES).slice(0,3);
  const now=new Date().toISOString().slice(0,16).replace('T',' ');

  const header=
`=== CAPSTONE PROJECT REQUIREMENT GENERATOR ===
Sector   : ${s}
Company  : ${company}
Generated: ${now}
CharLimit: ${limit.toLocaleString()}
Complexity: ${cx.label.toUpperCase()} ${cx.icon}

BUSINESS CONTEXT
${company} is a mid-sized technology consulting firm engaged with a leading
${s} organisation to modernise their fragmented data infrastructure.
Stakeholders: ${names[0]} (Chief Data Officer), ${names[1]} (VP Operations),
${names[2]} (Lead Data Engineer). Project spans 6 Agile sprints.

${cx.desc}

ENTITIES & FORMATS
1. ${e0.padEnd(32)} → CSV
2. ${e1.padEnd(32)} → JSON
3. ${e2.padEnd(32)} → Excel (.xlsx)
4. ${e3.padEnd(32)} → XML / Parquet

DATA SPECIFICATIONS
• Each dataset: 80,000 – 1,00,000 records
• Each dataset: 15–20 intentional inconsistencies
• All person names: non-Indian (Western / European only)
• No real registered company or organisation names
${cx.modifier}
`;

  const sections=[
`━━━ DATA INGESTION AND SHELL SCRIPTING ━━━
US-ING-01: As a data engineer, I want to ingest data from CSV, JSON, and Excel
  so that data from different sources can be unified into a single pipeline.
US-ING-02: As a system administrator, I want to automate ingestion using Unix
  shell scripting so that pipelines run without manual intervention.
US-ING-03: As a DevOps engineer, I want to schedule shell scripts via cron
  so that the system processes new data at defined intervals automatically.
US-ING-04: As a data architect, I want to store ingested data in a staging
  layer with source_file and load_timestamp so that raw records are auditable.
US-ING-05: As a developer, I want to validate file structure during ingestion
  using awk and grep so that malformed files are rejected before processing.

`,
`━━━ UNIX COMMANDS — 15 Story-Based Requirements ━━━
US-UNX-01: As a data analyst, I want to use grep -iE to extract rows from
  ${e0.toLowerCase()}.csv where status is ERROR or PENDING so that problematic
  records are isolated before ETL runs.
US-UNX-02: As a data engineer, I want to use awk to compute average score per
  region from ${e0.toLowerCase()}.csv so that regional KPIs are produced
  without loading data into any database.
US-UNX-03: As a system admin, I want to use sed to replace N/A, null, and --
  with 0 in ${e1.toLowerCase()}.txt so that downstream processes do not fail.
US-UNX-04: As a reporting analyst, I want to chain grep|cut|sort|uniq -c|sort -rn
  on ${e2.toLowerCase()}.csv so that top 20 category values are ranked.
US-UNX-05: As a DevOps engineer, I want to use find -mtime -7 with xargs to
  build daily manifest.txt of recently changed files for the backup script.
US-UNX-06: As a data steward, I want wc -l on all 4 entity files with tee
  so that counts go to console and to size_report.txt simultaneously.
US-UNX-07: As a data engineer, I want diff on ${e0.toLowerCase()}_v1.csv and
  ${e0.toLowerCase()}_v2.csv so that records changed between runs are flagged.
US-UNX-08: As a pipeline engineer, I want cat with awk to emit a schema report
  from all 4 files so that schema drift is detected before transformation.
US-UNX-09: As a data analyst, I want awk '{print $NF}' piped to sort|uniq -c
  on ${e1.toLowerCase()}.txt so that field cardinality is documented.
US-UNX-10: As a QA engineer, I want grep -c and awk to compute null density
  as a percentage per entity file so that a quality gate can be applied.
US-UNX-11: As a systems engineer, I want find -size +10M to list large files
  and redirect to large_files.txt so that storage alerts are triggered.
US-UNX-12: As a data analyst, I want cut -d',' -f1,3,6 piped to sort -k3 -rn
  on ${e0.toLowerCase()}.csv so that top-scoring records are extracted.
US-UNX-13: As a DevOps engineer, I want tr '[:upper:]' '[:lower:]' piped to
  sed to normalise category strings in ${e1.toLowerCase()}.txt to lowercase.
US-UNX-14: As a pipeline engineer, I want tail -n +2 on all 4 files piped
  through awk to prepend a source_entity column to combined_raw.csv.
US-UNX-15: As a DevOps engineer, I want xargs -P 4 to run grep in parallel
  across all 4 entity files to complete inconsistency detection in <30 seconds.

`,
`━━━ SHELL SCRIPTING — 10 Story-Based Requirements (8 analysis · 2 cleaning) ━━━
US-SH-01: As a data steward, I want a bash script iterating all 4 entity files
  counting total, null, and duplicate rows, writing audit_report.txt daily.
US-SH-02: As an operations analyst, I want a bash script reading ${e1.toLowerCase()}.txt
  computing sum/avg/max of value per category as an ASCII KPI table.
US-SH-03: As a data engineer, I want a bash script flagging rows where score is
  outside 0–100 in ${e0.toLowerCase()}.csv, writing them to anomalies.csv.
US-SH-04: As a pipeline engineer, I want a bash script merging all 4 entity files
  into combined_dataset.csv with a prepended source_entity column.
US-SH-05: As a reporting analyst, I want a bash script generating a daily HTML
  summary of record counts, top 5 categories, and null percentages.
US-SH-06: As a data engineer, I want a bash script accepting a date argument
  filtering ${e0.toLowerCase()}.csv by created_date to dated_extract_YYYYMMDD.csv.
US-SH-07: As a QA analyst, I want a bash script comparing raw vs cleaned file
  row counts, outputting records_removed and pct_cleaned per entity.
US-SH-08: As a pipeline engineer, I want a bash script monitoring landing
  directory with inotifywait, triggering ingestion on new file arrival.
US-SH-09: As a data engineer, I want a bash script removing empty mandatory
  rows from ${e0.toLowerCase()}.csv using awk, logging removed count. [CLEANING]
US-SH-10: As a DevOps engineer, I want a bash script using sed to fix delimiter
  inconsistencies in ${e2.toLowerCase()}.csv, normalising to commas. [CLEANING]

`,
`━━━ FILE HANDLING USING PYTHON ━━━
US-PY-01: As a Python developer, I want to read and write ${e0.toLowerCase()}.csv
  for deduplication using csv and io libraries.
  INPUT: data/${e0.toLowerCase()}.csv  OUTPUT: data/${e0.toLowerCase()}_clean.csv
US-PY-02: As a data engineer, I want to process ${e1.toLowerCase()}.json (80k–1L
  records) using json and pandas, saving to ${e1.toLowerCase()}_flat.csv.
US-PY-03: As a QA tester, I want to handle missing/corrupted ${e2.toLowerCase()}.xlsx
  using try-except so the pipeline logs errors rather than crashing.
US-PY-04: As a developer, I want to generate cleaned files for all 3 datasets
  in CSV, JSON, XLSX formats for downstream PySpark and SQL modules.
US-PY-05: As a data engineer, I want a Python script that randomly selects a
  sector at runtime, reads its dataset, applies cleaning rules, and generates
  sector-specific user stories producing unique non-repeating requirements.

`,
`━━━ DATA CLEANING USING PYSPARK — 6 Requirements ━━━
US-PS-01: As a data quality analyst, I want PySpark to identify null, missing,
  and duplicate values across all 4 entities before analysis begins.
US-PS-02: As a data engineer, I want to standardise inconsistent date, text, and
  numerical formats in ${e0.toLowerCase()} using PySpark DataFrame transformations.
US-PS-03: As a compliance analyst, I want to detect and resolve 10–15
  inconsistencies per dataset using PySpark for accurate reporting.
US-PS-04: As a data engineer, I want to apply business-rule transformations
  (normalise status enums, cap out-of-range scores, forward-fill sparse cols)
  using PySpark DataFrames so downstream SQL operates on validated data.
US-PS-05: As a data analyst, I want cleaned DataFrames validated with row-count
  and null-count assertions before writing to the cleansed layer.
US-PS-06: As a data engineer, I want to verify that the cleansed ${e0.toLowerCase()}
  DataFrame can generate valid MySQL INSERT statements via a PySpark UDF.

`,
`━━━ MONGODB CRUD — 11 Story-Based Requirements ━━━
US-MG-01: insertMany + compound index on status+region for ${e0.toLowerCase()}.
US-MG-02: find + projection + sort on ${e1.toLowerCase()} to minimise payload.
US-MG-03: updateMany setting status='ARCHIVED' on ${e0.toLowerCase()} records >2 years.
US-MG-04: deleteMany on low-severity ${e3.toLowerCase()} entries older than 3 years.
US-MG-05: $group/$sort/$project on ${e1.toLowerCase()} — sum/avg/count per category.
US-MG-06: $lookup joining ${e0.toLowerCase()} with ${e1.toLowerCase()}, writing combined_view.
US-MG-07: $unwind on ${e3.toLowerCase()} details array, $group for distinct event sub-types.
US-MG-08: $facet producing 3 sub-aggregations in a single pipeline round-trip.
US-MG-09: Group ${e0.toLowerCase()} by name+region where count>1 → review_duplicates.
US-MG-10: TTL index on ${e3.toLowerCase()} timestamp auto-deleting docs >180 days.
US-MG-11: $lookup+$unwind+$replaceRoot to flatten ${e2.toLowerCase()} nested references.

`,
`━━━ PYSPARK ANALYSIS — 15 Requirements (RDD · SQL · DataFrame) ━━━
[RDD]
US-RDD-01: Load ${e0.toLowerCase()}.csv as RDD, filter nulls, map to valid tuples.
US-RDD-02: RDD reduceByKey counting records by status in ${e0.toLowerCase()}.
US-RDD-03: RDD mapPartitions for per-partition statistics on ${e1.toLowerCase()}.
US-RDD-04: Union multiple entity RDDs, groupByKey for cross-entity analysis.
US-RDD-05: RDD aggregateByKey on ${e1.toLowerCase()} for weighted averages.
[PYSPARK SQL]
US-SQL-01: Multi-table JOIN via Spark SQL — avg score, total value, event count by region.
US-SQL-02: RANK() and LAG() partitioned by region on ${e0.toLowerCase()} for MoM trends.
US-SQL-03: GROUP BY ROLLUP on ${e1.toLowerCase()} for subtotal + grand-total aggregations.
US-SQL-04: CASE WHEN in Spark SQL classifying ${e0.toLowerCase()} into score buckets.
US-SQL-05: CTE expressions joining all 4 entity views for cross-entity insights.
[DATAFRAME]
US-DF-01: Join ${e0.toLowerCase()} with ${e1.toLowerCase()} using window functions, write Parquet.
US-DF-02: withColumn/cast/fillna/dropDuplicates on ${e2.toLowerCase()} for clean schema.
US-DF-03: groupBy and agg for multiple KPIs on ${e1.toLowerCase()} in a single pass.
US-DF-04: unionByName all 4 entity DataFrames with source_entity column.
US-DF-05: Write summarised Parquet partitions for Power BI and SQL consumption.

`,
`━━━ ADVANCED SQL — 15 Stored Procedures & Functions ━━━
US-ASQL-01: sp_GetRegionalSummary(p_region) — 3-table JOIN, avg score, active count.
US-ASQL-02: fn_CalculateRiskScore(p_id) — weighted composite from 3 entity tables.
US-ASQL-03: sp_MonthlyKPIReport(p_year,p_month) — RANK(), LAG(), LEAD() across entities.
US-ASQL-04: sp_CleanDuplicates(p_table) — CTE + ROW_NUMBER() PARTITION BY name,region.
US-ASQL-05: fn_GetStatusLabel(p_score) — CASE returning EXCELLENT/GOOD/AVERAGE/POOR/CRITICAL.
US-ASQL-06: sp_TopNByRegion(p_region,p_n) — DENSE_RANK() top-N by score.
US-ASQL-07: sp_ArchiveOldRecords(p_cutoff_date) — transaction + ROLLBACK on error.
US-ASQL-08: fn_ComputeGrowthPct(p_entity_id,p_period) — current vs previous period.
US-ASQL-09: sp_GenerateCrossEntityReport() — multi-CTE JOIN + PIVOT-style CASE.
US-ASQL-10: sp_GetDuplicateSummary() — duplicate counts per entity via INFORMATION_SCHEMA.
US-ASQL-11: fn_Normalize(p_val,p_min,p_max) — min-max normalisation returning 0–1 scale.
US-ASQL-12: sp_RebuildIndexes() — dynamic SQL ANALYZE TABLE across all 4 entities.
US-ASQL-13: sp_ValidateSchema(p_table) — null counts + out-of-range check via schema.
US-ASQL-14: sp_HeatmapData(p_dim1,p_dim2) — 2-dim GROUP + CASE-based pivot.
US-ASQL-15: fn_FormatCurrency(p_val) — locale-formatted VARCHAR for reporting layer.

`,
`━━━ POWER BI — 15 Power Query + 10 DAX ━━━
US-PBI-01: 15 Power Query steps building a star schema refreshed automatically.
US-PBI-02: 10 DAX measures — Total_Records, Avg_Score, Running_Total,
  MoM_Growth_Pct (DATEADD), Rank_By_Region (RANKX), YTD_Value (TOTALYTD),
  Pct_Share (DIVIDE+ALL), Rolling_30d_Avg (DATESINPERIOD),
  KPI_Status (SWITCH+TRUE()), Top_N_Dynamic (TOPN+RANKX).
US-PBI-03: 5-page dashboard — KPI cards · Regional combo · Decomposition tree
  · Matrix with conditional formatting · Time-series with forecast.
US-PBI-04: Calendar dimension for full time-intelligence support.

━━━ AUTOMATION & LLM ━━━
US-AUT-01: Dynamic runtime generation of datasets, sectors, and stories each run.
US-AUT-02: Claude LLM API trigger for automated requirement and solution authoring.
US-AUT-03: Generated Word document including title, business scenario, non-Indian
  names, entity schemas, Unix solutions, DAX formulas, PySpark scripts, AGILE sheet.

CONSTRAINT: All requirements must be user stories:
"As a [role], I want to [action] so that [benefit]."
Character limit: ${limit.toLocaleString()}
`,
  ];

  let prompt=header;
  for(const sec of sections){
    if((prompt+sec).length<=limit-120) prompt+=sec;
  }
  const note=`\n\nNOTE: All requirements are sector-specific to "${s}". `+
    `Complexity: ${cx.label.toUpperCase()}. Solutions must include working code `+
    `(bash, Python, MongoDB shell, MySQL, PySpark). `+
    `Each story must demonstrate measurable business value.`;
  if((prompt+note).length<=limit) prompt+=note;
  return prompt.slice(0,limit);
}

/* ── BUILD AND SHOW PROMPT ───────────────────────────────── */
function buildAndShowPrompt(){
  if(!sector) return;
  const entities=getEntities(sector);
  currentPrompt=buildPrompt(sector,entities,charLimit);

  const cx=CX[complexity];
  const cxPill=$('cx-pill');
  cxPill.textContent=`${cx.icon} ${cx.label}`;
  cxPill.className=`cx-pill ${cx.cls}`;

  $('prompt-box').textContent=currentPrompt;
  $('prompt-result').style.display='block';
  $('prompt-result').classList.add('fadein');

  const len=currentPrompt.length;
  const counter=$('char-counter');
  counter.textContent=`${len.toLocaleString()} / ${charLimit.toLocaleString()} chars`;
  counter.className='char-counter'+(len>charLimit?' over':'');
  $('badge-prompt').textContent=`${len.toLocaleString()} chars`;

  $('btn-run').disabled=false;
  $('snum-gen').classList.add('s-active');
  toast('success',`Prompt ready · ${len.toLocaleString()} chars · ${cx.label}`);
}

function copyPrompt(){
  if(!currentPrompt) return;
  navigator.clipboard.writeText(currentPrompt)
    .then(()=>toast('success','Prompt copied to clipboard'))
    .catch(()=>toast('error','Could not copy'));
}

/* ── PROGRESS ────────────────────────────────────────────── */
const STEPS=[
  'Connecting to Claude API…',
  'Sending sector and entity context…',
  'Generating business scenario…',
  'Building Unix story-based requirements…',
  'Writing Shell scripting requirements…',
  'Generating Python file handling stories…',
  'Building PySpark cleaning stories…',
  'Writing MongoDB CRUD and aggregation stories…',
  'Generating 15 Advanced SQL stored procedures…',
  'Building Power BI transformation stories…',
  'Compiling technical solutions with working code…',
  'Finalising output documents…',
];

function startProgress(){
  $('gen-progress').style.display='block';
  const stepsEl=$('progress-steps');
  stepsEl.innerHTML=STEPS.map((s,i)=>
    `<div class="progress-step" id="ps-${i}"><div class="step-dot"></div><span>${s}</span></div>`
  ).join('');
  $('progress-fill').style.width='0%';
  progressStep=0;
  progressTimer=setInterval(()=>{
    if(progressStep>0){
      const prev=$(`ps-${progressStep-1}`);
      if(prev){prev.classList.remove('active');prev.classList.add('done');}
    }
    if(progressStep<STEPS.length){
      const cur=$(`ps-${progressStep}`);
      if(cur) cur.classList.add('active');
      $('progress-fill').style.width=`${((progressStep+1)/STEPS.length*88).toFixed(1)}%`;
      progressStep++;
    }
  },600);
}

function stopProgress(){
  if(progressTimer) clearInterval(progressTimer);
  $('progress-fill').style.width='100%';
  document.querySelectorAll('.progress-step').forEach(el=>{
    el.classList.remove('active'); el.classList.add('done');
  });
}

/* ── GENERATE ────────────────────────────────────────────── */
async function runGenerate(){
  if(!sector||generating||!currentPrompt) return;
  generating=true;

  const entities=getEntities(sector);
  const apiKey  =$('api-key-input').value.trim();

  $('btn-run').disabled=true;
  $('btn-run-inner').innerHTML='<div class="spinner"></div> Generating…';
  $('card-download').style.display='none';
  startProgress();

  try{
    let req='', sol='';

    if(apiKey){
      /* ── REAL API CALL (via Flask backend) ── */
      const res=await fetch('/api/generate',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          api_key: apiKey,
          prompt:  currentPrompt,
          complexity,
          sector,
          entities,
        }),
      });
      const data=await res.json();
      if(!data.ok) throw new Error(data.error||'Server error');
      req=data.requirements;
      sol=data.solutions;

    } else {
      /* ── DEMO OUTPUT (via Flask backend, no key needed) ── */
      await new Promise(r=>setTimeout(r,7200));
      const res=await fetch('/api/generate',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({api_key:'',prompt:currentPrompt,complexity,sector,entities}),
      });
      const data=await res.json();
      req=data.requirements;
      sol=data.solutions;
    }

    stopProgress();
    await new Promise(r=>setTimeout(r,320));

    currentReq=req; currentSol=sol;
    $('gen-progress').style.display='none';
    buildDownloadCards();
    $('card-download').style.display='block';
    $('card-download').classList.add('fadein');
    $('snum-gen').className='step-num s-done';
    $('badge-gen').textContent='Done ✓';
    $('badge-gen').style.color='var(--green)';
    toast('success',`✓ Output ready · ${CX[complexity].label} · ${sector}`);

  } catch(err){
    stopProgress();
    $('gen-progress').style.display='none';
    toast('error','Error: '+err.message.slice(0,90));
    $('snum-gen').classList.remove('s-active');
  }

  generating=false;
  $('btn-run').disabled=false;
  $('btn-run-inner').innerHTML=
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><polygon points="5,3 19,12 5,21"/></svg> Generate Output';
}

/* ── DOWNLOAD CARDS ──────────────────────────────────────── */
function buildDownloadCards(){
  const safe=(sector||'output').replace(/ & /g,'_').replace(/ /g,'_');
  const ts=new Date().toISOString().slice(0,10);
  const cx=CX[complexity];
  const f1=`${safe}_${complexity}_requirements_${ts}.txt`;
  const f2=`${safe}_${complexity}_solutions_${ts}.txt`;

  $('output-grid').innerHTML=`
    <div class="output-card fadein">
      <div class="output-card-head">
        <div class="output-icon">📄</div>
        <div>
          <div class="output-name">${f1}</div>
          <div class="output-size">${currentReq.length.toLocaleString()} characters · <span style="color:${cx.cls.includes('easy')?'var(--green)':cx.cls.includes('medium')?'var(--amber)':cx.cls.includes('hard')?'var(--red)':'var(--purple)'}">${cx.label}</span></div>
        </div>
      </div>
      <div class="output-preview">${esc(currentReq.slice(0,280))}</div>
      <button class="btn-card-dl" onclick="downloadFile('req')">⬇ Download</button>
    </div>
    <div class="output-card fadein">
      <div class="output-card-head">
        <div class="output-icon">⚙️</div>
        <div>
          <div class="output-name">${f2}</div>
          <div class="output-size">${currentSol.length.toLocaleString()} characters · <span style="color:var(--accent)">Solutions</span></div>
        </div>
      </div>
      <div class="output-preview">${esc(currentSol.slice(0,280))}</div>
      <button class="btn-card-dl" onclick="downloadFile('sol')">⬇ Download</button>
    </div>`;
}

/* ── FILE DOWNLOAD ───────────────────────────────────────── */
function getFilename(type){
  const safe=(sector||'output').replace(/ & /g,'_').replace(/ /g,'_');
  const ts=new Date().toISOString().slice(0,10);
  return type==='req'
    ? `${safe}_${complexity}_requirements_${ts}.txt`
    : `${safe}_${complexity}_solutions_${ts}.txt`;
}

function downloadFile(type){
  const content=type==='req'?currentReq:currentSol;
  if(!content){toast('error','No content to download');return;}
  const blob=new Blob([content],{type:'text/plain;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=getFilename(type);
  a.click(); URL.revokeObjectURL(a.href);
  toast('success','⬇ '+a.download);
}

function downloadBoth(){
  downloadFile('req');
  setTimeout(()=>downloadFile('sol'),600);
}

/* ── RESET ───────────────────────────────────────────────── */
function resetForNewRun(){
  currentPrompt=''; currentReq=''; currentSol='';
  $('card-download').style.display='none';
  $('gen-progress').style.display='none';
  $('prompt-result').style.display='none';
  $('btn-run').disabled=true;
  $('snum-gen').className='step-num';
  $('badge-gen').textContent='';
  $('badge-prompt').textContent='';
  toast('info','Ready for new generation run');
}

/* ── TOAST ───────────────────────────────────────────────── */
let toastTimer=null;
function toast(type,msg){
  const el=$('toast');
  el.textContent=msg;
  el.className=`toast ${type} show`;
  if(toastTimer) clearTimeout(toastTimer);
  toastTimer=setTimeout(()=>el.classList.remove('show'),3600);
}