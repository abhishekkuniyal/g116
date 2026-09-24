// -------------------------------------------------------------
// IFFCO Demand Forecasting — Interactive Presentation Logic
// -------------------------------------------------------------

// Embedded Project Data
let projectData = null;

// Presenter Notes Dictionary (Speaker script & talking points for each slide)
const PRESENTER_NOTES = {
  0: {
    title: "Title Slide: Project G116 Overview",
    script: "Welcome respected panel members, faculty, and peers. Today I present Project G116: 'AI-Powered Fertilizer Demand Forecasting and Supply Chain Analytics Platform', developed in collaboration with IFFCO domain requirements. Our mission is to forecast state-level fertilizer demand for FY 2025-26 using multi-model machine learning, rigorous chronological validation, and an enterprise full-stack deployment."
  },
  1: {
    title: "Outline & Agenda",
    script: "Here is our structured presentation outline following the Department guidelines: we will cover the agricultural context, industrial motivation, academic literature review, gap analysis, problem formulation, data pipeline, reporting break discovery, multi-model evaluation, rolling validation results, full-stack architecture, and 2025-26 forecasts."
  },
  2: {
    title: "Introduction: Fertilizer Logistics & IFFCO Context",
    script: "Fertilizer distribution is the logistical lifeblood of Indian agriculture. We focus on 4 major product categories: Urea, DAP, MOP, and NPKS complexes across 36 States/UTs. IFFCO operates multi-state manufacturing plants. The core forecasting mandate is: at the end of FY t, use all information up to t to forecast demand for FY t+1 to plan production and import shipments."
  },
  3: {
    title: "Motivation: Bottlenecks, Sowing Windows & Fiscal Risks",
    script: "Why does this matter? Sowing windows are extremely unforgiving: a 1-week delay in fertilizer availability can reduce crop yields by 15-20%. Long import lead times and rail transit require 3-4 weeks planning. Furthermore, India's fertilizer subsidy bill exceeds ₹1.6 Lakh Crore annually, so accurate quotas prevent costly holding inventory and regional stockouts."
  },
  4: {
    title: "Review of Literature: Time-Series in Agriculture",
    script: "We systematically reviewed 4 modeling paradigms: classical time-series (ARIMA/Holt-Winters), modern machine learning (Random Forest/XGBoost), deep learning (LSTM/Transformers), and heuristic baselines. A key insight from literature is that complex neural models severely overfit small annual macro series (N=11 years), while persistence baselines often provide formidable benchmarks."
  },
  5: {
    title: "Gap Analysis: Overcoming Prior Limitations",
    script: "We identified 4 fatal gaps in prior work: (1) over-reliance on complex black-box models without proper temporal benchmarking, (2) failure to detect official reporting and geographic boundary breaks, (3) mismatched temporal and spatial grains, and (4) academic prototypes that never deploy into real software."
  },
  6: {
    title: "Problem Formulation & Mathematical Objectives",
    script: "We mathematically formalize the target: Y_{i, j, t+1} represents sales volume in LMT for state i and fertilizer j in year t+1. Our feature vector uses only information available up to year t. We evaluate 144 target series with zero future information leakage."
  },
  7: {
    title: "Proposed Methodology: Data Engineering Pipeline",
    script: "Our data pipeline ingests 11 fiscal years (2014-15 to 2024-25) from the Ministry of Chemicals and Fertilizers, combined with IFFCO plant production logs and Rajasthan district data. We harmonized state entities, engineered 1-year lags, and split data chronologically into train, validation, and test subsets."
  },
  8: {
    title: "Data Quality Finding: The 2018-19 Discontinuity",
    script: "A key contribution of our work was uncovering an anomalous reporting break in FY 2018-19. In the official data, Uttar Pradesh Urea/DAP recorded an unnatural 98% plunge, while Uttarakhand experienced a 20-fold spike. Rather than corrupting ground truth with manual overrides, we preserved data provenance and added a binary `potential_reporting_break` flag."
  },
  9: {
    title: "Machine Learning & Baseline Suite",
    script: "We evaluated 6 diverse models: Naive Persistence, Linear Regression with One-Hot encoding, Random Forest with 200 trees, Random Forest with engineered change features, Drift Baseline, and Recent-Change Baseline. All models operate under identical chronological constraints."
  },
  10: {
    title: "5-Year Rolling Window Cross-Validation Framework",
    script: "To prevent test-set bias, we implemented an expanding window cross-validation across 5 successive fiscal forecast periods: 2019-20 through 2023-24, totaling 720 out-of-sample predictions. This simulates true annual operational deployment."
  },
  11: {
    title: "Results & Discussion: 5-Year Rolling Benchmark",
    script: "The rolling validation yielded a remarkable empirical conclusion: Naive Persistence won in 4 out of 5 years with an average MAE of 0.4349 LMT and R² of 0.9894. Random Forest averaged MAE 0.5203, but won in 2023-24 with MAE 0.4944, proving valuable during structural turning points."
  },
  12: {
    title: "Results & Discussion: Disaggregated Fertilizer Errors",
    script: "Error analysis across chemical products shows that MOP has the lowest error (MAE 0.1831), followed by DAP (0.4564), NPKS (0.5319), and Urea (0.5683). Urea's error is higher primarily due to its massive national volume (59% of all consumption)."
  },
  13: {
    title: "System Architecture: End-to-End Enterprise Stack",
    script: "To bridge ML research with production, we engineered a 4-tier enterprise stack: Python data pipeline -> Microsoft SQL Server dimensional database -> high-speed FastAPI asynchronous REST API -> modern React 19 analytics dashboard."
  },
  14: {
    title: "System Implementation: API & Analytics UI",
    script: "Our FastAPI backend exposes dedicated endpoints for forecasts, sales history, multi-factor trends, and plant production. The React dashboard provides interactive Recharts time-series, KPI metric cards, and responsive state-level filters."
  },
  15: {
    title: "Final 2025-26 Demand Forecasts: National Allocations",
    script: "For FY 2025-26, our platform forecasts a total national demand of 655.94 Lakh Metric Tonnes: Urea accounts for 387.94 LMT, NPKS 149.72 LMT, DAP 96.27 LMT, and MOP 22.01 LMT. In this slide, panel members can interactively select any state to view exact predicted demand."
  },
  16: {
    title: "Operational Limitations & Responsible Deployment",
    script: "We highlight 3 critical operational boundaries: (1) forecasts are annual and require seasonal monthly downscaling for rake dispatch, (2) Rajasthan district data is maintained separately to prevent grain distortion, and (3) missing IFFCO plant output represents unmonitored facilities, not zero usage."
  },
  17: {
    title: "Conclusion & Future Research Roadmap",
    script: "In conclusion, G116 proves that disciplined empirical validation and baseline comparisons are crucial for macroeconomic forecasting. For future work, we propose integrating satellite NDVI indices, IMD monsoon rainfall anomalies, and Indian Railways rake scheduling."
  },
  18: {
    title: "References & Authoritative Documentation",
    script: "Our work builds on official Ministry of Chemicals & Fertilizers publications, IFFCO annual reports, and seminal peer-reviewed literature in time-series and ensemble machine learning."
  },
  19: {
    title: "Thank You & Floor Open for Questions",
    script: "Thank you esteemed panel members for your time and guidance. I invite any questions or discussion regarding our methodology, data quality findings, or software implementation."
  }
};

// State Variables
let currentSlideIndex = 0;
const totalSlides = 20;
let isFullscreen = false;
let isPresenterMode = false;
let isOverviewOpen = false;
let isShortcutsOpen = false;
let timerSeconds = 0;
let timerInterval = null;
let timerRunning = false;

// DOM Elements Cache
const slides = document.querySelectorAll('.slide');
const currentSlideNumEl = document.getElementById('currentSlideNum');
const totalSlidesNumEl = document.getElementById('totalSlidesNum');
const progressBarFillEl = document.getElementById('progressBarFill');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');
const timerBadge = document.getElementById('timerBadge');
const presenterDrawer = document.getElementById('presenterDrawer');
const overviewModal = document.getElementById('overviewModal');
const shortcutsModal = document.getElementById('shortcutsModal');
const presenterNotesEl = document.getElementById('presenterNotes');
const nextSlidePreviewEl = document.getElementById('nextSlidePreview');

// Initialize Presentation
async function initPresentation() {
  // Load data from global or fetch fallback
  if (window.PROJECT_DATA) {
    projectData = window.PROJECT_DATA;
    populateSimulator(projectData);
  } else {
    try {
      const res = await fetch('data.json');
      projectData = await res.json();
      populateSimulator(projectData);
    } catch (e) {
      console.warn('Could not load data.json via fetch', e);
    }
  }

  // Set total count
  totalSlidesNumEl.textContent = String(totalSlides).padStart(2, '0');
  
  // Set up listeners
  setupKeyboardNav();
  setupButtonListeners();
  buildOverviewGrid();
  
  // Go to initial slide
  goToSlide(0);
  startTimer();
}

// Navigation Functions
function goToSlide(index) {
  if (index < 0 || index >= totalSlides) return;
  
  slides[currentSlideIndex].classList.remove('active');
  currentSlideIndex = index;
  slides[currentSlideIndex].classList.add('active');
  
  // Update Header Badges
  currentSlideNumEl.textContent = String(currentSlideIndex + 1).padStart(2, '0');
  const progressPct = ((currentSlideIndex + 1) / totalSlides) * 100;
  progressBarFillEl.style.width = `${progressPct}%`;
  
  // Update Buttons
  prevBtn.disabled = currentSlideIndex === 0;
  nextBtn.disabled = currentSlideIndex === totalSlides - 1;
  
  // Update Presenter Notes
  updatePresenterNotes();
  
  // Update Overview Grid Active State
  const thumbs = document.querySelectorAll('.overview-thumb');
  thumbs.forEach((t, i) => {
    t.classList.toggle('current', i === currentSlideIndex);
  });
}

function nextSlide() {
  if (currentSlideIndex < totalSlides - 1) {
    goToSlide(currentSlideIndex + 1);
  }
}

function prevSlide() {
  if (currentSlideIndex > 0) {
    goToSlide(currentSlideIndex - 1);
  }
}

// Timer Functions
function startTimer() {
  if (timerRunning) return;
  timerRunning = true;
  timerInterval = setInterval(() => {
    timerSeconds++;
    const mins = String(Math.floor(timerSeconds / 60)).padStart(2, '0');
    const secs = String(timerSeconds % 60).padStart(2, '0');
    timerBadge.textContent = `⏱️ ${mins}:${secs}`;
  }, 1000);
}

function pauseTimer() {
  clearInterval(timerInterval);
  timerRunning = false;
}

function resetTimer() {
  pauseTimer();
  timerSeconds = 0;
  timerBadge.textContent = '⏱️ 00:00';
}

function toggleTimer() {
  if (timerRunning) {
    pauseTimer();
  } else {
    startTimer();
  }
}

// Fullscreen Toggle
function toggleFullscreen() {
  if (!document.fullscreenElement) {
    document.documentElement.requestFullscreen().catch(err => console.log(err));
    isFullscreen = true;
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
      isFullscreen = false;
    }
  }
}

// Presenter Mode Toggle
function togglePresenterMode() {
  isPresenterMode = !isPresenterMode;
  presenterDrawer.classList.toggle('active', isPresenterMode);
  document.getElementById('presenterBtn').classList.toggle('active', isPresenterMode);
  if (isPresenterMode) updatePresenterNotes();
}

function updatePresenterNotes() {
  const currentInfo = PRESENTER_NOTES[currentSlideIndex] || {
    title: `Slide ${currentSlideIndex + 1}`,
    script: "Detailed talking points and project metrics."
  };
  
  const nextInfo = PRESENTER_NOTES[currentSlideIndex + 1] || {
    title: "End of Presentation",
    script: "Summary and Q&A"
  };
  
  presenterNotesEl.innerHTML = `
    <h4>${currentInfo.title}</h4>
    <p>${currentInfo.script}</p>
  `;
  
  nextSlidePreviewEl.innerHTML = `
    <span class="next-preview-title">Next Slide [${currentSlideIndex + 2}/${totalSlides}]:</span>
    <span class="next-preview-name">${nextInfo.title}</span>
  `;
}

// Overview Modal Toggle
function toggleOverview() {
  isOverviewOpen = !isOverviewOpen;
  overviewModal.classList.toggle('active', isOverviewOpen);
  document.getElementById('overviewBtn').classList.toggle('active', isOverviewOpen);
}

function buildOverviewGrid() {
  const grid = document.getElementById('overviewGrid');
  grid.innerHTML = '';
  
  slides.forEach((slide, idx) => {
    const titleEl = slide.querySelector('.slide-title');
    const title = titleEl ? titleEl.textContent : `Slide ${idx + 1}`;
    
    const thumb = document.createElement('div');
    thumb.className = `overview-thumb ${idx === currentSlideIndex ? 'current' : ''}`;
    thumb.innerHTML = `
      <div class="overview-thumb-num">SLIDE ${String(idx + 1).padStart(2, '0')}</div>
      <div class="overview-thumb-title">${title}</div>
    `;
    thumb.onclick = () => {
      goToSlide(idx);
      toggleOverview();
    };
    grid.appendChild(thumb);
  });
}

// Shortcuts Modal Toggle
function toggleShortcuts() {
  isShortcutsOpen = !isShortcutsOpen;
  shortcutsModal.classList.toggle('active', isShortcutsOpen);
}

// Theme Toggle
function toggleTheme() {
  const current = document.body.getAttribute('data-theme');
  const next = current === 'light' ? 'dark' : 'light';
  document.body.setAttribute('data-theme', next);
}

// Keyboard Navigation
function setupKeyboardNav() {
  window.addEventListener('keydown', (e) => {
    // If typing in input, ignore
    if (['INPUT', 'SELECT', 'TEXTAREA'].includes(e.target.tagName)) return;
    
    switch (e.key) {
      case 'ArrowRight':
      case ' ':
      case 'PageDown':
        e.preventDefault();
        nextSlide();
        break;
      case 'ArrowLeft':
      case 'Backspace':
      case 'PageUp':
        e.preventDefault();
        prevSlide();
        break;
      case 'Home':
        e.preventDefault();
        goToSlide(0);
        break;
      case 'End':
        e.preventDefault();
        goToSlide(totalSlides - 1);
        break;
      case 'f':
      case 'F':
        e.preventDefault();
        toggleFullscreen();
        break;
      case 'p':
      case 'P':
        e.preventDefault();
        togglePresenterMode();
        break;
      case 'o':
      case 'O':
        e.preventDefault();
        toggleOverview();
        break;
      case 't':
      case 'T':
        e.preventDefault();
        toggleTimer();
        break;
      case '?':
      case '/':
        e.preventDefault();
        toggleShortcuts();
        break;
      case 'Escape':
        if (isOverviewOpen) toggleOverview();
        if (isShortcutsOpen) toggleShortcuts();
        break;
    }
  });
}

// Button Listeners
function setupButtonListeners() {
  prevBtn.onclick = prevSlide;
  nextBtn.onclick = nextSlide;
  document.getElementById('overviewBtn').onclick = toggleOverview;
  document.getElementById('presenterBtn').onclick = togglePresenterMode;
  document.getElementById('fullscreenBtn').onclick = toggleFullscreen;
  document.getElementById('themeBtn').onclick = toggleTheme;
  document.getElementById('shortcutsBtn').onclick = toggleShortcuts;
  document.getElementById('printBtn').onclick = () => window.print();
  timerBadge.onclick = toggleTimer;
  
  document.getElementById('closeOverview').onclick = toggleOverview;
  document.getElementById('closeShortcuts').onclick = toggleShortcuts;
  document.getElementById('closePresenter').onclick = togglePresenterMode;
}

// -------------------------------------------------------------
// Interactive Slide Widgets Logic
// -------------------------------------------------------------

// Slide 3: Fertilizer Product Switcher
window.selectFertilizerTab = function(type) {
  const cards = document.querySelectorAll('.fert-detail-card');
  const tabs = document.querySelectorAll('.fert-tab-btn');
  
  tabs.forEach(t => t.classList.toggle('active', t.dataset.fert === type));
  cards.forEach(c => c.style.display = c.dataset.fert === type ? 'flex' : 'none');
};

// Slide 5: Literature Review Category Filter
window.filterLiterature = function(cat) {
  const rows = document.querySelectorAll('.lit-row');
  const tabs = document.querySelectorAll('.lit-tab-btn');
  
  tabs.forEach(t => t.classList.toggle('active', t.dataset.cat === cat));
  rows.forEach(r => {
    if (cat === 'all' || r.dataset.cat === cat) {
      r.style.display = '';
    } else {
      r.style.display = 'none';
    }
  });
};

// Slide 8: Pipeline Stepper
window.showPipelineStage = function(stage) {
  const stages = document.querySelectorAll('.pipeline-stage-card');
  const btns = document.querySelectorAll('.pipeline-step-btn');
  
  btns.forEach(b => b.classList.toggle('active', b.dataset.stage === stage));
  stages.forEach(s => s.style.display = s.dataset.stage === stage ? 'block' : 'none');
};

// Slide 9: 2018-19 Discontinuity State Switcher
window.showDiscontinuityState = function(state) {
  const cards = document.querySelectorAll('.disc-card');
  const btns = document.querySelectorAll('.disc-btn');
  
  btns.forEach(b => b.classList.toggle('active', b.dataset.state === state));
  cards.forEach(c => c.style.display = c.dataset.state === state ? 'block' : 'none');
};

// Slide 11: 5-Year Rolling Timeline Buttons
window.selectRollingYear = function(year) {
  const details = document.querySelectorAll('.rolling-year-card');
  const btns = document.querySelectorAll('.rolling-year-btn');
  
  btns.forEach(b => b.classList.toggle('active', b.dataset.year === year));
  details.forEach(d => d.style.display = d.dataset.year === year ? 'block' : 'none');
};

// Slide 12: Benchmark Metric Toggle (MAE, RMSE, R2)
window.switchBenchmarkMetric = function(metric) {
  const btns = document.querySelectorAll('.bench-metric-btn');
  btns.forEach(b => b.classList.toggle('active', b.dataset.metric === metric));
  
  const metricData = {
    mae: { naive: 0.4349, rf: 0.5203, lr: 1.0312, label: 'Lakh Metric Tonnes (Lower is Better)', max: 1.2 },
    rmse: { naive: 0.9254, rf: 1.3111, lr: 1.8651, label: 'Root Mean Squared Error (Lower is Better)', max: 2.0 },
    r2: { naive: 0.9894, rf: 0.9760, lr: 0.9389, label: 'Coefficient of Determination (Higher is Better)', max: 1.0 }
  };
  
  const d = metricData[metric];
  document.getElementById('benchMetricLabel').textContent = d.label;
  
  // Animate bars
  const pNaive = (d.naive / d.max) * 100;
  const pRf = (d.rf / d.max) * 100;
  const pLr = (d.lr / d.max) * 100;
  
  document.getElementById('barNaiveVal').textContent = d.naive.toFixed(4);
  document.getElementById('barNaiveFill').style.width = `${pNaive}%`;
  
  document.getElementById('barRfVal').textContent = d.rf.toFixed(4);
  document.getElementById('barRfFill').style.width = `${pRf}%`;
  
  document.getElementById('barLrVal').textContent = d.lr.toFixed(4);
  document.getElementById('barLrFill').style.width = `${pLr}%`;
};

// Slide 15: Mock API Endpoint Tester
window.testApiEndpoint = function(endpoint) {
  const btns = document.querySelectorAll('.api-test-btn');
  btns.forEach(b => b.classList.toggle('active', b.dataset.endpoint === endpoint));
  
  const outputEl = document.getElementById('apiJsonOutput');
  const mockResponses = {
    forecasts: {
      status: 200,
      forecast_year: "2025-26",
      state: "Maharashtra",
      predictions: {
        urea: 26.50,
        npks: 23.95,
        dap: 8.78,
        mop: 4.66,
        total: 63.89
      },
      method: "Naive Persistence",
      basis: "2024-25 sales"
    },
    sales: {
      status: 200,
      state: "Maharashtra",
      fertilizer: "urea",
      series: [
        { year: "2021-22", sales: 25.12 },
        { year: "2022-23", sales: 25.80 },
        { year: "2023-24", sales: 26.10 },
        { year: "2024-25", sales: 26.50 }
      ]
    },
    summary: {
      status: 200,
      active_entities: 36,
      forecast_year: "2025-26",
      total_demand_lmt: 655.94,
      top_demanding_state: "Uttarakhand",
      method_selected: "Naive Persistence"
    },
    iffco: {
      status: 200,
      plant_count: 5,
      facilities: ["Kalol", "Kandla", "Phulpur", "Paradeep", "Aonla"],
      primary_grades: ["Urea", "DAP", "NPKS"]
    }
  };
  
  outputEl.textContent = JSON.stringify(mockResponses[endpoint] || {}, null, 2);
};

// Slide 16: Live 2025-26 Forecast Simulator
function populateSimulator(data) {
  if (!data || !data.forecasts) return;
  const select = document.getElementById('simStateSelect');
  if (!select) return;
  
  select.innerHTML = '';
  const states = Object.keys(data.forecasts).sort();
  
  states.forEach(st => {
    const opt = document.createElement('option');
    opt.value = st;
    opt.textContent = `${st} (Rank #${data.forecasts[st].rank})`;
    select.appendChild(opt);
  });
  
  // Set default state
  select.value = "Maharashtra";
  updateSimResults("Maharashtra");
  
  select.onchange = (e) => updateSimResults(e.target.value);
}

function updateSimResults(stateName) {
  if (!projectData || !projectData.forecasts) return;
  const item = projectData.forecasts[stateName];
  if (!item) return;
  
  document.getElementById('simUrea').textContent = `${item.urea.toFixed(2)} LMT`;
  document.getElementById('simDap').textContent = `${item.dap.toFixed(2)} LMT`;
  document.getElementById('simNpks').textContent = `${item.npks.toFixed(2)} LMT`;
  document.getElementById('simMop').textContent = `${item.mop.toFixed(2)} LMT`;
  document.getElementById('simTotal').textContent = `${item.total.toFixed(2)} LMT`;
  document.getElementById('simRank').textContent = `#${item.rank} of 36`;
  
  // Percentage shares
  const pUrea = item.total > 0 ? ((item.urea / item.total) * 100).toFixed(1) : 0;
  const pDap = item.total > 0 ? ((item.dap / item.total) * 100).toFixed(1) : 0;
  const pNpks = item.total > 0 ? ((item.npks / item.total) * 100).toFixed(1) : 0;
  const pMop = item.total > 0 ? ((item.mop / item.total) * 100).toFixed(1) : 0;
  
  document.getElementById('simUreaShare').textContent = `${pUrea}% of state`;
  document.getElementById('simDapShare').textContent = `${pDap}% of state`;
  document.getElementById('simNpksShare').textContent = `${pNpks}% of state`;
  document.getElementById('simMopShare').textContent = `${pMop}% of state`;
}

// Launch on DOM ready
document.addEventListener('DOMContentLoaded', initPresentation);
