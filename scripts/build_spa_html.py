"""Compiles the self-contained Yaquis de Ciudad Obregón Front Office SPA HTML."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PAYLOAD_PATH = BASE_DIR / "web" / "data" / "front_office_payload.json"
TAILWIND_CSS_PATH = BASE_DIR / "web" / "assets" / "tailwind.min.css"
OUT_HTML_PATH = BASE_DIR / "web" / "index.html"

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="referrer" content="no-referrer" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; font-src 'self' data:; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none';" />
  <title>Centro de Mando · Analítica 360° & Scouting — Club Yaquis de Ciudad Obregón (LMP)</title>
  <meta name="description" content="Plataforma interactiva autocontenida de Analítica 360°, Sabermetría (wRC+, FIP, OPS+), Telemetría Statcast 2D y Scouting 20–80 para Club Yaquis de Ciudad Obregón en la LMP (2006–2026)." />
  <!-- OpenGraph / LinkedIn & Social Preview (metadatos estáticos; cero peticiones en runtime bajo CSP estricto) -->
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="es_MX" />
  <meta property="og:site_name" content="Yaquis de Obregón · Front Office Analytics (LMP)" />
  <meta property="og:url" content="https://gzzalejandro.github.io/yaquis_obregon_analisis_de_datos_LMP/" />
  <meta property="og:title" content="Dashboard Front Office · Club Yaquis de Ciudad Obregón (LMP 2006–2026)" />
  <meta property="og:description" content="Analítica 360°, Sabermetría (wRC+, FIP, DER%), Spray Chart 2D, Zona de Strike 9-Zonas, Fatiga B2B y Scouting MLB 20–80 sobre 21 temporadas de la Liga ARCO Mexicana del Pacífico." />
  <meta property="og:image" content="https://gzzalejandro.github.io/yaquis_obregon_analisis_de_datos_LMP/assets/og_preview.png" />
  <meta property="og:image:type" content="image/png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="Dashboard Front Office Club Yaquis de Ciudad Obregón — Resumen Ejecutivo, KPIs LMP y Matriz Ofensiva vs Pitcheo" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Dashboard Front Office · Club Yaquis de Ciudad Obregón (LMP 2006–2026)" />
  <meta name="twitter:description" content="Analítica 360°, Sabermetría, Telemetría Statcast 2D y Scouting 20–80 sobre 21 temporadas de la LMP." />
  <meta name="twitter:image" content="https://gzzalejandro.github.io/yaquis_obregon_analisis_de_datos_LMP/assets/og_preview.png" />
  <style id="tw-static">__TAILWIND_CSS__</style>
  <style>
    :root {
      --yaquis-navy: #003B73;
      --yaquis-midnight: #002850;
      --yaquis-dark: #0B1320;
      --yaquis-royal: #0057A8;
      --yaquis-cyan: #0095DA;
      --yaquis-red: #E6392F;
      --bg-canvas: #F4F7FA;
      --surface: #FFFFFF;
      --border-subtle: #DDE6F0;
      --text-main: #0F172A;
      --text-muted: #475569;
      --ok: #16A34A;
      --warn: #D97706;
      --crit: #E6392F;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background-color: var(--bg-canvas);
      color: var(--text-main);
      font-family: 'Bahnschrift', 'Segoe UI', system-ui, -apple-system, sans-serif;
      -webkit-font-smoothing: antialiased;
    }

    .mono, .tabular-nums {
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum" 1;
    }

    .font-code {
      font-family: 'Consolas', 'Cascadia Mono', ui-monospace, monospace;
      font-variant-numeric: tabular-nums;
    }

    /* Slanted athletic jersey ribbons inspired by yaquis.com.mx */
    .jersey-ribbon {
      display: inline-flex;
      align-items: center;
      transform: skewX(-12deg);
      border-radius: 3px;
    }
    .jersey-ribbon > span {
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transform: skewX(12deg);
    }

    /* Sticky glass/navy bar */
    .sticky-filter-bar {
      position: sticky;
      top: 0;
      z-index: 40;
      background: rgba(255, 255, 255, 0.96);
      backdrop-filter: blur(8px);
      border-bottom: 2px solid var(--border-subtle);
      box-shadow: 0 4px 14px rgba(0, 40, 80, 0.06);
    }

    .card-surface {
      background: var(--surface);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
    }

    .telemetry-dark {
      background: radial-gradient(circle at 50% 25%, #0E2340 0%, #0B1320 75%);
      border: 1px solid #1E3A5F;
      color: #F8FAFC;
      border-radius: 10px;
    }

    /* Table polish & Sticky first column */
    .fo-table-wrap {
      overflow-x: auto;
      scrollbar-width: thin;
      scrollbar-color: #94A3B8 transparent;
    }
    table.fo-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      font-size: 13.5px;
    }
    table.fo-table thead th {
      position: sticky;
      top: 0;
      z-index: 15;
      background: #002850;
      color: #E2E8F0;
      font-size: 11.5px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 10px 12px;
      border-bottom: 2px solid var(--yaquis-cyan);
      white-space: nowrap;
      cursor: default;
      user-select: none;
      transition: background-color 0.15s ease;
    }
    table.fo-table thead th[data-sort-col],
    table.fo-table thead th[data-bsort],
    table.fo-table thead th[data-psort] {
      cursor: pointer;
    }
    table.fo-table thead th[data-sort-col]:hover,
    table.fo-table thead th[data-bsort]:hover,
    table.fo-table thead th[data-psort]:hover {
      background: #003B73;
      color: #FFFFFF;
    }
    table.fo-table thead th.sorted-col {
      background: #0057A8;
      color: #FFFFFF;
    }
    table.fo-table tbody td {
      padding: 10px 12px;
      border-bottom: 1px solid #E2E8F0;
      white-space: nowrap;
      font-variant-numeric: tabular-nums;
      background: #FFFFFF;
    }
    table.fo-table th:first-child,
    table.fo-table td:first-child {
      position: sticky;
      left: 0;
      z-index: 12;
      box-shadow: 3px 0 8px -3px rgba(0, 40, 80, 0.16);
    }
    table.fo-table thead th:first-child {
      z-index: 25;
      background: #002850;
    }
    table.fo-table thead th.sorted-col:first-child {
      background: #0057A8;
    }
    table.fo-table tbody tr:hover td {
      background: #F1F6FC;
    }
    table.fo-table tbody tr.yaquis-highlight-row td {
      background: #E8F4FD;
      font-weight: 700;
      color: #002850;
      border-top: 1px solid #0072B2;
      border-bottom: 1px solid #0072B2;
    }
    table.fo-table tbody tr.rival-highlight-row td {
      background: #FEF3C7;
      font-weight: 700;
      color: #78350F;
      border-top: 1px solid #D97706;
      border-bottom: 1px solid #D97706;
    }
    @media (max-width: 640px) {
      .sticky-filter-bar > div { padding-top: 0.45rem; padding-bottom: 0.35rem; gap: 0.35rem; }
      table.fo-table { font-size: 12.5px; }
      table.fo-table thead th, table.fo-table tbody td { padding: 8px 9px; }
    }

    .tab-btn {
      transition: all 0.18s ease;
      border-bottom: 3px solid transparent;
    }
    .tab-btn.active {
      color: var(--yaquis-navy);
      border-bottom-color: var(--yaquis-cyan);
      background: #EFF6FF;
    }

    .pill-btn {
      transition: all 0.15s ease;
      border: 1px solid #CBD5E1;
      background: #FFFFFF;
      color: #334155;
    }
    .pill-btn:hover {
      border-color: var(--yaquis-cyan);
      color: var(--yaquis-navy);
    }
    .pill-btn.active {
      background: var(--yaquis-navy);
      border-color: var(--yaquis-navy);
      color: #FFFFFF;
      box-shadow: 0 2px 6px rgba(0, 59, 115, 0.25);
    }

    /* Custom scrollbars for player sidebar */
    .roster-scroll {
      max-height: 300px;
      overflow-y: auto;
      scrollbar-width: thin;
      scrollbar-color: #94A3B8 transparent;
    }
    @media (min-width: 1024px) {
      .roster-scroll {
        max-height: 780px;
      }
    }

    /* Tooltips on SVG points */
    #svg-floating-tooltip {
      position: fixed;
      pointer-events: none;
      z-index: 90;
      background: rgba(11, 19, 32, 0.96);
      color: #F8FAFC;
      border: 1px solid #0095DA;
      border-radius: 8px;
      padding: 8px 11px;
      font-size: 12px;
      line-height: 1.4;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.35);
      display: none;
      max-width: 280px;
    }

    @media print {
      .sticky-filter-bar { position: static; }
    }
  </style>
</head>
<body>

  <!-- HEADER INSTITUCIONAL YAQUIS DE CIUDAD OBREGÓN -->
  <header style="background: linear-gradient(110deg, #002850 0%, #003B73 58%, #0057A8 100%);" class="text-white border-b-4 border-[#0095DA]">
    <div class="max-w-[1440px] mx-auto px-4 sm:px-6 py-4 space-y-3">
      <div class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-3 shrink-0">
            <div id="header-co-wrap" class="w-16 h-16 rounded-xl bg-[#002850] border-2 border-[#0095DA]/70 p-1.5 flex items-center justify-center shadow-lg">
              <!-- Populated with CO PNG + SVG fallback -->
            </div>
            <div id="header-mascot-wrap" class="hidden sm:flex w-16 h-16 rounded-xl bg-white p-1 items-center justify-center shadow-lg overflow-hidden border-2 border-white/80">
              <!-- Populated with Mascot JPG -->
            </div>
          </div>
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <span class="jersey-ribbon bg-[#E6392F] text-white text-[10px] font-extrabold tracking-widest px-2.5 py-0.5 uppercase">
                <span>FRONT OFFICE R&amp;D</span>
              </span>
              <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-bold tracking-wider px-2.5 py-0.5 uppercase">
                <span>ANALÍTICA 360° &amp; SCOUTING PROFESIONAL LMP</span>
              </span>
            </div>
            <div class="flex flex-wrap items-center gap-3 mt-1.5">
              <div id="header-wordmark-wrap" class="hidden md:flex items-center"></div>
              <h1 class="text-xl sm:text-2xl font-extrabold tracking-tight leading-tight">
                CLUB YAQUIS DE CIUDAD OBREGÓN
                <span class="font-normal text-[#93C5FD] text-sm sm:text-base block sm:inline sm:ml-2">Centro de Mando · Analítica 360° &amp; Scouting</span>
              </h1>
            </div>
          </div>
        </div>

        <!-- 7 Campeonatos + LMP Official Shield Badge -->
        <div class="flex flex-wrap items-center gap-3">
          <div class="bg-[#0B1320]/75 border border-[#0095DA]/45 rounded-xl px-4 py-2.5 flex items-center gap-3.5 shadow-md">
            <div class="flex flex-col">
              <span class="text-[10.5px] uppercase tracking-widest text-[#7DD3FC] font-bold">7 Campeonatos LMP</span>
              <div class="flex flex-wrap items-center gap-1 mt-0.5 text-xs font-bold text-amber-300 tabular-nums">
                <span>★ 1966</span><span>·</span><span>1973</span><span>·</span><span>1981</span><span>·</span><span>2008</span><span>·</span><span>2011</span><span>·</span><span>2012</span><span>·</span><span>2013</span>
              </div>
            </div>
            <div class="h-10 w-px bg-white/20 hidden sm:block"></div>
            <div class="flex items-center gap-2 text-xs text-slate-200">
              <div id="header-lmp-wrap" class="w-12 h-12 rounded-lg bg-white p-1 flex items-center justify-center shadow shrink-0"></div>
              <div class="leading-tight hidden sm:block">
                <div class="font-bold text-white text-xs">LIGA ARCO</div>
                <div class="text-[11px] text-[#7DD3FC] font-code">2006–2026 (21T)</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Cintillo Oficial de los 10 Clubes LMP -->
      <div class="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-white/15">
        <span class="text-[10.5px] font-bold uppercase tracking-widest text-[#7DD3FC]">Franquicias Activas LMP:</span>
        <div id="header-lmp-clubs-strip" class="flex flex-wrap items-center gap-2"></div>
      </div>
    </div>
  </header>

  <!-- BARRA GLOBAL DE FILTROS & PESTAÑAS (STICKY TOP) -->
  <div class="sticky-filter-bar">
    <div class="max-w-[1440px] mx-auto px-4 sm:px-6 pt-2.5 pb-2 space-y-2.5">
      <!-- Filter Controls Row -->
      <div class="flex flex-wrap items-center justify-between gap-2.5">
        <div class="flex flex-wrap items-center gap-2 sm:gap-3">
          <!-- Selector de Temporada -->
          <div class="flex items-center gap-1.5">
            <label for="sel-season" class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Temporada</label>
            <select id="sel-season" class="text-xs sm:text-sm font-bold text-[#003B73] bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:border-[#0095DA]">
              <option value="2025">2025–26 (Completa)</option>
              <option value="2026">2026–27 (En Curso · YTD)</option>
              <option value="hist">Histórico 2006–2026</option>
            </select>
          </div>

          <!-- Selector de Etapa -->
          <div class="flex items-center gap-1 overflow-x-auto max-w-full pb-0.5 sm:pb-0" role="group" aria-label="Etapa del torneo">
            <span class="text-[11px] font-bold uppercase tracking-wider text-slate-500 mr-1 hidden md:inline shrink-0">Etapa</span>
            <button data-stage="global_reg" class="stage-btn pill-btn active text-xs font-bold px-2.5 py-1 sm:py-1.5 rounded-md whitespace-nowrap">Global Rol Reg.</button>
            <button data-stage="v1" class="stage-btn pill-btn text-xs font-bold px-2.5 py-1 sm:py-1.5 rounded-md whitespace-nowrap">1ra Vuelta</button>
            <button data-stage="v2" class="stage-btn pill-btn text-xs font-bold px-2.5 py-1 sm:py-1.5 rounded-md whitespace-nowrap">2da Vuelta</button>
            <button data-stage="playoffs" class="stage-btn pill-btn text-xs font-bold px-2.5 py-1 sm:py-1.5 rounded-md whitespace-nowrap">Playoffs</button>
          </div>

          <!-- Filtro de Condición -->
          <div class="flex items-center gap-1.5">
            <label for="sel-cond" class="text-[11px] font-bold uppercase tracking-wider text-slate-500">Condición</label>
            <select id="sel-cond" class="text-xs sm:text-sm font-semibold text-slate-800 bg-slate-50 border border-slate-300 rounded-md px-2.5 py-1.5 focus:outline-none focus:border-[#0095DA]">
              <option value="all">Todos</option>
              <option value="home">Local (Estadio Yaquis)</option>
              <option value="away">Visita</option>
              <option value="vs_lhp">vs LHP (Zurdos)</option>
              <option value="vs_rhp">vs RHP (Derechos)</option>
              <option value="risp">Con Corredores en Pos. Anotadora (RISP)</option>
            </select>
          </div>
        </div>

        <!-- Estatus de Cobertura Visual & Analítica -->
        <div id="assets-status-pill" class="flex items-center gap-2 bg-[#002850] text-white border border-[#0095DA]/60 rounded-lg px-3 py-1.5 text-xs font-bold shadow-sm">
          <!-- Populated dynamically with team/photo coverage -->
        </div>
      </div>

      <!-- Navigation Tabs + Dynamic Status Pill -->
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 border-t border-slate-200 pt-1.5">
        <nav class="flex items-center gap-1 overflow-x-auto" aria-label="Módulos del Dashboard">
          <button data-tab="overview" class="tab-btn active px-3 py-2 text-xs sm:text-sm font-bold whitespace-nowrap rounded-t-md">
            01 · Resumen Ejecutivo &amp; LMP
          </button>
          <button data-tab="batting" class="tab-btn px-3 py-2 text-xs sm:text-sm font-bold whitespace-nowrap text-slate-600 rounded-t-md">
            02 · Bateo &amp; Spray Chart
          </button>
          <button data-tab="pitching" class="tab-btn px-3 py-2 text-xs sm:text-sm font-bold whitespace-nowrap text-slate-600 rounded-t-md">
            03 · Pitcheo, Zona 2D &amp; Fatiga
          </button>
          <button data-tab="scouting" class="tab-btn px-3 py-2 text-xs sm:text-sm font-bold whitespace-nowrap text-slate-600 rounded-t-md">
            04 · Scouting 360° &amp; Biometría
          </button>
        </nav>
        <div id="global-context-badge" class="text-[11px] font-semibold text-slate-600 flex items-center gap-2 pb-1 sm:pb-0"></div>
      </div>
    </div>
  </div>

  <!-- MAIN WORKSPACE -->
  <main class="max-w-[1440px] mx-auto px-4 sm:px-6 py-5 space-y-6">
    <!-- Dynamic Caveat / Season Status Banner -->
    <div id="context-alert-banner" class="hidden rounded-lg border px-4 py-2.5 text-xs sm:text-sm flex flex-wrap items-center justify-between gap-2"></div>

    <!-- Above-the-Fold Rival Matchup Comparison Banner (visible from any module when clicking an LMP club) -->
    <div id="rival-matchup-banner" class="hidden"></div>

    <!-- ========================================================== -->
    <!-- MÓDULO 1: RESUMEN EJECUTIVO & BENCHMARKING LMP              -->
    <!-- ========================================================== -->
    <section id="tab-overview" class="module-pane space-y-5">
      <!-- Grafana-Style KPI Cards Row -->
      <div id="kpi-cards-grid" class="grid grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3"></div>

      <!-- Active Condition Split Strip -->
      <div id="active-split-strip" class="card-surface p-4"></div>

      <!-- Stage Comparison + Historical Overview Grid -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Multi-Stage Comparison -->
        <div class="lg:col-span-5 card-surface p-4 flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between gap-2 mb-3">
              <div>
                <span class="jersey-ribbon bg-[#0057A8] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>DESGLOSE POR ETAPA</span></span>
                <h2 class="text-base font-extrabold text-[#002850] mt-1">1ra Vuelta vs 2da Vuelta vs Playoffs</h2>
              </div>
              <select id="sel-stage-metric" class="text-xs font-bold border border-slate-300 rounded px-2 py-1 bg-slate-50 text-[#003B73]">
                <option value="ops">OPS / wRC+ (Ofensiva)</option>
                <option value="era">ERA / FIP (Pitcheo)</option>
                <option value="cmd">InZone% / Whiff% (Comando)</option>
                <option value="def">DER% / OAA est. (Defensa)</option>
              </select>
            </div>
            <div id="stage-comparison-chart" class="w-full"></div>
            <div id="stage-story-box" class="mt-3"></div>
          </div>
          <p class="text-[11px] text-slate-500 mt-2">
            Nota: En la LMP los refuerzos e intercambios entre vueltas modifican el perfil competitivo de cada etapa; en Playoffs considera el tamaño de muestra (<span class="font-code font-bold">n</span>) de series cortas.
          </p>
        </div>

        <!-- 10-Team LMP Benchmarking Summary & Quick Visual -->
        <div class="lg:col-span-7 card-surface p-4 flex flex-col justify-between">
          <div>
            <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
              <div>
                <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>BENCHMARKING LIGA (10 CLUBES)</span></span>
                <h2 class="text-base font-extrabold text-[#002850] mt-1">Matriz Eficiencia Ofensiva vs Pitcheo LMP</h2>
              </div>
              <div class="text-[11px] text-slate-500">Eje X: <strong class="text-slate-700">wRC+</strong> · Eje Y: <strong class="text-slate-700">FIP</strong> (menor FIP arriba = mejor pitcheo)</div>
            </div>
            <div id="lmp-quadrant-chart" class="w-full overflow-x-auto"></div>
          </div>
          <div id="quadrant-story-box" class="mt-3"></div>
        </div>
      </div>

      <!-- Full Sortable 10-Club LMP Benchmarking Table -->
      <div class="card-surface p-4">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 mb-3">
          <div>
            <h2 class="text-base sm:text-lg font-extrabold text-[#002850]">Tabla Comparativa Completa de la LMP (<span id="bench-stage-label"></span>)</h2>
            <p class="text-xs text-slate-500">Haz clic en cualquier encabezado de columna para reordenar. Franquicias unificadas históricamente (id 674: Algodoneros ≤2013 / Charros ≥2014; id 6484/676: Mayos de Navojoa).</p>
          </div>
          <div class="flex flex-wrap items-center gap-1.5" id="bench-group-pills">
            <button data-bgroup="standings" class="bgroup-btn pill-btn active text-xs font-bold px-2.5 py-1 rounded">Standings &amp; Puntos LMP</button>
            <button data-bgroup="offense" class="bgroup-btn pill-btn text-xs font-bold px-2.5 py-1 rounded">Ofensiva &amp; Situacional</button>
            <button data-bgroup="pitching" class="bgroup-btn pill-btn text-xs font-bold px-2.5 py-1 rounded">Pitcheo &amp; Comando PBP</button>
            <button data-bgroup="defense" class="bgroup-btn pill-btn text-xs font-bold px-2.5 py-1 rounded">Defensa Espacial &amp; DER</button>
          </div>
        </div>
        <div id="bench-table-container" class="fo-table-wrap rounded-lg border border-slate-200"></div>
      </div>

      <!-- Bloque B: Balance Estructural de Roster (Nac/Ext/Nov & Abridores/Bullpen) -->
      <div id="overview-roster-balance-card" class="card-surface p-4 space-y-3"></div>

      <!-- HISTÓRICO 2006–2026 (21 TEMPORADAS) -->
      <div id="historical-section" class="card-surface p-4 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div>
            <span class="jersey-ribbon bg-[#E6392F] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>EVOLUCIÓN HISTÓRICA 2006–2026</span></span>
            <h2 class="text-base sm:text-lg font-extrabold text-[#002850] mt-1">Trayectoria de Yaquis de Obregón vs Promedio LMP (21 Temporadas)</h2>
            <p class="text-xs text-slate-500">Estrellas doradas señalan los campeonatos capturados en la ventana digital (2008, 2011, 2012, 2013). Las temporadas 2006–2010 tienen cobertura parcial de coordenadas PBP.</p>
          </div>
          <div class="flex items-center gap-2">
            <label for="sel-hist-metric" class="text-xs font-bold text-slate-600">Serie:</label>
            <select id="sel-hist-metric" class="text-xs font-bold text-[#003B73] bg-slate-50 border border-slate-300 rounded px-2.5 py-1.5">
              <option value="pct">PCT Ganados (Real vs Pitagórico)</option>
              <option value="ops">OPS Yaquis vs Promedio LMP</option>
              <option value="era">ERA Yaquis vs Promedio LMP</option>
              <option value="diff">Diferencial de Carreras (RS - RA)</option>
            </select>
          </div>
        </div>
        <div id="hist-story-box"></div>
        <div id="historical-chart-container" class="w-full"></div>
        <div id="historical-table-container" class="fo-table-wrap rounded-lg border border-slate-200 max-h-[380px]"></div>
      </div>
    </section>

    <!-- ========================================================== -->
    <!-- MÓDULO 2: LABORATORIO DE BATEO, SITUACIONAL & SPRAY CHART  -->
    <!-- ========================================================== -->
    <section id="tab-batting" class="module-pane hidden space-y-5">
      <div class="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <!-- Interactive Estadio Yaquis Diamond Spray Chart + Spatial Defense -->
        <div class="xl:col-span-5 telemetry-dark p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-extrabold px-2 py-0.5 uppercase"><span>DIAMANTE ESTADIO YAQUIS · STATCAST</span></span>
              <h2 class="text-base font-extrabold text-white mt-1">Spray Chart 2D &amp; Mapa Defensivo</h2>
            </div>
            <div class="flex rounded-md overflow-hidden border border-[#1E3A5F] text-xs font-bold">
              <button data-spraymode="off" class="spray-mode-btn bg-[#0072B2] text-white px-2.5 py-1">Bateo Yaquis</button>
              <button data-spraymode="def" class="spray-mode-btn bg-[#0B1320] text-slate-300 px-2.5 py-1 hover:text-white">Defensa / Rivales</button>
            </div>
          </div>

          <!-- Spray Chart Controls -->
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
            <select id="sel-spray-player" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Todo el Roster Yaquis</option>
            </select>
            <select id="sel-spray-res" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Todos los Resultados</option>
              <option value="hits">Solo Hits (1B/2B/3B/HR)</option>
              <option value="xbh">Solo Extrabases (2B/3B/HR)</option>
              <option value="hr">Solo Jonrones (HR)</option>
              <option value="outs">Solo Outs en Juego</option>
            </select>
            <select id="sel-spray-traj" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Toda Trayectoria (BIP)</option>
              <option value="line_drive">Línea (LD)</option>
              <option value="fly_ball">Elevado (FB)</option>
              <option value="ground_ball">Rola (GB)</option>
              <option value="popup">Elevado Cuadro (PU)</option>
            </select>
          </div>

          <!-- Selected Player / Club Banner -->
          <div id="spray-selected-card" class="bg-[#08101C] border border-[#1E3A5F] rounded-lg px-3 py-2 flex items-center justify-between gap-3"></div>

          <!-- SVG Diamond -->
          <div class="bg-[#08101C] rounded-lg border border-[#1E3A5F] p-2.5 flex flex-col items-center space-y-2">
            <svg id="spray-diamond-svg" viewBox="0 0 252 242" class="w-full max-w-[540px] h-auto select-none"></svg>
            <div class="flex flex-wrap justify-center gap-3 text-[11px] text-slate-300 pb-0.5">
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#0095DA] inline-block"></i> Sencillo (1B)</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full border-2 border-[#4ADE80] bg-[#16A34A] inline-block"></i> Doble (2B)</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full border-2 border-[#FDE047] bg-[#F59E0B] inline-block"></i> Triple (3B)</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rotate-45 border border-white bg-[#E6392F] inline-block"></i> Jonrón (HR)</span>
              <span class="flex items-center gap-1"><i class="w-2 h-2 rounded-full bg-[#94A3B8] opacity-70 inline-block"></i> Out en Juego</span>
            </div>
            <div id="spray-pull-bar" class="w-full pt-1 border-t border-[#1E3A5F]/70"></div>
          </div>

          <!-- Live Spray Metrics Strip -->
          <div id="spray-summary-strip" class="grid grid-cols-4 gap-2 text-center"></div>
          <div id="spray-story-box"></div>

          <!-- Spatial Defense Zone DER / OAA & Catcher CS% -->
          <div id="spatial-defense-panel" class="bg-[#08101C] border border-[#1E3A5F] rounded-lg p-3 space-y-2"></div>
        </div>

        <!-- Lineup & Situational Batting Lab Table -->
        <div class="xl:col-span-7 card-surface p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>LABORATORIO OFENSIVO</span></span>
              <h2 class="text-base sm:text-lg font-extrabold text-[#002850] mt-1">Lineup Completo, Disciplina &amp; Bateo Situacional</h2>
              <p id="bat-split-caption" class="text-xs text-slate-500"></p>
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <div class="flex items-center gap-1.5 bg-slate-50 border border-slate-300 rounded px-2.5 py-1 text-xs">
                <label for="inp-min-pa" class="font-bold text-slate-600">Mín PA:</label>
                <input id="inp-min-pa" type="number" min="0" max="300" step="5" value="10" class="w-14 bg-white border border-slate-300 rounded px-1.5 py-0.5 font-bold text-[#003B73] tabular-nums" />
              </div>
              <input id="inp-bat-search" type="search" placeholder="Buscar bateador..." class="text-xs border border-slate-300 rounded px-2.5 py-1.5 bg-slate-50 focus:outline-none focus:border-[#0095DA]" />
            </div>
          </div>

          <div id="batting-table-container" class="fo-table-wrap rounded-lg border border-slate-200 max-h-[670px]"></div>
          <p class="text-[11px] text-slate-500">Haz clic en 🎯 junto al nombre para proyectar sus batazos en el diamante, o clic en el nombre para abrir su Ficha de Scouting 360°.</p>
        </div>
      </div>

      <!-- Bloque B: Gráficas Comparativas Statcast de Bateo -->
      <div id="batting-comparative-charts" class="card-surface p-4 space-y-3"></div>
    </section>

    <!-- ========================================================== -->
    <!-- MÓDULO 3: PITCHEO, COMANDO 2D & CARGA DE TRABAJO           -->
    <!-- ========================================================== -->
    <section id="tab-pitching" class="module-pane hidden space-y-5">
      <div class="grid grid-cols-1 xl:grid-cols-12 gap-5">
        <!-- 2D Strike Zone Command Visualizer -->
        <div class="xl:col-span-5 telemetry-dark p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-extrabold px-2 py-0.5 uppercase"><span>TELEMETRÍA STATCAST 2D</span></span>
              <h2 class="text-base font-extrabold text-white mt-1">Zona de Strike, 9-Zonas &amp; Elipse 1-SD</h2>
            </div>
            <div class="flex rounded-md overflow-hidden border border-[#1E3A5F] text-[11px] font-bold">
              <button data-zonemode="dots" class="zone-mode-btn bg-[#0072B2] text-white px-2 py-1">Pitcheos + 1-SD</button>
              <button data-zonemode="heat_usage" class="zone-mode-btn bg-[#0B1320] text-slate-300 px-2 py-1 hover:text-white">9-Zonas %Uso</button>
              <button data-zonemode="heat_whiff" class="zone-mode-btn bg-[#0B1320] text-slate-300 px-2 py-1 hover:text-white">9-Zonas Whiff%</button>
            </div>
          </div>

          <!-- 2D Zone Filter Controls -->
          <div class="grid grid-cols-2 gap-2 text-xs">
            <select id="sel-zone-pitcher" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Todo el Staff de Yaquis</option>
              <option value="role:Abridor">Solo Abridores</option>
              <option value="role:Bullpen">Solo Bullpen</option>
            </select>
            <select id="sel-zone-batside" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">vs Bateadores (L &amp; R)</option>
              <option value="L">vs Bateador Zurdo (LHB)</option>
              <option value="R">vs Bateador Derecho (RHB)</option>
            </select>
            <select id="sel-zone-call" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Todo Resultado de Pitcheo</option>
              <option value="called_strike">Strikes Cantados</option>
              <option value="whiff">Swings Fallidos (Whiff)</option>
              <option value="foul">Fouls</option>
              <option value="inplay">Bolas en Juego</option>
              <option value="ball">Bolas Malas</option>
            </select>
            <select id="sel-zone-count" class="bg-[#0F1E33] border border-[#1E3A5F] text-slate-100 rounded px-2 py-1.5 font-semibold">
              <option value="all">Todo Conteo / Situación</option>
              <option value="0-0">Primer Pitcheo (0-0)</option>
              <option value="2K">Conteo con 2 Strikes</option>
              <option value="risp">Con Corredores en RISP</option>
            </select>
          </div>

          <!-- Selected Pitcher Mini-Card -->
          <div id="zone-selected-card" class="bg-[#08101C] border border-[#1E3A5F] rounded-lg px-3 py-2 flex items-center justify-between gap-3"></div>

          <div class="bg-[#08101C] rounded-lg border border-[#1E3A5F] p-2.5 flex flex-col items-center">
            <svg id="strike-zone-svg" viewBox="0 0 220 250" class="w-full max-w-[460px] h-auto select-none"></svg>
            <div id="strike-zone-legend" class="flex flex-wrap justify-center gap-3 text-[11px] text-slate-300 mt-1">
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#0095DA] inline-block"></i> Strike Cantado (C)</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#E6392F] inline-block"></i> Whiff (S)</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#F59E0B] inline-block"></i> Foul</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#16A34A] inline-block"></i> En Juego</span>
              <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#64748B] inline-block"></i> Bola</span>
            </div>
          </div>

          <div id="zone-telemetry-readout" class="grid grid-cols-3 sm:grid-cols-6 gap-2 text-center"></div>
          <div id="zone-story-box"></div>
        </div>

        <!-- Pitching Staff Table + Fatigue Semaphore -->
        <div class="xl:col-span-7 space-y-5">
          <div class="card-surface p-4 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>ROTACIÓN &amp; BULLPEN</span></span>
                <h2 class="text-base sm:text-lg font-extrabold text-[#002850] mt-1">Rendimiento Avanzado &amp; Métricas de Comando</h2>
                <p id="pit-split-caption" class="text-xs text-slate-500"></p>
              </div>
              <div class="flex flex-wrap items-center gap-1.5">
                <button data-pitrole="all" class="pit-role-btn pill-btn active text-xs font-bold px-2.5 py-1 rounded">Todos</button>
                <button data-pitrole="Abridor" class="pit-role-btn pill-btn text-xs font-bold px-2.5 py-1 rounded">Abridores</button>
                <button data-pitrole="Bullpen" class="pit-role-btn pill-btn text-xs font-bold px-2.5 py-1 rounded">Bullpen</button>
                <label class="text-[11px] font-bold text-slate-600 flex items-center gap-1 ml-1">
                  Mín IP:
                  <input id="inp-min-ip" type="number" min="0" step="1" value="0" class="w-14 text-xs font-code border border-slate-300 rounded px-1.5 py-1 bg-slate-50" />
                </label>
                <input id="inp-pit-search" type="search" placeholder="Buscar lanzador..." class="text-xs border border-slate-300 rounded px-2.5 py-1 bg-slate-50 focus:outline-none focus:border-[#0095DA]" />
              </div>
            </div>
            <div id="pitching-table-container" class="fo-table-wrap rounded-lg border border-slate-200 max-h-[380px]"></div>
          </div>

          <!-- Workload & Fatigue Monitor (7d / 14d / 30d) -->
          <div class="card-surface p-4 space-y-3">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="jersey-ribbon bg-[#E6392F] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>SEMÁFORO DE CARGA Y FATIGA</span></span>
                <h2 class="text-base font-extrabold text-[#002850] mt-1">Monitor de Volumen Acumulado (7d · 14d · 30d), B2B &amp; Últimas 3 Salidas</h2>
                <p class="text-[11px] text-slate-500">Regla 14d: <strong class="text-slate-700">Abridores ≥160/200p (límite 210p)</strong> · <strong class="text-slate-700">Relevistas ≥4G o 75p / ≥6G o 95p</strong> · alerta <span class="text-[#E6392F] font-bold">B2B</span> activa si lanzó días seguidos (descanso ≤2d)<span id="fatigue-cutoff-note" class="ml-1 font-code text-slate-600"></span></p>
              </div>
              <div class="flex items-center gap-2 text-[11px] font-bold">
                <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">● ÓPTIMO</span>
                <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800">● PRECAUCIÓN</span>
                <span class="px-2 py-0.5 rounded bg-red-100 text-red-800">● CRÍTICO</span>
              </div>
            </div>
            <div id="fatigue-cards-grid" class="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-[360px] overflow-y-auto pr-1"></div>
          </div>
        </div>
      </div>

      <!-- Bloque B: Gráficas Comparativas Statcast de Pitcheo -->
      <div id="pitching-comparative-charts" class="card-surface p-4 space-y-3"></div>
    </section>

    <!-- ========================================================== -->
    <!-- MÓDULO 4: FICHAS DE SCOUTING 360° & BIOMETRÍA              -->
    <!-- ========================================================== -->
    <section id="tab-scouting" class="module-pane hidden">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Roster Browser Sidebar -->
        <aside class="lg:col-span-4 xl:col-span-3 card-surface p-3.5 space-y-3">
          <div>
            <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>ROSTER ACTIVO / RESERVAS</span></span>
            <h2 class="text-base font-extrabold text-[#002850] mt-1">Selector de Jugadores (<span id="roster-count-label">0</span>)</h2>
          </div>
          <input id="inp-scout-search" type="search" placeholder="Nombre, país o posición..." class="w-full text-xs border border-slate-300 rounded-md px-3 py-2 bg-slate-50 focus:outline-none focus:border-[#0095DA]" />
          <div class="flex flex-wrap gap-1">
            <button data-srole="all" class="srole-btn pill-btn active text-[11px] font-bold px-2 py-1 rounded">Todos</button>
            <button data-srole="Bateador" class="srole-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Bateadores</button>
            <button data-srole="Abridor" class="srole-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Abridores</button>
            <button data-srole="Bullpen" class="srole-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Bullpen</button>
          </div>
          <div class="flex flex-wrap gap-1">
            <button data-sstatus="all" class="sstatus-btn pill-btn active text-[11px] font-bold px-2 py-1 rounded">Estatus: Todos</button>
            <button data-sstatus="Nacional" class="sstatus-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Nacional</button>
            <button data-sstatus="Extranjero" class="sstatus-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Extranjero</button>
            <button data-sstatus="Novato" class="sstatus-btn pill-btn text-[11px] font-bold px-2 py-1 rounded">Novato</button>
          </div>
          <div id="scout-roster-list" class="roster-scroll space-y-1.5 pr-1"></div>
        </aside>

        <!-- Detailed 360 Scouting Profile -->
        <div id="scout-detail-panel" class="lg:col-span-8 xl:col-span-9 space-y-5"></div>
      </div>
    </section>
  </main>

  <footer class="max-w-[1440px] mx-auto px-4 sm:px-6 py-6 text-center sm:text-left border-t border-slate-200 mt-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
    <div>
      <strong class="text-[#003B73]">Club Yaquis de Ciudad Obregón · Analítica 360° LMP (2006–2026)</strong> — Proyecto de portafolio educativo sin fines de lucro · Cero rastreadores o cookies.
    </div>
    <div>Estándar MLB Scouting 20–80 · Percentiles Savant LMP · Datos y emblemas: LMP, MLB Stats API &amp; Club Yaquis</div>
  </footer>

  <!-- Floating Tooltip for Interactive SVG Points & Bars -->
  <div id="svg-floating-tooltip"></div>

  <!-- Embedded Front Office JSON Payload -->
  <script id="fo-payload" type="application/json">__PAYLOAD_JSON__</script>

  <script>
  (() => {
    "use strict";

    // =========================================================================
    // 1. HYDRATION & GLOBAL STATE
    // =========================================================================
    const rawJson = document.getElementById("fo-payload").textContent;
    const PAYLOAD = JSON.parse(rawJson);
    const META = PAYLOAD.meta || {};
    const ZONE_CAL = META.zone_calibration || { x_lo: 82.0, x_hi: 134.3, y_lo: 115.9, y_hi: 182.8, cx: 107.9, cy: 154.1 };
    const HIST = PAYLOAD.historical_seasons || [];

    const STAGE_LABELS = {
      global_reg: "Global Rol Regular",
      v1: "1ra Vuelta",
      v2: "2da Vuelta",
      playoffs: "Playoffs",
    };
    const COND_LABELS = {
      all: "Todos",
      home: "Local (Estadio Yaquis)",
      away: "Visita",
      vs_lhp: "vs LHP (Zurdos)",
      vs_rhp: "vs RHP (Derechos)",
      risp: "Con RISP",
    };

    const state = {
      season: "2025",
      stage: "global_reg",
      cond: "all",
      tab: "overview",     // 'overview' | 'batting' | 'pitching' | 'scouting'
      highlightTeamId: 680,
      stageMetric: "ops",
      benchGroup: "standings",
      benchSort: { col: "Pts_Total", dir: -1 },
      rosterCompMode: "status",   // 'status' | 'pitchrole'
      rosterCompMetric: "OPS",    // 'OPS' | 'wRC_plus' | 'ERA' | 'FIP'
      histMetric: "pct",
      batSort: { col: "OPS", dir: -1 },
      batMinPA: 10,
      batSearch: "",
      batCompChart: "scatter",    // 'scatter' | 'boxplot' | 'wrc'
      batScatterMode: "disc",     // 'disc' (K% vs BB%) | 'power' (ISO vs AVG)
      batBoxGroup: "status",      // 'status' | 'bat_side'
      batBoxMetric: "OPS",
      sprayMode: "off",    // 'off' | 'def'
      sprayPlayer: "all",
      sprayRes: "all",
      sprayTraj: "all",
      pitSort: { col: "IP", dir: -1 },
      pitRoleFilter: "all",
      pitMinIP: 0,
      pitSearch: "",
      pitCompChart: "scatter",    // 'scatter' | 'boxplot' | 'bars'
      pitScatterMode: "cmd",      // 'cmd' (InZone% vs Whiff%) | 'erafip' (ERA vs FIP)
      pitBoxGroup: "rol",         // 'rol' | 'status'
      pitBoxMetric: "ERA",
      pitBarMode: "kbb",          // 'kbb' (K/9 vs BB/9) | 'erafip' (ERA vs FIP)
      zoneMode: "dots",    // 'dots' | 'heat_usage' | 'heat_whiff'
      zonePitcher: "all",
      zoneBatSide: "all",
      zoneCall: "all",
      zoneCount: "all",    // 'all' | '0-0' | '2K' | 'risp'
      scoutSearch: "",
      scoutRole: "all",
      scoutStatus: "all",
      selectedPlayerId: null,
      scoutCompareType: "batters",   // 'batters' | 'pitchers'
      scoutCompareSubRole: "all",    // 'all' | 'Abridor' | 'Bullpen'
      scoutCompareA: null,
      scoutCompareB: null,
    };

    // Profile lookup cache per active season
    const profileMapCache = {};
    function getProfileMap(seasonKey) {
      if (!profileMapCache[seasonKey]) {
        const map = {};
        const list = PAYLOAD.seasons?.[seasonKey]?.scouting_profiles || [];
        list.forEach((p) => { map[p.player_id] = p; });
        profileMapCache[seasonKey] = map;
      }
      return profileMapCache[seasonKey];
    }
    function getProfile(seasonKey, pid) {
      return getProfileMap(seasonKey)[pid] || {
        player_id: pid,
        full_name: `Jugador #${pid}`,
        initials: "YO",
        role_group: "Bateador",
        is_pitcher: false,
        primary_position: "UTIL",
        secondary_positions: [],
        age: null,
        birth_date: null,
        height: "—",
        weight: null,
        bat_side: "—",
        pitch_hand: "—",
        birth_country: "—",
        birth_city: "—",
        flag_code: "MX",
        roster_status: "Nacional",
        headshot_url: "",
        headshot_b64: null,
        percentiles: {},
        tools_20_80: {},
        scout_note: "Sin reporte de scouting detallado.",
        reg_pa: 0,
        reg_ip: 0,
      };
    }

    // =========================================================================
    // 2. VISUAL ASSETS: FLAGS SVG, YAQUIS CAP SILHOUETTE FALLBACK, TOOLTIPS
    // =========================================================================
    function renderFlagSVG(code) {
      const c = (code || "MX").toUpperCase();
      if (c === "MX") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="México"><rect width="7.3" height="15" fill="#006847"/><rect x="7.3" width="7.4" height="15" fill="#FFFFFF"/><rect x="14.7" width="7.3" height="15" fill="#CE1126"/><circle cx="11" cy="7.5" r="2.1" fill="#8B5A2B"/></svg>`;
      }
      if (c === "US") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Estados Unidos"><rect width="22" height="15" fill="#FFFFFF"/><g fill="#B22234"><rect y="0" width="22" height="2.2"/><rect y="4.3" width="22" height="2.2"/><rect y="8.6" width="22" height="2.2"/><rect y="12.8" width="22" height="2.2"/></g><rect width="10" height="8.6" fill="#3C3B6E"/></svg>`;
      }
      if (c === "CU") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Cuba"><rect width="22" height="15" fill="#002A8F"/><rect y="3" width="22" height="3" fill="#FFF"/><rect y="9" width="22" height="3" fill="#FFF"/><polygon points="0,0 11,7.5 0,15" fill="#CF142B"/><circle cx="3.8" cy="7.5" r="1.7" fill="#FFF"/></svg>`;
      }
      if (c === "DO") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="República Dominicana"><rect width="22" height="15" fill="#FFFFFF"/><rect x="0" y="0" width="9.2" height="6.2" fill="#002D62"/><rect x="12.8" y="0" width="9.2" height="6.2" fill="#CE1126"/><rect x="0" y="8.8" width="9.2" height="6.2" fill="#CE1126"/><rect x="12.8" y="8.8" width="9.2" height="6.2" fill="#002D62"/></svg>`;
      }
      if (c === "VE") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Venezuela"><rect width="22" height="5" fill="#FCD116"/><rect y="5" width="22" height="5" fill="#003893"/><rect y="10" width="22" height="5" fill="#CE1126"/><circle cx="11" cy="7.5" r="1.4" fill="#FFF"/></svg>`;
      }
      if (c === "PA") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Panamá"><rect width="22" height="15" fill="#FFF"/><rect x="11" y="0" width="11" height="7.5" fill="#DA121A"/><rect x="0" y="7.5" width="11" height="7.5" fill="#072357"/><circle cx="5.5" cy="3.8" r="1.8" fill="#072357"/><circle cx="16.5" cy="11.2" r="1.8" fill="#DA121A"/></svg>`;
      }
      if (c === "CO") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Colombia"><rect width="22" height="7.5" fill="#FCD116"/><rect y="7.5" width="22" height="3.75" fill="#003893"/><rect y="11.25" width="22" height="3.75" fill="#CE1126"/></svg>`;
      }
      if (c === "JP") {
        return `<svg width="22" height="15" viewBox="0 0 22 15" class="rounded-[2px] border border-slate-300 shrink-0" title="Japón"><rect width="22" height="15" fill="#FFFFFF"/><circle cx="11" cy="7.5" r="4" fill="#BC002D"/></svg>`;
      }
      return `<span class="inline-block px-1.5 py-0.5 text-[10px] font-bold bg-slate-200 text-slate-700 rounded">${esc(c)}</span>`;
    }

    let capSvgSeq = 0;
    function renderYaquisCapSilhouetteSVG(initials, sizeClass = "w-full h-full") {
      const gid = `capBgGrad_${++capSvgSeq}`;
      return `
        <svg viewBox="0 0 120 150" class="${sizeClass}" role="img" aria-label="Silueta gorra Yaquis de Obregón">
          <defs>
            <linearGradient id="${gid}" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stop-color="#002850"/>
              <stop offset="100%" stop-color="#0057A8"/>
            </linearGradient>
          </defs>
          <rect width="120" height="150" rx="12" fill="url(#${gid})"/>
          <circle cx="60" cy="68" r="50" fill="#0B1320" fill-opacity="0.35" stroke="#0095DA" stroke-opacity="0.45" stroke-width="1.5"/>
          <!-- Shoulders -->
          <path d="M18 144 C20 112, 38 100, 60 100 C82 100, 100 112, 102 144 Z" fill="#0F2744" stroke="#7DD3FC" stroke-opacity="0.4" stroke-width="1"/>
          <!-- Head silhouette -->
          <path d="M40 62 C40 85, 49 95, 60 95 C71 95, 80 85, 80 62 Z" fill="#1E3A5F"/>
          <!-- Yaquis Cap Dome + Visor -->
          <path d="M34 56 C34 33, 46 25, 60 25 C74 25, 86 33, 86 56 Z" fill="#003B73" stroke="#0095DA" stroke-width="1.5"/>
          <path d="M32 56 Q60 48 97 59 Q77 65 32 58 Z" fill="#001F3F" stroke="#0095DA" stroke-width="1.2"/>
          <!-- CO Cap Insignia -->
          <text x="60" y="46" text-anchor="middle" fill="#FFFFFF" font-size="12" font-weight="900" font-family="Bahnschrift, sans-serif" letter-spacing="-0.5">CO</text>
          <!-- Player Initials Badge -->
          <rect x="38" y="112" width="44" height="19" rx="4" fill="#0095DA"/>
          <text x="60" y="125" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="800" font-family="Consolas, monospace">${esc(initials || "YO")}</text>
        </svg>`;
    }

    function renderPlayerAvatar(profile, boxClass = "w-24 h-[120px]", roundedClass = "rounded-xl") {
      const pidKey = profile?.player_id != null ? String(profile.player_id) : "";
      const src = META.player_photos?.[pidKey] || profile?.headshot_b64 || "";
      const fallbackSvg = encodeURIComponent(renderYaquisCapSilhouetteSVG(profile?.initials || "YO", "w-full h-full"));
      const fallbackUri = `data:image/svg+xml;charset=utf-8,${fallbackSvg}`;
      if (!src) {
        return `<div class="${boxClass} ${roundedClass} overflow-hidden border-2 border-[#0095DA] bg-[#0D2542] shrink-0 shadow">${renderYaquisCapSilhouetteSVG(profile?.initials || "YO")}</div>`;
      }
      return `
        <div class="${boxClass} ${roundedClass} overflow-hidden border-2 border-[#0095DA] bg-[#0D2542] shrink-0 shadow">
          <img src="${esc(src)}" alt="${esc(profile?.full_name || "Jugador")}"
               class="w-full h-full object-cover object-top block"
               onerror="this.onerror=null;this.src='${fallbackUri}';" />
        </div>`;
    }

    function renderTeamLogo(teamId, equipoName = "", sizeClass = "w-8 h-8") {
      const entry = META.team_logos?.[String(teamId)];
      const code = entry?.code || (equipoName || "LMP").slice(0, 3).toUpperCase();
      const svgFb = encodeURIComponent(`<svg viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg"><circle cx="20" cy="20" r="19" fill="#003B73" stroke="#0095DA" stroke-width="2"/><text x="20" y="24.5" text-anchor="middle" fill="#FFFFFF" font-size="11" font-weight="900" font-family="Bahnschrift, sans-serif">${esc(code)}</text></svg>`);
      const uri = entry?.data_uri || entry?.svg_uri || `data:image/svg+xml;charset=utf-8,${svgFb}`;
      return `
        <span class="inline-flex items-center justify-center ${sizeClass} rounded-full bg-white p-0.5 border border-slate-200 shadow-sm shrink-0 overflow-hidden" title="${esc(equipoName || code)}">
          <img src="${esc(uri)}" alt="${esc(equipoName || code)}" class="w-full h-full object-contain"
               onerror="this.onerror=null;this.src='data:image/svg+xml;charset=utf-8,${svgFb}';" />
        </span>`;
    }

    function initBrandLogos() {
      const logos = META.logos || {};
      const coWrap = document.getElementById("header-co-wrap");
      const coFallback = `<svg viewBox="0 0 64 64" class="w-full h-full"><text x="32" y="42" text-anchor="middle" fill="#FFFFFF" font-size="28" font-weight="900">CO</text></svg>`;
      if (logos.co_monogram) {
        const img = document.createElement("img");
        img.src = logos.co_monogram;
        img.alt = "Monograma CO Yaquis";
        img.className = "w-full h-full object-contain";
        img.onerror = () => { coWrap.innerHTML = coFallback; };
        coWrap.innerHTML = "";
        coWrap.appendChild(img);
      } else {
        coWrap.innerHTML = coFallback;
      }

      const mWrap = document.getElementById("header-mascot-wrap");
      if (logos.mascot) {
        const imgM = document.createElement("img");
        imgM.src = logos.mascot;
        imgM.alt = "Mascota Yaquis de Obregón";
        imgM.className = "w-full h-full object-contain";
        imgM.onerror = () => { mWrap.style.display = "none"; };
        mWrap.innerHTML = "";
        mWrap.appendChild(imgM);
      } else {
        mWrap.style.display = "none";
      }

      const wmWrap = document.getElementById("header-wordmark-wrap");
      if (wmWrap && logos.yaquis_wordmark) {
        const imgW = document.createElement("img");
        imgW.src = logos.yaquis_wordmark;
        imgW.alt = "Wordmark Oficial Yaquis";
        imgW.className = "h-9 sm:h-10 w-auto object-contain drop-shadow";
        imgW.onerror = () => { wmWrap.style.display = "none"; };
        wmWrap.innerHTML = "";
        wmWrap.appendChild(imgW);
      }

      const lmpWrap = document.getElementById("header-lmp-wrap");
      const lmpFallback = `<svg viewBox="0 0 24 26" class="w-9 h-9"><path d="M12 1 L22 4.5 V12.5 C22 18.8 17.5 23.2 12 25 C6.5 23.2 2 18.8 2 12.5 V4.5 Z" fill="#0057A8" stroke="#0095DA" stroke-width="1.4"/><text x="12" y="15.5" text-anchor="middle" fill="#FFFFFF" font-size="7.5" font-weight="900">LMP</text></svg>`;
      if (lmpWrap) {
        if (logos.lmp_shield) {
          const imgL = document.createElement("img");
          imgL.src = logos.lmp_shield;
          imgL.alt = "Escudo Oficial LMP";
          imgL.className = "w-full h-full object-contain";
          imgL.onerror = () => { lmpWrap.innerHTML = lmpFallback; };
          lmpWrap.innerHTML = "";
          lmpWrap.appendChild(imgL);
        } else {
          lmpWrap.innerHTML = lmpFallback;
        }
      }

      const pill = document.getElementById("assets-status-pill");
      if (pill) {
        pill.innerHTML = `
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Analítica 360°</span>
          <span class="text-[#7DD3FC] font-code">· Front Office LMP</span>`;
      }
    }

    const sameClub = (a, b) => Number(a) === Number(b) || ((Number(a) === 676 || Number(a) === 6484) && (Number(b) === 676 || Number(b) === 6484));

    function renderHeaderClubsStrip(seasonKey) {
      const strip = document.getElementById("header-lmp-clubs-strip");
      if (!strip) return;
      const teams = PAYLOAD.seasons?.[seasonKey]?.team_benchmarks?.global_reg?.teams || [];
      if (!teams.length) {
        strip.innerHTML = "";
        return;
      }
      const ordered = [...teams].sort((a, b) => (b.team_id === 680) - (a.team_id === 680) || (b.PCT - a.PCT));
      const activeRival = ordered.find((t) => sameClub(t.team_id, state.highlightTeamId) && t.team_id !== 680);
      strip.innerHTML = ordered.map((t) => {
        const isY = t.team_id === 680;
        const isHi = sameClub(state.highlightTeamId, t.team_id);
        const short = (t.equipo || "").split(" ")[0];
        const cls = isHi
          ? (isY ? "bg-[#0072B2] border-2 border-[#7DD3FC] shadow" : "bg-amber-400 border-2 border-amber-200 text-[#0B1320] shadow")
          : "bg-[#0B1320]/50 border border-white/15 hover:border-[#7DD3FC]";
        const txtCls = isHi && !isY ? "text-[#0B1320]" : (isHi || isY ? "text-white" : "text-slate-200");
        return `
          <button data-club-tid="${t.team_id}" class="club-strip-btn flex items-center gap-1.5 px-2 py-1 rounded-full transition cursor-pointer ${cls}" title="${isY ? "Restablecer vista Yaquis" : `Comparar Yaquis vs ${esc(t.equipo)}`} (${t.W}-${t.L}, PCT ${fmtRate(t.PCT)})">
            ${renderTeamLogo(t.team_id, t.equipo, "w-7 h-7")}
            <span class="text-[11px] font-bold ${txtCls} hidden xl:inline">${esc(short)}</span>
          </button>`;
      }).join("") + `<span class="text-[10.5px] font-semibold ${activeRival ? "text-amber-300" : "text-sky-200/80"} ml-1">${activeRival ? `Frente a Frente: ${esc(activeRival.equipo)} (clic para limpiar)` : "Clic en un rival para comparar vs Yaquis"}</span>`;

      strip.querySelectorAll(".club-strip-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const tid = Number(btn.dataset.clubTid);
          state.highlightTeamId = (sameClub(state.highlightTeamId, tid) && tid !== 680) ? 680 : tid;
          renderAll();
        });
      });
    }

    function renderRivalMatchupBanner() {
      const wrap = document.getElementById("rival-matchup-banner");
      if (!wrap) return;
      if (!state.highlightTeamId || state.highlightTeamId === 680) {
        wrap.className = "hidden";
        wrap.innerHTML = "";
        return;
      }
      const { data: sdata } = activeSeasonData();
      let stgUsed = state.stage;
      let teams = sdata.team_benchmarks?.[stgUsed]?.teams || [];
      let yaq = teams.find((t) => t.team_id === 680);
      let rival = teams.find((t) => sameClub(t.team_id, state.highlightTeamId));
      let fallbackNote = "";

      if (!yaq || !rival) {
        stgUsed = "global_reg";
        teams = sdata.team_benchmarks?.global_reg?.teams || [];
        yaq = teams.find((t) => t.team_id === 680);
        rival = teams.find((t) => sameClub(t.team_id, state.highlightTeamId));
        if (!yaq || !rival) {
          wrap.className = "hidden";
          wrap.innerHTML = "";
          return;
        }
        fallbackNote = ` · Sin cruce activo en ${STAGE_LABELS[state.stage]}; comparando Global Rol Regular`;
      }

      const ranked = [...teams].sort((a, b) =>
        (stgUsed !== "playoffs" ? ((b.Pts_Total ?? -1) - (a.Pts_Total ?? -1)) : 0)
        || ((b.PCT ?? 0) - (a.PCT ?? 0))
        || ((b.Diff ?? 0) - (a.Diff ?? 0))
      );
      const posY = ranked.findIndex((t) => t.team_id === 680) + 1;
      const posR = ranked.findIndex((t) => sameClub(t.team_id, rival.team_id)) + 1;

      const deltaFormatters = {
        rate3: (d) => d.toFixed(3).replace(/^(-?)0\./, "$1."),
        dec2: (d) => d.toFixed(2),
        dec1: (d) => d.toFixed(1),
        pct1: (d) => `${d.toFixed(1)}%`,
        int0: (d) => String(Math.round(d)),
      };
      const cmpLine = (label, vy, vr, fmtFn, higherBetter = true, dFmtKey = "dec2") => {
        const ny = Number(vy), nr = Number(vr);
        const valid = vy !== null && vy !== undefined && vr !== null && vr !== undefined && Number.isFinite(ny) && Number.isFinite(nr);
        const yWins = valid && (higherBetter ? ny > nr : ny < nr);
        const rWins = valid && (higherBetter ? nr > ny : nr < ny);
        const diff = valid ? ny - nr : 0;
        const sign = diff > 0 ? "+" : "";
        const dStr = valid
          ? (diff === 0 ? "0" : `${sign}${(deltaFormatters[dFmtKey] || deltaFormatters.dec2)(diff)}`)
          : "—";
        return `
          <div class="flex items-center justify-between gap-2 text-[11px] py-1 border-b border-slate-100 last:border-0">
            <span class="font-bold text-slate-600">${esc(label)}</span>
            <div class="flex items-center gap-2 font-code tabular-nums">
              <span class="${yWins ? "font-black text-[#003B73] bg-sky-50 px-1 rounded" : "text-slate-700"}">${esc(fmtFn(vy))}</span>
              <span class="text-slate-400">vs</span>
              <span class="${rWins ? "font-black text-amber-800 bg-amber-100 px-1 rounded" : "text-slate-700"}">${esc(fmtFn(vr))}</span>
              <span class="text-[10px] font-bold ${yWins ? "text-emerald-700" : (rWins ? "text-red-700" : "text-slate-400")} w-16 text-right">Δ ${esc(dStr)}</span>
            </div>
          </div>`;
      };

      const ofAvgY = [yaq.DER_LF, yaq.DER_CF, yaq.DER_RF].filter((x) => x !== null && x !== undefined);
      const ofAvgR = [rival.DER_LF, rival.DER_CF, rival.DER_RF].filter((x) => x !== null && x !== undefined);
      const derOfY = ofAvgY.length ? ofAvgY.reduce((a, b) => a + b, 0) / ofAvgY.length : null;
      const derOfR = ofAvgR.length ? ofAvgR.reduce((a, b) => a + b, 0) / ofAvgR.length : null;

      const edges = [];
      const yWrc = Number(yaq.wRC_plus || 0), rWrc = Number(rival.wRC_plus || 0);
      if (yWrc > rWrc) edges.push(`Ataque +${Math.round(yWrc - rWrc)} wRC+`);
      else if (yWrc === rWrc) edges.push(`Empate ataque (${fmtInt(yWrc)} wRC+)`);
      else edges.push(`Rival lidera ataque (${fmtInt(rWrc)} vs ${fmtInt(yWrc)} wRC+)`);

      const yFip = Number(yaq.FIP || 9), rFip = Number(rival.FIP || 9);
      if (yFip < rFip) edges.push(`Pitcheo mejor FIP (${fmtNum(yaq.FIP,2)} vs ${fmtNum(rival.FIP,2)})`);
      else if (yFip === rFip) edges.push(`Empate FIP (${fmtNum(yaq.FIP,2)})`);
      else edges.push(`Rival lidera FIP (${fmtNum(rival.FIP,2)} vs ${fmtNum(yaq.FIP,2)})`);

      const yDer = Number(yaq.DER_pct || 0), rDer = Number(rival.DER_pct || 0);
      if (yDer > rDer) edges.push(`Defensa +${(yDer - rDer).toFixed(1)}% DER`);
      else if (yDer === rDer) edges.push(`Empate DER% (${fmtNum(yaq.DER_pct,1,"%")})`);
      else edges.push(`Rival mejor DER% (${fmtNum(rival.DER_pct,1,"%")} vs ${fmtNum(yaq.DER_pct,1,"%")})`);

      wrap.className = "card-surface p-4 border-t-4 border-t-[#D97706] shadow-md space-y-3";
      wrap.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200">
          <div class="flex flex-wrap items-center gap-2.5">
            <span class="jersey-ribbon bg-[#D97706] text-white text-[10px] font-black px-2 py-0.5 uppercase"><span>FRENTE A FRENTE LMP</span></span>
            <div class="flex items-center gap-2 text-sm sm:text-base font-black text-[#002850]">
              ${renderTeamLogo(680, "Yaquis", "w-7 h-7")}
              <span>Yaquis (#${posY} · ${yaq.W}-${yaq.L})</span>
              <span class="text-slate-400 font-bold text-xs">VS</span>
              ${renderTeamLogo(rival.team_id, rival.equipo, "w-7 h-7")}
              <span class="text-amber-900">${esc(rival.equipo)} (#${posR} · ${rival.W}-${rival.L})</span>
            </div>
            <span class="text-[11px] font-semibold text-slate-500">${esc(STAGE_LABELS[stgUsed])}${esc(fallbackNote)}</span>
          </div>
          <div class="flex items-center gap-2">
            <button id="btn-rival-goto-overview" class="text-xs font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-2.5 py-1 rounded transition">Ver en Matriz &amp; Tabla LMP ↓</button>
            <button id="btn-rival-clear" class="text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 px-2.5 py-1 rounded transition">× Cerrar comparativa</button>
          </div>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3">
          <div class="bg-slate-50/80 border border-slate-200 rounded-lg p-2.5">
            <div class="text-[10.5px] font-extrabold uppercase tracking-wider text-[#003B73] mb-1">1. Récord &amp; Puntos LMP</div>
            ${cmpLine("PCT Ganados", yaq.PCT, rival.PCT, (v) => fmtRate(v), true, "rate3")}
            ${cmpLine("Pts Totales LMP", yaq.Pts_Total, rival.Pts_Total, (v) => fmtNum(v,1), true, "dec1")}
            ${cmpLine("Diferencial", yaq.Diff, rival.Diff, (v) => (v > 0 ? `+${v}` : String(v)), true, "int0")}
            ${cmpLine("Pyth PCT", yaq.Pyth_PCT, rival.Pyth_PCT, (v) => fmtRate(v), true, "rate3")}
          </div>
          <div class="bg-slate-50/80 border border-slate-200 rounded-lg p-2.5">
            <div class="text-[10.5px] font-extrabold uppercase tracking-wider text-[#0072B2] mb-1">2. Ataque &amp; Situacional</div>
            ${cmpLine("OPS Equipo", yaq.OPS, rival.OPS, (v) => fmtRate(v), true, "rate3")}
            ${cmpLine("wRC+ Ofensivo", yaq.wRC_plus, rival.wRC_plus, fmtInt, true, "int0")}
            ${cmpLine("AVG con RISP", yaq.RISP_AVG, rival.RISP_AVG, (v) => fmtRate(v), true, "rate3")}
            ${cmpLine("BB% Equipo", yaq.BB_pct, rival.BB_pct, (v) => fmtNum(v,1,"%"), true, "pct1")}
            ${cmpLine("Jonrones (HR)", yaq.HR, rival.HR, fmtInt, true, "int0")}
          </div>
          <div class="bg-slate-50/80 border border-slate-200 rounded-lg p-2.5">
            <div class="text-[10.5px] font-extrabold uppercase tracking-wider text-[#0057A8] mb-1">3. Pitcheo &amp; Comando</div>
            ${cmpLine("ERA Staff", yaq.ERA, rival.ERA, (v) => fmtNum(v,2), false, "dec2")}
            ${cmpLine("FIP Staff", yaq.FIP, rival.FIP, (v) => fmtNum(v,2), false, "dec2")}
            ${cmpLine("InZone%", yaq.InZone_pct, rival.InZone_pct, (v) => fmtNum(v,1,"%"), true, "pct1")}
            ${cmpLine("Whiff%", yaq.Whiff_pct, rival.Whiff_pct, (v) => fmtNum(v,1,"%"), true, "pct1")}
          </div>
          <div class="bg-slate-50/80 border border-slate-200 rounded-lg p-2.5">
            <div class="text-[10.5px] font-extrabold uppercase tracking-wider text-emerald-700 mb-1">4. Defensa Espacial</div>
            ${cmpLine("DER% Global", yaq.DER_pct, rival.DER_pct, (v) => fmtNum(v,1,"%"), true, "pct1")}
            ${cmpLine("OAA Estimado", yaq.OAA_est, rival.OAA_est, (v) => (v > 0 ? `+${fmtNum(v,1)}` : fmtNum(v,1)), true, "dec1")}
            ${cmpLine("DER Infield", yaq.DER_INF, rival.DER_INF, (v) => fmtNum(v,1,"%"), true, "pct1")}
            ${cmpLine("DER Jardines", derOfY, derOfR, (v) => fmtNum(v,1,"%"), true, "pct1")}
            ${cmpLine("CS% Receptores", yaq.C_CS_pct, rival.C_CS_pct, (v) => fmtNum(v,1,"%"), true, "pct1")}
          </div>
        </div>
        <div class="bg-amber-50/90 border-l-4 border-[#D97706] rounded-r px-3 py-1.5 text-xs text-slate-800">
          <strong class="text-amber-900">Diagnóstico Táctico Directo:</strong> ${esc(edges.join(" · "))} · CS% Receptores Yaquis <strong>${fmtNum(yaq.C_CS_pct,1,"%")}</strong> vs ${fmtNum(rival.C_CS_pct,1,"%")}.
        </div>`;

      document.getElementById("btn-rival-clear")?.addEventListener("click", () => {
        state.highlightTeamId = 680;
        renderAll();
      });
      document.getElementById("btn-rival-goto-overview")?.addEventListener("click", () => {
        state.tab = "overview";
        if (state.season === "hist") state.season = "2025";
        renderAll();
        setTimeout(() => {
          document.getElementById("lmp-quadrant-chart")?.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 50);
      });
    }

    // Floating tooltip helper
    const tooltipEl = document.getElementById("svg-floating-tooltip");
    function showTooltip(evt, htmlContent) {
      tooltipEl.innerHTML = htmlContent;
      tooltipEl.style.display = "block";
      const pad = 14;
      let x = evt.clientX + pad;
      let y = evt.clientY + pad;
      if (x + 275 > window.innerWidth) x = evt.clientX - 275;
      if (y + 120 > window.innerHeight) y = evt.clientY - 120;
      tooltipEl.style.left = `${Math.max(8, x)}px`;
      tooltipEl.style.top = `${Math.max(8, y)}px`;
    }
    function hideTooltip() {
      tooltipEl.style.display = "none";
    }

    // =========================================================================
    // 3. FORMATTING & UTILITY HELPERS
    // =========================================================================
    function esc(v) {
      return String(v ?? "").replace(/[&<>"']/g, (m) => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;"
      }[m]));
    }
    function fmtRate(v, digits = 3) {
      if (v === null || v === undefined || v === "" || !Number.isFinite(Number(v))) return "—";
      const n = Number(v);
      const s = n.toFixed(digits);
      return digits === 3 && n >= 0 && n < 1 ? s.replace(/^0/, "") : s;
    }
    function fmtNum(v, digits = 1, suffix = "") {
      if (v === null || v === undefined || v === "" || !Number.isFinite(Number(v))) return "—";
      return Number(v).toFixed(digits) + suffix;
    }
    function fmtInt(v) {
      if (v === null || v === undefined || v === "" || !Number.isFinite(Number(v))) return "—";
      return String(Math.round(Number(v)));
    }
    const EV_ES = {
      single: "Sencillo (1B)", double: "Doble (2B)", triple: "Triple (3B)", home_run: "Jonrón (HR)",
      field_out: "Out en Juego", grounded_into_double_play: "Doble Play (RO)", force_out: "Out Forzado",
      field_error: "Error Defensivo", sac_fly: "Fly de Sacrificio", sac_bunt: "Toque de Sacrificio",
      fielders_choice: "Bola Ocupada", fielders_choice_out: "Out Ocupada", double_play: "Doble Play",
      sac_fly_double_play: "Doble Play Sacrificio"
    };
    const TRAJ_ES = {
      line_drive: "Línea (LD)", fly_ball: "Elevado (FB)", ground_ball: "Rola (GB)", popup: "Elevado Cuadro (PU)",
      bunt_grounder: "Toque Rola (BG)", bunt_popup: "Toque Elevado (BP)", bunt_line_drive: "Toque Línea (BL)"
    };
    const HARD_ES = { hard: "Contacto Fuerte", medium: "Contacto Medio", soft: "Contacto Débil" };
    const CALL_ES = {
      C: "Strike Cantado", S: "Swing Fallido (Whiff)", M: "Toque Fallido", W: "Whiff en Tiro",
      F: "Foul", T: "Foul Tip", L: "Bunt Foul", O: "Foul Bunt / Otro",
      X: "En Juego (Out)", D: "En Juego (No Out)", E: "En Juego (Hit)", H: "Hit by Pitch (HBP)",
      B: "Bola", "*B": "Bola en Tierra", P: "Pitchout"
    };
    const HIT_LOC_ES = { "1": "P", "2": "C", "3": "1B", "4": "2B", "5": "3B", "6": "SS", "7": "LF", "8": "CF", "9": "RF" };

    function pctBadgeColor(pct) {
      const p = Number(pct ?? 50);
      if (p >= 85) return "#E6392F";
      if (p >= 65) return "#F97316";
      if (p >= 40) return "#64748B";
      if (p >= 20) return "#2563EB";
      return "#1D4ED8";
    }
    function seededJitter(seed, span = 18) {
      const s = Math.sin((Number(seed) || 1) * 12.9898 + 78.233) * 43758.5453;
      const frac = s - Math.floor(s);
      return (frac - 0.5) * 2 * span;
    }
    function quantile(sortedVals, q) {
      if (!sortedVals.length) return 0;
      if (sortedVals.length === 1) return sortedVals[0];
      const pos = (sortedVals.length - 1) * q;
      const lo = Math.floor(pos);
      const hi = Math.ceil(pos);
      return lo === hi ? sortedVals[lo] : sortedVals[lo] + (sortedVals[hi] - sortedVals[lo]) * (pos - lo);
    }

    function buildBoxplotSwarmSVG({ groups, metricLabel, fmt, higherIsBetter = true, height = 270 }) {
      const nonEmpty = groups.filter((g) => g.items.length > 0);
      if (!nonEmpty.length) {
        return `<div class="text-xs text-slate-500 py-8 text-center">Sin muestra suficiente para construir el boxplot.</div>`;
      }
      const allVals = nonEmpty.flatMap((g) => g.items.map((it) => Number(it.val))).filter((v) => Number.isFinite(v));
      if (!allVals.length) {
        return `<div class="text-xs text-slate-500 py-8 text-center">Sin valores numéricos válidos para ${esc(metricLabel)}.</div>`;
      }
      let minV = Math.min(...allVals);
      let maxV = Math.max(...allVals);
      const span = Math.max(0.001, maxV - minV);
      minV -= span * 0.14;
      maxV += span * 0.16;

      const W = 680, H = height, pL = 58, pR = 24, pT = 34, pB = 48;
      const sy = (v) => higherIsBetter
        ? H - pB - ((v - minV) / Math.max(0.001, maxV - minV)) * (H - pT - pB)
        : pT + ((v - minV) / Math.max(0.001, maxV - minV)) * (H - pT - pB);
      const colW = (W - pL - pR) / nonEmpty.length;

      let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full h-auto bg-slate-50/60 rounded-lg border border-slate-200 select-none">`;
      svg += `<text x="${pL}" y="19" font-size="10.5" font-weight="800" fill="#002850">${esc(metricLabel)} <tspan fill="#64748B" font-weight="600">(${higherIsBetter ? "↑ Más alto es mejor" : "↓ Más bajo es mejor"})</tspan></text>`;

      for (let i = 0; i <= 4; i++) {
        const val = minV + (i / 4) * (maxV - minV);
        const yy = sy(val);
        svg += `<line x1="${pL}" y1="${yy.toFixed(1)}" x2="${W - pR}" y2="${yy.toFixed(1)}" stroke="#E2E8F0" stroke-width="1"/>`;
        svg += `<text x="${pL - 7}" y="${(yy + 3.5).toFixed(1)}" text-anchor="end" font-size="10" fill="#64748B" font-family="Consolas, monospace">${esc(fmt(val))}</text>`;
      }

      nonEmpty.forEach((grp, idx) => {
        const cx = pL + colW * (idx + 0.5);
        const vals = grp.items.map((it) => Number(it.val)).filter(Number.isFinite).sort((a, b) => a - b);
        const q1 = quantile(vals, 0.25);
        const med = quantile(vals, 0.5);
        const q3 = quantile(vals, 0.75);
        const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
        const iqr = q3 - q1;
        const loW = vals.find((v) => v >= q1 - 1.5 * iqr) ?? vals[0];
        const hiW = [...vals].reverse().find((v) => v <= q3 + 1.5 * iqr) ?? vals[vals.length - 1];
        const boxW = Math.min(72, colW * 0.44);

        const yQ1 = sy(q1), yQ3 = sy(q3), yMed = sy(med), yMean = sy(mean), yLo = sy(loW), yHi = sy(hiW);
        const topBox = Math.min(yQ1, yQ3), boxH = Math.max(3, Math.abs(yQ1 - yQ3));

        // Whiskers
        svg += `<line x1="${cx.toFixed(1)}" y1="${yLo.toFixed(1)}" x2="${cx.toFixed(1)}" y2="${yHi.toFixed(1)}" stroke="${grp.color}" stroke-width="1.6" stroke-dasharray="3 2"/>`;
        svg += `<line x1="${(cx - boxW * 0.25).toFixed(1)}" y1="${yLo.toFixed(1)}" x2="${(cx + boxW * 0.25).toFixed(1)}" y2="${yLo.toFixed(1)}" stroke="${grp.color}" stroke-width="1.6"/>`;
        svg += `<line x1="${(cx - boxW * 0.25).toFixed(1)}" y1="${yHi.toFixed(1)}" x2="${(cx + boxW * 0.25).toFixed(1)}" y2="${yHi.toFixed(1)}" stroke="${grp.color}" stroke-width="1.6"/>`;

        // IQR Box
        svg += `<rect x="${(cx - boxW / 2).toFixed(1)}" y="${topBox.toFixed(1)}" width="${boxW.toFixed(1)}" height="${boxH.toFixed(1)}" rx="4" fill="${grp.color}" fill-opacity="0.18" stroke="${grp.color}" stroke-width="2"/>`;
        // Median line + Mean diamond
        svg += `<line x1="${(cx - boxW / 2).toFixed(1)}" y1="${yMed.toFixed(1)}" x2="${(cx + boxW / 2).toFixed(1)}" y2="${yMed.toFixed(1)}" stroke="${grp.color}" stroke-width="3.2"/>`;
        svg += `<polygon points="${cx.toFixed(1)},${(yMean - 4.5).toFixed(1)} ${(cx + 4.5).toFixed(1)},${yMean.toFixed(1)} ${cx.toFixed(1)},${(yMean + 4.5).toFixed(1)} ${(cx - 4.5).toFixed(1)},${yMean.toFixed(1)}" fill="#FFFFFF" stroke="${grp.color}" stroke-width="1.8"/>`;

        // Swarm dots (compact 3.2px with seeded jitter)
        const jitSpan = Math.max(10, boxW * 0.36);
        grp.items.forEach((it) => {
          const px = cx + seededJitter(it.id, jitSpan);
          const py = sy(Number(it.val));
          svg += `<circle class="comp-pt cursor-pointer" cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="3.4" fill="${grp.color}" fill-opacity="0.88" stroke="#FFFFFF" stroke-width="1" data-tip="${esc(`<strong>${esc(it.name)}</strong> (${esc(grp.label)})<br>${esc(metricLabel)}: <b>${esc(fmt(it.val))}</b>${it.sub ? `<br>${esc(it.sub)}` : ""}`)}"/>`;
        });

        svg += `<text x="${cx.toFixed(1)}" y="${H - 24}" text-anchor="middle" font-size="11.5" font-weight="800" fill="#002850">${esc(grp.label)} (${vals.length})</text>`;
        svg += `<text x="${cx.toFixed(1)}" y="${H - 10}" text-anchor="middle" font-size="9.5" font-weight="700" fill="#475569" font-family="Consolas, monospace">Med ${esc(fmt(med))} · Prom ${esc(fmt(mean))}</text>`;
      });
      svg += `</svg>`;
      return svg;
    }

    function buildStatcastScatterSVG({ points, xLabel, yLabel, xAvg, yAvg, invertX = false, invertY = false, fmtX, fmtY, diagLine = false, diagLabel = "" }) {
      if (!points.length) {
        return `<div class="text-xs text-slate-500 py-8 text-center">Sin jugadores bajo el filtro mínimo actual para graficar.</div>`;
      }
      const xs = points.map((p) => Number(p.x)).filter(Number.isFinite);
      const ys = points.map((p) => Number(p.y)).filter(Number.isFinite);
      if (xAvg !== null && xAvg !== undefined && Number.isFinite(xAvg)) xs.push(xAvg);
      if (yAvg !== null && yAvg !== undefined && Number.isFinite(yAvg)) ys.push(yAvg);
      let xMin = Math.min(...xs), xMax = Math.max(...xs);
      let yMin = Math.min(...ys), yMax = Math.max(...ys);
      const xPad = Math.max(0.005, (xMax - xMin) * 0.14);
      const yPad = Math.max(0.005, (yMax - yMin) * 0.16);
      xMin -= xPad; xMax += xPad;
      yMin -= yPad; yMax += yPad;

      const W = 720, H = 310, pL = 56, pR = 26, pT = 30, pB = 42;
      const sx = (v) => invertX
        ? W - pR - ((v - xMin) / Math.max(0.001, xMax - xMin)) * (W - pL - pR)
        : pL + ((v - xMin) / Math.max(0.001, xMax - xMin)) * (W - pL - pR);
      const sy = (v) => invertY
        ? pT + ((v - yMin) / Math.max(0.001, yMax - yMin)) * (H - pT - pB)
        : H - pB - ((v - yMin) / Math.max(0.001, yMax - yMin)) * (H - pT - pB);

      let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full h-auto bg-slate-50/70 rounded-lg border border-slate-200 select-none">`;
      // Grid
      for (let i = 0; i <= 4; i++) {
        const xv = xMin + (i / 4) * (xMax - xMin);
        const yv = yMin + (i / 4) * (yMax - yMin);
        const xx = sx(xv), yy = sy(yv);
        svg += `<line x1="${xx.toFixed(1)}" y1="${pT}" x2="${xx.toFixed(1)}" y2="${H - pB}" stroke="#E2E8F0" stroke-width="1"/>`;
        svg += `<text x="${xx.toFixed(1)}" y="${H - pB + 14}" text-anchor="middle" font-size="9.5" fill="#64748B" font-family="Consolas, monospace">${esc(fmtX(xv))}</text>`;
        svg += `<line x1="${pL}" y1="${yy.toFixed(1)}" x2="${W - pR}" y2="${yy.toFixed(1)}" stroke="#E2E8F0" stroke-width="1"/>`;
        svg += `<text x="${pL - 6}" y="${(yy + 3.5).toFixed(1)}" text-anchor="end" font-size="9.5" fill="#64748B" font-family="Consolas, monospace">${esc(fmtY(yv))}</text>`;
      }
      // Zona Élite shading (top-right always = best when axes oriented so better = right & top!)
      const xRef = xAvg !== null && xAvg !== undefined ? sx(xAvg) : (pL + (W - pL - pR) / 2);
      const yRef = yAvg !== null && yAvg !== undefined ? sy(yAvg) : (pT + (H - pT - pB) / 2);
      svg += `<rect x="${xRef.toFixed(1)}" y="${pT}" width="${Math.max(0, W - pR - xRef).toFixed(1)}" height="${Math.max(0, yRef - pT).toFixed(1)}" fill="#16A34A" fill-opacity="0.06"/>`;
      svg += `<text x="${W - pR - 6}" y="${pT + 14}" text-anchor="end" font-size="9" font-weight="800" fill="#15803D">★ ZONA ÉLITE</text>`;

      if (diagLine) {
        const loD = Math.max(xMin, yMin), hiD = Math.min(xMax, yMax);
        if (hiD > loD) {
          svg += `<line x1="${sx(loD).toFixed(1)}" y1="${sy(loD).toFixed(1)}" x2="${sx(hiD).toFixed(1)}" y2="${sy(hiD).toFixed(1)}" stroke="#0072B2" stroke-width="1.5" stroke-dasharray="5 3" stroke-opacity="0.7"/>`;
          if (diagLabel) svg += `<text x="${pL + 8}" y="${H - pB - 8}" font-size="9.5" font-weight="800" fill="#0072B2">${esc(diagLabel)}</text>`;
        }
      }

      if (xAvg !== null && xAvg !== undefined) {
        svg += `<line x1="${xRef.toFixed(1)}" y1="${pT}" x2="${xRef.toFixed(1)}" y2="${H - pB}" stroke="#94A3B8" stroke-width="1.3" stroke-dasharray="4 3"/>`;
        svg += `<text x="${Math.min(W - pR - 4, xRef + 4).toFixed(1)}" y="${H - pB - 5}" font-size="8.5" font-weight="700" fill="#64748B">Prom. Yaquis</text>`;
      }
      if (yAvg !== null && yAvg !== undefined) {
        svg += `<line x1="${pL}" y1="${yRef.toFixed(1)}" x2="${W - pR}" y2="${yRef.toFixed(1)}" stroke="#94A3B8" stroke-width="1.3" stroke-dasharray="4 3"/>`;
        svg += `<text x="${pL + 5}" y="${Math.max(pT + 10, yRef - 4).toFixed(1)}" font-size="8.5" font-weight="700" fill="#64748B">Prom. Yaquis</text>`;
      }

      // Smart collision-free label solver
      const placedBoxes = [];
      const sortedPts = [...points].sort((a, b) => (b.vol || 0) - (a.vol || 0));
      const maxVol = Math.max(1, ...sortedPts.map((p) => p.vol || 1));

      sortedPts.forEach((pt, idx) => {
        const px = sx(pt.x), py = sy(pt.y);
        const rad = 4.0 + Math.sqrt((pt.vol || 1) / maxVol) * 4.5;
        svg += `<circle class="comp-pt cursor-pointer" cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${rad.toFixed(1)}" fill="${pt.color}" fill-opacity="0.88" stroke="#FFFFFF" stroke-width="1.3" data-tip="${esc(pt.tip)}"/>`;

        if (idx < 14) {
          const shortName = String(pt.name || "").split(" ").slice(-1)[0];
          const tw = shortName.length * 5.6 + 6;
          const th = 12;
          const cands = [
            { dx: 0, dy: -(rad + 5), anc: "middle" },
            { dx: rad + 5, dy: 3, anc: "start" },
            { dx: -(rad + 5), dy: 3, anc: "end" },
            { dx: 0, dy: rad + 11, anc: "middle" },
          ];
          for (const c of cands) {
            const lx = px + c.dx, ly = py + c.dy;
            const bx1 = c.anc === "middle" ? lx - tw / 2 : (c.anc === "start" ? lx : lx - tw);
            const by1 = ly - 9;
            if (bx1 < pL || bx1 + tw > W - pR || by1 < pT || by1 + th > H - pB) continue;
            const hitBox = placedBoxes.some((b) => !(bx1 + tw + 2 < b.x1 || bx1 > b.x2 + 2 || by1 + th + 2 < b.y1 || by1 > b.y2 + 2));
            if (hitBox) continue;
            placedBoxes.push({ x1: bx1, y1: by1, x2: bx1 + tw, y2: by1 + th });
            svg += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="${c.anc}" font-size="9.5" font-weight="800" fill="#0F172A" stroke="#FFFFFF" stroke-width="2.5" paint-order="stroke">${esc(shortName)}</text>`;
            break;
          }
        }
      });

      svg += `<text x="${((pL + W - pR) / 2).toFixed(1)}" y="${H - 8}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#002850">${esc(xLabel)}</text>`;
      svg += `<text x="14" y="${((pT + H - pB) / 2).toFixed(1)}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#002850" transform="rotate(-90 14 ${((pT + H - pB) / 2).toFixed(1)})">${esc(yLabel)}</text>`;
      svg += `</svg>`;
      return svg;
    }

    function bindComparativeTooltips(rootEl) {
      if (!rootEl) return;
      rootEl.querySelectorAll(".comp-pt").forEach((el) => {
        el.addEventListener("mousemove", (e) => { if (el.dataset.tip) showTooltip(e, el.dataset.tip); });
        el.addEventListener("mouseleave", hideTooltip);
      });
    }
    function rankBadgeHTML(rank, total = 10) {
      if (!rank) return "";
      let cls = "bg-slate-200 text-slate-700";
      if (rank <= 2) cls = "bg-emerald-100 text-emerald-800 border border-emerald-300";
      else if (rank <= 4) cls = "bg-sky-100 text-sky-800 border border-sky-300";
      else if (rank >= total - 1) cls = "bg-red-100 text-red-800 border border-red-300";
      return `<span class="text-[10px] font-extrabold px-1.5 py-0.5 rounded tabular-nums ${cls}">#${rank}/${total} LMP</span>`;
    }
    function sortRows(rows, sortState, accessor) {
      const { col, dir } = sortState;
      return [...rows].sort((a, b) => {
        const va = accessor ? accessor(a, col) : a[col];
        const vb = accessor ? accessor(b, col) : b[col];
        const aNull = va === null || va === undefined || va === "";
        const bNull = vb === null || vb === undefined || vb === "";
        if (aNull && bNull) return 0;
        if (aNull) return 1;
        if (bNull) return -1;
        if (typeof va === "string" && typeof vb === "string") {
          return va.localeCompare(vb, "es") * dir;
        }
        return (Number(va) - Number(vb)) * dir;
      });
    }
    function activeSeasonData() {
      const key = state.season === "hist" ? "2025" : state.season;
      return { key, data: PAYLOAD.seasons?.[key] || {} };
    }
    function emptyStageCard(msg) {
      return `
        <div class="card-surface p-8 text-center space-y-3 border-dashed border-2 border-slate-300">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-slate-100 text-[#003B73] font-black text-lg">LMP</div>
          <h3 class="text-base font-extrabold text-[#002850]">Sin datos registrados para esta combinación</h3>
          <p class="text-xs sm:text-sm text-slate-600 max-w-xl mx-auto">${esc(msg)}</p>
          <div>
            <button onclick="window.__resetStageGlobal()" class="bg-[#003B73] hover:bg-[#0057A8] text-white text-xs font-bold px-4 py-2 rounded-md transition">
              Volver a Global Rol Regular
            </button>
          </div>
        </div>`;
    }
    window.__resetStageGlobal = () => {
      state.stage = "global_reg";
      state.cond = "all";
      renderAll();
    };
    window.__resetSprayPlayer = () => {
      state.sprayPlayer = "all";
      const sel = document.getElementById("sel-spray-player");
      if (sel) sel.value = "all";
      renderBattingModule();
    };
    window.__resetZonePitcher = () => {
      state.zonePitcher = "all";
      const sel = document.getElementById("sel-zone-pitcher");
      if (sel) sel.value = "all";
      renderPitchingModule();
    };
    window.__jumpToPlayer = (pid, targetTab = "scouting") => {
      const numPid = Number(pid);
      state.selectedPlayerId = numPid;
      state.tab = targetTab;
      if (targetTab === "scouting" && state.scoutCompareA === null && state.scoutCompareB === null) {
        const { key: sk } = activeSeasonData();
        const prof = getProfile(sk, numPid);
        state.scoutCompareType = prof.is_pitcher ? "pitchers" : "batters";
        state.scoutCompareSubRole = "all";
      }
      if (targetTab === "batting") {
        state.sprayMode = "off";
        state.sprayPlayer = String(pid);
      }
      if (targetTab === "pitching") state.zonePitcher = String(pid);
      renderAll();
      window.scrollTo({ top: 0, behavior: "smooth" });
    };
    window.__filterSprayPlayer = (pid, mode = "off") => {
      state.sprayMode = mode;
      state.sprayPlayer = String(pid);
      syncControlPills();
      renderBattingModule();
      document.getElementById("spray-diamond-svg")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };
    window.__filterZonePitcher = (pid) => {
      state.zonePitcher = String(pid);
      renderPitchingModule();
      document.getElementById("strike-zone-svg")?.scrollIntoView({ behavior: "smooth", block: "nearest" });
    };

    // =========================================================================
    // 4. MÓDULO 1: OVERVIEW, BENCHMARKING LMP & HISTÓRICO 2006–2026
    // =========================================================================
    function renderOverview() {
      const { key: sk, data: sdata } = activeSeasonData();
      const tb = sdata.team_benchmarks?.[state.stage] || {};
      const teams = tb.teams || [];
      const nTeams = teams.length || 10;
      const yaq = teams.find((t) => t.team_id === 680 || (t.equipo || "").includes("Yaquis"));
      const ranks = tb.yaquis_ranks || {};
      const lgCtx = tb.lg_ctx || {};

      // Mean LMP metrics for comparisons
      const lgAvg = (field) => {
        if (!teams.length) return null;
        const vals = teams.map((t) => Number(t[field])).filter((x) => !Number.isNaN(x));
        return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
      };

      const kpiWrap = document.getElementById("kpi-cards-grid");
      if (!yaq) {
        kpiWrap.innerHTML = `<div class="col-span-full">${emptyStageCard(state.season === "2026" ? "En la temporada 2026–27 (YTD al 15 de noviembre de 2026) solo se ha disputado la 1ra Vuelta del rol regular." : "Sin registros colectivos disponibles para la etapa seleccionada.")}</div>`;
      } else {
        const lmpOps = lgAvg("OPS");
        const lmpEra = lgAvg("ERA");
        const lmpInz = lgAvg("InZone_pct");
        const lmpDer = lgAvg("DER_pct");
        const orderedPts = [...teams].sort((a, b) =>
          (state.stage !== "playoffs" ? ((b.Pts_Total ?? -1) - (a.Pts_Total ?? -1)) : 0)
          || ((b.PCT ?? 0) - (a.PCT ?? 0))
          || ((b.Diff ?? 0) - (a.Diff ?? 0))
        );
        const ptsRankIdx = orderedPts.findIndex((t) => t.team_id === 680);
        const ptsRank = ptsRankIdx >= 0 ? ptsRankIdx + 1 : ranks.PCT;

        const cards = [
          {
            label: "Récord & Puntos LMP",
            accent: "#003B73",
            main: `${yaq.W}-${yaq.L}`,
            sub: `PCT ${fmtRate(yaq.PCT)} · Pyth ${yaq.Pyth_W}-${yaq.Pyth_L} (${fmtRate(yaq.Pyth_PCT)})`,
            extra: `Pts V1: ${fmtNum(yaq.Pts_V1, 1)} · V2: ${fmtNum(yaq.Pts_V2, 1)} · Tot: ${fmtNum(yaq.Pts_Total, 1)}`,
            rank: ptsRank,
          },
          {
            label: "Diferencial de Carreras",
            accent: yaq.Diff >= 0 ? "#16A34A" : "#E6392F",
            main: `${yaq.Diff >= 0 ? "+" : ""}${yaq.Diff}`,
            sub: `RS ${yaq.RS} vs RA ${yaq.RA} (${yaq.G} JJ)`,
            extra: `Últimos 10: ${yaq.L10 || "—"} · Racha: ${yaq.Streak || "—"}`,
            rank: null,
          },
          {
            label: "Ofensiva (OPS / wRC+)",
            accent: "#0095DA",
            main: `${fmtRate(yaq.OPS)} / ${fmtInt(yaq.wRC_plus)}`,
            sub: `LMP prom OPS: ${fmtRate(lmpOps)} · BB% ${fmtNum(yaq.BB_pct, 1, "%")} · K% ${fmtNum(yaq.K_pct, 1, "%")}`,
            extra: `wOBA ${fmtRate(yaq.wOBA)} · OPS+ ${fmtInt(yaq.OPS_plus)} · RISP ${fmtRate(yaq.RISP_AVG)}`,
            rank: ranks.wRC_plus || ranks.OPS,
          },
          {
            label: "Pitcheo (ERA / FIP / ERA-)",
            accent: "#0057A8",
            main: `${fmtNum(yaq.ERA, 2)} / ${fmtNum(yaq.FIP, 2)}`,
            sub: `LMP prom ERA: ${fmtNum(lmpEra, 2)} · ERA- ${fmtInt(yaq.ERA_minus)}`,
            extra: `K/9 ${fmtNum(yaq.K9, 2)} · BB/9 ${fmtNum(yaq.BB9, 2)} · LOB% ${fmtNum(yaq.LOB_pct, 1, "%")}`,
            rank: ranks.ERA,
          },
          {
            label: "Comando PBP & Swings",
            accent: "#0284C7",
            main: `${fmtNum(yaq.InZone_pct, 1, "%")}`,
            sub: `InZone% (LMP prom ${fmtNum(lmpInz, 1, "%")})`,
            extra: `Strike% ${fmtNum(yaq.Strike_pct, 1, "%")} · FPS% ${fmtNum(yaq.FPS_pct, 1, "%")} · Whiff% ${fmtNum(yaq.Whiff_pct, 1, "%")}`,
            rank: ranks.InZone_pct,
          },
          {
            label: "Defensa (DER% / OAA est.)",
            accent: "#16A34A",
            main: `${fmtNum(yaq.DER_pct, 1, "%")} / ${yaq.OAA_est >= 0 ? "+" : ""}${fmtNum(yaq.OAA_est, 1)}`,
            sub: `LMP prom DER%: ${fmtNum(lmpDer, 1, "%")} · E ${yaq.E} · FPCT ${fmtNum(yaq.FPCT, 3)}`,
            extra: `CS% Receptores: ${fmtNum(yaq.C_CS_pct, 1, "%")} · OAA INF ${fmtNum(yaq.OAA_INF, 1)}`,
            rank: ranks.DER_pct,
          },
        ];

        kpiWrap.innerHTML = cards.map((c) => `
          <div class="card-surface p-3.5 border-t-4 flex flex-col justify-between" style="border-top-color:${c.accent}">
            <div class="flex items-center justify-between gap-1">
              <span class="text-[11px] font-extrabold uppercase tracking-wider text-slate-500">${esc(c.label)}</span>
              ${c.rank ? rankBadgeHTML(c.rank, nTeams) : ""}
            </div>
            <div class="text-2xl font-black text-[#002850] mt-1.5 tabular-nums tracking-tight">${esc(c.main)}</div>
            <div class="text-[11.5px] font-semibold text-slate-700 mt-1 tabular-nums">${esc(c.sub)}</div>
            <div class="text-[11px] text-slate-500 mt-1 pt-1.5 border-t border-slate-100 tabular-nums">${esc(c.extra)}</div>
          </div>
        `).join("");
      }

      // Active Condition Split Strip
      const splitObj = sdata.yaquis_team_splits?.[state.stage]?.[state.cond];
      const splitStrip = document.getElementById("active-split-strip");
      if (!splitObj || !splitObj.bat_PA) {
        splitStrip.innerHTML = `<div class="text-xs text-slate-500">Sin registros PBP de Yaquis en la condición <strong>${esc(COND_LABELS[state.cond])}</strong> para ${esc(STAGE_LABELS[state.stage])}.</div>`;
      } else {
        const s = splitObj;
        splitStrip.innerHTML = `
          <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
            <div class="flex items-center gap-2">
              <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-extrabold px-2 py-0.5 uppercase"><span>CORTE PBP ACTIVO</span></span>
              <span class="text-sm font-extrabold text-[#002850]">${esc(STAGE_LABELS[state.stage])} · ${esc(COND_LABELS[state.cond])}</span>
            </div>
            <span class="text-xs font-code text-slate-500">${s.bat_PA} PA Bateo · ${fmtNum(s.pit_IP, 1)} IP Pitcheo · ${fmtInt(s.pitches_pbp)} Pitcheos</span>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2.5 text-center">
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">BATEO AVG/OBP/SLG</div><div class="text-xs font-black text-[#003B73] mt-0.5 tabular-nums">${fmtRate(s.bat_AVG)}/${fmtRate(s.bat_OBP)}/${fmtRate(s.bat_SLG)}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">OPS · HR · RBI</div><div class="text-xs font-black text-[#003B73] mt-0.5 tabular-nums">${fmtRate(s.bat_OPS)} · ${s.bat_HR} · ${s.bat_RBI}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">wOBA · wRC+</div><div class="text-xs font-black text-[#0057A8] mt-0.5 tabular-nums">${fmtRate(s.bat_wOBA)} · ${fmtInt(s.bat_wRC_plus)}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">ISO · BABIP</div><div class="text-xs font-black text-slate-800 mt-0.5 tabular-nums">${fmtRate(s.bat_ISO)} · ${fmtRate(s.bat_BABIP)}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">BB% · K%</div><div class="text-xs font-black text-slate-800 mt-0.5 tabular-nums">${fmtNum(s.bat_BB_pct,1,"%")} · ${fmtNum(s.bat_K_pct,1,"%")}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">PITCH WHIP · AVG</div><div class="text-xs font-black text-[#003B73] mt-0.5 tabular-nums">${fmtNum(s.pit_WHIP,2)} · ${fmtRate(s.pit_AVG_against)}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">PITCH FIP · K/9</div><div class="text-xs font-black text-[#0057A8] mt-0.5 tabular-nums">${fmtNum(s.pit_FIP,2)} · ${fmtNum(s.pit_K9,2)}</div></div>
            <div class="bg-slate-50 border border-slate-200 rounded p-2"><div class="text-[10px] font-bold text-slate-500">INZONE% · WHIFF%</div><div class="text-xs font-black text-emerald-700 mt-0.5 tabular-nums">${fmtNum(s.InZone_pct,1,"%")} · ${fmtNum(s.Whiff_pct,1,"%")}</div></div>
          </div>`;
      }

      renderStageComparisonChart(sdata);
      renderQuadrantChart(teams);
      renderBenchTable(teams);
      renderRosterBalanceCard(teams, sdata);
      renderHistoricalSection();
    }

    function renderStageComparisonChart(sdata) {
      const container = document.getElementById("stage-comparison-chart");
      const storyEl = document.getElementById("stage-story-box");
      const stages = ["v1", "v2", "playoffs"];
      const metricCfg = {
        ops: { m1: "OPS", l1: "OPS", f1: (v) => fmtRate(v), inv1: false, m2: "wRC_plus", l2: "wRC+", f2: fmtInt, inv2: false, lgFix2: 100 },
        era: { m1: "ERA", l1: "ERA (→ más larga = mejor)", f1: (v) => fmtNum(v, 2), inv1: true, m2: "FIP", l2: "FIP (→ más larga = mejor)", f2: (v) => fmtNum(v, 2), inv2: true, lgFix2: null },
        cmd: { m1: "InZone_pct", l1: "InZone%", f1: (v) => fmtNum(v, 1, "%"), inv1: false, m2: "Whiff_pct", l2: "Whiff%", f2: (v) => fmtNum(v, 1, "%"), inv2: false, lgFix2: null },
        def: { m1: "DER_pct", l1: "DER%", f1: (v) => fmtNum(v, 1, "%"), inv1: false, m2: "OAA_est", l2: "OAA est.", f2: (v) => (v > 0 ? `+${fmtNum(v, 1)}` : fmtNum(v, 1)), inv2: false, lgFix2: 0 },
      }[state.stageMetric];

      const rows = stages.map((st) => {
        const y = (sdata.team_benchmarks?.[st]?.teams || []).find((t) => t.team_id === 680);
        return { st, label: STAGE_LABELS[st], y };
      }).filter((r) => r.y);

      if (!rows.length) {
        container.innerHTML = `<div class="text-xs text-slate-400 py-8 text-center">Sin etapas registradas.</div>`;
        if (storyEl) storyEl.innerHTML = "";
        return;
      }

      const lgTeams = sdata.team_benchmarks?.global_reg?.teams || [];
      const lgAvg = (f) => {
        const vals = lgTeams.map((t) => Number(t[f])).filter(Number.isFinite);
        return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
      };
      const ref1 = lgAvg(metricCfg.m1);
      const ref2 = metricCfg.lgFix2 !== null ? metricCfg.lgFix2 : lgAvg(metricCfg.m2);

      // Compute independent normalized domains for Panel 1 & Panel 2
      const buildDomain = (field, refVal, inv) => {
        const vals = rows.map((r) => Number(r.y[field] ?? 0));
        if (refVal !== null) vals.push(refVal);
        let lo = Math.min(...vals), hi = Math.max(...vals);
        if (!inv && lo > 0 && field !== "OAA_est") lo = Math.min(lo * 0.85, lo);
        if (field === "OAA_est") {
          const absMax = Math.max(4, Math.abs(lo), Math.abs(hi)) * 1.18;
          return { min: -absMax, max: absMax, inv };
        }
        const span = Math.max(0.05, hi - lo);
        return { min: Math.max(0, lo - span * 0.25), max: hi + span * 0.25, inv };
      };
      const dom1 = buildDomain(metricCfg.m1, ref1, metricCfg.inv1);
      const dom2 = buildDomain(metricCfg.m2, ref2, metricCfg.inv2);
      const pctTrack = (v, dom) => {
        const t = (v - dom.min) / Math.max(0.001, dom.max - dom.min);
        return Math.max(0.05, Math.min(0.98, dom.inv ? 1.0 - t : t));
      };

      const W = 520, trackW = 148, x1L = 94, x2L = 304;
      const rowH = 54, yTop = 34;
      const H = Math.max(150, yTop + rows.length * rowH + 16);
      let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full h-auto select-none">`;
      // Panel headers + independent Media LMP tags
      svg += `<rect x="${x1L}" y="4" width="9" height="9" rx="2" fill="#003B73"/><text x="${x1L + 13}" y="12" font-size="9.5" font-weight="800" fill="#002850">${esc(metricCfg.l1)}</text>`;
      if (ref1 !== null) {
        const rx1 = x1L + pctTrack(ref1, dom1) * trackW;
        svg += `<line x1="${rx1.toFixed(1)}" y1="25" x2="${rx1.toFixed(1)}" y2="${H - 8}" stroke="#94A3B8" stroke-width="1.3" stroke-dasharray="3 3"/>`;
        svg += `<text x="${x1L}" y="21" font-size="8.5" font-weight="700" fill="#64748B">LMP: ${metricCfg.f1(ref1)}</text>`;
      }
      svg += `<rect x="${x2L}" y="4" width="9" height="9" rx="2" fill="#0072B2"/><text x="${x2L + 13}" y="12" font-size="9.5" font-weight="800" fill="#002850">${esc(metricCfg.l2)}</text>`;
      if (ref2 !== null) {
        const rx2 = x2L + pctTrack(ref2, dom2) * trackW;
        svg += `<line x1="${rx2.toFixed(1)}" y1="25" x2="${rx2.toFixed(1)}" y2="${H - 8}" stroke="#94A3B8" stroke-width="1.3" stroke-dasharray="3 3"/>`;
        svg += `<text x="${x2L}" y="21" font-size="8.5" font-weight="700" fill="#64748B">${metricCfg.m2 === "OAA_est" ? "Base 0.0" : `LMP: ${metricCfg.f2(ref2)}`}</text>`;
      }

      rows.forEach((r, idx) => {
        const y0 = yTop + idx * rowH;
        const v1 = Number(r.y[metricCfg.m1] ?? 0);
        const v2 = Number(r.y[metricCfg.m2] ?? 0);
        const w1 = pctTrack(v1, dom1) * trackW;

        svg += `<text x="2" y="${y0 + 18}" font-size="11" font-weight="800" fill="#002850">${esc(r.label)}</text>`;
        svg += `<text x="2" y="${y0 + 33}" font-size="9.5" font-weight="700" fill="#64748B">(${r.y.W}-${r.y.L} · ${fmtRate(r.y.PCT)})</text>`;

        // Track 1
        svg += `<rect x="${x1L}" y="${y0 + 12}" width="${trackW}" height="16" rx="3" fill="#EEF2F6"/>`;
        svg += `<rect x="${x1L}" y="${y0 + 12}" width="${w1.toFixed(1)}" height="16" rx="3" fill="#003B73"/>`;
        svg += `<text x="${x1L + trackW + 5}" y="${y0 + 24}" font-size="10.5" font-weight="800" fill="#003B73" font-family="Consolas, monospace">${metricCfg.f1(v1)}</text>`;

        // Track 2 (special diverging zero for OAA_est)
        svg += `<rect x="${x2L}" y="${y0 + 12}" width="${trackW}" height="16" rx="3" fill="#EEF2F6"/>`;
        if (metricCfg.m2 === "OAA_est") {
          const zX = x2L + trackW * 0.5;
          const vX = x2L + pctTrack(v2, dom2) * trackW;
          const bx = Math.min(zX, vX), bw = Math.max(3, Math.abs(vX - zX));
          svg += `<rect x="${bx.toFixed(1)}" y="${y0 + 12}" width="${bw.toFixed(1)}" height="16" rx="3" fill="${v2 >= 0 ? "#16A34A" : "#E6392F"}"/>`;
          svg += `<text x="${x2L + trackW + 5}" y="${y0 + 24}" font-size="10.5" font-weight="800" fill="${v2 >= 0 ? "#15803D" : "#B91C1C"}" font-family="Consolas, monospace">${metricCfg.f2(v2)}</text>`;
        } else {
          const w2 = pctTrack(v2, dom2) * trackW;
          svg += `<rect x="${x2L}" y="${y0 + 12}" width="${w2.toFixed(1)}" height="16" rx="3" fill="#0072B2"/>`;
          svg += `<text x="${x2L + trackW + 5}" y="${y0 + 24}" font-size="10.5" font-weight="800" fill="#0057A8" font-family="Consolas, monospace">${metricCfg.f2(v2)}</text>`;
        }
      });
      svg += `</svg>`;
      container.innerHTML = svg;

      if (storyEl) {
        const v1r = rows.find((r) => r.st === "v1")?.y;
        const v2r = rows.find((r) => r.st === "v2")?.y;
        const por = rows.find((r) => r.st === "playoffs")?.y;
        const sm = state.stageMetric;
        let msg = "";
        if (v1r && v2r) {
          if (sm === "era") {
            const dEra = (v2r.ERA || 0) - (v1r.ERA || 0);
            const dFip = (v2r.FIP || 0) - (v1r.FIP || 0);
            const eraVerb = dEra <= 0 ? "mejoró" : "subió";
            msg = `<strong>Pitcheo por Vueltas:</strong> La efectividad ${eraVerb} de <strong>${fmtNum(v1r.ERA,2)} ERA</strong> (${fmtNum(v1r.FIP,2)} FIP) en V1 a <strong>${fmtNum(v2r.ERA,2)} ERA</strong> (${dEra >= 0 ? "+" : ""}${dEra.toFixed(2)}) y <strong>${fmtNum(v2r.FIP,2)} FIP</strong> (${dFip >= 0 ? "+" : ""}${dFip.toFixed(2)}) en V2.`;
          } else if (sm === "cmd") {
            const dInz = (v2r.InZone_pct || 0) - (v1r.InZone_pct || 0);
            const dWhf = (v2r.Whiff_pct || 0) - (v1r.Whiff_pct || 0);
            msg = `<strong>Comando por Vueltas:</strong> Zona de strike pasó de <strong>${fmtNum(v1r.InZone_pct,1,"%")} InZone%</strong> (${fmtNum(v1r.Whiff_pct,1,"%")} Whiff%) en V1 a <strong>${fmtNum(v2r.InZone_pct,1,"%")}</strong> (${dInz >= 0 ? "+" : ""}${dInz.toFixed(1)}%) y <strong>${fmtNum(v2r.Whiff_pct,1,"%")} Whiff%</strong> (${dWhf >= 0 ? "+" : ""}${dWhf.toFixed(1)}%) en V2.`;
          } else if (sm === "def") {
            const dDer = (v2r.DER_pct || 0) - (v1r.DER_pct || 0);
            msg = `<strong>Defensa por Vueltas:</strong> La eficiencia DER% evolucionó de <strong>${fmtNum(v1r.DER_pct,1,"%")}</strong> (OAA ${v1r.OAA_est > 0 ? "+" : ""}${fmtNum(v1r.OAA_est,1)}) en V1 a <strong>${fmtNum(v2r.DER_pct,1,"%")}</strong> (${dDer >= 0 ? "+" : ""}${dDer.toFixed(1)}%) con <strong>OAA ${v2r.OAA_est > 0 ? "+" : ""}${fmtNum(v2r.OAA_est,1)}</strong> en V2.`;
          } else {
            const dWrc = Math.round((v2r.wRC_plus || 0) - (v1r.wRC_plus || 0));
            const dEra = ((v2r.ERA || 0) - (v1r.ERA || 0)).toFixed(2);
            msg = `<strong>Lectura por Vueltas:</strong> De V1 (<strong>${v1r.W}-${v1r.L}</strong> · ${fmtNum(v1r.Pts_V1,1)} pts · wRC+ ${fmtInt(v1r.wRC_plus)} · ${fmtNum(v1r.ERA,2)} ERA) a V2 (<strong>${v2r.W}-${v2r.L}</strong> · ${fmtNum(v2r.Pts_V2,1)} pts · wRC+ ${fmtInt(v2r.wRC_plus)}, ${dWrc >= 0 ? "+" : ""}${dWrc}), el pitcheo pasó a <strong>${fmtNum(v2r.ERA,2)} ERA</strong> (${Number(dEra) >= 0 ? "+" : ""}${dEra}) con <strong>DER% ${fmtNum(v2r.DER_pct,1,"%")}</strong> (OAA ${v2r.OAA_est > 0 ? "+" : ""}${fmtNum(v2r.OAA_est,1)}).`;
          }
          if (por) msg += ` En Playoffs (<em>n=${por.G}</em>): <strong>${por.W}-${por.L}</strong> · ${metricCfg.l1} ${metricCfg.f1(por[metricCfg.m1])} · ${metricCfg.l2} ${metricCfg.f2(por[metricCfg.m2])}.`;
        } else if (v1r) {
          msg = `<strong>Avance YTD 1ra Vuelta:</strong> Marca de <strong>${v1r.W}-${v1r.L}</strong> (${fmtNum(v1r.Pts_V1,1)} pts) · ${esc(metricCfg.l1)} <strong>${esc(metricCfg.f1(v1r[metricCfg.m1]))}</strong> · ${esc(metricCfg.l2)} <strong>${esc(metricCfg.f2(v1r[metricCfg.m2]))}</strong>.`;
        }
        storyEl.innerHTML = msg ? `<div class="bg-sky-50 border-l-4 border-[#0057A8] rounded-r px-3 py-2 text-xs text-slate-700 leading-relaxed">${msg}</div>` : "";
      }
    }

    function renderQuadrantChart(teams) {
      const wrap = document.getElementById("lmp-quadrant-chart");
      const storyEl = document.getElementById("quadrant-story-box");
      if (!teams.length) {
        wrap.innerHTML = `<div class="text-xs text-slate-400 py-10 text-center">No hay clubes activos en esta etapa.</div>`;
        if (storyEl) storyEl.innerHTML = "";
        return;
      }
      const xField = "wRC_plus";
      const yField = "FIP";
      const xs = teams.map((t) => Number(t[xField]));
      const ys = teams.map((t) => Number(t[yField]));
      const xRawSpan = Math.max(10, Math.max(...xs) - Math.min(...xs));
      const yRawSpan = Math.max(0.6, Math.max(...ys) - Math.min(...ys));
      const xMin = Math.min(...xs) - Math.max(8, xRawSpan * 0.16);
      const xMax = Math.max(...xs) + Math.max(10, xRawSpan * 0.18);
      const yMin = Math.min(...ys) - Math.max(0.28, yRawSpan * 0.18);
      const yMax = Math.max(...ys) + Math.max(0.28, yRawSpan * 0.18);
      const avgX = xs.reduce((a, b) => a + b, 0) / xs.length;
      const avgY = ys.reduce((a, b) => a + b, 0) / ys.length;

      const W = 680, H = 340, pL = 58, pR = 38, pT = 32, pB = 44;
      const sx = (v) => pL + ((v - xMin) / Math.max(0.001, xMax - xMin)) * (W - pL - pR);
      // Lower FIP is BETTER, so invert Y: smaller FIP near TOP
      const sy = (v) => pT + ((v - yMin) / Math.max(0.001, yMax - yMin)) * (H - pT - pB);

      const cx = sx(avgX), cy = sy(avgY);
      let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full min-w-[490px] h-auto">`;

      // Quadrant background shading for visual storytelling
      svg += `<rect x="${cx.toFixed(1)}" y="${pT}" width="${(W - pR - cx).toFixed(1)}" height="${(cy - pT).toFixed(1)}" fill="#16A34A" fill-opacity="0.06"/>`;
      svg += `<rect x="${pL}" y="${pT}" width="${(cx - pL).toFixed(1)}" height="${(cy - pT).toFixed(1)}" fill="#0095DA" fill-opacity="0.04"/>`;
      svg += `<rect x="${cx.toFixed(1)}" y="${cy.toFixed(1)}" width="${(W - pR - cx).toFixed(1)}" height="${(H - pB - cy).toFixed(1)}" fill="#D97706" fill-opacity="0.04"/>`;
      svg += `<rect x="${pL}" y="${pT}" width="${W-pL-pR}" height="${H-pT-pB}" fill="none" stroke="#CBD5E1"/>`;

      // Axis ticks
      for (let t = 0; t <= 4; t++) {
        const xv = xMin + (t / 4) * (xMax - xMin);
        const xx = sx(xv);
        svg += `<line x1="${xx.toFixed(1)}" y1="${H-pB}" x2="${xx.toFixed(1)}" y2="${H-pB+4}" stroke="#94A3B8"/>`;
        svg += `<text x="${xx.toFixed(1)}" y="${H-pB+15}" text-anchor="middle" font-size="9.5" fill="#64748B" font-family="Consolas, monospace">${Math.round(xv)}</text>`;

        const yv = yMin + (t / 4) * (yMax - yMin);
        const yy = sy(yv);
        svg += `<line x1="${pL-4}" y1="${yy.toFixed(1)}" x2="${pL}" y2="${yy.toFixed(1)}" stroke="#94A3B8"/>`;
        svg += `<text x="${pL-7}" y="${(yy+3).toFixed(1)}" text-anchor="end" font-size="9.5" fill="#64748B" font-family="Consolas, monospace">${yv.toFixed(2)}</text>`;
      }

      // Average Crosshairs
      svg += `<line x1="${cx.toFixed(1)}" y1="${pT}" x2="${cx.toFixed(1)}" y2="${H-pB}" stroke="#64748B" stroke-width="1.2" stroke-dasharray="4 3"/>`;
      svg += `<line x1="${pL}" y1="${cy.toFixed(1)}" x2="${W-pR}" y2="${cy.toFixed(1)}" stroke="#64748B" stroke-width="1.2" stroke-dasharray="4 3"/>`;

      // Quadrant Storytelling Corner Callouts
      svg += `<text x="${W-pR-6}" y="${pT+13}" text-anchor="end" font-size="9.5" font-weight="800" fill="#15803D">★ ÉLITE INTEGRAL (+wRC+ / -FIP)</text>`;
      svg += `<text x="${pL+6}" y="${pT+13}" text-anchor="start" font-size="9.5" font-weight="800" fill="#0057A8">🛡 PITCHEO &amp; DEFENSA (-wRC+ / -FIP)</text>`;
      svg += `<text x="${W-pR-6}" y="${H-pB-7}" text-anchor="end" font-size="9.5" font-weight="800" fill="#B45309">⚡ BATEO DE PODER (+wRC+ / +FIP)</text>`;
      svg += `<text x="${pL+6}" y="${H-pB-7}" text-anchor="start" font-size="9.5" font-weight="800" fill="#B91C1C">▼ ZONA DE RIESGO (-wRC+ / +FIP)</text>`;

      svg += `<text x="${W/2}" y="${H-7}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#334155">wRC+ Ofensivo (Media LMP: ${Math.round(avgX)}) →</text>`;
      svg += `<text x="15" y="${H/2}" text-anchor="middle" font-size="10.5" font-weight="800" fill="#334155" transform="rotate(-90 15 ${H/2})">FIP Pitcheo (Media LMP: ${avgY.toFixed(2)} · menor arriba) ↑</text>`;

      // Precompute all dot coordinates + corner safe-boxes so zero label collision occurs
      const dots = teams.map((t) => {
        const px = sx(Number(t[xField]));
        const py = sy(Number(t[yField]));
        const isY = t.team_id === 680;
        const short = (t.equipo || "").split(" ")[0];
        return { t, px, py, isY, short, rDot: isY ? 10 : 6.5 };
      });

      const placedBoxes = [
        { x1: W - pR - 185, y1: pT + 2, x2: W - pR, y2: pT + 18 },
        { x1: pL, y1: pT + 2, x2: pL + 195, y2: pT + 18 },
        { x1: W - pR - 185, y1: H - pB - 18, x2: W - pR, y2: H - pB - 2 },
        { x1: pL, y1: H - pB - 18, x2: pL + 175, y2: H - pB - 2 },
      ];

      // Candidate radii & 16 angles for zero-overlap placement
      const angles = [];
      for (let a = 0; a < 16; a++) angles.push((a * Math.PI * 2) / 16 - Math.PI / 2);
      const radii = [18, 26, 35, 44, 54];

      // Draw precision dots first
      dots.forEach((d) => {
        const { t, px, py, isY } = d;
        const isRiv = !isY && sameClub(state.highlightTeamId, t.team_id);
        svg += `<g class="cursor-pointer q-dot" data-tid="${t.team_id}" data-team="${esc(t.equipo)}" data-rec="${t.W}-${t.L}" data-x="${t[xField]}" data-y="${t[yField]}" data-ops="${fmtRate(t.OPS)}" data-era="${fmtNum(t.ERA,2)}" data-der="${t.DER_pct}">`;
        if (isY) svg += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="10.5" fill="#0095DA" fill-opacity="0.22" stroke="#0095DA" stroke-width="1.5"/>`;
        if (isRiv) svg += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="9.5" fill="#F59E0B" fill-opacity="0.22" stroke="#F59E0B" stroke-width="2" stroke-dasharray="3 2"/>`;
        svg += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${isY ? 6.5 : (isRiv ? 5.8 : 4.6)}" fill="${isY ? "#E6392F" : (isRiv ? "#D97706" : "#0057A8")}" stroke="#FFFFFF" stroke-width="1.5"/>`;
        svg += `</g>`;
      });

      // Solve non-overlapping label pills with mini-shields
      const sortedForLabels = [...dots].sort((a, b) => (b.isY ? 2 : (sameClub(state.highlightTeamId, b.t.team_id) ? 1 : 0)) - (a.isY ? 2 : (sameClub(state.highlightTeamId, a.t.team_id) ? 1 : 0)));
      sortedForLabels.forEach((d) => {
        const { t, px, py, isY, short } = d;
        const labelW = 24 + short.length * 5.8;
        const labelH = 19;
        const logoEntry = META.team_logos?.[String(t.team_id)];
        const logoUri = logoEntry?.data_uri || logoEntry?.svg_uri || "";

        let best = null;
        let bestPenalty = Infinity;

        for (const rad of radii) {
          for (const ang of angles) {
            const cxL = px + rad * Math.cos(ang);
            const cyL = py + rad * Math.sin(ang);
            const x1 = cxL - labelW / 2;
            const y1 = cyL - labelH / 2;
            const x2 = cxL + labelW / 2;
            const y2 = cyL + labelH / 2;

            // Keep inside chart plotting box
            if (x1 < pL + 3 || x2 > W - pR - 3 || y1 < pT + 3 || y2 > H - pB - 3) continue;

            let penalty = rad * 0.4;
            // Dot collision penalty
            for (const other of dots) {
              const nearX = Math.max(x1 - 3, Math.min(other.px, x2 + 3));
              const nearY = Math.max(y1 - 3, Math.min(other.py, y2 + 3));
              const dist = Math.hypot(other.px - nearX, other.py - nearY);
              if (dist < other.rDot + 2) penalty += 10000;
            }
            // Label collision penalty
            for (const b of placedBoxes) {
              if (!(x2 + 3 < b.x1 || x1 - 3 > b.x2 || y2 + 3 < b.y1 || y1 - 3 > b.y2)) {
                penalty += 10000;
              }
            }
            if (penalty < bestPenalty) {
              bestPenalty = penalty;
              best = { x1, y1, x2, y2, cxL, cyL };
            }
            if (penalty < 100) break;
          }
          if (bestPenalty < 100) break;
        }

        if (!best) {
          const x1 = Math.max(pL + 4, Math.min(W - pR - labelW - 4, px - labelW / 2));
          const y1 = Math.max(pT + 20, Math.min(H - pB - labelH - 4, py + 12));
          best = { x1, y1, x2: x1 + labelW, y2: y1 + labelH, cxL: x1 + labelW / 2, cyL: y1 + labelH / 2 };
        }
        placedBoxes.push({ x1: best.x1, y1: best.y1, x2: best.x2, y2: best.y2 });

        const distC = Math.hypot(best.cxL - px, best.cyL - py);
        const isHl = sameClub(state.highlightTeamId, t.team_id);
        const borderC = isY ? "#0095DA" : (isHl ? "#D97706" : "#CBD5E1");
        const fillC = isY ? "#002850" : (isHl ? "#FEF3C7" : "#FFFFFF");
        if (distC > 13) {
          svg += `<line x1="${px.toFixed(1)}" y1="${py.toFixed(1)}" x2="${best.cxL.toFixed(1)}" y2="${best.cyL.toFixed(1)}" stroke="${isY ? "#0095DA" : (isHl ? "#D97706" : "#94A3B8")}" stroke-width="${isY || isHl ? 1.3 : 0.9}" stroke-opacity="0.85"/>`;
        }
        svg += `<g class="cursor-pointer q-dot" data-tid="${t.team_id}" data-team="${esc(t.equipo)}" data-rec="${t.W}-${t.L}" data-x="${t[xField]}" data-y="${t[yField]}" data-ops="${fmtRate(t.OPS)}" data-era="${fmtNum(t.ERA,2)}" data-der="${t.DER_pct}">`;
        svg += `<rect x="${best.x1.toFixed(1)}" y="${best.y1.toFixed(1)}" width="${labelW.toFixed(1)}" height="${labelH}" rx="9.5" fill="${fillC}" fill-opacity="0.96" stroke="${borderC}" stroke-width="${isY || isHl ? 1.7 : 1}"/>`;
        if (logoUri) {
          svg += `<circle cx="${(best.x1 + 9.5).toFixed(1)}" cy="${best.cyL.toFixed(1)}" r="7.5" fill="#FFFFFF"/>`;
          svg += `<image href="${esc(logoUri)}" x="${(best.x1 + 2.5).toFixed(1)}" y="${(best.cyL - 7).toFixed(1)}" width="14" height="14" preserveAspectRatio="xMidYMid meet"/>`;
        }
        svg += `<text x="${(best.x1 + 20).toFixed(1)}" y="${(best.cyL + 3.5).toFixed(1)}" font-size="${isY ? 9.8 : 9.2}" font-weight="${isY ? 900 : 700}" fill="${isY ? "#FFFFFF" : "#1E293B"}">${esc(short)}</text>`;
        svg += `</g>`;
      });

      svg += `</svg>`;
      wrap.innerHTML = svg;

      wrap.querySelectorAll(".q-dot").forEach((el) => {
        el.addEventListener("mousemove", (e) => {
          showTooltip(e, `<strong>${esc(el.dataset.team)}</strong> (${esc(el.dataset.rec)})<br>wRC+: <b>${el.dataset.x}</b> (OPS ${el.dataset.ops})<br>FIP: <b>${el.dataset.y}</b> (ERA ${el.dataset.era}) · DER%: <b>${el.dataset.der}%</b>`);
        });
        el.addEventListener("mouseleave", hideTooltip);
        el.addEventListener("click", () => {
          const tid = Number(el.dataset.tid);
          if (tid) {
            state.highlightTeamId = (sameClub(state.highlightTeamId, tid) && tid !== 680) ? 680 : tid;
            renderAll();
          }
        });
      });

      if (storyEl) {
        const yaq = teams.find((t) => t.team_id === 680);
        const bestOff = [...teams].sort((a, b) => b.wRC_plus - a.wRC_plus)[0];
        const bestPit = [...teams].sort((a, b) => a.FIP - b.FIP)[0];
        if (yaq) {
          const quadDesc = yaq.wRC_plus >= avgX && yaq.FIP <= avgY
            ? "Cuadrante Élite Integral (por encima de la media LMP en bateo y supresión FIP)"
            : (yaq.wRC_plus < avgX && yaq.FIP <= avgY
              ? "Cuadrante de Pitcheo & Defensa (staff sólido con oportunidad de elevar poder ofensivo)"
              : (yaq.wRC_plus >= avgX ? "Cuadrante de Bateo de Poder (+wRC+ con FIP por debajo del corte de liga)" : "Cuadrante de Ajuste Bilateral"));
          storyEl.innerHTML = `<div class="bg-slate-50 border-l-4 border-[#0095DA] rounded-r px-3 py-2 text-xs text-slate-700 leading-relaxed"><strong>Diagnóstico Posicional LMP:</strong> Yaquis se ubica en el <strong>${quadDesc}</strong> (wRC+ <strong>${fmtInt(yaq.wRC_plus)}</strong> vs media ${Math.round(avgX)} · FIP <strong>${fmtNum(yaq.FIP,2)}</strong> vs media ${avgY.toFixed(2)}). Referentes de etapa: <strong>${esc(bestOff.equipo)}</strong> en ataque (wRC+ ${fmtInt(bestOff.wRC_plus)}) y <strong>${esc(bestPit.equipo)}</strong> en pitcheo (FIP ${fmtNum(bestPit.FIP,2)}).</div>`;
        } else {
          storyEl.innerHTML = "";
        }
      }
    }

    function renderBenchTable(teams) {
      document.getElementById("bench-stage-label").textContent = STAGE_LABELS[state.stage] || state.stage;
      const container = document.getElementById("bench-table-container");
      if (!teams.length) {
        container.innerHTML = `<div class="p-6 text-center text-xs text-slate-500">Sin clubes registrados para esta etapa en la temporada seleccionada.</div>`;
        return;
      }

      const clubCell = {
        k: "equipo",
        l: "Club LMP",
        align: "left",
        fmt: (v, r) => {
          let poTag = "";
          if (r._pos && state.stage !== "playoffs") {
            if (r._pos <= 4) {
              poTag = `<span class="ml-1.5 text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-sky-100 text-sky-900 border border-sky-300" title="Localía asegurada en 1ra Ronda de Playoffs (Top 4)">TOP 4</span>`;
            } else if (r._pos <= 8) {
              poTag = `<span class="ml-1.5 text-[9px] font-extrabold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200" title="Zona de clasificación a Playoffs (Top 8)">TOP 8 PO</span>`;
            }
          }
          return `<div class="flex items-center gap-2">${renderTeamLogo(r.team_id, v, "w-7 h-7")}<span>${esc(v)}</span>${poTag}</div>`;
        },
      };

      const standingsRanked = [...teams].sort((a, b) =>
        (state.stage !== "playoffs" ? ((b.Pts_Total ?? -1) - (a.Pts_Total ?? -1)) : 0)
        || ((b.PCT ?? 0) - (a.PCT ?? 0))
        || ((b.Diff ?? 0) - (a.Diff ?? 0))
      );
      standingsRanked.forEach((t, idx) => { t._pos = idx + 1; });

      const COL_GROUPS = {
        standings: [
          clubCell,
          { k: "_pos", l: "Pos", align: "center", fmt: (v) => `<span class="font-code font-extrabold ${v <= 8 ? "text-emerald-700" : "text-slate-500"}">#${v}</span>` },
          { k: "G", l: "JJ", fmt: fmtInt },
          { k: "W", l: "G", fmt: fmtInt },
          { k: "L", l: "P", fmt: fmtInt },
          { k: "PCT", l: "PCT", fmt: (v) => fmtRate(v) },
          { k: "Pts_V1", l: "Pts V1", fmt: (v) => fmtNum(v, 1) },
          { k: "Pts_V2", l: "Pts V2", fmt: (v) => fmtNum(v, 1) },
          { k: "Pts_Total", l: "Pts Tot", fmt: (v) => fmtNum(v, 1) },
          { k: "RS", l: "CA", fmt: fmtInt },
          { k: "RA", l: "CP", fmt: fmtInt },
          { k: "Diff", l: "Diff", fmt: (v) => (v > 0 ? `+${v}` : String(v)) },
          { k: "Pyth_W", l: "Pyth G-P", fmt: (v, r) => `${r.Pyth_W}-${r.Pyth_L} (${fmtRate(r.Pyth_PCT)})` },
          { k: "L10", l: "L10", fmt: (v) => esc(v) },
          { k: "Streak", l: "Racha", fmt: (v) => esc(v) },
        ],
        offense: [
          clubCell,
          { k: "PA", l: "PA", fmt: fmtInt },
          { k: "AVG", l: "AVG", fmt: (v) => fmtRate(v) },
          { k: "OBP", l: "OBP", fmt: (v) => fmtRate(v) },
          { k: "SLG", l: "SLG", fmt: (v) => fmtRate(v) },
          { k: "OPS", l: "OPS", fmt: (v) => fmtRate(v) },
          { k: "OPS_plus", l: "OPS+", fmt: fmtInt },
          { k: "wOBA", l: "wOBA", fmt: (v) => fmtRate(v) },
          { k: "wRC_plus", l: "wRC+", fmt: fmtInt },
          { k: "ISO", l: "ISO", fmt: (v) => fmtRate(v) },
          { k: "BABIP", l: "BABIP", fmt: (v) => fmtRate(v) },
          { k: "BB_pct", l: "BB%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "K_pct", l: "K%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "HR", l: "HR", fmt: fmtInt },
          { k: "SB_pct", l: "SB%", fmt: (v, r) => `${r.SB}/${r.SB+r.CS} (${fmtNum(v,0,"%")})` },
          { k: "RISP_AVG", l: "RISP AVG", fmt: (v) => fmtRate(v) },
          { k: "HIGH_LEV_OPS", l: "HighLev OPS", fmt: (v) => fmtRate(v) },
        ],
        pitching: [
          clubCell,
          { k: "IP", l: "IP", fmt: (v) => fmtNum(v, 1) },
          { k: "ERA", l: "ERA", fmt: (v) => fmtNum(v, 2) },
          { k: "ERA_minus", l: "ERA-", fmt: fmtInt },
          { k: "FIP", l: "FIP", fmt: (v) => fmtNum(v, 2) },
          { k: "xFIP", l: "xFIP", fmt: (v) => fmtNum(v, 2) },
          { k: "WHIP", l: "WHIP", fmt: (v) => fmtNum(v, 2) },
          { k: "K9", l: "K/9", fmt: (v) => fmtNum(v, 2) },
          { k: "BB9", l: "BB/9", fmt: (v) => fmtNum(v, 2) },
          { k: "K_BB", l: "K/BB", fmt: (v) => fmtNum(v, 2) },
          { k: "LOB_pct", l: "LOB%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "GB_FB", l: "GB/FB", fmt: (v) => fmtNum(v, 2) },
          { k: "Strike_pct", l: "Strike%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "FPS_pct", l: "FPS%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "InZone_pct", l: "InZone%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "Chase_pct", l: "Chase%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "Whiff_pct", l: "Whiff%", fmt: (v) => fmtNum(v, 1, "%") },
        ],
        defense: [
          clubCell,
          { k: "FPCT", l: "FPCT", fmt: (v) => fmtNum(v, 4) },
          { k: "E", l: "Errores", fmt: fmtInt },
          { k: "DER_pct", l: "DER%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "OAA_est", l: "OAA est", fmt: (v) => (v > 0 ? `+${fmtNum(v,1)}` : fmtNum(v,1)) },
          { k: "DER_INF", l: "DER INF", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "OAA_INF", l: "OAA INF", fmt: (v) => fmtNum(v, 1) },
          { k: "DER_LF", l: "DER LF", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "DER_CF", l: "DER CF", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "DER_RF", l: "DER RF", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "C_CS_pct", l: "CS% C", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "BIP_GB_pct", l: "GB%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "BIP_LD_pct", l: "LD%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "BIP_FB_pct", l: "FB%", fmt: (v) => fmtNum(v, 1, "%") },
        ],
      };

      const effSort = (state.stage === "playoffs" && state.benchSort.col === "Pts_Total")
        ? { col: "PCT", dir: -1 }
        : state.benchSort;
      const benchAccessor = (row, col) => {
        if (col === "L10") {
          const w = parseInt(String(row.L10 || "0").split("-")[0], 10);
          return Number.isFinite(w) ? w : -1;
        }
        if (col === "Streak") {
          const m = String(row.Streak || "").trim().match(/^([GPWL])(\d+)$/i);
          if (!m) return 0;
          const n = parseInt(m[2], 10);
          return (m[1].toUpperCase() === "G" || m[1].toUpperCase() === "W") ? n : -n;
        }
        return row[col];
      };
      const cols = COL_GROUPS[state.benchGroup] || COL_GROUPS.standings;
      const sorted = sortRows(teams, effSort, benchAccessor);

      let htmlStr = `<table class="fo-table"><thead><tr>`;
      cols.forEach((c) => {
        const isSorted = effSort.col === c.k;
        const cls = `${isSorted ? "sorted-col " : ""}${c.align === "left" ? "text-left" : "text-right"}`;
        const arrow = isSorted ? (effSort.dir === 1 ? " ▲" : " ▼") : "";
        htmlStr += `<th class="${cls}" data-sort-col="${c.k}">${esc(c.l)}${arrow}</th>`;
      });
      htmlStr += `</tr></thead><tbody>`;

      sorted.forEach((row) => {
        const isYaq = row.team_id === 680 || (row.equipo || "").includes("Yaquis");
        const isRivalHi = !isYaq && sameClub(state.highlightTeamId, row.team_id);
        const rowCls = isYaq ? "yaquis-highlight-row" : (isRivalHi ? "rival-highlight-row" : "");
        htmlStr += `<tr class="${rowCls}">`;
        cols.forEach((c) => {
          const cls = `${c.align === "left" ? "text-left font-bold" : "text-right"}`;
          htmlStr += `<td class="${cls}">${c.fmt(row[c.k], row)}</td>`;
        });
        htmlStr += `</tr>`;
      });
      htmlStr += `</tbody></table>`;
      container.innerHTML = htmlStr;

      container.querySelectorAll("th[data-sort-col]").forEach((th) => {
        th.addEventListener("click", () => {
          const k = th.dataset.sortCol;
          if (state.benchSort.col === k) state.benchSort.dir *= -1;
          else {
            state.benchSort.col = k;
            state.benchSort.dir = ["_pos", "ERA", "FIP", "xFIP", "ERA_minus", "WHIP", "BB9", "E"].includes(k) ? 1 : -1;
          }
          renderBenchTable(teams);
        });
      });
    }

    function renderHistoricalSection() {
      const wrapChart = document.getElementById("historical-chart-container");
      const wrapTbl = document.getElementById("historical-table-container");
      const storyEl = document.getElementById("hist-story-box");
      if (!HIST.length) return;

      const sortedAsc = [...HIST].sort((a, b) => a.season - b.season);
      const metric = state.histMetric;
      const cfgBase = {
        pct: { y1: "reg_PCT", l1: "Yaquis PCT Real", y2: "Pyth_PCT", l2: "Yaquis Pyth PCT", pad: 0.04, inv: false, baseVal: 0.500, baseLbl: ".500", fmt: (v) => fmtRate(v) },
        ops: { y1: "yaq_OPS", l1: "Yaquis OPS", y2: "lmp_OPS", l2: "Promedio LMP OPS", pad: 0.025, inv: false, baseVal: null, baseLbl: "", fmt: (v) => fmtRate(v) },
        era: { y1: "yaq_ERA", l1: "Yaquis ERA (↑ Mejor)", y2: "lmp_ERA", l2: "Promedio LMP ERA", pad: 0.4, inv: true, baseVal: null, baseLbl: "", fmt: (v) => fmtNum(v, 2) },
        diff: { y1: "Diff", l1: "Diferencial Carreras (RS-RA)", y2: null, l2: "", pad: 20, inv: false, baseVal: 0, baseLbl: "0", fmt: (v) => (v > 0 ? `+${Math.round(v)}` : String(Math.round(v))) },
      }[metric];
      const allVals = sortedAsc.flatMap((d) => [Number(d[cfgBase.y1]), cfgBase.y2 ? Number(d[cfgBase.y2]) : null]).filter((x) => x !== null && !Number.isNaN(x));
      if (cfgBase.baseVal !== null) allVals.push(cfgBase.baseVal);
      const cfg = {
        ...cfgBase,
        min: Math.min(...allVals) - cfgBase.pad,
        max: Math.max(...allVals) + cfgBase.pad,
      };

      const W = 940, H = 262, pL = 56, pR = 26, pT = 46, pB = 38;
      const sx = (i) => pL + (i / Math.max(1, sortedAsc.length - 1)) * (W - pL - pR);
      const sy = (v) => cfg.inv
        ? pT + ((v - cfg.min) / Math.max(0.001, cfg.max - cfg.min)) * (H - pT - pB)
        : H - pB - ((v - cfg.min) / Math.max(0.001, cfg.max - cfg.min)) * (H - pT - pB);

      let svg = `<div class="overflow-x-auto pb-1"><div class="min-w-[680px]"><svg viewBox="0 0 ${W} ${H}" class="w-full h-auto bg-slate-50/70 rounded-lg border border-slate-200">`;
      // Horizontal grid lines
      for (let g = 0; g <= 4; g++) {
        const val = cfg.min + (g / 4) * (cfg.max - cfg.min);
        const yy = sy(val);
        svg += `<line x1="${pL}" y1="${yy.toFixed(1)}" x2="${W-pR}" y2="${yy.toFixed(1)}" stroke="#E2E8F0" stroke-width="1"/>`;
        svg += `<text x="${pL-7}" y="${(yy+3.5).toFixed(1)}" text-anchor="end" font-size="10" fill="#64748B" font-family="Consolas, monospace">${cfg.fmt(val)}</text>`;
      }
      if (cfg.baseVal !== null) {
        const yb = sy(cfg.baseVal);
        svg += `<line x1="${pL}" y1="${yb.toFixed(1)}" x2="${W-pR}" y2="${yb.toFixed(1)}" stroke="#64748B" stroke-width="1.3" stroke-dasharray="5 3"/>`;
        svg += `<text x="${W-pR}" y="${(yb - 4).toFixed(1)}" text-anchor="end" font-size="9" font-weight="800" fill="#475569">Línea base ${cfg.baseLbl}</text>`;
      }

      // Partial pitch-tracking shading 2006-2010 & Tricampeonato 2010-2012 bands dynamically anchored
      const i2010 = Math.max(0, sortedAsc.findIndex((h) => h.season === 2010));
      const i2012 = Math.max(i2010 + 2, sortedAsc.findIndex((h) => h.season === 2012));
      const xEnd2010 = sx(Math.min(sortedAsc.length - 1, i2010)) + 10;
      svg += `<rect x="${pL}" y="${pT}" width="${(xEnd2010 - pL).toFixed(1)}" height="${H-pT-pB}" fill="#F59E0B" fill-opacity="0.08"/>`;
      svg += `<text x="${pL+4}" y="16" font-size="9.5" font-weight="800" fill="#B45309">2006–2010: PBP Parcial</text>`;

      const xTri1 = sx(i2010) - 10, xTri2 = sx(i2012) + 10;
      svg += `<rect x="${xTri1.toFixed(1)}" y="${pT}" width="${(xTri2 - xTri1).toFixed(1)}" height="${H-pT-pB}" fill="#0095DA" fill-opacity="0.09"/>`;
      svg += `<text x="${((xTri1+xTri2)/2).toFixed(1)}" y="16" text-anchor="middle" font-size="9.5" font-weight="800" fill="#0057A8">★ Tricampeonato (2010–13)</text>`;

      // Legend cleanly top-right above pT (including ★ Campeón & ● 2025-27 Actual)
      svg += `<line x1="${W-455}" y1="13" x2="${W-435}" y2="13" stroke="#003B73" stroke-width="3"/><text x="${W-430}" y="16.5" font-size="10" font-weight="800" fill="#002850">${esc(cfg.l1)}</text>`;
      if (cfg.y2) {
        svg += `<line x1="${W-290}" y1="13" x2="${W-270}" y2="13" stroke="#0095DA" stroke-width="2" stroke-dasharray="5 3"/><text x="${W-265}" y="16.5" font-size="10" font-weight="700" fill="#475569">${esc(cfg.l2)}</text>`;
      }
      svg += `<text x="${W-130}" y="16.5" font-size="10" font-weight="800" fill="#D97706">★ Campeón</text>`;
      svg += `<circle cx="${W-62}" cy="13" r="4" fill="#E6392F"/><text x="${W-55}" y="16.5" font-size="10" font-weight="800" fill="#E6392F">2025–27</text>`;

      if (cfg.y2) {
        const pts2 = sortedAsc.map((d, i) => `${sx(i).toFixed(1)},${sy(Number(d[cfg.y2] ?? cfg.min)).toFixed(1)}`).join(" ");
        svg += `<polyline fill="none" stroke="#0095DA" stroke-width="2" stroke-dasharray="5 3" points="${pts2}"/>`;
      }
      const pts1 = sortedAsc.map((d, i) => `${sx(i).toFixed(1)},${sy(Number(d[cfg.y1] ?? cfg.min)).toFixed(1)}`).join(" ");
      svg += `<polyline fill="none" stroke="#003B73" stroke-width="2.8" points="${pts1}"/>`;

      sortedAsc.forEach((d, i) => {
        const px = sx(i);
        const py = sy(Number(d[cfg.y1] ?? cfg.min));
        const isChamp = d.outcome === "Campeón";
        const color = isChamp ? "#F59E0B" : (d.season >= 2025 ? "#E6392F" : "#003B73");
        svg += `<g class="hist-dot cursor-pointer" data-label="${esc(d.label)}" data-rec="${d.reg_W}-${d.reg_L}" data-out="${esc(d.outcome)}" data-ops="${fmtRate(d.yaq_OPS)}" data-era="${fmtNum(d.yaq_ERA,2)}" data-diff="${d.Diff}">`;
        svg += `<circle cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="${isChamp ? 6.2 : 4.2}" fill="${color}" stroke="#FFFFFF" stroke-width="1.5"/>`;
        if (isChamp) svg += `<text x="${px.toFixed(1)}" y="${(py - 9).toFixed(1)}" text-anchor="middle" font-size="11.5" fill="#D97706">★</text>`;
        if (i % 2 === 0 || i === sortedAsc.length - 1) {
          const sEnd = String((d.season + 1) % 100).padStart(2, "0");
          const sLbl = `'${String(d.season).slice(-2)}-${sEnd}`;
          svg += `<text x="${px.toFixed(1)}" y="${H-13}" text-anchor="middle" font-size="9.3" font-weight="700" fill="#475569">${esc(sLbl)}</text>`;
        }
        svg += `</g>`;
      });
      svg += `</svg></div></div>`;
      wrapChart.innerHTML = svg;

      wrapChart.querySelectorAll(".hist-dot").forEach((el) => {
        el.addEventListener("mousemove", (e) => {
          showTooltip(e, `<strong>Temporada ${esc(el.dataset.label)}</strong> · ${esc(el.dataset.out)}<br>Récord: <b>${esc(el.dataset.rec)}</b> (Diff ${el.dataset.diff > 0 ? "+" : ""}${el.dataset.diff})<br>OPS: <b>${el.dataset.ops}</b> · ERA: <b>${el.dataset.era}</b>`);
        });
        el.addEventListener("mouseleave", hideTooltip);
      });

      if (storyEl) {
        const bestPct = [...sortedAsc].sort((a, b) => b.reg_PCT - a.reg_PCT)[0];
        const champs = sortedAsc.filter((h) => h.outcome === "Campeón").map((h) => h.label).join(", ");
        const cur25 = sortedAsc.find((h) => h.season === 2025);
        const cur25Txt = cur25 ? ` En <strong>2025–26</strong> Yaquis lideró el rol regular (<strong>${cur25.reg_W}-${cur25.reg_L}</strong>) sustentado en <strong>${fmtNum(cur25.yaq_ERA,2)} ERA</strong> (vs ${fmtNum(cur25.lmp_ERA,2)} LMP).` : "";
        storyEl.innerHTML = `<div class="bg-slate-50 border-l-4 border-[#003B73] rounded-r px-3 py-2 text-xs text-slate-700 leading-relaxed"><strong>Contexto 21 Temporadas:</strong> Títulos en la era digital: <strong>${esc(champs)}</strong>. Mejor campaña regular: <strong>${esc(bestPct.label)}</strong> (<strong>${bestPct.reg_W}-${bestPct.reg_L}</strong>, PCT ${fmtRate(bestPct.reg_PCT)}).${cur25Txt}</div>`;
      }

      // Historical Table
      let tbl = `<table class="fo-table"><thead><tr>
        <th class="text-left">Temp.</th><th class="text-left">Resultado LMP</th><th class="text-right">G-P Reg</th><th class="text-right">PCT</th><th class="text-right">Pyth</th>
        <th class="text-right">CA / CP</th><th class="text-right">Diff</th><th class="text-right">OPS (LMP)</th><th class="text-right">ERA (LMP)</th><th class="text-right">WHIP</th>
        <th class="text-right">G-P PO</th><th class="text-right">Strike%</th><th class="text-right">InZone%</th>
      </tr></thead><tbody>`;
      HIST.forEach((h) => {
        const badgeCls = h.outcome === "Campeón"
          ? "bg-amber-100 text-amber-800 border border-amber-300"
          : (h.outcome === "Subcampeón" ? "bg-sky-100 text-sky-800" : "bg-slate-100 text-slate-700");
        const partialTag = !h.pitch_tracking_full ? ` <span title="2006–2010 tracking parcial PBP" class="text-[9px] bg-amber-100 text-amber-800 px-1 rounded">PBP*</span>` : "";
        tbl += `<tr class="${h.season >= 2025 ? "yaquis-highlight-row" : ""}">
          <td class="text-left font-bold">${esc(h.label)}${partialTag}</td>
          <td class="text-left"><span class="text-[11px] font-bold px-2 py-0.5 rounded ${badgeCls}">${h.outcome === "Campeón" ? "★ " : ""}${esc(h.outcome)}</span></td>
          <td class="text-right">${h.reg_W}-${h.reg_L}</td>
          <td class="text-right font-bold">${fmtRate(h.reg_PCT)}</td>
          <td class="text-right">${fmtRate(h.Pyth_PCT)}</td>
          <td class="text-right">${h.RS}/${h.RA}</td>
          <td class="text-right font-bold ${h.Diff >= 0 ? "text-emerald-700" : "text-red-700"}">${h.Diff > 0 ? `+${h.Diff}` : h.Diff}</td>
          <td class="text-right">${fmtRate(h.yaq_OPS)} <span class="text-slate-400">(${fmtRate(h.lmp_OPS)})</span></td>
          <td class="text-right">${fmtNum(h.yaq_ERA, 2)} <span class="text-slate-400">(${fmtNum(h.lmp_ERA, 2)})</span></td>
          <td class="text-right">${fmtNum(h.yaq_WHIP, 2)}</td>
          <td class="text-right">${h.po_G ? `${h.po_W}-${h.po_L}` : "—"}</td>
          <td class="text-right">${fmtNum(h.Strike_pct, 1, "%")}</td>
          <td class="text-right">${fmtNum(h.InZone_pct, 1, "%")}</td>
        </tr>`;
      });
      tbl += `</tbody></table>`;
      wrapTbl.innerHTML = tbl;
    }

    // =========================================================================
    // 5. MÓDULO 2: BATEO LAB & ESTADIO YAQUIS SPRAY CHART 2D
    // =========================================================================
    function renderBattingModule() {
      const { key: sk, data: sdata } = activeSeasonData();
      const rawBatters = (sdata.yaquis_batters || []).filter((b) => b.etapa === state.stage);
      const spraySel = document.getElementById("sel-spray-player");
      const condName = COND_LABELS[state.cond] || state.cond;
      document.getElementById("bat-split-caption").textContent = `${STAGE_LABELS[state.stage]} · Condición: ${condName} · ${rawBatters.length} bateadores con aparición`;

      // Populate spray player selector matching active sprayMode ('off' = batters, 'def' = pitchers!)
      const pMap = {};
      if (state.sprayMode === "def") {
        (sdata.spray_points || []).forEach((pt) => {
          const stageOk = state.stage === "global_reg" ? (pt[0] === "v1" || pt[0] === "v2") : (pt[0] === state.stage);
          if (stageOk && pt[1] === 1 && pt[3]) {
            pMap[pt[3]] = getProfile(sk, pt[3]).full_name;
          }
        });
      } else {
        rawBatters.forEach((b) => { pMap[b.player_id] = getProfile(sk, b.player_id).full_name; });
      }
      const prevPlayer = state.sprayPlayer;
      let optHtml = state.sprayMode === "def"
        ? `<option value="all">Todo el Staff Defensivo Yaquis</option>`
        : `<option value="all">Todo el Roster Yaquis (Bateo)</option>`;
      Object.entries(pMap)
        .sort((a, b) => a[1].localeCompare(b[1], "es"))
        .forEach(([pid, name]) => {
          optHtml += `<option value="${pid}">${esc(name)}</option>`;
        });
      spraySel.innerHTML = optHtml;
      spraySel.value = pMap[prevPlayer] ? prevPlayer : "all";
      state.sprayPlayer = spraySel.value;

      // Table assembly
      const rows = rawBatters.map((b) => {
        const sp = b.splits?.[state.cond] || {};
        const spAll = b.splits?.all || {};
        const prof = getProfile(sk, b.player_id);
        return {
          player_id: b.player_id,
          prof,
          name: prof.full_name,
          pos: prof.primary_position,
          bt: `${prof.bat_side || "?"}/${prof.pitch_hand || "?"}`,
          status: prof.roster_status,
          ...sp,
          SB: b.SB ?? sp.SB ?? spAll.SB ?? 0,
          CS: b.CS ?? sp.CS ?? spAll.CS ?? 0,
          SB_pct: b.SB_pct ?? sp.SB_pct ?? spAll.SB_pct,
          RISP_AVG: b.RISP_AVG ?? sp.RISP_AVG ?? spAll.RISP_AVG,
          TWO_OUT_RISP_AVG: b.TWO_OUT_RISP_AVG ?? sp.TWO_OUT_RISP_AVG ?? spAll.TWO_OUT_RISP_AVG,
          LATE_CLOSE_OPS: b.LATE_CLOSE_OPS ?? sp.LATE_CLOSE_OPS ?? spAll.LATE_CLOSE_OPS,
          HIGH_LEV_OPS: b.HIGH_LEV_OPS ?? sp.HIGH_LEV_OPS ?? spAll.HIGH_LEV_OPS,
        };
      }).filter((r) => (r.PA || 0) > 0 && (r.PA || 0) >= state.batMinPA && (!state.batSearch || r.name.toLowerCase().includes(state.batSearch.toLowerCase())));

      const tblContainer = document.getElementById("batting-table-container");
      if (!rawBatters.length) {
        tblContainer.innerHTML = emptyStageCard("No hay estadísticas individuales de bateo registradas en esta etapa.");
      } else if (!rows.length) {
        tblContainer.innerHTML = `<div class="p-6 text-center text-xs text-slate-500">Ningún bateador cumple con el filtro de <strong>≥ ${state.batMinPA} PA</strong> y búsqueda actual. Reduce el mínimo de PA.</div>`;
      } else {
        const isAllCond = state.cond === "all";
        const cols = [
          {
            k: "name",
            l: "Bateador",
            align: "left",
            fmt: (v, r) => `
              <div class="flex items-center gap-2.5">
                ${renderPlayerAvatar(r.prof, "w-8 h-10", "rounded-md")}
                <div>
                  <button onclick="window.__jumpToPlayer(${r.player_id}, 'scouting')" class="text-left font-extrabold text-[#003B73] hover:text-[#0072B2] hover:underline block leading-tight">${esc(v)}</button>
                  <span class="text-[10.5px] text-slate-500 font-code">${esc(r.pos)} · ${esc(r.bt)}</span>
                </div>
              </div>`,
          },
          { k: "PA", l: "PA", fmt: fmtInt },
          { k: "AB", l: "AB", fmt: fmtInt },
          { k: "H", l: "H", fmt: fmtInt },
          { k: "2B", l: "2B", fmt: fmtInt },
          { k: "HR", l: "HR", fmt: fmtInt },
          { k: "RBI", l: "RBI", fmt: fmtInt },
          { k: "AVG", l: "AVG", fmt: (v) => fmtRate(v) },
          { k: "OBP", l: "OBP", fmt: (v) => fmtRate(v) },
          { k: "SLG", l: "SLG", fmt: (v) => fmtRate(v) },
          { k: "OPS", l: "OPS", fmt: (v) => fmtRate(v) },
          { k: "OPS_plus", l: "OPS+", fmt: fmtInt },
          { k: "wOBA", l: "wOBA", fmt: (v) => fmtRate(v) },
          { k: "wRC_plus", l: "wRC+", fmt: fmtInt },
          { k: "ISO", l: "ISO", fmt: (v) => fmtRate(v) },
          { k: "BABIP", l: "BABIP", fmt: (v) => fmtRate(v) },
          { k: "BB_pct", l: "BB%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "K_pct", l: "K%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "BB_K", l: "BB/K", fmt: (v) => fmtNum(v, 2) },
          { k: "SB", l: isAllCond ? "BR" : "BR*", fmt: (v, r) => `${r.SB ?? 0}-${r.CS ?? 0}` },
          { k: "RISP_AVG", l: isAllCond ? "RISP" : "RISP*", fmt: (v) => fmtRate(v) },
          { k: "TWO_OUT_RISP_AVG", l: isAllCond ? "2Out RISP" : "2Out RISP*", fmt: (v) => fmtRate(v) },
          { k: "HIGH_LEV_OPS", l: isAllCond ? "HiLev OPS" : "HiLev OPS*", fmt: (v) => fmtRate(v) },
        ];

        const sorted = sortRows(rows, state.batSort);
        let h = `<table class="fo-table"><thead><tr>`;
        cols.forEach((c) => {
          const isSorted = state.batSort.col === c.k;
          const cls = `${isSorted ? "sorted-col " : ""}${c.align === "left" ? "text-left" : "text-right"}`;
          const arrow = isSorted ? (state.batSort.dir === 1 ? " ▲" : " ▼") : "";
          h += `<th class="${cls}" data-bsort="${c.k}">${esc(c.l)}${arrow}</th>`;
        });
        h += `</tr></thead><tbody>`;
        sorted.forEach((r) => {
          const smallSample = (r.PA || 0) < 30;
          const isSelected = String(r.player_id) === String(state.sprayPlayer);
          h += `<tr class="${isSelected ? "yaquis-highlight-row" : ""}">`;
          cols.forEach((c) => {
            const cls = `${c.align === "left" ? "text-left" : "text-right"}`;
            const badge = c.k === "PA" && smallSample ? ` <span title="Muestra pequeña (<30 PA)" class="text-[9px] text-amber-700 font-bold">●</span>` : "";
            const sprayBtn = c.align === "left"
              ? ` <button onclick="window.__filterSprayPlayer(${r.player_id}, 'off')" title="Ver rocío de batazos en Diamante" class="ml-1 text-[11px] px-1 py-0.5 rounded bg-sky-50 hover:bg-[#0072B2] text-[#003B73] hover:text-white border border-sky-200 transition">🎯</button>`
              : "";
            h += `<td class="${cls}">${c.fmt(r[c.k], r)}${badge}${sprayBtn}</td>`;
          });
          h += `</tr>`;
        });
        h += `</tbody></table>`;
        if (!isAllCond) {
          h += `<div class="px-3 py-1.5 text-[10.5px] text-slate-500 bg-slate-50 border-t border-slate-200">* Columnas situacionales (BR, RISP, 2Out RISP, HiLev OPS) preservan su muestra completa de la etapa para mantener el contexto situacional al cambiar Condición.</div>`;
        }
        tblContainer.innerHTML = h;

        tblContainer.querySelectorAll("th[data-bsort]").forEach((th) => {
          th.addEventListener("click", () => {
            const k = th.dataset.bsort;
            if (state.batSort.col === k) state.batSort.dir *= -1;
            else { state.batSort.col = k; state.batSort.dir = k === "K_pct" ? 1 : -1; }
            renderBattingModule();
          });
        });
      }

      renderSprayDiamond(sk, sdata);
      renderSpatialDefenseCard(sdata);
      renderBattingComparativeCharts(rows, sdata, sk);
    }

    function renderSprayDiamond(sk, sdata) {
      const svgEl = document.getElementById("spray-diamond-svg");
      const cardEl = document.getElementById("spray-selected-card");
      const allPoints = sdata.spray_points || [];
      const isDefTarget = state.sprayMode === "def" ? 1 : 0;

      if (cardEl) {
        if (state.sprayPlayer !== "all") {
          const spProf = getProfile(sk, Number(state.sprayPlayer));
          cardEl.innerHTML = `
            <div class="flex items-center gap-3 min-w-0">
              ${renderPlayerAvatar(spProf, "w-11 h-[54px]", "rounded-lg")}
              <div class="min-w-0">
                <div class="text-xs font-extrabold text-white truncate">${esc(spProf.full_name)}</div>
                <div class="text-[11px] text-[#7DD3FC] font-code">${esc(spProf.primary_position)} · B/T ${esc(spProf.bat_side)}/${esc(spProf.pitch_hand)} · ${esc(spProf.roster_status)}</div>
              </div>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <button onclick="window.__resetSprayPlayer()" class="text-[11px] font-bold bg-[#0F1E33] hover:bg-slate-800 text-slate-200 border border-[#1E3A5F] px-2 py-1 rounded">× Ver todo</button>
              <button onclick="window.__jumpToPlayer(${spProf.player_id}, 'scouting')" class="text-[11px] font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-2.5 py-1 rounded">Ficha 360° →</button>
            </div>`;
        } else {
          cardEl.innerHTML = `
            <div class="flex items-center gap-3">
              ${renderTeamLogo(680, "Yaquis de Obregón", "w-10 h-10")}
              <div>
                <div class="text-xs font-extrabold text-white">${state.sprayMode === "def" ? "Mapa Defensivo Yaquis vs Rivales" : "Ofensiva Colectiva Yaquis"}</div>
                <div class="text-[11px] text-slate-300">${esc(STAGE_LABELS[state.stage])} · ${esc(COND_LABELS[state.cond])}</div>
              </div>
            </div>
            <span class="text-[10px] font-code text-[#7DD3FC]">Estadio Yaquis 330–400 ft</span>`;
        }
      }

      // Filter points: [etapa, is_def, batter_id, pitcher_id, x, y, loc, traj, hard, ev, is_out, bat_side, pitch_hand, is_risp, is_home]
      const pts = allPoints.filter((p) => {
        if (state.stage === "global_reg") {
          if (p[0] !== "v1" && p[0] !== "v2") return false;
        } else if (p[0] !== state.stage) {
          return false;
        }
        if (p[1] !== isDefTarget) return false;
        if (state.cond === "home" && p[14] !== 1) return false;
        if (state.cond === "away" && p[14] !== 0) return false;
        if (state.cond === "vs_lhp" && p[12] !== "L") return false;
        if (state.cond === "vs_rhp" && p[12] !== "R") return false;
        if (state.cond === "risp" && p[13] !== 1) return false;

        if (state.sprayPlayer !== "all") {
          const targetId = Number(state.sprayPlayer);
          if (isDefTarget === 0 && p[2] !== targetId) return false;
          if (isDefTarget === 1 && p[3] !== targetId) return false;
        }
        if (state.sprayTraj !== "all") {
          const tMatch = p[7] === state.sprayTraj
            || (state.sprayTraj === "ground_ball" && p[7] === "bunt_grounder")
            || (state.sprayTraj === "popup" && p[7] === "bunt_popup")
            || (state.sprayTraj === "line_drive" && p[7] === "bunt_line_drive");
          if (!tMatch) return false;
        }

        const ev = p[9];
        const isHit = ["single", "double", "triple", "home_run"].includes(ev);
        const isXbh = ["double", "triple", "home_run"].includes(ev);
        if (state.sprayRes === "hits" && !isHit) return false;
        if (state.sprayRes === "xbh" && !isXbh) return false;
        if (state.sprayRes === "hr" && ev !== "home_run") return false;
        if (state.sprayRes === "outs" && p[10] !== 1) return false;
        return true;
      });

      // Calibrated Gameday Diamond Geometry: Home Plate at (125.4, 199)
      let svg = `
        <defs>
          <radialGradient id="turfGrad" cx="50%" cy="82%" r="75%">
            <stop offset="0%" stop-color="#133829"/>
            <stop offset="100%" stop-color="#0B221A"/>
          </radialGradient>
        </defs>
        <!-- Fair territory & Estadio Yaquis outfield wall arc -->
        <path d="M125.4,199 L23,96.6 Q125.4,24 227.8,96.6 Z" fill="url(#turfGrad)" stroke="#0095DA" stroke-width="1.4"/>
        <!-- Outfield warning track / depth arc rings -->
        <path d="M51,124.6 Q125.4,68 199.8,124.6" fill="none" stroke="#1E4D3B" stroke-width="1" stroke-dasharray="3 3"/>
        <path d="M23,96.6 Q125.4,24 227.8,96.6" fill="none" stroke="#E6392F" stroke-width="1.8" stroke-opacity="0.75"/>
        <!-- Infield dirt diamond (approx 90ft scaled to ~35.5px) -->
        <path d="M125.4,199 L155,169.4 Q125.4,132 95.8,169.4 Z" fill="#4A3525" fill-opacity="0.65" stroke="#8C6B4E" stroke-width="0.9"/>
        <!-- Base paths -->
        <polygon points="125.4,199 150.5,173.9 125.4,148.8 100.3,173.9" fill="#133829" stroke="#CBD5E1" stroke-width="0.9"/>
        <!-- Pitcher Mound -->
        <circle cx="125.4" cy="176" r="4" fill="#6B4D37" stroke="#94A3B8" stroke-width="0.6"/>
        <!-- Bases & Home -->
        <rect x="148.5" y="171.9" width="4" height="4" fill="#FFFFFF"/>
        <rect x="123.4" y="146.8" width="4" height="4" fill="#FFFFFF"/>
        <rect x="98.3" y="171.9" width="4" height="4" fill="#FFFFFF"/>
        <polygon points="125.4,201 123,198.5 123,196.5 127.8,196.5 127.8,198.5" fill="#FFFFFF"/>
        <!-- Sector guides LF / CF / RF -->
        <line x1="125.4" y1="199" x2="88" y2="56" stroke="#FFFFFF" stroke-opacity="0.18" stroke-dasharray="3 3"/>
        <line x1="125.4" y1="199" x2="163" y2="56" stroke="#FFFFFF" stroke-opacity="0.18" stroke-dasharray="3 3"/>
      `;

      const evColors = { single: "#0095DA", double: "#16A34A", triple: "#F59E0B", home_run: "#E6392F" };
      const dense = pts.length > 600;
      const ordered = [...pts].sort((a, b) => (b[10] - a[10]));
      ordered.forEach((p) => {
        const cx = p[4], cy = p[5], ev = p[9];
        const color = evColors[ev] || "#94A3B8";
        const r = dense ? (ev === "home_run" ? 3.2 : (evColors[ev] ? 2.1 : 1.45)) : (ev === "home_run" ? 4.2 : (evColors[ev] ? 2.9 : 2.1));
        const op = dense ? (evColors[ev] ? 0.85 : 0.44) : (evColors[ev] ? 0.94 : 0.65);
        const bName = getProfile(sk, p[2]).full_name;
        const pitName = getProfile(sk, p[3]).full_name;
        const dAttrs = `data-bat="${esc(bName)}" data-pit="${esc(pitName)}" data-ev="${esc(ev)}" data-traj="${esc(p[7])}" data-hard="${esc(p[8])}" data-loc="${esc(p[6])}" data-risp="${p[13]}"`;
        if (ev === "home_run") {
          svg += `<circle cx="${cx}" cy="${cy}" r="${(r + 2.2).toFixed(1)}" fill="none" stroke="#FDE047" stroke-width="0.9" stroke-opacity="0.75" pointer-events="none"/>`;
          svg += `<polygon class="sp-pt cursor-pointer" points="${cx},${(cy - r).toFixed(1)} ${(cx + r).toFixed(1)},${cy} ${cx},${(cy + r).toFixed(1)} ${(cx - r).toFixed(1)},${cy}" fill="${color}" fill-opacity="${op}" stroke="#FFFFFF" stroke-width="0.75" ${dAttrs}/>`;
        } else if (ev === "double" || ev === "triple") {
          const ringC = ev === "triple" ? "#FDE047" : "#4ADE80";
          svg += `<circle class="sp-pt cursor-pointer" cx="${cx}" cy="${cy}" r="${r.toFixed(1)}" fill="${color}" fill-opacity="${op}" stroke="${ringC}" stroke-width="0.95" ${dAttrs}/>`;
        } else {
          svg += `<circle class="sp-pt cursor-pointer" cx="${cx}" cy="${cy}" r="${r.toFixed(1)}" fill="${color}" fill-opacity="${op}" stroke="#08101C" stroke-width="0.3" ${dAttrs}/>`;
        }
      });

      // Fence dimension pills rendered cleanly OUTSIDE / ABOVE the field so dots never cover labels
      svg += `
        <g pointer-events="none">
          <rect x="6" y="76" width="38" height="12" rx="3" fill="#0B1320" fill-opacity="0.92" stroke="#1E3A5F" stroke-width="0.7"/>
          <text x="25" y="84.5" text-anchor="middle" font-size="6.5" font-weight="800" fill="#CBD5E1">LF 330'</text>
          <rect x="106" y="12" width="39" height="12" rx="3" fill="#0B1320" fill-opacity="0.92" stroke="#1E3A5F" stroke-width="0.7"/>
          <text x="125.5" y="20.5" text-anchor="middle" font-size="6.5" font-weight="800" fill="#CBD5E1">CF 400'</text>
          <rect x="207" y="76" width="38" height="12" rx="3" fill="#0B1320" fill-opacity="0.92" stroke="#1E3A5F" stroke-width="0.7"/>
          <text x="226" y="84.5" text-anchor="middle" font-size="6.5" font-weight="800" fill="#CBD5E1">RF 330'</text>
        </g>`;

      if (!pts.length) {
        svg += `<text x="126" y="120" text-anchor="middle" font-size="8.5" font-weight="700" fill="#94A3B8">Sin bolas en juego para los filtros activos</text>`;
      }
      svgEl.innerHTML = svg;

      svgEl.querySelectorAll(".sp-pt").forEach((el) => {
        el.addEventListener("mousemove", (e) => {
          const evTxt = EV_ES[el.dataset.ev] || el.dataset.ev.toUpperCase();
          const trTxt = TRAJ_ES[el.dataset.traj] || el.dataset.traj || "—";
          const hdTxt = HARD_ES[el.dataset.hard] || el.dataset.hard || "—";
          const locTxt = HIT_LOC_ES[String(el.dataset.loc || "")] || (el.dataset.loc ? `Pos. ${el.dataset.loc}` : "Campo");
          const rispBadge = el.dataset.risp === "1" ? ` · <span class="text-amber-300 font-bold">Con RISP</span>` : "";
          showTooltip(e, `<strong>${esc(evTxt)}</strong> (${esc(trTxt)})${rispBadge}<br>Bateador: <b>${esc(el.dataset.bat)}</b><br>Lanzador: ${esc(el.dataset.pit)}<br>${esc(hdTxt)} · Sector ${esc(locTxt)}`);
        });
        el.addEventListener("mouseleave", hideTooltip);
      });

      // Live summary cards & Handedness-adjusted Pull% · Center% · Oppo% bar
      const nBip = pts.length;
      const hits = pts.filter((p) => ["single", "double", "triple", "home_run"].includes(p[9])).length;
      const hrs = pts.filter((p) => p[9] === "home_run").length;
      const gbs = pts.filter((p) => (p[7] || "").includes("ground")).length;
      const lds = pts.filter((p) => p[7] === "line_drive").length;
      const fbs = pts.filter((p) => (p[7] || "").includes("fly") || (p[7] || "").includes("popup")).length;
      const lfSide = pts.filter((p) => p[4] < 106).length;
      const cfSide = pts.filter((p) => p[4] >= 106 && p[4] <= 145).length;
      const rfSide = pts.filter((p) => p[4] > 145).length;
      let pullCnt = 0, centCnt = 0, oppoCnt = 0;
      pts.forEach((p) => {
        const px = p[4], bs = p[11];
        if (px >= 106 && px <= 145) { centCnt++; }
        else if (bs === "L") { if (px > 145) pullCnt++; else oppoCnt++; }
        else { if (px < 106) pullCnt++; else oppoCnt++; }
      });
      const pullPct = nBip ? Math.round(pullCnt / nBip * 100) : 0;
      const centPct = nBip ? Math.round(centCnt / nBip * 100) : 0;
      const oppoPct = nBip ? Math.max(0, 100 - pullPct - centPct) : 0;
      const pullWrap = document.getElementById("spray-pull-bar");
      if (pullWrap) {
        const dirPrefix = state.sprayMode === "def" ? `<span class="text-slate-300 font-semibold mr-1">Tendencia Rival Permitida ·</span>` : "";
        pullWrap.innerHTML = nBip ? `
          <div class="flex flex-wrap items-center justify-between gap-1 text-[10.5px] font-bold mb-1">
            <span>${dirPrefix}<span class="text-[#7DD3FC]">Jalar (Pull) ${pullPct}%</span></span>
            <span class="text-emerald-300">Centro ${centPct}%</span>
            <span class="text-amber-300">Campo Opuesto ${oppoPct}%</span>
          </div>
          <div class="w-full h-2.5 rounded-full overflow-hidden flex bg-slate-800 border border-[#1E3A5F]">
            <div style="width:${pullPct}%;background:#0095DA" title="Pull ${pullPct}%"></div>
            <div style="width:${centPct}%;background:#16A34A" title="Centro ${centPct}%"></div>
            <div style="width:${oppoPct}%;background:#F59E0B" title="Oppo ${oppoPct}%"></div>
          </div>` : `<div class="text-[10.5px] text-slate-400 text-center">Sin perfil direccional Pull/Center/Oppo</div>`;
      }

      document.getElementById("spray-summary-strip").innerHTML = `
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-2"><div class="text-[10px] text-slate-400 font-bold">BIP</div><div class="text-sm font-black text-white tabular-nums">${nBip}</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-2"><div class="text-[10px] text-slate-400 font-bold">HITS (BIP%)</div><div class="text-sm font-black text-[#7DD3FC] tabular-nums">${hits} (${nBip ? Math.round(hits/nBip*100) : 0}%)</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-2"><div class="text-[10px] text-slate-400 font-bold">GB% / LD%</div><div class="text-sm font-black text-emerald-400 tabular-nums">${nBip ? Math.round(gbs/nBip*100) : 0}% / ${nBip ? Math.round(lds/nBip*100) : 0}%</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-2"><div class="text-[10px] text-slate-400 font-bold">FB% / HR</div><div class="text-sm font-black text-amber-400 tabular-nums">${nBip ? Math.round(fbs/nBip*100) : 0}% (${hrs})</div></div>
      `;
      const sprayStoryEl = document.getElementById("spray-story-box");
      if (sprayStoryEl) {
        sprayStoryEl.innerHTML = nBip
          ? `<div class="bg-[#0F1E33] border-l-4 border-[#0095DA] rounded-r px-3 py-2 text-[11px] text-slate-200 leading-relaxed"><strong class="text-[#7DD3FC]">Distribución Direccional (n=${nBip}):</strong> Jardín Izq <strong>${Math.round(lfSide/nBip*100)}%</strong> · Centro <strong>${Math.round(cfSide/nBip*100)}%</strong> · Jardín Der <strong>${Math.round(rfSide/nBip*100)}%</strong> · Jalar <strong>${pullPct}%</strong> vs Opuesto <strong>${oppoPct}%</strong> · Líneas <strong>${(lds/nBip*100).toFixed(1)}%</strong>.</div>`
          : "";
      }
    }

    function renderSpatialDefenseCard(sdata) {
      const tb = sdata.team_benchmarks?.[state.stage] || {};
      const yaq = (tb.teams || []).find((t) => t.team_id === 680);
      const wrap = document.getElementById("spatial-defense-panel");
      if (!yaq) {
        wrap.innerHTML = `<div class="text-xs text-slate-400">Sin datos defensivos espaciales para la etapa actual.</div>`;
        return;
      }
      const zones = [
        { k: "INF", label: "Infield (1–6)", der: yaq.DER_INF, oaa: yaq.OAA_INF },
        { k: "LF", label: "Jardín Izq (7)", der: yaq.DER_LF, oaa: yaq.OAA_LF },
        { k: "CF", label: "Jardín Cen (8)", der: yaq.DER_CF, oaa: yaq.OAA_CF },
        { k: "RF", label: "Jardín Der (9)", der: yaq.DER_RF, oaa: yaq.OAA_RF },
      ];
      wrap.innerHTML = `
        <div class="flex items-center justify-between text-xs">
          <span class="font-extrabold text-[#7DD3FC] uppercase tracking-wider">Eficiencia Defensiva Espacial (DER% &amp; OAA est.)</span>
          <span class="text-slate-300 font-code">CS% Receptores: <strong class="text-emerald-400">${fmtNum(yaq.C_CS_pct,1,"%")}</strong> · FPCT ${fmtNum(yaq.FPCT,4)}</span>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
          ${zones.map((z) => `
            <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-2">
              <div class="text-[10px] font-bold text-slate-400">${esc(z.label)}</div>
              <div class="text-xs font-black text-white mt-0.5 tabular-nums">DER ${fmtNum(z.der, 1, "%")}</div>
              <div class="text-[11px] font-bold ${(z.oaa || 0) >= 0 ? "text-emerald-400" : "text-red-400"} tabular-nums">OAA ${z.oaa > 0 ? "+" : ""}${fmtNum(z.oaa, 1)}</div>
            </div>
          `).join("")}
        </div>`;
    }

    // =========================================================================
    // 6. MÓDULO 3: PITCHEO, ZONA DE STRIKE 2D & CARGA DE TRABAJO
    // =========================================================================
    function renderPitchingModule() {
      const { key: sk, data: sdata } = activeSeasonData();
      const rawPitchers = (sdata.yaquis_pitchers || []).filter((p) => p.etapa === state.stage);

      // Condition note for pitching
      let condNote = "";
      if (state.cond === "vs_lhp" || state.cond === "vs_rhp") {
        condNote = ` · Nota: ${COND_LABELS[state.cond]} aplica a Bateo; en Pitcheo usa "vs Bateadores (L/R)" en Zona 2D o splits LHB/RHB en Scouting.`;
      } else if (state.cond !== "all") {
        condNote = ` · Nota: la tabla muestra ${STAGE_LABELS[state.stage]} completo; la Zona 2D y los Splits en Scouting filtran "${COND_LABELS[state.cond]}".`;
      }
      document.getElementById("pit-split-caption").textContent = `${STAGE_LABELS[state.stage]} · ${rawPitchers.length} lanzadores${condNote}`;

      // Populate zone pitcher selector
      const zSel = document.getElementById("sel-zone-pitcher");
      const prevZ = state.zonePitcher;
      let zOpts = `<option value="all">Todo el Staff de Yaquis</option><option value="role:Abridor">Solo Abridores</option><option value="role:Bullpen">Solo Bullpen</option>`;
      const pMap = {};
      rawPitchers.forEach((p) => { pMap[p.player_id] = getProfile(sk, p.player_id).full_name; });
      Object.entries(pMap)
        .sort((a, b) => a[1].localeCompare(b[1], "es"))
        .forEach(([pid, name]) => { zOpts += `<option value="${pid}">${esc(name)}</option>`; });
      zSel.innerHTML = zOpts;
      if (prevZ === "all" || prevZ.startsWith("role:") || pMap[prevZ]) zSel.value = prevZ;
      else zSel.value = "all";
      state.zonePitcher = zSel.value;

      // Filter pitchers: fatigue monitor stays independent of pitMinIP so low-IP B2B/Critical relievers remain visible
      const roleSearchPits = rawPitchers.map((p) => {
        const prof = getProfile(sk, p.player_id);
        return { ...p, prof, name: prof.full_name, hand: prof.pitch_hand };
      }).filter((p) => {
        if (state.pitRoleFilter !== "all" && p.rol !== state.pitRoleFilter) return false;
        if (state.pitSearch && !p.name.toLowerCase().includes(state.pitSearch.toLowerCase())) return false;
        return true;
      });
      const filteredPits = roleSearchPits.filter((p) => (p.IP || 0) >= state.pitMinIP);

      const tblWrap = document.getElementById("pitching-table-container");
      if (!rawPitchers.length) {
        tblWrap.innerHTML = emptyStageCard("No hay estadísticas de pitcheo disponibles para esta etapa.");
      } else if (!filteredPits.length) {
        tblWrap.innerHTML = `<div class="p-6 text-center text-xs text-slate-500">Sin lanzadores que coincidan con el mínimo de ${state.pitMinIP} IP y búsqueda actual.</div>`;
      } else {
        const cols = [
          {
            k: "name",
            l: "Lanzador",
            align: "left",
            fmt: (v, r) => `
              <div class="flex items-center gap-2">
                ${renderPlayerAvatar(r.prof, "w-8 h-10", "rounded-md")}
                <div class="min-w-0">
                  <button onclick="window.__jumpToPlayer(${r.player_id}, 'scouting')" class="text-left font-extrabold text-[#003B73] hover:text-[#0072B2] hover:underline block leading-tight">${esc(v)}</button>
                  <span class="text-[10.5px] font-code text-slate-500">${esc(r.hand || "?")}HP</span>
                </div>
                <button onclick="window.__filterZonePitcher(${r.player_id})" title="Cargar pitcheos en Zona 2D" class="ml-auto text-[11px] px-1 py-0.5 rounded bg-sky-50 hover:bg-[#0072B2] text-[#003B73] hover:text-white border border-sky-200 transition">🎯</button>
              </div>`,
          },
          { k: "rol", l: "Rol", align: "left", fmt: (v) => `<span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${v === "Abridor" ? "bg-sky-100 text-sky-900" : "bg-indigo-100 text-indigo-900"}">${esc(v)}</span>` },
          { k: "G", l: "G/GS", fmt: (v, r) => `${r.G}/${r.GS}` },
          { k: "W", l: "G-P-SV", fmt: (v, r) => `${r.W}-${r.L}-${r.SV}` },
          { k: "IP", l: "IP", fmt: (v) => `${fmtNum(v, 1)}${Number(v ?? 0) < 10 ? ` <span title="Muestra pequeña (&lt;10 IP)" class="text-[9px] text-amber-700 font-bold">●</span>` : ""}` },
          { k: "ERA", l: "ERA", fmt: (v) => fmtNum(v, 2) },
          { k: "ERA_minus", l: "ERA-", fmt: fmtInt },
          { k: "FIP", l: "FIP", fmt: (v) => fmtNum(v, 2) },
          { k: "xFIP", l: "xFIP", fmt: (v) => fmtNum(v, 2) },
          { k: "WHIP", l: "WHIP", fmt: (v) => fmtNum(v, 2) },
          { k: "K9", l: "K/9", fmt: (v) => fmtNum(v, 2) },
          { k: "BB9", l: "BB/9", fmt: (v) => fmtNum(v, 2) },
          { k: "K_BB", l: "K/BB", fmt: (v) => fmtNum(v, 2) },
          { k: "LOB_pct", l: "LOB%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "GB_FB", l: "GB/FB", fmt: (v) => fmtNum(v, 2) },
          { k: "Strike_pct", l: "Strike%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "InZone_pct", l: "InZone%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "Chase_pct", l: "Chase%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "Whiff_pct", l: "Whiff%", fmt: (v) => fmtNum(v, 1, "%") },
          { k: "IR", l: "IR/IRS", fmt: (v, r) => `${r.IR ?? 0}/${r.IRS ?? 0}` },
        ];
        const sorted = sortRows(filteredPits, state.pitSort);
        let h = `<table class="fo-table"><thead><tr>`;
        cols.forEach((c) => {
          const isSorted = state.pitSort.col === c.k;
          const cls = `${isSorted ? "sorted-col " : ""}${c.align === "left" ? "text-left" : "text-right"}`;
          const arrow = isSorted ? (state.pitSort.dir === 1 ? " ▲" : " ▼") : "";
          h += `<th class="${cls}" data-psort="${c.k}">${esc(c.l)}${arrow}</th>`;
        });
        h += `</tr></thead><tbody>`;
        sorted.forEach((r) => {
          const isSelected = String(r.player_id) === String(state.zonePitcher);
          h += `<tr class="${isSelected ? "yaquis-highlight-row" : ""}">`;
          cols.forEach((c) => {
            const cls = `${c.align === "left" ? "text-left" : "text-right"}`;
            h += `<td class="${cls}">${c.fmt(r[c.k], r)}</td>`;
          });
          h += `</tr>`;
        });
        h += `</tbody></table>`;
        tblWrap.innerHTML = h;

        tblWrap.querySelectorAll("th[data-psort]").forEach((th) => {
          th.addEventListener("click", () => {
            const k = th.dataset.psort;
            if (state.pitSort.col === k) state.pitSort.dir *= -1;
            else {
              state.pitSort.col = k;
              state.pitSort.dir = ["ERA", "ERA_minus", "FIP", "xFIP", "WHIP", "BB9"].includes(k) ? 1 : -1;
            }
            renderPitchingModule();
          });
        });
      }

      renderStrikeZone2D(sk, sdata, rawPitchers);
      renderFatigueMonitor(roleSearchPits);
      renderPitchingComparativeCharts(filteredPits, sdata, sk);
    }

    function renderStrikeZone2D(sk, sdata, rawPitchers) {
      const svgEl = document.getElementById("strike-zone-svg");
      const zCardEl = document.getElementById("zone-selected-card");
      const allPitches = sdata.pitch_points || [];
      const modeLbl = state.zoneMode === "heat_usage" ? "9-Zonas %Uso" : (state.zoneMode === "heat_whiff" ? "9-Zonas Whiff%" : "Elipse 1-SD Activa");

      if (zCardEl) {
        if (state.zonePitcher !== "all" && !state.zonePitcher.startsWith("role:")) {
          const zpId = Number(state.zonePitcher);
          const zpProf = getProfile(sk, zpId);
          const zpStat = rawPitchers.find((p) => p.player_id === zpId);
          zCardEl.innerHTML = `
            <div class="flex items-center gap-3 min-w-0">
              ${renderPlayerAvatar(zpProf, "w-11 h-[54px]", "rounded-lg")}
              <div class="min-w-0">
                <div class="text-xs font-extrabold text-white truncate">${esc(zpProf.full_name)}</div>
                <div class="text-[11px] text-[#7DD3FC] font-code">${esc(zpStat?.rol || zpProf.role_group)} · ${esc(zpProf.pitch_hand || "?")}HP${zpStat ? ` · ERA ${fmtNum(zpStat.ERA,2)} · FIP ${fmtNum(zpStat.FIP,2)}` : ""}</div>
              </div>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <button onclick="window.__resetZonePitcher()" class="text-[11px] font-bold bg-[#0F1E33] hover:bg-slate-800 text-slate-200 border border-[#1E3A5F] px-2 py-1 rounded">× Ver todo</button>
              <button onclick="window.__jumpToPlayer(${zpProf.player_id}, 'scouting')" class="text-[11px] font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-2.5 py-1 rounded">Ficha 360° →</button>
            </div>`;
        } else {
          const lbl = state.zonePitcher.startsWith("role:") ? `Staff Yaquis · ${state.zonePitcher.split(":")[1]}` : "Todo el Staff de Pitcheo Yaquis";
          zCardEl.innerHTML = `
            <div class="flex items-center gap-3">
              ${renderTeamLogo(680, "Yaquis de Obregón", "w-10 h-10")}
              <div>
                <div class="text-xs font-extrabold text-white">${esc(lbl)}</div>
                <div class="text-[11px] text-slate-300">${esc(STAGE_LABELS[state.stage])} · Zona Calibrada LMP</div>
              </div>
            </div>
            <span class="text-[10px] font-code text-[#7DD3FC]">${esc(modeLbl)}</span>`;
        }
      }

      const roleById = {};
      rawPitchers.forEach((p) => { roleById[p.player_id] = p.rol; });

      // 13 cols: [etapa, pitcher_id, batter_id, px, py, call_code, is_strike, in_zone, pnum, bat_side, is_home, is_risp, count_state]
      const pts = allPitches.filter((p) => {
        if (state.stage === "global_reg") {
          if (p[0] !== "v1" && p[0] !== "v2") return false;
        } else if (p[0] !== state.stage) {
          return false;
        }
        if (state.cond === "home" && p[10] !== 1) return false;
        if (state.cond === "away" && p[10] !== 0) return false;
        if (state.cond === "risp" && p[11] !== 1) return false;

        if (state.zonePitcher.startsWith("role:")) {
          const reqRol = state.zonePitcher.split(":")[1];
          if (roleById[p[1]] !== reqRol) return false;
        } else if (state.zonePitcher !== "all") {
          if (p[1] !== Number(state.zonePitcher)) return false;
        }

        if (state.zoneBatSide !== "all" && p[9] !== state.zoneBatSide) return false;
        if (state.zoneCount === "0-0" && p[12] !== "0-0") return false;
        if (state.zoneCount === "2K" && p[12] !== "2K") return false;
        if (state.zoneCount === "risp" && p[11] !== 1) return false;

        const cc = p[5];
        if (state.zoneCall === "called_strike" && cc !== "C") return false;
        if (state.zoneCall === "whiff" && cc !== "S" && cc !== "M" && cc !== "W") return false;
        if (state.zoneCall === "foul" && !["F", "T", "L", "O"].includes(cc)) return false;
        if (state.zoneCall === "inplay" && !["X", "D", "E"].includes(cc)) return false;
        if (state.zoneCall === "ball" && cc !== "B" && cc !== "*B") return false;
        return true;
      });

      const z = ZONE_CAL;
      const zw = z.x_hi - z.x_lo;
      const zh = z.y_hi - z.y_lo;
      const zThirdW = zw / 3;
      const zThirdH = zh / 3;

      let svg = `
        <!-- Outer canvas grid & Batter silhouettes (Catcher perspective: RHB on left, LHB on right) -->
        <rect x="0" y="0" width="220" height="250" fill="#08101C"/>
        <text x="${z.cx}" y="13" text-anchor="middle" font-size="7.5" font-weight="800" fill="#7DD3FC">PERSPECTIVA RECEPTOR · ZONA OFICIAL</text>
        <text x="${z.cx}" y="${(z.y_lo - 6).toFixed(1)}" text-anchor="middle" font-size="6.5" font-weight="800" fill="#94A3B8" letter-spacing="1.2">ZONA ALTA</text>
        <text x="${z.cx}" y="${(z.y_hi + 12).toFixed(1)}" text-anchor="middle" font-size="6.5" font-weight="800" fill="#94A3B8" letter-spacing="1.2">ZONA BAJA</text>
      `;

      // Subtle Batter Silhouettes + Interior/Exterior directional tags
      if (state.zoneBatSide === "all" || state.zoneBatSide === "R") {
        const op = state.zoneBatSide === "R" ? 0.45 : 0.16;
        svg += `<g opacity="${op}"><circle cx="34" cy="72" r="10" fill="#334155"/><path d="M22,86 Q34,82 46,86 L50,152 L40,210 L26,210 L20,152 Z" fill="#1E293B"/><text x="34" y="224" text-anchor="middle" font-size="6.8" font-weight="800" fill="#94A3B8">RHB</text></g>`;
      }
      if (state.zoneBatSide === "all" || state.zoneBatSide === "L") {
        const op = state.zoneBatSide === "L" ? 0.45 : 0.16;
        svg += `<g opacity="${op}"><circle cx="186" cy="72" r="10" fill="#334155"/><path d="M174,86 Q186,82 198,86 L200,152 L194,210 L180,210 L170,152 Z" fill="#1E293B"/><text x="186" y="224" text-anchor="middle" font-size="6.8" font-weight="800" fill="#94A3B8">LHB</text></g>`;
      }
      if (state.zoneBatSide === "R") {
        svg += `<text x="64" y="${(z.y_hi + 22).toFixed(1)}" text-anchor="end" font-size="6.3" font-weight="800" fill="#7DD3FC">INTERIOR</text>`;
        svg += `<text x="156" y="${(z.y_hi + 22).toFixed(1)}" text-anchor="start" font-size="6.3" font-weight="800" fill="#94A3B8">EXTERIOR</text>`;
      } else if (state.zoneBatSide === "L") {
        svg += `<text x="64" y="${(z.y_hi + 22).toFixed(1)}" text-anchor="end" font-size="6.3" font-weight="800" fill="#94A3B8">EXTERIOR</text>`;
        svg += `<text x="156" y="${(z.y_hi + 22).toFixed(1)}" text-anchor="start" font-size="6.3" font-weight="800" fill="#7DD3FC">INTERIOR</text>`;
      }

      svg += `
        <line x1="${z.cx}" y1="20" x2="${z.cx}" y2="230" stroke="#1E3A5F" stroke-dasharray="3 3"/>
        <line x1="15" y1="${z.cy}" x2="205" y2="${z.cy}" stroke="#1E3A5F" stroke-dasharray="3 3"/>
        <rect x="${z.x_lo}" y="${z.y_lo}" width="${zw.toFixed(1)}" height="${zh.toFixed(1)}" fill="#003B73" fill-opacity="0.16"/>
        <!-- Catcher Perspective Home Plate -->
        <polygon points="${z.x_lo+4},232 ${z.x_hi-4},232 ${z.x_hi-4},238 ${z.cx},244 ${z.x_lo+4},238" fill="#1E293B" stroke="#94A3B8" stroke-width="1.2"/>
      `;

      const callColor = (cc) => {
        if (cc === "C") return "#0095DA";
        if (cc === "S" || cc === "M" || cc === "W") return "#E6392F";
        if (["F", "T", "L"].includes(cc)) return "#F59E0B";
        if (["X", "D", "E"].includes(cc)) return "#16A34A";
        return "#64748B";
      };

      const isHeat = state.zoneMode === "heat_usage" || state.zoneMode === "heat_whiff";
      if (isHeat && pts.length) {
        const rowNames = ["Alta", "Media", "Baja"];
        const colNames = state.zoneBatSide === "L" ? ["Exterior", "Centro", "Interior"] : (state.zoneBatSide === "R" ? ["Interior", "Centro", "Exterior"] : ["Izq.", "Centro", "Der."]);
        const heatFill = (ratio) => {
          if (ratio >= 0.72) return "#E6392F";
          if (ratio >= 0.48) return "#F97316";
          if (ratio >= 0.25) return "#0072B2";
          return "#0F2942";
        };
        for (let rIdx = 0; rIdx < 3; rIdx++) {
          for (let cIdx = 0; cIdx < 3; cIdx++) {
            const x0 = z.x_lo + cIdx * zThirdW, x1 = x0 + zThirdW;
            const y0 = z.y_lo + rIdx * zThirdH, y1 = y0 + zThirdH;
            const cellPts = pts.filter((p) => p[3] >= x0 && p[3] <= x1 && p[4] >= y0 && p[4] <= y1);
            const cN = cellPts.length;
            const cSw = cellPts.filter((p) => ["S", "M", "W", "F", "T", "L", "O", "X", "D", "E"].includes(p[5])).length;
            const cWh = cellPts.filter((p) => p[5] === "S" || p[5] === "M" || p[5] === "W").length;
            const usagePct = pts.length ? (cN / pts.length) * 100 : 0;
            const whiffPct = cSw >= 3 ? (cWh / cSw) * 100 : null;
            const ratio = state.zoneMode === "heat_usage" ? Math.min(1, usagePct / 11.5) : (whiffPct !== null ? Math.min(1, whiffPct / 38.0) : 0);
            const fill = (state.zoneMode === "heat_whiff" && whiffPct === null) ? "#0F1E33" : heatFill(ratio);
            const mainTxt = state.zoneMode === "heat_usage" ? `${usagePct.toFixed(1)}%` : (whiffPct !== null ? `${Math.round(whiffPct)}%` : "—");
            const subTxt = state.zoneMode === "heat_usage" ? `(${cN}p)` : `(${cSw} sw)`;
            const tip = `<strong>Cuadrante ${rowNames[rIdx]} ${colNames[cIdx]}</strong><br>Pitcheos: <b>${cN}</b> (${usagePct.toFixed(1)}% uso)<br>Swings: <b>${cSw}</b> · Whiff%: <b>${whiffPct !== null ? `${whiffPct.toFixed(1)}%` : "—"}</b>`;
            svg += `<rect class="pz-pt cursor-pointer" x="${x0.toFixed(1)}" y="${y0.toFixed(1)}" width="${zThirdW.toFixed(1)}" height="${zThirdH.toFixed(1)}" fill="${fill}" fill-opacity="0.82" data-tip="${esc(tip)}"/>`;
            svg += `<text x="${(x0 + zThirdW / 2).toFixed(1)}" y="${(y0 + zThirdH / 2 - 1).toFixed(1)}" text-anchor="middle" font-size="7.8" font-weight="900" fill="#FFFFFF" pointer-events="none">${mainTxt}</text>`;
            svg += `<text x="${(x0 + zThirdW / 2).toFixed(1)}" y="${(y0 + zThirdH / 2 + 8).toFixed(1)}" text-anchor="middle" font-size="5.6" font-weight="700" fill="#E2E8F0" pointer-events="none">${subTxt}</text>`;
          }
        }
      } else {
        // Scatter dots
        const drawPts = pts.length > 1600 ? pts.filter((_, idx) => idx % Math.ceil(pts.length / 1600) === 0) : pts;
        const densePts = pts.length > 500;
        drawPts.forEach((p) => {
          const px = Math.max(6, Math.min(214, p[3]));
          const py = Math.max(18, Math.min(228, p[4]));
          const col = callColor(p[5]);
          const r = densePts ? (p[5] === "S" ? 2.1 : 1.55) : (p[5] === "S" ? 2.9 : 2.2);
          const op = densePts ? (p[5] === "S" ? 0.72 : 0.45) : 0.80;
          const pName = getProfile(sk, p[1]).full_name;
          const callEs = CALL_ES[p[5]] || p[5];
          const tip = `<strong>${esc(pName)}</strong><br>${esc(callEs)} · <b>${p[7] === 1 ? "En Zona" : "Fuera de Zona"}</b><br>vs ${esc(p[9] || "?")}HB${p[12] === "0-0" ? " · Primer Pitcheo 0-0" : (p[12] === "2K" ? " · 2 Strikes" : "")}${p[11] === 1 ? " · Con RISP" : ""}`;
          svg += `<circle class="pz-pt cursor-pointer" cx="${px}" cy="${py}" r="${r}" fill="${col}" fill-opacity="${op}" stroke="#08101C" stroke-width="0.3" data-tip="${esc(tip)}"/>`;
        });
      }

      // Top overlay: 9-zone strike grid + 1-SD Command Dispersion Ellipse ALWAYS visible above dots
      svg += `
        <g pointer-events="none">
          <rect x="${z.x_lo}" y="${z.y_lo}" width="${zw.toFixed(1)}" height="${zh.toFixed(1)}" fill="none" stroke="#7DD3FC" stroke-width="1.9"/>
          <line x1="${(z.x_lo + zThirdW).toFixed(1)}" y1="${z.y_lo}" x2="${(z.x_lo + zThirdW).toFixed(1)}" y2="${z.y_hi}" stroke="#7DD3FC" stroke-opacity="0.55" stroke-width="0.95"/>
          <line x1="${(z.x_lo + 2*zThirdW).toFixed(1)}" y1="${z.y_lo}" x2="${(z.x_lo + 2*zThirdW).toFixed(1)}" y2="${z.y_hi}" stroke="#7DD3FC" stroke-opacity="0.55" stroke-width="0.95"/>
          <line x1="${z.x_lo}" y1="${(z.y_lo + zThirdH).toFixed(1)}" x2="${z.x_hi}" y2="${(z.y_lo + zThirdH).toFixed(1)}" stroke="#7DD3FC" stroke-opacity="0.55" stroke-width="0.95"/>
          <line x1="${z.x_lo}" y1="${(z.y_lo + 2*zThirdH).toFixed(1)}" x2="${z.x_hi}" y2="${(z.y_lo + 2*zThirdH).toFixed(1)}" stroke="#7DD3FC" stroke-opacity="0.55" stroke-width="0.95"/>
      `;

      let mx = 0, my = 0, sdx = 0, sdy = 0;
      if (pts.length >= 5) {
        mx = pts.reduce((a, p) => a + p[3], 0) / pts.length;
        my = pts.reduce((a, p) => a + p[4], 0) / pts.length;
        sdx = Math.sqrt(pts.reduce((a, p) => a + (p[3] - mx) ** 2, 0) / pts.length);
        sdy = Math.sqrt(pts.reduce((a, p) => a + (p[4] - my) ** 2, 0) / pts.length);
        if (!isHeat) {
          svg += `<ellipse cx="${mx.toFixed(1)}" cy="${my.toFixed(1)}" rx="${sdx.toFixed(1)}" ry="${sdy.toFixed(1)}" fill="none" stroke="#08101C" stroke-width="3.4" stroke-opacity="0.7"/>`;
          svg += `<ellipse cx="${mx.toFixed(1)}" cy="${my.toFixed(1)}" rx="${sdx.toFixed(1)}" ry="${sdy.toFixed(1)}" fill="none" stroke="#FACC15" stroke-width="1.8" stroke-dasharray="4 3"/>`;
          svg += `<circle cx="${mx.toFixed(1)}" cy="${my.toFixed(1)}" r="4.2" fill="#FACC15" stroke="#08101C" stroke-width="1.5"/>`;
        }
      } else if (!pts.length) {
        svg += `<text x="110" y="135" text-anchor="middle" font-size="8.5" font-weight="700" fill="#94A3B8">Sin pitcheos en la muestra filtrada</text>`;
      }
      svg += `</g>`;
      svgEl.innerHTML = svg;

      svgEl.querySelectorAll(".pz-pt").forEach((el) => {
        el.addEventListener("mousemove", (e) => {
          showTooltip(e, el.dataset.tip || "");
        });
        el.addEventListener("mouseleave", hideTooltip);
      });

      // Dynamic Strike Zone Legend
      const zLeg = document.getElementById("strike-zone-legend");
      if (zLeg) {
        if (isHeat) {
          const unitTxt = state.zoneMode === "heat_usage" ? "Frecuencia de uso (%)" : "Tasa de swing fallido (Whiff%)";
          zLeg.innerHTML = `
            <span class="text-slate-400 font-bold">${esc(unitTxt)}:</span>
            <span class="flex items-center gap-1"><i class="w-3 h-2.5 rounded-sm bg-[#0F2942] border border-slate-500 inline-block"></i> Bajo</span>
            <span class="flex items-center gap-1"><i class="w-3 h-2.5 rounded-sm bg-[#0072B2] inline-block"></i> Medio</span>
            <span class="flex items-center gap-1"><i class="w-3 h-2.5 rounded-sm bg-[#F97316] inline-block"></i> Alto</span>
            <span class="flex items-center gap-1"><i class="w-3 h-2.5 rounded-sm bg-[#E6392F] inline-block"></i> Caliente</span>`;
        } else {
          zLeg.innerHTML = `
            <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#0095DA] inline-block"></i> Strike Cantado (C)</span>
            <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#E6392F] inline-block"></i> Whiff (S)</span>
            <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#F59E0B] inline-block"></i> Foul</span>
            <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#16A34A] inline-block"></i> En Juego</span>
            <span class="flex items-center gap-1"><i class="w-2.5 h-2.5 rounded-full bg-[#64748B] inline-block"></i> Bola</span>
            <span class="flex items-center gap-1"><i class="w-3 h-2 rounded-full border-2 border-dashed border-[#FACC15] inline-block"></i> Elipse 1-SD</span>`;
        }
      }

      // Live Telemetry KPIs
      const n = pts.length;
      const strikes = pts.filter((p) => p[6] === 1).length;
      const inZone = pts.filter((p) => p[7] === 1).length;
      const swings = pts.filter((p) => ["S", "M", "W", "F", "T", "L", "O", "X", "D", "E"].includes(p[5])).length;
      const whiffs = pts.filter((p) => ["S", "M", "W"].includes(p[5])).length;
      const outZone = pts.filter((p) => p[7] === 0);
      const outSwings = outZone.filter((p) => ["S", "M", "W", "F", "T", "L", "O", "X", "D", "E"].includes(p[5])).length;
      const fpsAll = pts.filter((p) => p[8] === 1);
      const fpsK = fpsAll.filter((p) => p[6] === 1).length;

      document.getElementById("zone-telemetry-readout").innerHTML = `
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">PITCHEOS</div><div class="text-xs font-black text-white tabular-nums">${n}</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">STRIKE%</div><div class="text-xs font-black text-[#7DD3FC] tabular-nums">${n ? (strikes/n*100).toFixed(1) : "—"}%</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">INZONE%</div><div class="text-xs font-black text-emerald-400 tabular-nums">${n ? (inZone/n*100).toFixed(1) : "—"}%</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">CHASE%</div><div class="text-xs font-black text-amber-400 tabular-nums">${outZone.length ? (outSwings/outZone.length*100).toFixed(1) : "—"}%</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">WHIFF%</div><div class="text-xs font-black text-red-400 tabular-nums">${swings ? (whiffs/swings*100).toFixed(1) : "—"}%</div></div>
        <div class="bg-[#0F1E33] border border-[#1E3A5F] rounded p-1.5"><div class="text-[9.5px] text-slate-400 font-bold">FPS%</div><div class="text-xs font-black text-white tabular-nums">${fpsAll.length ? (fpsK/fpsAll.length*100).toFixed(1) : "—"}%</div></div>
      `;
      const zStory = document.getElementById("zone-story-box");
      if (zStory) {
        const vertLoc = my < z.cy - zh / 6 ? "Zona Alta" : (my > z.cy + zh / 6 ? "Zona Baja" : "Altura Media");
        let horizLoc = mx < z.cx - zw / 6 ? "Lado Izq. (RHB)" : (mx > z.cx + zw / 6 ? "Lado Der. (LHB)" : "Sobre el Centro");
        if (state.zoneBatSide === "R") {
          horizLoc = mx < z.cx - zw / 6 ? "Zona Interior (vs RHB)" : (mx > z.cx + zw / 6 ? "Zona Exterior (vs RHB)" : "Sobre el Centro");
        } else if (state.zoneBatSide === "L") {
          horizLoc = mx < z.cx - zw / 6 ? "Zona Exterior (vs LHB)" : (mx > z.cx + zw / 6 ? "Zona Interior (vs LHB)" : "Sobre el Centro");
        }
        const cmdTight = (sdx + sdy) / 2 < 24 ? "Comando compacto (baja dispersión)" : "Dispersión amplia en la zona";
        zStory.innerHTML = n >= 5
          ? `<div class="bg-[#0F1E33] border-l-4 border-[#FACC15] rounded-r px-3 py-2 text-[11px] text-slate-200 leading-relaxed"><strong class="text-amber-300">Lectura de Comando (n=${n}):</strong> Tendencia hacia <strong>${vertLoc} · ${horizLoc}</strong> · ${cmdTight} · Primer Strike (FPS%) <strong>${fpsAll.length ? (fpsK/fpsAll.length*100).toFixed(1) : "—"}%</strong> · Whiff% <strong>${swings ? (whiffs/swings*100).toFixed(1) : "—"}%</strong>.</div>`
          : "";
      }
    }

    function renderFatigueMonitor(pitchers) {
      const cutEl = document.getElementById("fatigue-cutoff-note");
      if (cutEl) {
        const { key: sk } = activeSeasonData();
        cutEl.textContent = sk === "2026"
          ? "· Corte YTD: 15 nov 2026"
          : `· Corte: cierre ${STAGE_LABELS[state.stage]} 2025–26`;
      }
      const wrap = document.getElementById("fatigue-cards-grid");
      if (!pitchers.length) {
        wrap.innerHTML = `<div class="col-span-full text-xs text-slate-400 py-4 text-center">Sin datos de carga de trabajo para mostrar.</div>`;
        return;
      }
      const orderRank = { "CRÍTICO": 0, "PRECAUCIÓN": 1, "ÓPTIMO": 2 };
      const sorted = [...pitchers].sort((a, b) => (orderRank[a.fatigue_status] ?? 9) - (orderRank[b.fatigue_status] ?? 9) || (b.pitches_14d || 0) - (a.pitches_14d || 0));

      wrap.innerHTML = sorted.map((p) => {
        const st = p.fatigue_status || "ÓPTIMO";
        const badge = st === "CRÍTICO"
          ? "bg-red-100 text-red-800 border border-red-300"
          : (st === "PRECAUCIÓN" ? "bg-amber-100 text-amber-800 border border-amber-300" : "bg-emerald-100 text-emerald-800 border border-emerald-300");
        const barCol = st === "CRÍTICO" ? "#E6392F" : (st === "PRECAUCIÓN" ? "#D97706" : "#16A34A");
        const max14 = p.rol === "Abridor" ? 210 : 95;
        const pct14 = Math.min(100, Math.round(((p.pitches_14d || 0) / max14) * 100));
        const b2bBadge = p.is_b2b
          ? `<span class="text-[9.5px] font-black px-1.5 py-0.5 rounded bg-red-600 text-white shrink-0" title="Lanzó en días consecutivos (Back-to-Back)">B2B</span>`
          : "";
        const outings = (p.last_outings || []).slice(-3);
        const outingsHtml = outings.length ? `
          <div class="flex flex-wrap gap-1 mt-2 pt-1.5 border-t border-slate-200/80">
            <span class="text-[9.5px] font-bold text-slate-400 uppercase mr-0.5">Últ. ${outings.length}:</span>
            ${outings.map((o) => `<span class="text-[9.5px] font-code bg-white border border-slate-200 rounded px-1.5 py-0.5 text-slate-700" title="${esc(o.date)}: ${esc(o.ip)} IP, ${o.pitches} pitcheos, ${o.er} CL">${esc(o.date.slice(5))} · <b>${esc(o.ip)}</b>IP/${o.pitches}p${o.er > 0 ? `/<span class="text-red-600 font-bold">${o.er}CL</span>` : ""}</span>`).join("")}
          </div>` : "";
        return `
          <div class="border border-slate-200 rounded-lg p-3 bg-slate-50/70 hover:bg-white transition flex items-start gap-3">
            ${renderPlayerAvatar(p.prof, "w-10 h-[50px]", "rounded-lg")}
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-1.5">
                <button onclick="window.__jumpToPlayer(${p.player_id}, 'scouting')" class="text-xs font-extrabold text-[#003B73] hover:text-[#0072B2] hover:underline truncate">${esc(p.name)}</button>
                <div class="flex items-center gap-1 shrink-0">
                  ${b2bBadge}
                  <span class="text-[10px] font-extrabold px-2 py-0.5 rounded ${badge}">${esc(st)}</span>
                </div>
              </div>
              <div class="flex items-center justify-between text-[11px] text-slate-600 mt-0.5 tabular-nums">
                <span>${esc(p.rol)} · Última: <strong>${esc(p.last_date || "—")}</strong></span>
                <span>Descanso: <strong>${p.rest_days ?? "—"}d</strong></span>
              </div>
              <div class="w-full h-2.5 bg-slate-200 rounded-full overflow-hidden mt-2">
                <div class="h-full rounded-full" style="width:${pct14}%;background:${barCol}"></div>
              </div>
              <div class="flex items-center justify-between text-[10.5px] font-code text-slate-600 mt-1.5">
                <span>7d: <strong>${p.pitches_7d ?? 0}</strong>p (${p.apps_7d ?? 0}G)</span>
                <span>14d: <strong>${p.pitches_14d ?? 0}/${max14}</strong>p</span>
                <span>30d: <strong>${p.pitches_30d ?? 0}</strong>p</span>
              </div>
              ${outingsHtml}
            </div>
          </div>`;
      }).join("");
    }

    // =========================================================================
    // 7. MÓDULO 4: SCOUTING 360°, BIOMETRÍA, RADAR 20–80 & SAVANT PERCENTILES
    // =========================================================================
    function renderScoutingModule() {
      const { key: sk, data: sdata } = activeSeasonData();
      const allProfiles = sdata.scouting_profiles || [];
      const filtered = allProfiles.filter((p) => {
        if (state.scoutRole !== "all" && p.role_group !== state.scoutRole) return false;
        if (state.scoutStatus !== "all" && p.roster_status !== state.scoutStatus) return false;
        if (state.scoutSearch) {
          const q = state.scoutSearch.toLowerCase();
          const match = (p.full_name || "").toLowerCase().includes(q)
            || (p.primary_position || "").toLowerCase().includes(q)
            || (p.birth_country || "").toLowerCase().includes(q);
          if (!match) return false;
        }
        return true;
      });

      document.getElementById("roster-count-label").textContent = String(filtered.length);
      const listWrap = document.getElementById("scout-roster-list");

      if (state.selectedPlayerId !== null && !allProfiles.some((p) => p.player_id === state.selectedPlayerId)) {
        state.selectedPlayerId = null;
      }

      if (!filtered.length) {
        listWrap.innerHTML = `<div class="p-4 text-center text-xs text-slate-500">Sin jugadores bajo estos filtros.</div>`;
      } else {
        listWrap.innerHTML = filtered.map((p) => {
          const active = p.player_id === state.selectedPlayerId;
          const stCls = p.roster_status === "Extranjero"
            ? "bg-amber-100 text-amber-800"
            : (p.roster_status === "Novato" ? "bg-emerald-100 text-emerald-800" : "bg-sky-100 text-sky-900");
          const vol = p.is_pitcher ? `${fmtNum(p.reg_ip, 1)} IP` : `${p.reg_pa} PA`;
          return `
            <button data-pick-player="${p.player_id}" class="w-full text-left p-2 rounded-lg border transition flex items-center justify-between gap-2.5 ${active ? "bg-[#003B73] text-white border-[#0095DA] shadow-md" : "bg-slate-50 hover:bg-slate-100 text-slate-800 border-slate-200"}">
              <div class="flex items-center gap-2.5 min-w-0">
                ${renderPlayerAvatar(p, "w-10 h-[50px]", "rounded-lg")}
                <div class="min-w-0">
                  <div class="text-xs font-extrabold truncate">${esc(p.full_name)}</div>
                  <div class="text-[11px] ${active ? "text-sky-200" : "text-slate-500"} flex items-center gap-1.5">
                    <span class="font-code font-bold">${esc(p.primary_position)}</span> · <span>${esc(vol)}</span>
                  </div>
                </div>
              </div>
              <div class="flex flex-col items-end gap-1 shrink-0">
                ${renderFlagSVG(p.flag_code)}
                <span class="text-[9px] font-bold px-1.5 rounded ${stCls}">${esc(p.roster_status.slice(0, 3).toUpperCase())}</span>
              </div>
            </button>`;
        }).join("");

        listWrap.querySelectorAll("button[data-pick-player]").forEach((btn) => {
          btn.addEventListener("click", () => {
            const clickedId = Number(btn.dataset.pickPlayer);
            state.selectedPlayerId = (state.selectedPlayerId === clickedId) ? null : clickedId;
            renderScoutingModule();
            if (state.selectedPlayerId !== null && window.innerWidth < 1024) {
              document.getElementById("scout-detail-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
            }
          });
        });
      }

      const prof = state.selectedPlayerId !== null
        ? allProfiles.find((p) => p.player_id === state.selectedPlayerId) || null
        : null;
      if (prof) {
        renderScoutDetail(prof, sdata);
      } else {
        renderScoutEmptyState(allProfiles, filtered, sdata);
      }
    }

    function renderScoutEmptyState(allProfiles, filtered, sdata) {
      const panel = document.getElementById("scout-detail-panel");
      const nBat = allProfiles.filter((p) => !p.is_pitcher).length;
      const nAbr = allProfiles.filter((p) => p.role_group === "Abridor").length;
      const nRel = allProfiles.filter((p) => p.role_group === "Bullpen").length;
      const nNac = allProfiles.filter((p) => p.roster_status === "Nacional").length;
      const nExt = allProfiles.filter((p) => p.roster_status === "Extranjero").length;
      const nNov = allProfiles.filter((p) => p.roster_status === "Novato").length;

      panel.innerHTML = `
        <div class="card-surface p-5 border-t-4 border-t-[#003B73] space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>EVALUADOR SCOUTING 360°</span></span>
              <h2 class="text-lg font-extrabold text-[#002850] mt-1">Ningún jugador seleccionado por defecto</h2>
              <p class="text-xs text-slate-600">Elige un jugador en la lista lateral izquierda para abrir su ficha biométrica, radar 20–80, percentiles y splits, o utiliza directamente el comparador inferior.</p>
            </div>
            <div class="flex flex-wrap gap-2 text-xs font-code">
              <span class="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 font-bold text-[#002850]">${nBat} Bateadores</span>
              <span class="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 font-bold text-[#003B73]">${nAbr} Abridores</span>
              <span class="px-2.5 py-1 rounded bg-slate-100 border border-slate-200 font-bold text-[#0072B2]">${nRel} Bullpen</span>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-[11px] font-bold">
            <span class="px-2 py-0.5 rounded bg-sky-100 text-sky-900">Nacionales: ${nNac}</span>
            <span class="px-2 py-0.5 rounded bg-amber-100 text-amber-800">Extranjeros: ${nExt}</span>
            <span class="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">Novatos: ${nNov}</span>
            <span class="text-slate-500 font-normal ml-auto">Listado filtrado visible: ${filtered.length} jugadores</span>
          </div>
        </div>
        ${buildScoutCompareHTML(null, sdata)}
      `;
      bindScoutCompareEvents(sdata);
    }

    function scoutingGradeText(g) {
      const n = Number(g || 50);
      if (n >= 70) return "Plus-Plus (Élite)";
      if (n >= 60) return "Plus (Impacto)";
      if (n >= 55) return "Sobre Promedio";
      if (n >= 45) return "Promedio LMP";
      return "Reserva / Ajuste";
    }

    function getStageAwareMetricValue(prof, sdata, metric) {
      const stg = state.stage;
      if (!prof.is_pitcher) {
        const bRow = (sdata.yaquis_batters || []).find((b) => b.player_id === prof.player_id && b.etapa === stg);
        if (!bRow) return { val: "—", nStr: "0 PA", usedStage: stg, hasData: false };
        const sp = state.cond === "all" ? (bRow.splits?.all || {}) : (bRow.splits?.[state.cond] || {});
        if (!(sp.PA > 0)) return { val: "—", nStr: "0 PA", usedStage: stg, hasData: false };
        const map = {
          AVG: fmtRate(sp.AVG),
          OBP: fmtRate(sp.OBP),
          SLG: fmtRate(sp.SLG),
          OPS: fmtRate(sp.OPS),
          ISO: fmtRate(sp.ISO),
          "BB%": fmtNum(sp.BB_pct, 1, "%"),
          "K%": fmtNum(sp.K_pct, 1, "%"),
          BABIP: fmtRate(sp.BABIP),
          "Velocidad (SB)": state.cond === "all" ? `${bRow.SB ?? sp.SB ?? 0} BR` : "—",
        };
        return { val: map[metric] ?? "—", nStr: `${sp.PA} PA`, usedStage: stg, hasData: true };
      } else {
        const pRow = (sdata.yaquis_pitchers || []).find((p) => p.player_id === prof.player_id && p.etapa === stg);
        if (!pRow) return { val: "—", nStr: "0 IP", usedStage: stg, hasData: false };
        const isCondSplit = ["home", "away", "risp"].includes(state.cond);
        if (isCondSplit) {
          const sp = pRow.splits?.[state.cond] || {};
          if (!(sp.PA > 0)) return { val: "—", nStr: "0 BF", usedStage: stg, hasData: false };
          const mapSplit = {
            ERA: sp.ERA !== null && sp.ERA !== undefined ? fmtNum(sp.ERA, 2) : "—",
            FIP: fmtNum(sp.FIP, 2),
            WHIP: fmtNum(sp.WHIP, 2),
            K9: fmtNum(sp.K9, 2),
            BB9: fmtNum(sp.BB9, 2),
            HR9: "—",
            "InZone%": fmtNum(sp.InZone_pct, 1, "%"),
            "Whiff%": fmtNum(sp.Whiff_pct, 1, "%"),
            "Chase%": fmtNum(sp.Chase_pct, 1, "%"),
          };
          return { val: mapSplit[metric] ?? "—", nStr: `${fmtNum(sp.IP, 1)} IP (${sp.PA} BF)`, usedStage: stg, hasData: true };
        }
        const map = {
          ERA: fmtNum(pRow.ERA, 2),
          FIP: fmtNum(pRow.FIP, 2),
          WHIP: fmtNum(pRow.WHIP, 2),
          K9: fmtNum(pRow.K9, 2),
          BB9: fmtNum(pRow.BB9, 2),
          HR9: fmtNum(pRow.HR9, 2),
          "InZone%": fmtNum(pRow.InZone_pct, 1, "%"),
          "Whiff%": fmtNum(pRow.Whiff_pct, 1, "%"),
          "Chase%": fmtNum(pRow.Chase_pct, 1, "%"),
        };
        return { val: map[metric] ?? "—", nStr: `${fmtNum(pRow.IP, 1)} IP`, usedStage: stg, hasData: (pRow.IP || 0) > 0 || (pRow.Pitches || 0) > 0 };
      }
    }

    function renderScoutDetail(prof, sdata) {
      const panel = document.getElementById("scout-detail-panel");
      const cleanBio = (v) => (v === null || v === undefined || v === "" || v === "SIN_DATO") ? "—" : v;
      const secPos = (prof.secondary_positions || []).length ? ` / ${prof.secondary_positions.join(", ")}` : "";
      const statusBadge = prof.roster_status === "Extranjero"
        ? "bg-amber-400 text-[#0B1320]"
        : (prof.roster_status === "Novato" ? "bg-emerald-400 text-[#0B1320]" : "bg-[#0072B2] text-white");

      // Tool 20-80 SVG Radar
      const toolsEntries = Object.entries(prof.tools_20_80 || {});
      const radarHtml = buildScoutingRadarSVG(toolsEntries);

      // Savant Diverging Percentile Bars (synced real values with active stage/cond; suppress synthetic 50s if 0 reg PA/IP)
      const hasRegSample = prof.is_pitcher ? ((prof.reg_ip || 0) > 0) : ((prof.reg_pa || 0) > 0);
      const pctEntries = Object.entries(prof.percentiles || {});
      const invMetrics = new Set(["K%", "ERA", "FIP", "WHIP", "BB9", "HR9"]);
      const tierBadge = (v) => {
        if (v >= 85) return { lbl: "ÉLITE", cls: "bg-red-100 text-red-800 border border-red-200" };
        if (v >= 65) return { lbl: "ALTO", cls: "bg-orange-100 text-orange-800 border border-orange-200" };
        if (v >= 40) return { lbl: "MEDIO", cls: "bg-slate-100 text-slate-700 border border-slate-200" };
        return { lbl: "BAJO", cls: "bg-blue-100 text-blue-800 border border-blue-200" };
      };
      const firstInfo = pctEntries.length ? getStageAwareMetricValue(prof, sdata, pctEntries[0][0]) : { nStr: "—", usedStage: state.stage };
      const condNotePct = (prof.is_pitcher && (state.cond === "vs_lhp" || state.cond === "vs_rhp"))
        ? `${COND_LABELS[state.cond]} (splits LHB/RHB abajo)`
        : COND_LABELS[state.cond];
      const pctHtml = !hasRegSample
        ? `<div class="bg-amber-50 border border-amber-200 rounded-lg p-4 text-xs text-amber-900"><strong>Sin muestra reglamentaria en Rol Regular:</strong> este jugador no registró ${prof.is_pitcher ? "innings lanzados" : "apariciones al bat"} en Rol Regular (refuerzo exclusivo de Playoffs o 0 ${prof.is_pitcher ? "IP" : "PA"}); los percentiles LMP de rol regular no aplican. Revisa su desempeño específico en la tabla inferior de <strong>Splits Dinámicos</strong>.</div>`
        : (pctEntries.length ? `
        <div class="flex flex-wrap items-center justify-between gap-2 text-[10.5px] text-slate-600 bg-slate-50 border border-slate-200 rounded px-2.5 py-1.5 mb-2">
          <span>Barras: <strong>Percentil LMP (Rol Reg.)</strong> · Valor numérico real: <strong>${esc(STAGE_LABELS[state.stage])} · ${esc(condNotePct)}</strong> (muestra <strong class="font-code">${esc(firstInfo.nStr)}</strong>)</span>
          <span class="text-[10px] font-semibold text-slate-500">↓ = Menor número es mejor percentil</span>
        </div>
        <div class="grid grid-cols-[120px_1fr] sm:grid-cols-[158px_1fr_82px] gap-2 sm:gap-3 items-center text-[10px] font-bold text-slate-500 uppercase tracking-wider pb-1 border-b border-slate-100">
          <span>Métrica · Real</span>
          <div class="mx-3.5 flex justify-between"><span>1 · Bajo</span><span class="hidden sm:inline">25</span><span class="text-[#003B73]">50 · LMP</span><span class="hidden sm:inline">75</span><span>100 · Élite</span></div>
          <span class="hidden sm:block text-right">Nivel</span>
        </div>
        ${pctEntries.map(([metric, val]) => {
          const v = Math.max(1, Math.min(100, Number(val ?? 50)));
          const col = pctBadgeColor(v);
          const { val: realVal } = getStageAwareMetricValue(prof, sdata, metric);
          const tb = tierBadge(v);
          const isInv = invMetrics.has(metric);
          return `
            <div class="grid grid-cols-1 sm:grid-cols-[158px_1fr_82px] gap-1.5 sm:gap-3 items-center py-0.5">
              <div class="flex items-center justify-between sm:justify-between gap-2 min-w-0">
                <span class="text-xs sm:text-[13px] font-bold text-slate-800 truncate" title="${esc(metric)}${isInv ? " (menor es mejor)" : ""}">${esc(metric)}${isInv ? ` <span class="text-[10px] text-[#0072B2]" title="Menor valor = mayor percentil">↓</span>` : ""}</span>
                <span class="text-[11px] font-code font-bold text-[#003B73] bg-sky-50 border border-sky-200 px-1.5 py-0.5 rounded shrink-0">${esc(realVal)}</span>
              </div>
              <div class="relative h-7 flex items-center mx-3.5">
                <div class="absolute inset-x-0 h-2.5 bg-slate-200 rounded-full"></div>
                <div class="absolute inset-y-1.5 w-px bg-slate-300" style="left:25%"></div>
                <div class="absolute inset-y-1 w-0.5 bg-slate-500/80" style="left:50%"></div>
                <div class="absolute inset-y-1.5 w-px bg-slate-300" style="left:75%"></div>
                <div class="absolute left-0 h-2.5 rounded-full" style="width:${v}%;background:${col};opacity:0.88"></div>
                <div class="pct-node absolute top-1/2 -translate-x-1/2 -translate-y-1/2 w-[26px] h-[26px] rounded-full border-2 border-white shadow-md flex items-center justify-center text-[11px] font-black text-white tabular-nums" style="left:${v}%;background:${col}">${v}</div>
              </div>
              <div class="hidden sm:flex justify-end">
                <span class="text-[10px] font-extrabold px-2 py-0.5 rounded ${tb.cls}">${tb.lbl}</span>
              </div>
            </div>`;
        }).join("")}
      ` : `<div class="text-xs text-slate-500">Percentiles disponibles al superar muestra mínima reglamentaria en la LMP.</div>`);

      // Player Splits Matrix across stages & conditions
      const splitsMatrixHtml = buildPlayerSplitsHTML(prof, sdata);
      const compareHtml = buildScoutCompareHTML(prof, sdata);
      const cleanCity = cleanBio(prof.birth_city);
      const cleanCountry = cleanBio(prof.birth_country);
      const quickJumpBtn = !prof.is_pitcher
        ? `<button onclick="window.__jumpToPlayer(${prof.player_id}, 'batting')" class="text-[11px] font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-2.5 py-1 rounded transition">Ver Spray Chart →</button>`
        : `<button onclick="window.__jumpToPlayer(${prof.player_id}, 'pitching')" class="text-[11px] font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-2.5 py-1 rounded transition">Ver Zona 2D →</button>`;

      panel.innerHTML = `
        <!-- BIOMETRIC HERO CARD -->
        <div class="rounded-xl p-5 sm:p-6 text-white shadow-lg border border-[#0095DA]/50" style="background: linear-gradient(125deg, #002850 0%, #003B73 65%, #004E98 100%);">
          <div class="flex flex-col sm:flex-row sm:items-center gap-5 sm:gap-6">
            ${renderPlayerAvatar(prof, "w-28 h-[140px] sm:w-32 sm:h-40", "rounded-2xl")}
            <div class="flex-1 space-y-2">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="jersey-ribbon text-[10px] font-black px-2.5 py-0.5 uppercase ${statusBadge}"><span>${esc(prof.roster_status)} · ${esc(prof.role_group)}</span></span>
                  <span class="bg-[#0B1320]/70 border border-[#0095DA]/40 text-[#7DD3FC] text-[11px] font-bold px-2 py-0.5 rounded font-code">Pos: ${esc(prof.primary_position + secPos)}</span>
                  <span class="bg-[#0B1320]/70 text-slate-200 text-[11px] font-bold px-2 py-0.5 rounded font-code">B/T: ${esc(cleanBio(prof.bat_side))}/${esc(cleanBio(prof.pitch_hand))}</span>
                </div>
                <div class="flex items-center gap-1.5">
                  ${quickJumpBtn}
                  <button id="btn-scout-clear-player" class="text-[11px] font-bold bg-[#0B1320]/75 hover:bg-[#0B1320] text-slate-200 border border-white/25 px-2.5 py-1 rounded transition">× Limpiar ficha</button>
                </div>
              </div>
              <h2 class="text-2xl sm:text-3xl font-black tracking-tight">${esc(prof.full_name)}</h2>
              <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-xs text-slate-200">
                <span class="flex items-center gap-1.5">${renderFlagSVG(prof.flag_code)} <strong>${esc(cleanCity !== "—" ? `${cleanCity}, ` : "")}${esc(cleanCountry)}</strong></span>
                <span>Edad: <strong class="tabular-nums">${prof.age ?? "—"}</strong> años (${esc(prof.birth_date || "—")})</span>
                <span>Est/Peso: <strong class="tabular-nums">${esc(cleanBio(prof.height))} / ${prof.weight ? `${Math.round(prof.weight)} lb` : "—"}</strong></span>
              </div>
              <div class="bg-[#0B1320]/65 border-l-4 border-[#0095DA] rounded-r px-3.5 py-2 text-xs text-slate-100 leading-relaxed">
                <strong class="text-[#7DD3FC] uppercase tracking-wider text-[10px] block mb-0.5">Reporte de Scouting Front Office</strong>
                ${esc(prof.scout_note)}
              </div>
            </div>
          </div>
        </div>

        <!-- 20-80 RADAR + SAVANT PERCENTILES -->
        <div class="grid grid-cols-1 xl:grid-cols-12 gap-5">
          <div class="xl:col-span-5 card-surface p-4 flex flex-col items-center justify-between">
            <div class="w-full flex items-center justify-between mb-1">
              <div>
                <span class="jersey-ribbon bg-[#0057A8] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>ESCALA MLB 20–80</span></span>
                <h3 class="text-sm font-extrabold text-[#002850] mt-1">Perfil de Herramientas (Tools)</h3>
              </div>
              <span class="text-[10px] font-code text-slate-500">50 = Promedio LMP</span>
            </div>
            ${radarHtml}
            <div class="w-full grid grid-cols-2 sm:grid-cols-3 gap-2 pt-3 border-t border-slate-100">
              ${toolsEntries.map(([name, val]) => `
                <div class="bg-slate-50 border border-slate-200 rounded-md p-2 flex flex-col justify-between">
                  <div class="text-[11px] font-bold text-slate-700 leading-tight">${esc(name)}</div>
                  <div class="flex items-baseline justify-between gap-1 mt-1">
                    <span class="text-base font-black ${val >= 60 ? "text-[#E6392F]" : (val >= 50 ? "text-[#003B73]" : "text-slate-600")} tabular-nums">${val}</span>
                    <span class="text-[10px] font-semibold text-slate-600 text-right">${esc(scoutingGradeText(val))}</span>
                  </div>
                </div>
              `).join("")}
            </div>
          </div>

          <div class="xl:col-span-7 card-surface p-4 space-y-2.5">
            <div class="flex flex-wrap items-center justify-between gap-2">
              <div>
                <span class="jersey-ribbon bg-[#E6392F] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>PERCENTILES LMP (1–100)</span></span>
                <h3 class="text-sm font-extrabold text-[#002850] mt-1">Ranking Relativo en Liga Mexicana del Pacífico</h3>
              </div>
              <div class="flex flex-wrap items-center gap-2 text-[10.5px] font-bold text-slate-600">
                <span class="text-blue-600">● Bajo (1–39)</span>
                <span>● Medio (40–64)</span>
                <span class="text-orange-600">● Alto (65–84)</span>
                <span class="text-red-600">● Élite (85–100)</span>
              </div>
            </div>
            <div class="space-y-2 pt-1">${pctHtml}</div>
          </div>
        </div>

        <!-- SPLITS MATRIX -->
        <div class="card-surface p-4 space-y-3">
          <div class="flex flex-wrap items-center justify-between gap-2">
            <div>
              <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>SPLITS DINÁMICOS</span></span>
              <h3 class="text-sm sm:text-base font-extrabold text-[#002850] mt-1">Desglose por Etapa y Condición de Juego</h3>
            </div>
            <div class="flex gap-2">
              ${!prof.is_pitcher ? `<button onclick="window.__jumpToPlayer(${prof.player_id}, 'batting')" class="text-xs font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-3 py-1 rounded transition">Ver en Spray Chart →</button>`
                : `<button onclick="window.__jumpToPlayer(${prof.player_id}, 'pitching')" class="text-xs font-bold bg-[#0072B2] hover:bg-[#0057A8] text-white px-3 py-1 rounded transition">Ver Zona 2D →</button>`}
            </div>
          </div>
          ${splitsMatrixHtml}
        </div>

        <!-- COMPARADOR CARA A CARA A vs B -->
        ${compareHtml}
      `;

      document.getElementById("btn-scout-clear-player")?.addEventListener("click", () => {
        state.selectedPlayerId = null;
        renderScoutingModule();
      });
      bindScoutCompareEvents(sdata, prof);
    }

    function buildScoutingRadarSVG(entries, compareEntries = null, nameA = "", nameB = "") {
      if (!entries.length) return `<div class="text-xs text-slate-400 py-10">Sin herramientas 20–80 evaluadas.</div>`;
      const cx = 215, cy = 148, maxR = 82;
      const n = entries.length;
      const pt = (i, grade) => {
        const ang = -Math.PI / 2 + (i * 2 * Math.PI) / n;
        const r = ((Math.max(20, Math.min(80, grade)) - 10) / 70) * maxR;
        return [cx + r * Math.cos(ang), cy + r * Math.sin(ang)];
      };

      let svg = `<svg viewBox="0 0 430 296" class="w-full max-w-[390px] h-auto select-none">`;
      [20, 40, 50, 60, 80].forEach((ring) => {
        const poly = entries.map((_, i) => pt(i, ring).map((x) => x.toFixed(1)).join(",")).join(" ");
        svg += `<polygon points="${poly}" fill="none" stroke="${ring === 50 ? "#0095DA" : "#CBD5E1"}" stroke-width="${ring === 50 ? 1.5 : 0.9}" stroke-dasharray="${ring === 50 ? "4 2" : "none"}"/>`;
        if ([20, 50, 80].includes(ring)) {
          const [, ry] = pt(0, ring);
          svg += `<text x="${cx + 5}" y="${(ry + 3).toFixed(1)}" font-size="8.5" font-weight="800" fill="${ring === 50 ? "#0072B2" : "#64748B"}" stroke="#FFFFFF" stroke-width="2" paint-order="stroke" font-family="Consolas, monospace">${ring}</text>`;
        }
      });
      entries.forEach(([label, val], i) => {
        const [ox, oy] = pt(i, 80);
        svg += `<line x1="${cx}" y1="${cy}" x2="${ox.toFixed(1)}" y2="${oy.toFixed(1)}" stroke="#CBD5E1" stroke-width="1"/>`;
        const [lx, ly] = pt(i, 96);
        const anchor = Math.abs(lx - cx) < 16 ? "middle" : (lx > cx ? "start" : "end");
        const cleanLbl = String(label).replace(/\s*\([^)]*\)/g, "").trim();
        const cmpPair = compareEntries ? compareEntries[i] : null;
        svg += `<text x="${lx.toFixed(1)}" y="${(ly - 1).toFixed(1)}" text-anchor="${anchor}" font-size="10.5" font-weight="800" fill="#002850">${esc(cleanLbl)}</text>`;
        if (cmpPair) {
          svg += `<text x="${lx.toFixed(1)}" y="${(ly + 10.5).toFixed(1)}" text-anchor="${anchor}" font-size="9.5" font-weight="800" font-family="Consolas, monospace"><tspan fill="#003B73">${val}</tspan><tspan fill="#64748B"> vs </tspan><tspan fill="#E6392F">${cmpPair[1]}</tspan></text>`;
        } else {
          svg += `<text x="${lx.toFixed(1)}" y="${(ly + 10.5).toFixed(1)}" text-anchor="${anchor}" font-size="9.5" font-weight="800" fill="#0072B2" font-family="Consolas, monospace">${val}</text>`;
        }
      });

      const valPoly = entries.map(([, val], i) => pt(i, val).map((x) => x.toFixed(1)).join(",")).join(" ");
      svg += `<polygon points="${valPoly}" fill="#0095DA" fill-opacity="0.28" stroke="#003B73" stroke-width="2.4"/>`;
      entries.forEach(([, val], i) => {
        const [vx, vy] = pt(i, val);
        svg += `<circle cx="${vx.toFixed(1)}" cy="${vy.toFixed(1)}" r="4.6" fill="${val >= 60 ? "#E6392F" : "#003B73"}" stroke="#FFFFFF" stroke-width="1.4"/>`;
      });

      if (compareEntries && compareEntries.length === entries.length) {
        const cmpPoly = compareEntries.map(([, val], i) => pt(i, val).map((x) => x.toFixed(1)).join(",")).join(" ");
        svg += `<polygon points="${cmpPoly}" fill="#E6392F" fill-opacity="0.18" stroke="#E6392F" stroke-width="2.2" stroke-dasharray="5 3"/>`;
        compareEntries.forEach(([, val], i) => {
          const [vx, vy] = pt(i, val);
          svg += `<circle cx="${vx.toFixed(1)}" cy="${vy.toFixed(1)}" r="4.2" fill="#E6392F" stroke="#FFFFFF" stroke-width="1.2"/>`;
        });
      }
      svg += `</svg>`;
      return svg;
    }

    function bindScoutCompareEvents(sdata, activeProf = null) {
      document.querySelectorAll(".cmp-type-btn").forEach((b) => {
        b.addEventListener("click", () => {
          if (state.scoutCompareType !== b.dataset.cmptype) {
            state.scoutCompareType = b.dataset.cmptype;
            state.scoutCompareSubRole = "all";
            state.scoutCompareA = null;
            state.scoutCompareB = null;
            renderScoutingModule();
          }
        });
      });
      document.querySelectorAll(".cmp-subrole-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.scoutCompareSubRole = b.dataset.cmpsubrole;
          renderScoutingModule();
        });
      });
      document.getElementById("sel-scout-compare-a")?.addEventListener("change", (e) => {
        const val = e.target.value ? Number(e.target.value) : null;
        if (val !== null && val === state.scoutCompareB) state.scoutCompareB = null;
        state.scoutCompareA = val;
        renderScoutingModule();
      });
      document.getElementById("sel-scout-compare-b")?.addEventListener("change", (e) => {
        const val = e.target.value ? Number(e.target.value) : null;
        if (val !== null && val === state.scoutCompareA) state.scoutCompareA = null;
        state.scoutCompareB = val;
        renderScoutingModule();
      });
      document.getElementById("btn-cmp-use-active")?.addEventListener("click", () => {
        if (activeProf) {
          state.scoutCompareType = activeProf.is_pitcher ? "pitchers" : "batters";
          state.scoutCompareSubRole = "all";
          state.scoutCompareA = activeProf.player_id;
          if (state.scoutCompareB === activeProf.player_id) state.scoutCompareB = null;
          renderScoutingModule();
          setTimeout(() => {
            document.getElementById("scout-compare-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
          }, 40);
        }
      });
      document.getElementById("btn-cmp-clear")?.addEventListener("click", () => {
        state.scoutCompareA = null;
        state.scoutCompareB = null;
        renderScoutingModule();
      });
    }

    function buildScoutCompareHTML(activeProf, sdata) {
      const profiles = sdata.scouting_profiles || [];
      const cmpType = state.scoutCompareType || "batters";
      const subRole = state.scoutCompareSubRole || "all";

      const pool = profiles.filter((p) => {
        if (cmpType === "pitchers") {
          if (!p.is_pitcher) return false;
          if (subRole !== "all" && p.role_group !== subRole) return false;
          return true;
        }
        return !p.is_pitcher;
      });

      if (state.scoutCompareA !== null && !pool.some((p) => p.player_id === state.scoutCompareA)) {
        state.scoutCompareA = null;
      }
      if (state.scoutCompareB !== null && !pool.some((p) => p.player_id === state.scoutCompareB)) {
        state.scoutCompareB = null;
      }

      const profA = state.scoutCompareA !== null ? pool.find((p) => p.player_id === state.scoutCompareA) : null;
      const profB = state.scoutCompareB !== null ? pool.find((p) => p.player_id === state.scoutCompareB) : null;
      const canUseActive = activeProf && ((cmpType === "pitchers" && activeProf.is_pitcher) || (cmpType === "batters" && !activeProf.is_pitcher));

      const controlsBar = `
        <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-200">
          <div>
            <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>COMPARADOR CARA A CARA (A vs B)</span></span>
            <h3 class="text-sm sm:text-base font-extrabold text-[#002850] mt-1">Comparador por Rol: Bateadores o Pitchers</h3>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-cmptype="batters" class="cmp-type-btn px-3 py-1.5 ${cmpType === "batters" ? "bg-[#003B73] text-white" : "bg-white text-slate-700 hover:bg-slate-50"}">⚾ Comparar Bateadores</button>
              <button data-cmptype="pitchers" class="cmp-type-btn px-3 py-1.5 ${cmpType === "pitchers" ? "bg-[#003B73] text-white" : "bg-white text-slate-700 hover:bg-slate-50"}">🎯 Comparar Pitchers</button>
            </div>
            ${cmpType === "pitchers" ? `
              <div class="flex rounded-md overflow-hidden border border-slate-300 text-[11px] font-bold">
                <button data-cmpsubrole="all" class="cmp-subrole-btn px-2 py-1 ${subRole === "all" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Todos</button>
                <button data-cmpsubrole="Abridor" class="cmp-subrole-btn px-2 py-1 ${subRole === "Abridor" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Abridores</button>
                <button data-cmpsubrole="Bullpen" class="cmp-subrole-btn px-2 py-1 ${subRole === "Bullpen" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Bullpen</button>
              </div>` : ""}
            ${canUseActive ? `<button id="btn-cmp-use-active" class="text-[11px] font-bold bg-sky-50 hover:bg-[#0072B2] text-[#003B73] hover:text-white border border-sky-200 px-2.5 py-1 rounded transition">Usar ficha activa como A</button>` : ""}
            ${(profA || profB) ? `<button id="btn-cmp-clear" class="text-[11px] font-bold bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-300 px-2.5 py-1 rounded transition">Limpiar A y B</button>` : ""}
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="bg-slate-50 border border-[#003B73]/30 rounded-lg p-2.5 flex flex-col gap-1">
            <label for="sel-scout-compare-a" class="text-[10.5px] font-extrabold uppercase tracking-wider text-[#003B73]">Jugador A (Azul)</label>
            <select id="sel-scout-compare-a" class="border border-slate-300 rounded px-2.5 py-1.5 text-xs font-bold text-[#002850] bg-white">
              <option value="">— Seleccionar Jugador A (Ninguno) —</option>
              ${pool.map((p) => {
                const isSelA = profA && p.player_id === profA.player_id;
                const isDisB = profB && p.player_id === profB.player_id;
                return `<option value="${p.player_id}" ${isSelA ? "selected" : ""} ${isDisB ? "disabled" : ""}>${esc(p.full_name)} (${esc(p.primary_position)} · ${esc(p.roster_status)} · ${p.is_pitcher ? `${fmtNum(p.reg_ip,1)} IP` : `${p.reg_pa} PA`})${isDisB ? " [En B]" : ""}</option>`;
              }).join("")}
            </select>
          </div>
          <div class="bg-slate-50 border border-[#E6392F]/30 rounded-lg p-2.5 flex flex-col gap-1">
            <label for="sel-scout-compare-b" class="text-[10.5px] font-extrabold uppercase tracking-wider text-[#E6392F]">Jugador B (Rojo)</label>
            <select id="sel-scout-compare-b" class="border border-slate-300 rounded px-2.5 py-1.5 text-xs font-bold text-[#002850] bg-white">
              <option value="">— Seleccionar Jugador B (Ninguno) —</option>
              ${pool.map((p) => {
                const isSelB = profB && p.player_id === profB.player_id;
                const isDisA = profA && p.player_id === profA.player_id;
                return `<option value="${p.player_id}" ${isSelB ? "selected" : ""} ${isDisA ? "disabled" : ""}>${esc(p.full_name)} (${esc(p.primary_position)} · ${esc(p.roster_status)} · ${p.is_pitcher ? `${fmtNum(p.reg_ip,1)} IP` : `${p.reg_pa} PA`})${isDisA ? " [En A]" : ""}</option>`;
              }).join("")}
            </select>
          </div>
        </div>`;

      if (!profA || !profB) {
        return `
          <div id="scout-compare-panel" class="card-surface p-4 space-y-3 border-t-4 border-t-[#0072B2]">
            ${controlsBar}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              ${[{ slot: "A", p: profA, col: "#003B73" }, { slot: "B", p: profB, col: "#E6392F" }].map((it) => it.p ? `
                <div class="border rounded-lg p-3 bg-white flex items-center gap-3" style="border-left:4px solid ${it.col}">
                  ${renderPlayerAvatar(it.p, "w-14 h-[70px]", "rounded-xl")}
                  <div>
                    <div class="text-[10px] font-extrabold uppercase" style="color:${it.col}">Jugador ${it.slot} seleccionado</div>
                    <div class="text-sm font-black text-[#002850]">${esc(it.p.full_name)}</div>
                    <div class="text-[11px] font-code text-slate-600">${esc(it.p.role_group)} · ${esc(it.p.primary_position)} · ${esc(it.p.roster_status)}</div>
                  </div>
                </div>` : `
                <div class="border border-dashed border-slate-300 rounded-lg p-4 bg-slate-50/70 text-center text-xs text-slate-500">
                  <strong class="block text-[#002850] mb-0.5">Jugador ${it.slot} sin seleccionar</strong>
                  Elige un ${cmpType === "pitchers" ? "lanzador" : "bateador"} en el menú superior para habilitar el radar dual y la tabla comparativa.
                </div>`).join("")}
            </div>
          </div>`;
      }

      const stageLbl = STAGE_LABELS[state.stage];
      const condLbl = COND_LABELS[state.cond];
      const toolsA = Object.entries(profA.tools_20_80 || {});
      const alignedToolsB = toolsA.map(([tName]) => [tName, profB.tools_20_80?.[tName] ?? 50]);
      const sameAxes = toolsA.length > 0 && profA.is_pitcher === profB.is_pitcher;
      const dualRadar = buildScoutingRadarSVG(toolsA, sameAxes ? alignedToolsB : null, profA.full_name, profB.full_name);

      // Strict stage-synced & condition-synced head-to-head rows (NO silent fallback to global_reg or splits.all!)
      const stg = state.stage;
      const hasRegA = cmpType === "pitchers" ? ((profA.reg_ip || 0) > 0) : ((profA.reg_pa || 0) > 0);
      const hasRegB = cmpType === "pitchers" ? ((profB.reg_ip || 0) > 0) : ((profB.reg_pa || 0) > 0);
      let volA = "", volB = "", shortA = false, shortB = false;
      let cmpRows = [];

      const formatDelta = (diff, dFmt, lowerBetter) => {
        if (diff === 0 || !Number.isFinite(diff)) return { text: "Empate", cls: "text-slate-400" };
        const aWins = lowerBetter ? diff < 0 : diff > 0;
        const sign = diff > 0 ? "+" : "";
        return {
          text: `${aWins ? "A" : "B"} (${sign}${dFmt(diff)})`,
          cls: aWins ? "text-[#003B73] font-black" : "text-[#E6392F] font-black",
        };
      };

      if (cmpType === "batters") {
        const getB = (pid) => (sdata.yaquis_batters || []).find((b) => b.player_id === pid && b.etapa === stg);
        const bA = getB(profA.player_id), bB = getB(profB.player_id);
        const rawSA = bA ? (state.cond === "all" ? (bA.splits?.all || {}) : (bA.splits?.[state.cond] || {})) : {};
        const rawSB = bB ? (state.cond === "all" ? (bB.splits?.all || {}) : (bB.splits?.[state.cond] || {})) : {};
        const paA = rawSA.PA ?? 0, paB = rawSB.PA ?? 0;
        const actA = paA > 0, actB = paB > 0;
        const sA = actA ? rawSA : {}, sB = actB ? rawSB : {};
        volA = actA ? `${paA} PA` : `0 PA (sin actividad)`;
        volB = actB ? `${paB} PA` : `0 PA (sin actividad)`;
        shortA = paA > 0 && paA < 25;
        shortB = paB > 0 && paB < 25;

        const specs = [
          { lbl: "PA (Apariciones)", a: bA ? paA : null, b: bB ? paB : null, fmt: fmtInt, df: (d) => Math.round(d), pctK: null, lb: false, noWinner: !(actA && actB) },
          { lbl: "AVG", a: sA.AVG, b: sB.AVG, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "AVG", lb: false },
          { lbl: "OBP", a: sA.OBP, b: sB.OBP, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "OBP", lb: false },
          { lbl: "SLG", a: sA.SLG, b: sB.SLG, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "SLG", lb: false },
          { lbl: "OPS", a: sA.OPS, b: sB.OPS, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "OPS", lb: false },
          { lbl: "OPS vs LHP*", a: bA?.splits?.vs_lhp?.PA ? bA.splits.vs_lhp.OPS : null, b: bB?.splits?.vs_lhp?.PA ? bB.splits.vs_lhp.OPS : null, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
          { lbl: "OPS vs RHP*", a: bA?.splits?.vs_rhb?.PA ? bA.splits.vs_rhb.OPS : null, b: bB?.splits?.vs_rhb?.PA ? bB.splits.vs_rhb.OPS : null, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
          { lbl: "wOBA", a: sA.wOBA, b: sB.wOBA, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
          { lbl: "wRC+", a: sA.wRC_plus, b: sB.wRC_plus, fmt: fmtInt, df: (d) => Math.round(d), pctK: null, lb: false },
          { lbl: "ISO (Poder Aislado)", a: sA.ISO, b: sB.ISO, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "ISO", lb: false },
          { lbl: "BABIP", a: sA.BABIP, b: sB.BABIP, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: "BABIP", lb: false },
          { lbl: "BB% (Disciplina)", a: sA.BB_pct, b: sB.BB_pct, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: "BB%", lb: false },
          { lbl: "K% ↓ (Menor = Mejor)", a: sA.K_pct, b: sB.K_pct, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: "K%", lb: true },
          { lbl: "Jonrones (HR)", a: actA ? sA.HR : null, b: actB ? sB.HR : null, fmt: fmtInt, df: (d) => `${Math.round(d)} HR`, pctK: null, lb: false },
          { lbl: "Carreras Impulsadas (RBI)", a: actA ? sA.RBI : null, b: actB ? sB.RBI : null, fmt: fmtInt, df: (d) => `${Math.round(d)} RBI`, pctK: null, lb: false },
          { lbl: "Bases Robadas (SB)*", a: bA ? bA.SB : null, b: bB ? bB.SB : null, fmt: fmtInt, df: (d) => Math.round(d), pctK: "Velocidad (SB)", lb: false },
          { lbl: "AVG con RISP*", a: bA?.RISP_AVG, b: bB?.RISP_AVG, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
          { lbl: "AVG 2Out RISP*", a: bA?.TWO_OUT_RISP_AVG, b: bB?.TWO_OUT_RISP_AVG, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
          { lbl: "HighLev OPS*", a: bA?.HIGH_LEV_OPS, b: bB?.HIGH_LEV_OPS, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: false },
        ];
        cmpRows = specs;
      } else {
        const getP = (pid) => (sdata.yaquis_pitchers || []).find((p) => p.player_id === pid && p.etapa === stg);
        const pA = getP(profA.player_id), pB = getP(profB.player_id);
        const isSplitCond = ["home", "away", "risp"].includes(state.cond);
        const spA = pA && isSplitCond ? (pA.splits?.[state.cond] || {}) : (pA || {});
        const spB = pB && isSplitCond ? (pB.splits?.[state.cond] || {}) : (pB || {});
        const hasSplitA = !isSplitCond ? Boolean(pA) : Boolean(spA.PA > 0);
        const hasSplitB = !isSplitCond ? Boolean(pB) : Boolean(spB.PA > 0);
        const vA_ip = hasSplitA ? (spA.IP ?? 0) : 0;
        const vB_ip = hasSplitB ? (spB.IP ?? 0) : 0;
        volA = pA ? (hasSplitA ? `${fmtNum(vA_ip, 1)} IP` : `0.0 IP (${condLbl})`) : `0.0 IP (sin actividad)`;
        volB = pB ? (hasSplitB ? `${fmtNum(vB_ip, 1)} IP` : `0.0 IP (${condLbl})`) : `0.0 IP (sin actividad)`;
        shortA = vA_ip > 0 && vA_ip < 8;
        shortB = vB_ip > 0 && vB_ip < 8;

        const max14A = profA.role_group === "Abridor" ? 210 : 95;
        const max14B = profB.role_group === "Abridor" ? 210 : 95;
        const pctLoadA = pA ? Math.round(((pA.pitches_14d || 0) / max14A) * 100) : null;
        const pctLoadB = pB ? Math.round(((pB.pitches_14d || 0) / max14B) * 100) : null;
        const bothActiveWorkload = Boolean(pA && (pA.IP || 0) > 0 && pB && (pB.IP || 0) > 0 && ((pA.pitches_14d || 0) > 0 || (pB.pitches_14d || 0) > 0));

        const specs = [
          { lbl: isSplitCond ? `Innings (${condLbl})` : "Innings (IP · G/GS)", a: hasSplitA ? spA.IP : null, b: hasSplitB ? spB.IP : null, dispA: hasSplitA ? (isSplitCond ? `${fmtNum(spA.IP,1)} (${spA.PA} BF)` : `${fmtNum(pA.IP,1)} (${pA.G}/${pA.GS})`) : "—", dispB: hasSplitB ? (isSplitCond ? `${fmtNum(spB.IP,1)} (${spB.PA} BF)` : `${fmtNum(pB.IP,1)} (${pB.G}/${pB.GS})`) : "—", df: (d) => `${d.toFixed(1)} IP`, pctK: null, lb: false },
          { lbl: "Salvamentos (SV)*", a: (!isSplitCond && pA) ? pA.SV : null, b: (!isSplitCond && pB) ? pB.SV : null, fmt: fmtInt, df: (d) => `${Math.round(d)} SV`, pctK: null, lb: false },
          { lbl: "ERA ↓", a: hasSplitA ? spA.ERA : null, b: hasSplitB ? spB.ERA : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "ERA", lb: true },
          { lbl: "ERA- ↓*", a: (!isSplitCond && pA) ? pA.ERA_minus : null, b: (!isSplitCond && pB) ? pB.ERA_minus : null, fmt: fmtInt, df: (d) => Math.round(d), pctK: null, lb: true },
          { lbl: "FIP ↓", a: hasSplitA ? spA.FIP : null, b: hasSplitB ? spB.FIP : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "FIP", lb: true },
          { lbl: "xFIP ↓*", a: (!isSplitCond && pA) ? pA.xFIP : null, b: (!isSplitCond && pB) ? pB.xFIP : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: null, lb: true },
          { lbl: "WHIP ↓", a: hasSplitA ? spA.WHIP : null, b: hasSplitB ? spB.WHIP : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "WHIP", lb: true },
          { lbl: "K/9", a: hasSplitA ? spA.K9 : null, b: hasSplitB ? spB.K9 : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "K9", lb: false },
          { lbl: "BB/9 ↓", a: hasSplitA ? spA.BB9 : null, b: hasSplitB ? spB.BB9 : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "BB9", lb: true },
          { lbl: "HR/9 ↓*", a: (!isSplitCond && pA) ? pA.HR9 : null, b: (!isSplitCond && pB) ? pB.HR9 : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: "HR9", lb: true },
          { lbl: "K/BB*", a: (!isSplitCond && pA) ? pA.K_BB : null, b: (!isSplitCond && pB) ? pB.K_BB : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: null, lb: false },
          { lbl: "GB/FB*", a: (!isSplitCond && pA) ? pA.GB_FB : null, b: (!isSplitCond && pB) ? pB.GB_FB : null, fmt: (v) => fmtNum(v,2), df: (d) => d.toFixed(2), pctK: null, lb: false },
          { lbl: "LOB%*", a: (!isSplitCond && pA) ? pA.LOB_pct : null, b: (!isSplitCond && pB) ? pB.LOB_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: null, lb: false },
          { lbl: "IR / IRS*", a: (!isSplitCond && pA) ? pA.IR : null, b: (!isSplitCond && pB) ? pB.IR : null, dispA: (!isSplitCond && pA) ? `${pA.IR ?? 0}/${pA.IRS ?? 0}` : "—", dispB: (!isSplitCond && pB) ? `${pB.IR ?? 0}/${pB.IRS ?? 0}` : "—", noWinner: true },
          { lbl: "Strike%", a: hasSplitA ? spA.Strike_pct : null, b: hasSplitB ? spB.Strike_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: null, lb: false },
          { lbl: "FPS% (1er Strike)", a: hasSplitA ? spA.FPS_pct : null, b: hasSplitB ? spB.FPS_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: null, lb: false },
          { lbl: "InZone%", a: hasSplitA ? spA.InZone_pct : null, b: hasSplitB ? spB.InZone_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: "InZone%", lb: false },
          { lbl: "Whiff%", a: hasSplitA ? spA.Whiff_pct : null, b: hasSplitB ? spB.Whiff_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: "Whiff%", lb: false },
          { lbl: "Chase%", a: hasSplitA ? spA.Chase_pct : null, b: hasSplitB ? spB.Chase_pct : null, fmt: (v) => fmtNum(v,1,"%"), df: (d) => `${d.toFixed(1)}%`, pctK: "Chase%", lb: false },
          { lbl: "OPS vs LHB ↓*", a: pA?.splits?.vs_lhb?.OPS_against, b: pB?.splits?.vs_lhb?.OPS_against, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: true },
          { lbl: "OPS vs RHB ↓*", a: pA?.splits?.vs_rhb?.OPS_against, b: pB?.splits?.vs_rhb?.OPS_against, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: true },
          { lbl: "OPS con RISP ↓*", a: pA?.splits?.risp?.OPS_against, b: pB?.splits?.risp?.OPS_against, fmt: fmtRate, df: (d) => d.toFixed(3), pctK: null, lb: true },
          { lbl: "Descanso (días) & B2B*", a: pA ? pA.rest_days : null, b: pB ? pB.rest_days : null, dispA: pA ? `${pA.rest_days ?? "—"}d${pA.is_b2b ? " · B2B" : ""}` : "—", dispB: pB ? `${pB.rest_days ?? "—"}d${pB.is_b2b ? " · B2B" : ""}` : "—", noWinner: true },
          { lbl: "% Carga 14d (vs límite rol)*", a: pctLoadA, b: pctLoadB, dispA: pA ? `${pA.pitches_14d ?? 0}/${max14A}p · ${pctLoadA}% (${pA.fatigue_status || "—"})` : "—", dispB: pB ? `${pB.pitches_14d ?? 0}/${max14B}p · ${pctLoadB}% (${pB.fatigue_status || "—"})` : "—", df: (d) => `${Math.round(d)}%`, pctK: null, lb: true, noWinner: !bothActiveWorkload },
        ];
        cmpRows = specs;
      }

      // Append 20-80 tools comparison rows matched by key (suppress winner if either lacks reg sample)
      toolsA.forEach(([tName, tValA]) => {
        const tValB = profB.tools_20_80?.[tName];
        cmpRows.push({
          lbl: `Tool 20–80: ${tName}`,
          a: hasRegA ? tValA : null,
          b: hasRegB ? tValB : null,
          dispA: hasRegA ? String(tValA) : "— (0 reg.)",
          dispB: hasRegB && tValB != null ? String(tValB) : "— (0 reg.)",
          fmt: fmtInt,
          df: (d) => `${Math.round(d)} pts`,
          pctK: null,
          lb: false,
          noWinner: !(hasRegA && hasRegB),
        });
      });

      const condTag = state.cond !== "all" ? ` · ${condLbl}` : "";
      return `
        <div id="scout-compare-panel" class="card-surface p-4 space-y-3 border-t-4 border-t-[#0072B2]">
          ${controlsBar}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div class="border border-[#003B73]/30 rounded-lg p-3 bg-sky-50/40 flex items-center gap-3">
              ${renderPlayerAvatar(profA, "w-14 h-[70px]", "rounded-xl")}
              <div class="min-w-0">
                <div class="text-[10px] font-extrabold uppercase text-[#003B73] flex flex-wrap items-center gap-1.5">
                  <span>Jugador A · ${esc(volA)}</span>
                  ${shortA ? `<span class="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">⚠ Muestra corta</span>` : ""}
                </div>
                <div class="text-sm font-black text-[#002850] truncate">${esc(profA.full_name)}</div>
                <div class="text-[11px] font-code text-slate-600">${esc(profA.role_group)} (${esc(profA.primary_position)}) · ${esc(profA.roster_status)} · B/T ${esc(profA.bat_side)}/${esc(profA.pitch_hand)}</div>
              </div>
            </div>
            <div class="border border-[#E6392F]/30 rounded-lg p-3 bg-red-50/40 flex items-center gap-3">
              ${renderPlayerAvatar(profB, "w-14 h-[70px]", "rounded-xl")}
              <div class="min-w-0">
                <div class="text-[10px] font-extrabold uppercase text-[#E6392F] flex flex-wrap items-center gap-1.5">
                  <span>Jugador B · ${esc(volB)}</span>
                  ${shortB ? `<span class="px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">⚠ Muestra corta</span>` : ""}
                </div>
                <div class="text-sm font-black text-[#002850] truncate">${esc(profB.full_name)}</div>
                <div class="text-[11px] font-code text-slate-600">${esc(profB.role_group)} (${esc(profB.primary_position)}) · ${esc(profB.roster_status)} · B/T ${esc(profB.bat_side)}/${esc(profB.pitch_hand)}</div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 xl:grid-cols-12 gap-4 items-start">
            <div class="xl:col-span-5 flex flex-col items-center">
              <div class="flex flex-wrap justify-center gap-3 text-[11px] font-bold mb-1">
                <span class="flex items-center gap-1.5 text-[#003B73]"><i class="w-3 h-3 rounded-sm bg-[#0095DA]/40 border-2 border-[#003B73] inline-block"></i> ${esc(profA.full_name)}</span>
                <span class="flex items-center gap-1.5 text-[#E6392F]"><i class="w-3 h-3 rounded-sm bg-[#E6392F]/30 border-2 border-dashed border-[#E6392F] inline-block"></i> ${esc(profB.full_name)}</span>
              </div>
              ${dualRadar}
            </div>
            <div class="xl:col-span-7 space-y-1.5">
              <div class="fo-table-wrap rounded-lg border border-slate-200 max-h-[520px]">
                <table class="fo-table">
                  <thead>
                    <tr>
                      <th class="text-left">Métrica (${esc(stageLbl)}${esc(condTag)})</th>
                      <th class="text-right">${esc(profA.full_name)} (A)</th>
                      <th class="text-right">Pct A (Reg.)</th>
                      <th class="text-right">${esc(profB.full_name)} (B)</th>
                      <th class="text-right">Pct B (Reg.)</th>
                      <th class="text-right">Ventaja (Δ)</th>
                    </tr>
                  </thead>
                  <tbody>
                    ${cmpRows.map((row) => {
                      const na = Number(row.a), nb = Number(row.b);
                      const hasA = row.a !== null && row.a !== undefined && Number.isFinite(na);
                      const hasB = row.b !== null && row.b !== undefined && Number.isFinite(nb);
                      const validBoth = hasA && hasB && !row.noWinner;
                      const winA = validBoth && (row.lb ? na < nb : na > nb);
                      const winB = validBoth && (row.lb ? nb < na : nb > na);
                      const diffInfo = validBoth ? formatDelta(na - nb, row.df, row.lb) : { text: "—", cls: "text-slate-400" };
                      const pA = (hasRegA && row.pctK) ? profA.percentiles?.[row.pctK] : null;
                      const pB = (hasRegB && row.pctK) ? profB.percentiles?.[row.pctK] : null;
                      const vA = row.dispA ?? (row.fmt ? row.fmt(row.a) : "—");
                      const vB = row.dispB ?? (row.fmt ? row.fmt(row.b) : "—");
                      return `<tr>
                        <td class="text-left font-bold text-slate-800">${esc(row.lbl)}</td>
                        <td class="text-right font-code ${winA ? "font-black text-[#003B73] bg-sky-50" : "text-slate-700"}">${esc(vA)}</td>
                        <td class="text-right font-code font-bold" style="${pA != null ? `color:${pctBadgeColor(pA)}` : "color:#94A3B8"}">${pA != null ? pA : "—"}</td>
                        <td class="text-right font-code ${winB ? "font-black text-[#E6392F] bg-red-50" : "text-slate-700"}">${esc(vB)}</td>
                        <td class="text-right font-code font-bold" style="${pB != null ? `color:${pctBadgeColor(pB)}` : "color:#94A3B8"}">${pB != null ? pB : "—"}</td>
                        <td class="text-right font-code text-[11px] ${diffInfo.cls}">${esc(diffInfo.text)}</td>
                      </tr>`;
                    }).join("")}
                  </tbody>
                </table>
              </div>
              <p class="text-[10.5px] text-slate-500 px-1">* Métricas situacionales/carga a nivel etapa completa. Percentiles <strong class="text-slate-600">(Reg.)</strong> y escala 20–80 reflejan muestra reglamentaria de Rol Regular.</p>
            </div>
          </div>
        </div>`;
    }

    function buildPlayerSplitsHTML(prof, sdata) {
      if (!prof.is_pitcher) {
        const bStages = (sdata.yaquis_batters || []).filter((b) => b.player_id === prof.player_id);
        if (!bStages.length) return `<div class="text-xs text-slate-500">Sin apariciones de bateo en esta temporada.</div>`;

        const order = ["global_reg", "v1", "v2", "playoffs"];
        const stageRows = order.map((st) => bStages.find((x) => x.etapa === st)).filter(Boolean);
        if (!stageRows.length) return `<div class="text-xs text-slate-500">Sin apariciones de bateo en esta temporada.</div>`;
        const glob = stageRows.find((x) => x.etapa === state.stage) || stageRows.find((x) => x.etapa === "global_reg") || stageRows[0];
        const splitRows = [
          ...stageRows.map((x) => ({ label: `Etapa: ${STAGE_LABELS[x.etapa]}`, d: x.splits?.all || {} })),
          ...["home", "away", "vs_lhp", "vs_rhp", "risp"].map((c) => ({ label: `Split (${STAGE_LABELS[glob.etapa]}): ${COND_LABELS[c]}`, d: glob.splits?.[c] || {} })),
        ];

        return `
          <div class="fo-table-wrap rounded-lg border border-slate-200">
            <table class="fo-table">
              <thead><tr>
                <th class="text-left">Corte</th><th class="text-right">PA</th><th class="text-right">AB</th><th class="text-right">H</th><th class="text-right">HR</th><th class="text-right">RBI</th>
                <th class="text-right">AVG</th><th class="text-right">OBP</th><th class="text-right">SLG</th><th class="text-right">OPS</th>
                <th class="text-right">wOBA</th><th class="text-right">wRC+</th><th class="text-right">BB%</th><th class="text-right">K%</th>
              </tr></thead>
              <tbody>
                ${splitRows.map((row) => {
                  const d = row.d;
                  if (!d || !d.PA) return `<tr><td class="text-left text-slate-400">${esc(row.label)}</td><td class="text-right text-slate-400" colspan="13">0 PA registrados</td></tr>`;
                  const shortTag = d.PA < 25 ? ` <span title="Muestra corta (&lt;25 PA)" class="text-[9.5px] text-amber-700 font-bold">⚠</span>` : "";
                  return `<tr>
                    <td class="text-left font-bold text-[#002850]">${esc(row.label)}${shortTag}</td>
                    <td class="text-right">${d.PA}</td><td class="text-right">${d.AB}</td><td class="text-right">${d.H}</td><td class="text-right">${d.HR}</td><td class="text-right">${d.RBI}</td>
                    <td class="text-right font-bold">${fmtRate(d.AVG)}</td><td class="text-right">${fmtRate(d.OBP)}</td><td class="text-right">${fmtRate(d.SLG)}</td>
                    <td class="text-right font-extrabold text-[#003B73]">${fmtRate(d.OPS)}</td>
                    <td class="text-right">${fmtRate(d.wOBA)}</td><td class="text-right font-bold">${fmtInt(d.wRC_plus)}</td>
                    <td class="text-right">${fmtNum(d.BB_pct,1,"%")}</td><td class="text-right">${fmtNum(d.K_pct,1,"%")}</td>
                  </tr>`;
                }).join("")}
              </tbody>
            </table>
          </div>`;
      } else {
        const pStages = (sdata.yaquis_pitchers || []).filter((p) => p.player_id === prof.player_id);
        if (!pStages.length) return `<div class="text-xs text-slate-500">Sin actuaciones de pitcheo en esta temporada.</div>`;
        const order = ["global_reg", "v1", "v2", "playoffs"];
        const stageRows = order.map((st) => pStages.find((x) => x.etapa === st)).filter(Boolean);
        if (!stageRows.length) return `<div class="text-xs text-slate-500">Sin actuaciones de pitcheo en esta temporada.</div>`;
        const refStage = stageRows.find((x) => x.etapa === state.stage) || stageRows.find((x) => x.etapa === "global_reg") || stageRows[0];
        const pSplits = refStage?.splits || {};
        const splitList = [
          { key: "home", label: `Split (${STAGE_LABELS[refStage.etapa]}): Local (Estadio Yaquis)` },
          { key: "away", label: `Split (${STAGE_LABELS[refStage.etapa]}): Visita` },
          { key: "vs_lhb", label: `Split (${STAGE_LABELS[refStage.etapa]}): vs Bateadores Zurdos (LHB)` },
          { key: "vs_rhb", label: `Split (${STAGE_LABELS[refStage.etapa]}): vs Bateadores Derechos (RHB)` },
          { key: "risp", label: `Split (${STAGE_LABELS[refStage.etapa]}): Con RISP` },
        ];
        return `
          <div class="space-y-3">
            <div class="fo-table-wrap rounded-lg border border-slate-200">
              <table class="fo-table">
                <thead><tr>
                  <th class="text-left">Etapa</th><th class="text-right">G/GS</th><th class="text-right">IP</th><th class="text-right">ERA</th>
                  <th class="text-right">ERA-</th><th class="text-right">FIP</th><th class="text-right">xFIP</th>
                  <th class="text-right">WHIP</th><th class="text-right">K/9</th><th class="text-right">BB/9</th>
                  <th class="text-right">Strike%</th><th class="text-right">InZone%</th><th class="text-right">Whiff%</th><th class="text-right">Fatiga 14d</th>
                </tr></thead>
                <tbody>
                  ${stageRows.map((d) => {
                    const shortIp = (d.IP || 0) < 8 ? ` <span title="Muestra corta (&lt;8 IP)" class="text-[9.5px] text-amber-700 font-bold">⚠</span>` : "";
                    return `<tr>
                      <td class="text-left font-bold text-[#002850]">${esc(STAGE_LABELS[d.etapa])}${shortIp}</td>
                      <td class="text-right">${d.G}/${d.GS}</td>
                      <td class="text-right">${fmtNum(d.IP,1)}</td>
                      <td class="text-right font-extrabold text-[#003B73]">${fmtNum(d.ERA,2)}</td>
                      <td class="text-right">${fmtInt(d.ERA_minus)}</td>
                      <td class="text-right">${fmtNum(d.FIP,2)}</td>
                      <td class="text-right">${fmtNum(d.xFIP,2)}</td>
                      <td class="text-right">${fmtNum(d.WHIP,2)}</td>
                      <td class="text-right">${fmtNum(d.K9,2)}</td>
                      <td class="text-right">${fmtNum(d.BB9,2)}</td>
                      <td class="text-right">${fmtNum(d.Strike_pct,1,"%")}</td>
                      <td class="text-right">${fmtNum(d.InZone_pct,1,"%")}</td>
                      <td class="text-right">${fmtNum(d.Whiff_pct,1,"%")}</td>
                      <td class="text-right font-bold">${d.pitches_14d ?? 0}p (${esc(d.fatigue_status)})</td>
                    </tr>`;
                  }).join("")}
                </tbody>
              </table>
            </div>
            <div class="fo-table-wrap rounded-lg border border-slate-200">
              <table class="fo-table">
                <thead><tr>
                  <th class="text-left">Split Situacional / Mano</th><th class="text-right">PA</th><th class="text-right">IP est</th><th class="text-right">ERA</th>
                  <th class="text-right">FIP</th><th class="text-right">WHIP</th><th class="text-right">AVG vs</th><th class="text-right">OPS vs</th>
                  <th class="text-right">K/9</th><th class="text-right">BB/9</th><th class="text-right">Strike%</th><th class="text-right">InZone%</th><th class="text-right">Whiff%</th><th class="text-right">Chase%</th>
                </tr></thead>
                <tbody>
                  ${splitList.map((sp) => {
                    const d = pSplits[sp.key];
                    if (!d || !d.PA) return `<tr><td class="text-left text-slate-400">${esc(sp.label)}</td><td class="text-right text-slate-400" colspan="13">0 PA registrados en esta etapa</td></tr>`;
                    const shortSp = (d.IP || 0) < 8 ? ` <span title="Muestra corta (&lt;8 IP)" class="text-[9.5px] text-amber-700 font-bold">⚠</span>` : "";
                    return `<tr>
                      <td class="text-left font-bold text-[#002850]">${esc(sp.label)}${shortSp}</td>
                      <td class="text-right">${d.PA}</td>
                      <td class="text-right">${fmtNum(d.IP,1)}</td>
                      <td class="text-right font-bold">${d.ERA !== null && d.ERA !== undefined ? fmtNum(d.ERA,2) : "—"}</td>
                      <td class="text-right font-extrabold text-[#003B73]">${fmtNum(d.FIP,2)}</td>
                      <td class="text-right">${fmtNum(d.WHIP,2)}</td>
                      <td class="text-right">${fmtRate(d.AVG_against)}</td>
                      <td class="text-right font-bold">${fmtRate(d.OPS_against)}</td>
                      <td class="text-right">${fmtNum(d.K9,2)}</td>
                      <td class="text-right">${fmtNum(d.BB9,2)}</td>
                      <td class="text-right">${fmtNum(d.Strike_pct,1,"%")}</td>
                      <td class="text-right">${fmtNum(d.InZone_pct,1,"%")}</td>
                      <td class="text-right">${fmtNum(d.Whiff_pct,1,"%")}</td>
                      <td class="text-right">${fmtNum(d.Chase_pct,1,"%")}</td>
                    </tr>`;
                  }).join("")}
                </tbody>
              </table>
            </div>
          </div>`;
      }
    }

    // =========================================================================
    // 7B. BLOQUE B: BALANCE DE ROSTER Y GRÁFICAS COMPARATIVAS STATCAST
    // =========================================================================
    function renderRosterBalanceCard(teams, sdata) {
      const wrap = document.getElementById("overview-roster-balance-card");
      if (!wrap) return;
      const mode = state.rosterCompMode || "status";
      const metric = state.rosterCompMetric || (mode === "status" ? "OPS" : "ERA");
      const batters = (sdata.yaquis_batters || []).filter((b) => b.etapa === state.stage);
      const pitchers = (sdata.yaquis_pitchers || []).filter((p) => p.etapa === state.stage);
      const { key: sk } = activeSeasonData();

      let groups = [];
      let metricCfg = {};
      let summaryRows = [];

      if (mode === "status") {
        const mOptions = {
          OPS: { label: "OPS (Bateadores ≥10 PA)", fmt: (v) => fmtRate(v), higher: true },
          wRC_plus: { label: "wRC+ (Media LMP = 100)", fmt: fmtInt, higher: true },
          BB_pct: { label: "BB% (Disciplina)", fmt: (v) => fmtNum(v, 1, "%"), higher: true },
        };
        metricCfg = mOptions[metric] || mOptions.OPS;
        const statusMeta = [
          { key: "Nacional", label: "Nacionales", color: "#003B73" },
          { key: "Extranjero", label: "Extranjeros", color: "#D97706" },
          { key: "Novato", label: "Novatos", color: "#16A34A" },
        ];
        const getBatSplit = (b) => state.cond === "all" ? (b.splits?.all || {}) : (b.splits?.[state.cond] || {});
        const totalPA = batters.reduce((acc, b) => acc + (getBatSplit(b).PA || 0), 0);
        groups = statusMeta.map((sm) => {
          const items = [];
          let paTotal = 0, paQual = 0, opsSum = 0, wrcSum = 0;
          batters.forEach((b) => {
            const prof = getProfile(sk, b.player_id);
            if (prof.roster_status !== sm.key) return;
            const sp = getBatSplit(b);
            const pa = sp.PA || 0;
            paTotal += pa;
            if (pa < 10) return;
            paQual += pa;
            opsSum += (sp.OPS || 0) * pa;
            wrcSum += (sp.wRC_plus ?? 100) * pa;
            const val = sp[metric in mOptions ? metric : "OPS"];
            if (val !== null && val !== undefined) {
              items.push({ id: b.player_id, name: prof.full_name, val: Number(val), sub: `${pa} PA · ${prof.primary_position}` });
            }
          });
          summaryRows.push({
            label: sm.label, color: sm.color, n: items.length,
            share: totalPA ? `${Math.round(paTotal / totalPA * 100)}% PA` : "0% PA",
            statA: paQual ? `OPS ${fmtRate(opsSum / paQual)}` : "OPS —",
            statB: paQual ? `wRC+ ${Math.round(wrcSum / paQual)}` : "wRC+ —",
          });
          return { ...sm, items };
        });
      } else {
        const mOptions = {
          ERA: { label: "ERA (Efectividad · ≥3 IP)", fmt: (v) => fmtNum(v, 2), higher: false },
          FIP: { label: "FIP (Periféricos)", fmt: (v) => fmtNum(v, 2), higher: false },
          K9: { label: "Ponches por 9 IP (K/9)", fmt: (v) => fmtNum(v, 2), higher: true },
        };
        metricCfg = mOptions[metric] || mOptions.ERA;
        const roleMeta = [
          { key: "Abridor", label: "Abridores", color: "#003B73" },
          { key: "Bullpen", label: "Bullpen / Relevistas", color: "#0072B2" },
        ];
        const totalIP = pitchers.reduce((acc, p) => acc + (p.IP || 0), 0);
        groups = roleMeta.map((rm) => {
          const items = [];
          let ipTotal = 0, ipQual = 0, eraSum = 0, fipSum = 0;
          pitchers.forEach((p) => {
            if (p.rol !== rm.key) return;
            const ip = p.IP || 0;
            ipTotal += ip;
            if (ip < 3) return;
            ipQual += ip;
            const prof = getProfile(sk, p.player_id);
            eraSum += (p.ERA ?? 0) * ip;
            fipSum += (p.FIP ?? 0) * ip;
            const val = p[metric in mOptions ? metric : "ERA"];
            if (val !== null && val !== undefined) {
              items.push({ id: p.player_id, name: prof.full_name, val: Number(val), sub: `${fmtNum(ip, 1)} IP · ${prof.roster_status}` });
            }
          });
          summaryRows.push({
            label: rm.label, color: rm.color, n: items.length,
            share: totalIP ? `${Math.round(ipTotal / totalIP * 100)}% IP` : "0% IP",
            statA: ipQual ? `ERA ${fmtNum(eraSum / ipQual, 2)}` : "ERA —",
            statB: ipQual ? `FIP ${fmtNum(fipSum / ipQual, 2)}` : "FIP —",
          });
          return { ...rm, items };
        });
      }

      const metricOpts = mode === "status"
        ? [["OPS", "OPS"], ["wRC_plus", "wRC+"], ["BB_pct", "BB%"]]
        : [["ERA", "ERA"], ["FIP", "FIP"], ["K9", "K/9"]];

      const boxSvg = buildBoxplotSwarmSVG({
        groups,
        metricLabel: metricCfg.label,
        fmt: metricCfg.fmt,
        higherIsBetter: metricCfg.higher,
        height: 255,
      });

      const condTag = (mode === "status" && state.cond !== "all") ? ` · ${COND_LABELS[state.cond]}` : "";
      wrap.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span class="jersey-ribbon bg-[#0072B2] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>BALANCE ESTRUCTURAL DEL ROSTER</span></span>
            <h2 class="text-base font-extrabold text-[#002850] mt-1">Comparativo de Producción Interna (${esc(STAGE_LABELS[state.stage])}${esc(condTag)})</h2>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-rcmode="status" class="rc-mode-btn px-2.5 py-1 ${mode === "status" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Nac · Ext · Nov</button>
              <button data-rcmode="pitchrole" class="rc-mode-btn px-2.5 py-1 ${mode === "pitchrole" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Abridores · Bullpen</button>
            </div>
            <select id="sel-rc-metric" class="text-xs font-bold text-[#003B73] bg-slate-50 border border-slate-300 rounded px-2.5 py-1">
              ${metricOpts.map(([k, l]) => `<option value="${k}" ${(metric === k) ? "selected" : ""}>${l}</option>`).join("")}
            </select>
          </div>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          <div class="lg:col-span-4 space-y-2.5">
            ${summaryRows.map((sr) => `
              <div class="border border-slate-200 rounded-lg p-3 bg-slate-50/70 flex items-center justify-between gap-2" style="border-left: 4px solid ${sr.color}">
                <div>
                  <div class="text-xs font-extrabold text-[#002850]">${esc(sr.label)} <span class="font-code text-slate-500">(n=${sr.n})</span></div>
                  <div class="text-[11px] font-bold text-slate-600 mt-0.5 font-code">${esc(sr.statA)} · ${esc(sr.statB)}</div>
                </div>
                <span class="text-[11px] font-extrabold px-2 py-0.5 rounded bg-white border border-slate-200 text-[#003B73] font-code">${esc(sr.share)}</span>
              </div>
            `).join("")}
          </div>
          <div class="lg:col-span-8">${boxSvg}</div>
        </div>`;

      bindComparativeTooltips(wrap);
      wrap.querySelectorAll(".rc-mode-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.rosterCompMode = b.dataset.rcmode;
          state.rosterCompMetric = state.rosterCompMode === "status" ? "OPS" : "ERA";
          renderRosterBalanceCard(teams, sdata);
        });
      });
      document.getElementById("sel-rc-metric")?.addEventListener("change", (e) => {
        state.rosterCompMetric = e.target.value;
        renderRosterBalanceCard(teams, sdata);
      });
    }

    function renderBattingComparativeCharts(rows, sdata, sk) {
      const wrap = document.getElementById("batting-comparative-charts");
      if (!wrap) return;
      const chart = state.batCompChart || "scatter";
      const tb = sdata.team_benchmarks?.[state.stage] || {};
      const yaq = (tb.teams || []).find((t) => t.team_id === 680) || {};
      const statusCol = { Nacional: "#003B73", Extranjero: "#D97706", Novato: "#16A34A", "Sin Registro": "#64748B" };
      const handCol = { R: "#003B73", L: "#0072B2", S: "#D97706", SIN_DATO: "#64748B" };

      let bodyHtml = "";
      let controlsHtml = "";

      if (chart === "scatter") {
        const sm = state.batScatterMode || "disc";
        controlsHtml = `
          <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
            <button data-bsc="disc" class="bsc-mode-btn px-2.5 py-1 ${sm === "disc" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Disciplina: K% vs BB%</button>
            <button data-bsc="power" class="bsc-mode-btn px-2.5 py-1 ${sm === "power" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Contacto vs Poder: ISO vs AVG</button>
          </div>`;

        const pts = rows.map((r) => {
          const xVal = sm === "disc" ? r.K_pct : r.AVG;
          const yVal = sm === "disc" ? r.BB_pct : r.ISO;
          if (xVal === null || xVal === undefined || yVal === null || yVal === undefined) return null;
          return {
            name: r.name, vol: r.PA || 1, x: Number(xVal), y: Number(yVal),
            color: statusCol[r.prof?.roster_status] || "#003B73",
            tip: `<strong>${esc(r.name)}</strong> (${esc(r.prof?.roster_status)} · ${r.PA} PA)<br>${sm === "disc" ? `K%: <b>${fmtNum(r.K_pct,1,"%")}</b> · BB%: <b>${fmtNum(r.BB_pct,1,"%")}</b>` : `AVG: <b>${fmtRate(r.AVG)}</b> · ISO: <b>${fmtRate(r.ISO)}</b>`}<br>OPS: <b>${fmtRate(r.OPS)}</b> · wRC+: <b>${fmtInt(r.wRC_plus)}</b>`,
          };
        }).filter(Boolean);

        bodyHtml = buildStatcastScatterSVG({
          points: pts,
          xLabel: sm === "disc" ? "Tasa de Ponches K% (→ Menor K% = Mejor contacto)" : "Promedio de Bateo AVG (→ Mejor contacto)",
          yLabel: sm === "disc" ? "Tasa de Boletos BB% (↑ Disciplina)" : "Poder Aislado ISO (↑ Extrabases)",
          xAvg: sm === "disc" ? yaq.K_pct : yaq.AVG,
          yAvg: sm === "disc" ? yaq.BB_pct : yaq.ISO,
          invertX: sm === "disc",
          invertY: false,
          fmtX: sm === "disc" ? (v) => `${v.toFixed(1)}%` : (v) => fmtRate(v),
          fmtY: sm === "disc" ? (v) => `${v.toFixed(1)}%` : (v) => fmtRate(v),
        });
      } else if (chart === "boxplot") {
        const bg = state.batBoxGroup || "status";
        const bm = state.batBoxMetric || "OPS";
        const mMeta = {
          OPS: { label: "OPS", fmt: (v) => fmtRate(v), higher: true },
          wRC_plus: { label: "wRC+", fmt: fmtInt, higher: true },
          BB_pct: { label: "BB%", fmt: (v) => fmtNum(v, 1, "%"), higher: true },
          K_pct: { label: "K%", fmt: (v) => fmtNum(v, 1, "%"), higher: false },
        }[bm] || { label: "OPS", fmt: (v) => fmtRate(v), higher: true };

        controlsHtml = `
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-bbgrp="status" class="bbg-btn px-2.5 py-1 ${bg === "status" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Por Estatus</button>
              <button data-bbgrp="bat_side" class="bbg-btn px-2.5 py-1 ${bg === "bat_side" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Por Mano</button>
            </div>
            <select id="sel-bat-box-metric" class="text-xs font-bold text-[#003B73] bg-slate-50 border border-slate-300 rounded px-2 py-1">
              <option value="OPS" ${bm === "OPS" ? "selected" : ""}>OPS</option>
              <option value="wRC_plus" ${bm === "wRC_plus" ? "selected" : ""}>wRC+</option>
              <option value="BB_pct" ${bm === "BB_pct" ? "selected" : ""}>BB%</option>
              <option value="K_pct" ${bm === "K_pct" ? "selected" : ""}>K%</option>
            </select>
          </div>`;

        const defs = bg === "status"
          ? [
              { key: "Nacional", label: "Nacionales", color: "#003B73" },
              { key: "Extranjero", label: "Extranjeros", color: "#D97706" },
              { key: "Novato", label: "Novatos", color: "#16A34A" },
            ]
          : [
              { key: "R", label: "Derechos (R)", color: "#003B73" },
              { key: "L", label: "Zurdos (L)", color: "#0072B2" },
              { key: "S", label: "Ambidiestros (S)", color: "#D97706" },
            ];
        const groups = defs.map((d) => ({
          ...d,
          items: rows.filter((r) => (bg === "status" ? r.prof?.roster_status : r.prof?.bat_side) === d.key && r[bm] !== null && r[bm] !== undefined)
            .map((r) => ({ id: r.player_id, name: r.name, val: Number(r[bm]), sub: `${r.PA} PA · ${r.prof?.primary_position}` })),
        }));
        bodyHtml = buildBoxplotSwarmSVG({ groups, metricLabel: mMeta.label, fmt: mMeta.fmt, higherIsBetter: mMeta.higher, height: 280 });
      } else {
        // Diverging wRC+ bars vs 100 LMP
        const ranked = [...rows].filter((r) => r.wRC_plus !== null && r.wRC_plus !== undefined).sort((a, b) => b.wRC_plus - a.wRC_plus).slice(0, 16);
        if (!ranked.length) {
          bodyHtml = `<div class="text-xs text-slate-500 py-8 text-center">Sin jugadores bajo el filtro mínimo de PA para comparar wRC+.</div>`;
        } else {
          const maxDev = Math.max(40, ...ranked.map((r) => Math.abs(r.wRC_plus - 100))) * 1.15;
          const W = 720, rowH = 22, pL = 138, pR = 44, pT = 26, pB = 18;
          const H = pT + pB + ranked.length * rowH;
          const midX = pL + (W - pL - pR) / 2;
          const sx = (v) => midX + ((v - 100) / maxDev) * ((W - pL - pR) / 2);
          let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full h-auto bg-slate-50/70 rounded-lg border border-slate-200 select-none">`;
          svg += `<line x1="${midX.toFixed(1)}" y1="${pT - 6}" x2="${midX.toFixed(1)}" y2="${H - pB}" stroke="#002850" stroke-width="1.6" stroke-dasharray="4 3"/>`;
          svg += `<text x="${midX.toFixed(1)}" y="14" text-anchor="middle" font-size="10" font-weight="800" fill="#002850">Media LMP (100 wRC+)</text>`;
          ranked.forEach((r, i) => {
            const yy = pT + i * rowH;
            const xv = sx(r.wRC_plus);
            const isPos = r.wRC_plus >= 100;
            const bx = isPos ? midX : xv;
            const bw = Math.max(2, Math.abs(xv - midX));
            const col = r.wRC_plus >= 120 ? "#E6392F" : (isPos ? "#0072B2" : "#64748B");
            svg += `<text x="${pL - 6}" y="${yy + 14.5}" text-anchor="end" font-size="10.5" font-weight="700" fill="#0F172A">${esc(r.name.slice(0, 20))} (${r.PA})</text>`;
            svg += `<rect class="comp-pt cursor-pointer" x="${bx.toFixed(1)}" y="${yy + 4}" width="${bw.toFixed(1)}" height="13" rx="3" fill="${col}" fill-opacity="0.88" data-tip="${esc(`<strong>${esc(r.name)}</strong> (${r.PA} PA)<br>wRC+: <b>${fmtInt(r.wRC_plus)}</b> · OPS: <b>${fmtRate(r.OPS)}</b>`)}"/>`;
            svg += `<text x="${(isPos ? xv + 5 : xv - 5).toFixed(1)}" y="${yy + 14.5}" text-anchor="${isPos ? "start" : "end"}" font-size="10" font-weight="800" fill="${col}" font-family="Consolas, monospace">${fmtInt(r.wRC_plus)}</text>`;
          });
          svg += `</svg>`;
          bodyHtml = svg;
        }
      }

      let batLegendHtml = `
        <span class="text-[#003B73]">● Nacional</span>
        <span class="text-amber-600">● Extranjero</span>
        <span class="text-emerald-600">● Novato</span>
        <span class="text-slate-400 font-normal">· Tamaño proporcional a PA</span>`;
      if (chart === "boxplot" && (state.batBoxGroup || "status") === "bat_side") {
        batLegendHtml = `
          <span class="text-[#003B73]">● Derechos (R)</span>
          <span class="text-[#0072B2]">● Zurdos (L)</span>
          <span class="text-amber-600">● Ambidiestros (S)</span>
          <span class="text-slate-400 font-normal">· ◆ Media · Línea = Mediana</span>`;
      } else if (chart === "boxplot") {
        batLegendHtml = `
          <span class="text-[#003B73]">● Nacional</span>
          <span class="text-amber-600">● Extranjero</span>
          <span class="text-emerald-600">● Novato</span>
          <span class="text-slate-400 font-normal">· ◆ Media · Línea = Mediana</span>`;
      } else if (chart === "wrc") {
        batLegendHtml = `
          <span class="text-[#E6392F]">■ Élite (wRC+ ≥ 120)</span>
          <span class="text-[#0072B2]">■ Sobre Media (100–119)</span>
          <span class="text-slate-500">■ Debajo de Media (&lt;100 LMP)</span>`;
      }

      wrap.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>ANÁLISIS COMPARATIVO OFENSIVO</span></span>
            <h2 class="text-base font-extrabold text-[#002850] mt-1">Gráficas Statcast del Lineup (Mín. ${state.batMinPA} PA · ${esc(COND_LABELS[state.cond])})</h2>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-bcchart="scatter" class="bc-tab-btn px-2.5 py-1 ${chart === "scatter" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Dispersión</button>
              <button data-bcchart="boxplot" class="bc-tab-btn px-2.5 py-1 ${chart === "boxplot" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Boxplot + Swarm</button>
              <button data-bcchart="wrc" class="bc-tab-btn px-2.5 py-1 ${chart === "wrc" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Barras wRC+</button>
            </div>
            ${controlsHtml}
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-3 text-[11px] font-bold text-slate-600">
          ${batLegendHtml}
        </div>
        <div>${bodyHtml}</div>`;

      bindComparativeTooltips(wrap);
      wrap.querySelectorAll(".bc-tab-btn").forEach((b) => {
        b.addEventListener("click", () => { state.batCompChart = b.dataset.bcchart; renderBattingComparativeCharts(rows, sdata, sk); });
      });
      wrap.querySelectorAll(".bsc-mode-btn").forEach((b) => {
        b.addEventListener("click", () => { state.batScatterMode = b.dataset.bsc; renderBattingComparativeCharts(rows, sdata, sk); });
      });
      wrap.querySelectorAll(".bbg-btn").forEach((b) => {
        b.addEventListener("click", () => { state.batBoxGroup = b.dataset.bbgrp; renderBattingComparativeCharts(rows, sdata, sk); });
      });
      document.getElementById("sel-bat-box-metric")?.addEventListener("change", (e) => {
        state.batBoxMetric = e.target.value;
        renderBattingComparativeCharts(rows, sdata, sk);
      });
    }

    function renderPitchingComparativeCharts(pitchers, sdata, sk) {
      const wrap = document.getElementById("pitching-comparative-charts");
      if (!wrap) return;
      const chart = state.pitCompChart || "scatter";
      const tb = sdata.team_benchmarks?.[state.stage] || {};
      const yaq = (tb.teams || []).find((t) => t.team_id === 680) || {};
      const roleCol = { Abridor: "#003B73", Bullpen: "#0072B2" };
      const pool = pitchers.filter((p) => (p.IP || 0) >= Math.max(1, state.pitMinIP));

      let bodyHtml = "";
      let controlsHtml = "";

      if (chart === "scatter") {
        const sm = state.pitScatterMode || "cmd";
        controlsHtml = `
          <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
            <button data-psc="cmd" class="psc-mode-btn px-2.5 py-1 ${sm === "cmd" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">InZone% vs Whiff%</button>
            <button data-psc="erafip" class="psc-mode-btn px-2.5 py-1 ${sm === "erafip" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">ERA vs FIP</button>
          </div>`;
        const pts = pool.map((p) => {
          const xv = sm === "cmd" ? p.InZone_pct : p.FIP;
          const yv = sm === "cmd" ? p.Whiff_pct : p.ERA;
          if (xv === null || xv === undefined || yv === null || yv === undefined) return null;
          return {
            name: p.name, vol: p.IP || 1, x: Number(xv), y: Number(yv),
            color: roleCol[p.rol] || "#003B73",
            tip: `<strong>${esc(p.name)}</strong> (${esc(p.rol)} · ${fmtNum(p.IP,1)} IP)<br>${sm === "cmd" ? `InZone%: <b>${fmtNum(p.InZone_pct,1,"%")}</b> · Whiff%: <b>${fmtNum(p.Whiff_pct,1,"%")}</b>` : `ERA: <b>${fmtNum(p.ERA,2)}</b> · FIP: <b>${fmtNum(p.FIP,2)}</b> (Diff ${fmtNum((p.ERA ?? 0) - (p.FIP ?? 0), 2)})`}<br>K/9: <b>${fmtNum(p.K9,2)}</b> · BB/9: <b>${fmtNum(p.BB9,2)}</b>`,
          };
        }).filter(Boolean);

        bodyHtml = buildStatcastScatterSVG({
          points: pts,
          xLabel: sm === "cmd" ? "InZone% (Comando dentro de zona →)" : "FIP Independiente Defensa (→ Menor FIP = Mejor)",
          yLabel: sm === "cmd" ? "Whiff% (Swings fallidos ↑)" : "ERA Efectividad (↑ Mejor / Más baja)",
          xAvg: sm === "cmd" ? yaq.InZone_pct : yaq.FIP,
          yAvg: sm === "cmd" ? yaq.Whiff_pct : yaq.ERA,
          invertX: sm !== "cmd",
          invertY: sm !== "cmd",
          fmtX: sm === "cmd" ? (v) => `${v.toFixed(1)}%` : (v) => v.toFixed(2),
          fmtY: sm === "cmd" ? (v) => `${v.toFixed(1)}%` : (v) => v.toFixed(2),
          diagLine: sm !== "cmd",
          diagLabel: sm !== "cmd" ? "Línea ERA = FIP" : "",
        });
      } else if (chart === "boxplot") {
        const bg = state.pitBoxGroup || "rol";
        const bm = state.pitBoxMetric || "ERA";
        const mMeta = {
          ERA: { label: "ERA", fmt: (v) => fmtNum(v, 2), higher: false },
          FIP: { label: "FIP", fmt: (v) => fmtNum(v, 2), higher: false },
          K9: { label: "K/9", fmt: (v) => fmtNum(v, 2), higher: true },
          Whiff_pct: { label: "Whiff%", fmt: (v) => fmtNum(v, 1, "%"), higher: true },
          InZone_pct: { label: "InZone%", fmt: (v) => fmtNum(v, 1, "%"), higher: true },
        }[bm] || { label: "ERA", fmt: (v) => fmtNum(v, 2), higher: false };

        controlsHtml = `
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-pbgrp="rol" class="pbg-btn px-2.5 py-1 ${bg === "rol" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Abridor vs Bullpen</button>
              <button data-pbgrp="status" class="pbg-btn px-2.5 py-1 ${bg === "status" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">Por Estatus</button>
            </div>
            <select id="sel-pit-box-metric" class="text-xs font-bold text-[#003B73] bg-slate-50 border border-slate-300 rounded px-2 py-1">
              <option value="ERA" ${bm === "ERA" ? "selected" : ""}>ERA</option>
              <option value="FIP" ${bm === "FIP" ? "selected" : ""}>FIP</option>
              <option value="K9" ${bm === "K9" ? "selected" : ""}>K/9</option>
              <option value="Whiff_pct" ${bm === "Whiff_pct" ? "selected" : ""}>Whiff%</option>
              <option value="InZone_pct" ${bm === "InZone_pct" ? "selected" : ""}>InZone%</option>
            </select>
          </div>`;

        const defs = bg === "rol"
          ? [
              { key: "Abridor", label: "Abridores", color: "#003B73" },
              { key: "Bullpen", label: "Bullpen", color: "#0072B2" },
            ]
          : [
              { key: "Nacional", label: "Nacionales", color: "#003B73" },
              { key: "Extranjero", label: "Extranjeros", color: "#D97706" },
              { key: "Novato", label: "Novatos", color: "#16A34A" },
            ];
        const groups = defs.map((d) => ({
          ...d,
          items: pool.filter((p) => (bg === "rol" ? p.rol : p.prof?.roster_status) === d.key && p[bm] !== null && p[bm] !== undefined)
            .map((p) => ({ id: p.player_id, name: p.name, val: Number(p[bm]), sub: `${fmtNum(p.IP,1)} IP · ${p.rol}` })),
        }));
        bodyHtml = buildBoxplotSwarmSVG({ groups, metricLabel: mMeta.label, fmt: mMeta.fmt, higherIsBetter: mMeta.higher, height: 280 });
      } else {
        const bm = state.pitBarMode || "kbb";
        controlsHtml = `
          <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
            <button data-pbm="kbb" class="pbm-btn px-2.5 py-1 ${bm === "kbb" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">K/9 vs BB/9</button>
            <button data-pbm="erafip" class="pbm-btn px-2.5 py-1 ${bm === "erafip" ? "bg-[#003B73] text-white" : "bg-white text-slate-700"}">ERA vs FIP</button>
          </div>`;
        const topP = [...pool].sort((a, b) => (b.IP || 0) - (a.IP || 0)).slice(0, 14);
        if (!topP.length) {
          bodyHtml = `<div class="text-xs text-slate-500 py-8 text-center">Sin lanzadores bajo los filtros activos.</div>`;
        } else {
          const maxX = bm === "kbb"
            ? Math.max(10, ...topP.flatMap((p) => [p.K9 || 0, p.BB9 || 0])) * 1.15
            : Math.max(6, ...topP.flatMap((p) => [p.ERA || 0, p.FIP || 0])) * 1.15;
          const W = 720, rowH = 26, pL = 148, pR = 60, pT = 28, pB = 16;
          const H = pT + pB + topP.length * rowH;
          const sx = (v) => pL + (Math.max(0, v) / maxX) * (W - pL - pR);
          let svg = `<svg viewBox="0 0 ${W} ${H}" class="w-full h-auto bg-slate-50/70 rounded-lg border border-slate-200 select-none">`;
          svg += `<text x="${pL}" y="15" font-size="10" font-weight="800" fill="#003B73">${bm === "kbb" ? "■ K/9 (Dominio)" : "■ ERA Real"}</text>`;
          svg += `<text x="${pL + 130}" y="15" font-size="10" font-weight="800" fill="${bm === "kbb" ? "#E6392F" : "#0072B2"}">${bm === "kbb" ? "■ BB/9 (Control)" : "■ FIP (Esperado)"}</text>`;
          topP.forEach((p, i) => {
            const yy = pT + i * rowH;
            const v1 = bm === "kbb" ? (p.K9 ?? 0) : (p.ERA ?? 0);
            const v2 = bm === "kbb" ? (p.BB9 ?? 0) : (p.FIP ?? 0);
            svg += `<text x="${pL - 6}" y="${yy + 14.5}" text-anchor="end" font-size="10.5" font-weight="700" fill="#0F172A">${esc(p.name.slice(0, 19))} (${fmtNum(p.IP,1)})</text>`;
            svg += `<rect class="comp-pt cursor-pointer" x="${pL}" y="${yy + 3}" width="${Math.max(2, sx(v1) - pL).toFixed(1)}" height="9" rx="2" fill="#003B73" data-tip="${esc(`<strong>${esc(p.name)}</strong> (${fmtNum(p.IP,1)} IP)<br>${bm === "kbb" ? `K/9: <b>${fmtNum(v1,2)}</b> vs BB/9: <b>${fmtNum(v2,2)}</b>` : `ERA: <b>${fmtNum(v1,2)}</b> vs FIP: <b>${fmtNum(v2,2)}</b>`}`)}"/>`;
            svg += `<rect class="comp-pt cursor-pointer" x="${pL}" y="${yy + 13}" width="${Math.max(2, sx(v2) - pL).toFixed(1)}" height="8" rx="2" fill="${bm === "kbb" ? "#E6392F" : "#0072B2"}" fill-opacity="0.85" data-tip="${esc(`<strong>${esc(p.name)}</strong> (${fmtNum(p.IP,1)} IP)<br>${bm === "kbb" ? `K/9: <b>${fmtNum(v1,2)}</b> vs BB/9: <b>${fmtNum(v2,2)}</b>` : `ERA: <b>${fmtNum(v1,2)}</b> vs FIP: <b>${fmtNum(v2,2)}</b>`}`)}"/>`;
            const lblX = Math.max(sx(v1), sx(v2)) + 5;
            svg += `<text x="${lblX.toFixed(1)}" y="${yy + 14.5}" font-size="9.5" font-weight="800" fill="#334155" font-family="Consolas, monospace">${fmtNum(v1,2)} / ${fmtNum(v2,2)}</text>`;
          });
          svg += `</svg>`;
          bodyHtml = svg;
        }
      }

      let pitLegendHtml = `
        <span class="text-[#003B73]">● Abridor</span>
        <span class="text-[#0072B2]">● Bullpen / Relevista</span>
        <span class="text-slate-400 font-normal">· Tamaño proporcional a IP</span>`;
      if (chart === "boxplot" && (state.pitBoxGroup || "rol") === "status") {
        pitLegendHtml = `
          <span class="text-[#003B73]">● Nacional</span>
          <span class="text-amber-600">● Extranjero</span>
          <span class="text-emerald-600">● Novato</span>
          <span class="text-slate-400 font-normal">· ◆ Media · Línea = Mediana</span>`;
      } else if (chart === "boxplot") {
        pitLegendHtml = `
          <span class="text-[#003B73]">● Abridor</span>
          <span class="text-[#0072B2]">● Bullpen</span>
          <span class="text-slate-400 font-normal">· ◆ Media · Línea = Mediana</span>`;
      } else if (chart === "bars") {
        pitLegendHtml = (state.pitBarMode || "kbb") === "kbb"
          ? `<span class="text-[#003B73]">■ K/9 (Dominio)</span><span class="text-[#E6392F]">■ BB/9 (Control)</span>`
          : `<span class="text-[#003B73]">■ ERA Real</span><span class="text-[#0072B2]">■ FIP Esperado</span>`;
      }

      wrap.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span class="jersey-ribbon bg-[#003B73] text-white text-[10px] font-bold px-2 py-0.5 uppercase"><span>ANÁLISIS COMPARATIVO DEL STAFF</span></span>
            <h2 class="text-base font-extrabold text-[#002850] mt-1">Gráficas Statcast de Pitcheo (Mín. ${Math.max(1, state.pitMinIP)} IP · ${esc(STAGE_LABELS[state.stage])})</h2>
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <div class="flex rounded-md overflow-hidden border border-slate-300 text-xs font-bold">
              <button data-pcchart="scatter" class="pc-tab-btn px-2.5 py-1 ${chart === "scatter" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Dispersión</button>
              <button data-pcchart="boxplot" class="pc-tab-btn px-2.5 py-1 ${chart === "boxplot" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Boxplot + Swarm</button>
              <button data-pcchart="bars" class="pc-tab-btn px-2.5 py-1 ${chart === "bars" ? "bg-[#0072B2] text-white" : "bg-white text-slate-700"}">Barras Staff</button>
            </div>
            ${controlsHtml}
          </div>
        </div>
        <div class="flex flex-wrap items-center gap-3 text-[11px] font-bold text-slate-600">
          ${pitLegendHtml}
        </div>
        <div>${bodyHtml}</div>`;

      bindComparativeTooltips(wrap);
      wrap.querySelectorAll(".pc-tab-btn").forEach((b) => {
        b.addEventListener("click", () => { state.pitCompChart = b.dataset.pcchart; renderPitchingComparativeCharts(pitchers, sdata, sk); });
      });
      wrap.querySelectorAll(".psc-mode-btn").forEach((b) => {
        b.addEventListener("click", () => { state.pitScatterMode = b.dataset.psc; renderPitchingComparativeCharts(pitchers, sdata, sk); });
      });
      wrap.querySelectorAll(".pbg-btn").forEach((b) => {
        b.addEventListener("click", () => { state.pitBoxGroup = b.dataset.pbgrp; renderPitchingComparativeCharts(pitchers, sdata, sk); });
      });
      document.getElementById("sel-pit-box-metric")?.addEventListener("change", (e) => {
        state.pitBoxMetric = e.target.value;
        renderPitchingComparativeCharts(pitchers, sdata, sk);
      });
      wrap.querySelectorAll(".pbm-btn").forEach((b) => {
        b.addEventListener("click", () => { state.pitBarMode = b.dataset.pbm; renderPitchingComparativeCharts(pitchers, sdata, sk); });
      });
    }

    // =========================================================================
    // 8. SHELL SYNC, ALERTS & EVENT BINDING
    // =========================================================================
    function syncControlPills() {
      document.querySelectorAll(".bgroup-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.bgroup === state.benchGroup);
      });
      document.querySelectorAll(".spray-mode-btn").forEach((b) => {
        const on = b.dataset.spraymode === state.sprayMode;
        b.className = `spray-mode-btn px-2.5 py-1 ${on ? "bg-[#0072B2] text-white" : "bg-[#0B1320] text-slate-300 hover:text-white"}`;
      });
      document.querySelectorAll(".zone-mode-btn").forEach((b) => {
        const on = b.dataset.zonemode === state.zoneMode;
        b.className = `zone-mode-btn px-2.5 py-1 ${on ? "bg-[#0072B2] text-white" : "bg-[#0B1320] text-slate-300 hover:text-white"}`;
      });
      document.querySelectorAll(".pit-role-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.pitrole === state.pitRoleFilter);
      });
      document.querySelectorAll(".srole-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.srole === state.scoutRole);
      });
      document.querySelectorAll(".sstatus-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.sstatus === state.scoutStatus);
      });
    }

    function syncHeaderUI() {
      document.getElementById("sel-season").value = state.season;
      document.getElementById("sel-cond").value = state.cond;

      document.querySelectorAll(".stage-btn").forEach((b) => {
        b.classList.toggle("active", b.dataset.stage === state.stage);
      });
      document.querySelectorAll(".tab-btn").forEach((b) => {
        const isActive = b.dataset.tab === state.tab;
        b.classList.toggle("active", isActive);
        b.classList.toggle("text-slate-600", !isActive);
      });
      document.querySelectorAll(".module-pane").forEach((p) => {
        p.classList.toggle("hidden", p.id !== `tab-${state.tab}`);
      });

      syncControlPills();

      // Global context pill, LMP strip & alert banner
      const { key: sk } = activeSeasonData();
      renderHeaderClubsStrip(sk);
      const sLabel = state.season === "hist"
        ? "2025–26 + Histórico (21T)"
        : (sk === "2026" ? "2026–27 (YTD)" : "2025–26");
      document.getElementById("global-context-badge").innerHTML = `
        <span class="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-[#003B73] font-bold">${esc(sLabel)}</span>
        <span class="px-2 py-0.5 rounded bg-slate-100 border border-slate-200">${esc(STAGE_LABELS[state.stage])}</span>
        <span class="px-2 py-0.5 rounded bg-sky-50 border border-sky-200 text-sky-900">${esc(COND_LABELS[state.cond])}</span>
      `;

      const alertEl = document.getElementById("context-alert-banner");
      let msgs = [];
      if (state.season === "2026") {
        msgs.push("Temporada 2026–27 en curso (YTD hasta el 15 de noviembre de 2026): muestra activa de 1ra Vuelta; 2da Vuelta y Playoffs aún por jugarse.");
      }
      if (state.stage === "playoffs" && state.season !== "2026") {
        msgs.push("Aviso estadístico: En Playoffs 2025–26 Yaquis acumuló n=4 juegos; interpreta tasas de porcentaje y OAA considerando la variabilidad de muestra corta.");
      }
      if (msgs.length) {
        alertEl.className = "rounded-lg border border-amber-300 bg-amber-50 text-amber-900 px-4 py-2 text-xs font-semibold flex items-center justify-between gap-2";
        alertEl.innerHTML = `<span>⚠ ${esc(msgs.join(" "))}</span>`;
      } else {
        alertEl.className = "hidden";
        alertEl.innerHTML = "";
      }
    }

    function renderAll() {
      hideTooltip();
      syncHeaderUI();
      renderRivalMatchupBanner();
      if (state.tab === "overview") renderOverview();
      else if (state.tab === "batting") renderBattingModule();
      else if (state.tab === "pitching") renderPitchingModule();
      else if (state.tab === "scouting") renderScoutingModule();
    }

    function bindEvents() {
      document.getElementById("sel-season").addEventListener("change", (e) => {
        state.season = e.target.value;
        if (state.season === "hist") {
          state.tab = "overview";
          renderAll();
          setTimeout(() => {
            document.getElementById("historical-section")?.scrollIntoView({ behavior: "smooth" });
          }, 60);
          return;
        }
        renderAll();
      });

      document.querySelectorAll(".stage-btn").forEach((b) => {
        b.addEventListener("click", () => { state.stage = b.dataset.stage; renderAll(); });
      });
      document.getElementById("sel-cond").addEventListener("change", (e) => {
        state.cond = e.target.value;
        renderAll();
      });
      document.querySelectorAll(".tab-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.tab = b.dataset.tab;
          if (state.tab !== "overview" && state.season === "hist") state.season = "2025";
          renderAll();
        });
      });

      document.getElementById("sel-stage-metric").addEventListener("change", (e) => {
        state.stageMetric = e.target.value;
        renderOverview();
      });
      document.querySelectorAll(".bgroup-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.benchGroup = b.dataset.bgroup;
          const defSorts = {
            standings: { col: "Pts_Total", dir: -1 },
            offense: { col: "wRC_plus", dir: -1 },
            pitching: { col: "ERA", dir: 1 },
            defense: { col: "DER_pct", dir: -1 },
          };
          state.benchSort = defSorts[state.benchGroup] || { col: "Pts_Total", dir: -1 };
          syncControlPills();
          renderOverview();
        });
      });
      document.getElementById("sel-hist-metric").addEventListener("change", (e) => {
        state.histMetric = e.target.value;
        renderHistoricalSection();
      });

      // Batting & Spray events
      document.getElementById("inp-min-pa").addEventListener("input", (e) => {
        state.batMinPA = Math.max(0, Number(e.target.value || 0));
        renderBattingModule();
      });
      document.getElementById("inp-bat-search").addEventListener("input", (e) => {
        state.batSearch = e.target.value;
        renderBattingModule();
      });
      document.querySelectorAll(".spray-mode-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.sprayMode = b.dataset.spraymode;
          syncControlPills();
          renderBattingModule();
        });
      });
      document.getElementById("sel-spray-player").addEventListener("change", (e) => {
        state.sprayPlayer = e.target.value;
        renderBattingModule();
      });
      document.getElementById("sel-spray-res").addEventListener("change", (e) => {
        state.sprayRes = e.target.value;
        renderBattingModule();
      });
      document.getElementById("sel-spray-traj").addEventListener("change", (e) => {
        state.sprayTraj = e.target.value;
        renderBattingModule();
      });

      // Pitching & 2D Zone events
      document.querySelectorAll(".pit-role-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.pitRoleFilter = b.dataset.pitrole;
          syncControlPills();
          renderPitchingModule();
        });
      });
      document.getElementById("inp-min-ip")?.addEventListener("input", (e) => {
        state.pitMinIP = Math.max(0, Number(e.target.value || 0));
        renderPitchingModule();
      });
      document.getElementById("inp-pit-search").addEventListener("input", (e) => {
        state.pitSearch = e.target.value;
        renderPitchingModule();
      });
      document.querySelectorAll(".zone-mode-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.zoneMode = b.dataset.zonemode;
          syncControlPills();
          renderPitchingModule();
        });
      });
      document.getElementById("sel-zone-pitcher").addEventListener("change", (e) => {
        state.zonePitcher = e.target.value;
        renderPitchingModule();
      });
      document.getElementById("sel-zone-batside").addEventListener("change", (e) => {
        state.zoneBatSide = e.target.value;
        renderPitchingModule();
      });
      document.getElementById("sel-zone-call").addEventListener("change", (e) => {
        state.zoneCall = e.target.value;
        renderPitchingModule();
      });
      document.getElementById("sel-zone-count")?.addEventListener("change", (e) => {
        state.zoneCount = e.target.value;
        renderPitchingModule();
      });

      // Scouting events
      document.getElementById("inp-scout-search").addEventListener("input", (e) => {
        state.scoutSearch = e.target.value;
        renderScoutingModule();
      });
      document.querySelectorAll(".srole-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.scoutRole = b.dataset.srole;
          syncControlPills();
          renderScoutingModule();
        });
      });
      document.querySelectorAll(".sstatus-btn").forEach((b) => {
        b.addEventListener("click", () => {
          state.scoutStatus = b.dataset.sstatus;
          syncControlPills();
          renderScoutingModule();
        });
      });
    }

    initBrandLogos();
    bindEvents();
    renderAll();
  })();
  </script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Compila el Dashboard Front Office Yaquis como HTML autocontenido.")
    parser.add_argument(
        "--mirror",
        default=os.environ.get("YAQUIS_MIRROR_HTML_PATH", ""),
        help="Ruta opcional para escribir una copia espejo adicional del HTML compilado.",
    )
    args = parser.parse_args()

    if not PAYLOAD_PATH.exists():
        raise FileNotFoundError(f"No se encontró el payload JSON en {PAYLOAD_PATH}")
    if not TAILWIND_CSS_PATH.exists():
        raise FileNotFoundError(
            f"No se encontró el CSS estático compilado en {TAILWIND_CSS_PATH}. Ejecuta primero Tailwind CLI."
        )

    raw_json = PAYLOAD_PATH.read_text(encoding="utf-8")
    raw_css = TAILWIND_CSS_PATH.read_text(encoding="utf-8")
    # Escape closing script/style tags defensively when embedding inline
    safe_json = raw_json.replace("</", "<\\/")
    safe_css = raw_css.replace("</style", "<\\/style")

    final_html = HTML_TEMPLATE.replace("__TAILWIND_CSS__", safe_css).replace("__PAYLOAD_JSON__", safe_json)
    OUT_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML_PATH.write_text(final_html, encoding="utf-8")

    size_kb = OUT_HTML_PATH.stat().st_size / 1024.0
    print(f"SPA compilada correctamente: {OUT_HTML_PATH} ({size_kb:.1f} KB)")

    if args.mirror:
        mirror_path = Path(args.mirror)
        mirror_path.parent.mkdir(parents=True, exist_ok=True)
        mirror_path.write_text(final_html, encoding="utf-8")
        print(f"Copia espejo generada: {mirror_path} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
