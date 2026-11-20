# Yaquis de Obregón (LMP) — Auditoría Estadística Profunda y Blueprint de Storytelling & Dashboard

> **Alcance:** Análisis de solo lectura sobre `data/yaquis_lmp.db` (vista `v_valid_games`) cubriendo el contexto histórico **2006–2026**, la temporada **2025–26** (`1ra Vuelta <= 2025-11-23`, `2da Vuelta >= 2025-11-24`, `Playoffs`), el cruce ante **Águilas de Mexicali (`team_id=673`)**, y el arranque **2026–27 YTD** (al `2026-11-15`).
>
> **Principio rector:** Todas las cifras, nombres de jugadores, `game_pk` y pruebas estadísticas provienen directamente de la ejecución verificada de `deep_analysis.py`. Se distinguen explícitamente los hallazgos confirmados, matizados y refutados, junto con las limitaciones de muestra (`n = 4` juegos en Playoffs 2025–26).

---

## 1. Validación de Datos y Hallazgos Críticos de Calidad (Audit)

### 1.1 Cobertura general de `yaquis_lmp.db`
| Tabla | Filas totales | Notas de validación |
|---|---:|---|
| `teams` | 13 | Incluye `680` (Yaquis), `673` (Mexicali), `58` (TBD Playoffs), e ID `674` resuelto por temporada en `v_valid_games` (`<=2013` Algodoneros / `>=2014` Charros). |
| `games` | 7,038 | `v_valid_games` filtra `is_completed=1`, marcadores no nulos y excluye cancelados/pospuestos sin PBP. |
| `players` | 2,708 | Catálogo limpio enriquecido con perfil scout (`birth_country`, `birth_city`, `birth_date`, `height`, `weight`, `mlb_debut_date`, `headshot_url`). |
| `batting_game_stats` | 143,586 | Estadísticas oficiales de bateo por juego y jugador. |
| `pitching_game_stats` | 66,453 | Estadísticas oficiales de pitcheo (`games_started`, `outs`, `pitches_thrown`, `IR/IRS`). |
| `fielding_game_stats` | 209,944 | Estadísticas defensivas por posición (`LF`, `CF`, `RF`, etc.). |
| `plate_appearances` | 514,065 | Play-by-play con tipo de evento, trayectoria, dureza y coordenadas 2D de batazo. |
| `pitches` | 1,688,238 | Secuencia pitch-by-pitch con conteo, llamada y coordenadas 2D. |

### 1.2 Cobertura 2025–26 y 2026–27 YTD
- **Temporada 2025–26 (`season = 2025`):** `375` juegos válidos en `v_valid_games`: `340` de temporada regular (`2025-10-15` a `2025-12-30`; `339` `Final` + `1` `Postponed` con `has_pbp=1`) y `35` de playoffs (`2026-01-01` a `2026-01-25`: `22` tipo `D`, `9` tipo `L`, `4` tipo `W`). **100% de los juegos tienen PBP (`has_pbp = 1`)**.
  - Total PA 2025–26: `29,213` (`20,913` con `hit_coord_x/y`, `71.6%`).
  - Total pitcheos 2025–26: `111,352` (`111,264` con `pitch_x/y`, `99.9%`).
- **Temporada 2026–27 YTD (`season = 2026`):** `145` juegos válidos (`2026-10-13` a `2026-11-15`), `100%` PBP, `11,205` PA (`69.9%` hit XY) y `42,863` pitcheos (`99.9%` pitch XY). Yaquis marcha `15-14` (`.517`, `29 JJ`, `139 CF`, `119 CC`, `+20` Dif, `Pyth W% = .571`, `Luck = -0.054`).

### 1.3 Cuatro salvedades técnicas obligatorias antes de modelar o graficar
1. **Registro parcial de pitcheos en `2006–2010`:** Aunque cada campaña `2006–2010` tiene `304–305` juegos y `22,867–23,795` PA, la tabla `pitches` solo contiene `37,513–38,811` filas por año (~`1.6` pitcheos/PA), saltando abruptamente en `2011` a `87,308` pitcheos (~`3.7` pitcheos/PA, nivel estable `2011–2026`). **Regla:** excluir `2006–2010` de cualquier métrica de `Strike%`, `FPS%`, conteos o carga acumulada de pitcheos.
2. **Escala real de `pitches.pitch_x` y `pitch_y` (Coordenadas Gameday Canvas vs Pies Statcast):**
   - `sz_top` (`media = 3.194`, rango `2.898–3.600`) y `sz_bot` (`media = 1.595`, rango `1.380–1.755`) están en **pies**.
   - En contraste, `pitch_x` (`media = 109.26`, `DE = 27.51`, `min = 10.02`, `max = 216.00`) y `pitch_y` (`media = 155.27`, `DE = 32.01`, `min = 31.58`, `max = 253.51`) son **coordenadas de lienzo 2D de MLB Gameday (píxeles ~0–250)** capturadas manualmente por el anotador oficial (sin tracking óptico Hawk-Eye/Statcast de velocidad o *spin*).
   - Calibrando empíricamente los percentiles `2%–98%` de strikes cantados en 2025–26, la zona de strike en este lienzo corresponde a **`X = [82.0, 134.3]`, `Y = [115.9, 182.8]`, centro `(107.9, 154.1)`**. Cualquier gráfico que superponga una caja `[-0.83, +0.83]` sobre `pitch_x/y` sería erróneo.
3. **Etiqueta por defecto en `plate_appearances.hit_hardness`:** Entre `91.9%` (Yaquis Playoffs) y `98.4%` (LMP Otros 2da Vuelta) de los batazos están marcados como `"medium"`. Solo `0.6%–4.4%` figuran como `"hard"` y `0.9%–3.7%` como `"soft"`. Refleja una clasificación manual conservadora del anotador y no velocidad de salida objetiva.
4. **Corrección y revalidación de `plate_appearances.is_risp` (Resuelto en `scraper/parser.py` y `enrich_and_fix_risp.py`):**
   - El análisis inicial detectó promedios imposibles (`.540–.556` AVG con `is_risp=1`) porque `matchup.splits.menOnBase` en `statsapi.mlb.com` refleja el estado **post-turno**, no pre-turno.
   - Se corrigió el parser para derivar `is_risp` del `menOnBase` del turno anterior dentro del mismo medio inning y se recalculó sobre `520` juegos (`2025` y `2026`).
   - **Resultado revalidado (Yaquis 2025–26):**
     - *1ra Vuelta:* `.264` sin RISP (`213/808`) vs **`.247` con RISP** (`80/324, 119 RBI`).
     - *2da Vuelta:* `.238` sin RISP (`189/794`) vs **`.271` con RISP** (`73/269, 108 RBI`).
     - ***Playoffs (`n=4` JJ):* `.282` sin RISP (`33/117`) vs `.125` con RISP (`4/32, 1 HR, 6 BB, 7 RBI`).** Confirmado: Yaquis embasó corredores normalmente, pero colapsó en situación *clutch* con corredores en posición de anotar.

---

## 2. Hallazgos Estadísticos Verificados (Temporada 2025–26 y Contexto Histórico)

### Resumen de Verificación de Hipótesis

| Hipótesis | Veredicto | Evidencia principal observada | Confianza / Límite muestral |
|---|---|---|---|
| **H1. Desplome ofensivo / SLG `.322` en Playoffs** | **Confirmada con matiz** (falta de poder crudo y caída de líderes, **no** exceso de contacto débil) | OPS baja `0.703 (V1) -> 0.681 (V2) -> 0.667 (PO)`; SLG `.322`, ISO `.074`, solo `6 XBH` (`3 2B, 1 3B, 2 HR`) y `0 HR` de bateadores derechos en `75 PA`. `Hard-Hit%` en PO (`4.4%`) no cayó vs Regular (`2.15%`, Fisher `p=0.126`). | `n = 4 JJ` (`175 PA`, `136 BIP`); pruebas de conversión BIP no significativas (`p >= 0.367`). |
| **H2. Degradación de comando de pitcheo + fatiga acumulada** | **Confirmada (Factor primario)** | `BB/9` de abridores sube `3.67 -> 4.83 -> 6.64`; `Strike%` abridores cae `61.9% -> 60.3% -> 57.3%`. `InZone%` de Yaquis cae `-7.56 pp` (`55.14% -> 47.57%`, `p=0.0003`) y `SD_X` sube `26.72 -> 27.70 -> 32.02` (Levene `p<1e-5`). Cuatro abridores cargaron `782–1,190` pitcheos en Regular con fuerte uso dic 18–30. | Alta potencia por volumen de pitcheos (`n = 5,160 / 4,663 / 639` lanzamientos). |
| **H3. Debilidad defensiva en Jardín Izquierdo (`LF / '7'`)** | **Refutada como causa estructural** | En Regular, `DER%` en LF de Yaquis fue **`48.07%`** (`137/285`) vs **`46.75%`** del resto de LMP (`1,203/2,573`, `p=0.673`). En Playoffs `DER%` bajó a `42.9%` (`9/21`, `p=0.316` vs MEX; `p=0.644` vs Reg), con **0 errores** de Gaitán/Macías; el daño en LF incluyó **3 HR** (7 carreras) y 7 líneas limpias. | `n = 21 BIP` (excl. HR) en PO; IC Wilson `[24.5%, 63.5%]`. |
| **H4. Ventaja de localía y dominio H2H previo vs Mexicali** | **Confirmada en Regular / Revertida en juegos cerrados de PO** | Yaquis ganó `4-2` H2H en Regular (`2-1` casa, `2-1` visita) y fue `22-12` (`.647`, `3.03 ERA`) en casa. En PO perdió `0-4`, pero **3 de 4 juegos fueron por 1–2 carreras** (2 en extra innings en Obregón: 10 y 12 inn). | `n = 6 JJ` Reg vs `n = 4 JJ` PO. |
| **H5. Paradoja histórica 2006–2026** | **Confirmada** | `40-28` (`.588`) es la **3ra mejor campaña regular** en 21 años (detrás de `2019` `.667` y `2020` `.638`), superando en `%` a los 4 años de campeonato (`2007, 2010, 2011, 2012`), pero terminó en la única barrida `0-4` de 1ra ronda. | Serie histórica completa `2006–2025` (`15` temporadas con playoffs). |

---

### 2.1 Ofensiva y Calidad de Contacto (Equipo e Individual)

#### Evolución por etapa (2025–26)
| Etapa | Equipo | JJ | PA | R | R/G | AVG | OBP | SLG | OPS | ISO | BB% | K% | BABIP | SB / CS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **1ra Vuelta** | **Yaquis** | 35 | 1,328 | 146 | 4.17 | .260 | .346 | .357 | .703 | .097 | 10.0% | 15.3% | .306 | 50 / 18 |
| 1ra Vuelta | Mexicali | 35 | 1,368 | 145 | 4.14 | .257 | .352 | .357 | .709 | .100 | 11.7% | 16.7% | .303 | 51 / 10 |
| 1ra Vuelta | LMP Total | 350* | 13,654 | 1,569 | 4.48 | .256 | .344 | .371 | .715 | .115 | 10.5% | 16.8% | .299 | — |
| **2da Vuelta** | **Yaquis** | 33 | 1,241 | 148 | 4.48 | .247 | .330 | .351 | .681 | .104 | 10.0% | 14.0% | .280 | 26 / 6 |
| 2da Vuelta | Mexicali | 33 | 1,219 | 136 | 4.12 | .254 | .340 | .370 | .710 | .116 | 10.3% | 17.4% | .300 | 22 / 14 |
| 2da Vuelta | LMP Total | 330* | 12,636 | 1,492 | 4.52 | .260 | .349 | .372 | .721 | .112 | 10.7% | 15.7% | .299 | — |
| **Playoffs** | **Yaquis** | 4 | 175 | 12 | 3.00 | .248 | .345 | **.322** | **.667** | **.074** | 12.0% | **9.7%** | .269 | 6 / 1 |
| Playoffs | Mexicali | 9 | 374 | 36 | 4.00 | .248 | .346 | .360 | .706 | .112 | 13.4% | 12.8% | .264 | 6 / 2 |
| Playoffs | LMP Total | 70* | 2,815 | 327 | 4.67 | .258 | .348 | .374 | .722 | .116 | 10.9% | 14.1% | .286 | — |

*\*`team_games` en LMP Total; `R/G` calculado sobre juegos de equipo.*

#### Rotación ofensiva y splits individuales (`1ra Vuelta -> 2da Vuelta -> Playoffs`)
- **El desplome de la columna vertebral y las bajas de mitad de temporada:**
  - **Allen Córdoba** (`323 PA` totales): MVP de 1ra Vuelta (`.339/.451/.496`, `.947 OPS`, `16 SB` en `154 PA`), cayó abruptamente en 2da Vuelta (`.220/.303/.268`, `.571 OPS`, `0 HR` en `148 PA`) y no remontó en Playoffs (`.222/.263/.333`, `.596 OPS`, `0 BB` en `21 PA`).
  - **Riley Unroe**: tras `139 PA` aceptables en 1ra Vuelta (`.240/.336/.360`, `.696 OPS`), se hundió en 2da Vuelta a `.138/.271/.155` (`.426 OPS`, `75 PA`) y no jugó en Playoffs.
  - **Roberto Valenzuela**: sólido en 1ra (`.751 OPS`) y 2da Vuelta (`.792 OPS`, `.771` Regular), pero se apagó en Playoffs a `.188/.350/.188` (`.538 OPS`, `0 XBH` en `20 PA`).
  - **Victor Mendoza**: inverso en regular (`.581 OPS` en V1 → `.936 OPS` con `.342/.423/.513` en V2), pero en Playoffs bateó `.176/.263/.353` (`.616 OPS`, `1 HR` en `19 PA`).
  - **Bajas de roster tras 1ra Vuelta:** **Kyren Paris** (`.814 OPS`, `20.8% BB%` en `72 PA`) y **Andrew Navigato** (`.627 OPS`, `72 PA`) no regresaron para 2da Vuelta; **Miguel Guzmán** bajó de `113 PA` (V1) a `13 PA` (V2) y `0` en PO.
- **Quienes cargaron el ataque en Playoffs:**
  - **Sebastián Elizalde**: constante todo el año (`.749` → `.808` → **`.874 OPS`**, `.368/.400/.474`, `0 K` en `20 PA` de Playoffs).
  - **Juan Carlos Gamboa**: `.788 OPS` en Regular (`136 PA`) y **`.946 OPS`** en Playoffs (`.333/.529/.417`, `5 BB` en `18 PA`).
  - **Leobaldo Piña** (`.400/.455/.400`, `.855 OPS` en `11 PA`) y **Antonis Macías** (`3/6`, `.500` en `6 PA`), más el refuerzo **Ramiro Peña** (`.222/.300/.389`, `1 HR`, `20 PA`).
- **Splits por mano (`bat_side` vs `pitch_hand`):**
  - En Playoffs, Yaquis enfrentó **exclusivamente pitcheo derecho (`175/175 PA vs RHP`)**. Los bateadores derechos de Obregón batearon apenas **`.226/.333/.258` (`.591 OPS`, `0 HR` en `75 PA`)**, mientras los zurdos produjeron **`.264/.354/.368` (`.721 OPS`, `2 HR` en `100 PA`)**.
  - A pesar de mantener una élite de contacto y paciencia en Playoffs (`9.7% K%`, `12.0% BB%`), sin poder derecho la ofensiva quedó reducida a **2 carreras en los últimos 18 innings** en Mexicali (`1-2` y `1-4`).

#### Calidad de contacto (¿Mala suerte o falta de impacto?)
- **Dureza de batazo (`hit_hardness`):** En Playoffs, Yaquis tuvo `4.4%` de contacto `"hard"` (`6/136`, IC Wilson `[2.0%, 9.3%]`) vs `2.15%` en Regular (`41/1903`, Fisher `p=0.126`) y superior al `0.72%` (`2/276`) de Mexicali (`p_raw=0.0177`, `n=6 vs 2` muy pequeño). En bolas `"hard"` batearon `.500` (`3/6`) en PO vs `.293` (`12/41`) en Regular (`p=0.367`). En bolas `"medium"` (`91.9%` de sus BIP), batearon `.256` (`.344 SLG`) vs `.294` en Regular (`Chi2 p=0.367`).
- **Trayectoria (`hit_trajectory`):** `Line-Drive%` subió levemente a `20.6%` (`28/136`) vs `18.1%` en Regular (`p=0.474`), pero su AVG en líneas cayó de **`.724` (V1) y `.661` (V2) a `.536` (`15/28`)** y en elevados (`fly_ball`, `25.0%` de BIP) cayó a **`.118` (`4/34`, `10 TB`)** frente a `.185–.191` en Regular.
- **Conclusión H1:** No hubo colapso mecánico hacia contacto débil (`popups`/`rolas`), sino una combinación de **bajo techo de poder derecho de todo el año** (`.097–.104` ISO regular → `.074` en PO) y **varianza desfavorable moderada** en líneas y elevados dentro de una muestra corta (`n = 136 BIP`), donde las diferencias de conversión caen dentro de la variabilidad esperada (`p >= 0.367`).

---

### 2.2 Comando de Pitcheo, Rotación de Staff y Fatiga Acumulada

#### Pitcheo por etapa y rol (Yaquis vs Mexicali vs Resto de LMP)
| Etapa | Grupo | Rol | IP | ERA | WHIP | K/9 | BB/9 | HR/9 | Strike% | IR / IRS |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1ra Vuelta | **Yaquis** | **Abridor** | 181.3 | 3.33 | 1.27 | 6.35 | **3.67** | 0.50 | **61.9%** | — |
| 1ra Vuelta | **Yaquis** | **Relevista** | 129.3 | 3.76 | 1.40 | 7.59 | 4.18 | 0.90 | 62.6% | 59 / 14 |
| 1ra Vuelta | Mexicali | Total | 310.3 | 3.07 | 1.25 | 6.64 | 3.74 | 0.41 | 62.3% | 85 / 16 |
| 2da Vuelta | **Yaquis** | **Abridor** | 177.0 | 2.95 | 1.36 | **4.93** | **4.83** | 0.41 | **60.3%** | — |
| 2da Vuelta | **Yaquis** | **Relevista** | 113.3 | 3.89 | 1.31 | 7.07 | 3.57 | 0.64 | 63.3% | 57 / 21 |
| 2da Vuelta | Mexicali | Total | 280.3 | 3.72 | 1.34 | 5.71 | 3.76 | 0.48 | 62.0% | 52 / 24 |
| **Playoffs** | **Yaquis** | **Abridor** | 20.3 | **4.43** | **1.72** | **4.43** | **6.64** | 0.89 | **57.3%** | — |
| **Playoffs** | **Yaquis** | **Relevista** | 18.7 | **4.34** | **1.50** | 6.75 | **4.82** | 0.48 | 61.7% | 6 / 1 |
| **Playoffs** | **Yaquis** | **Total** | 39.0 | **4.38** | **1.62** | **5.54** | **5.77** | 0.69 | **59.4%** | 6 / 1 |
| Playoffs | Mexicali | Total | 86.0 | 3.56 | 1.53 | 4.50 | 4.71 | 0.73 | 61.9% | 22 / 6 |

#### Evidencia geométrica de pérdida de comando (`pitches` 2D Gameday)
Comparando todos los lanzamientos registrados de Yaquis (`n = 5,160` en V1, `n = 4,663` en V2 con XY, `n = 639` en Playoffs con XY; zona calibrada `X=[82.0, 134.3]`, `Y=[115.9, 182.8]`):

| Etapa | Pitcheos XY | Strike% | First-Pitch Strike% | In-Zone% (IC 95% Wilson) | `SD_X` (dispersión horiz.) | `SD_Y` | Distancia radial media / mediana al centro |
|---|---:|---:|---:|---:|---:|---:|---:|
| **1ra Vuelta** | 5,160 | 43.78% | 47.04% | **55.14%** `[53.8%, 56.5%]` | **26.72** | 33.17 | 36.75 / 30.73 |
| **2da Vuelta** | 4,663 | 42.44% | 47.24% | **54.06%** `[52.6%, 55.5%]` | **27.70** | 30.38 | 36.31 / 31.28 |
| **Playoffs** | 639 | **39.59%** | **40.57%** | **47.57%** `[43.7%, 51.5%]` | **32.02** | 32.64 | **40.67 / 36.50** |

- **Pruebas estadísticas formales:**
  - **V1 vs V2:** La dispersión horizontal y vertical ya cambiaba significativamente antes de Playoffs (`Levene_X F = 18.99, p = 0.00001`; `Levene_Y F = 38.43, p < 1e-5`), aunque `InZone%` (`-1.07 pp, p = 0.287`) y `dist_center` (`MWU p = 0.672`) se mantuvieron estables porque los abridores aún compensaban (`2.95 ERA` en V2).
  - **V1 / V2 vs Playoffs:** El comando colapsó de forma estadísticamente contundente:
    - `SD_X` aumentó `+5.30` unidades vs V1 (`Levene_X F = 54.80, p < 1e-5`) y `+4.32` vs V2 (`Levene_X F = 29.03, p < 1e-5`).
    - La distancia radial al centro aumentó `+4.36` unidades (`Mann-Whitney U p < 1e-5` vs V1 y vs V2).
    - `InZone%` se desplomó **`-7.56 pp`** vs V1 (`Chi2 p = 0.0003`, `V = 0.048`) y **`-6.49 pp`** vs V2 (`Chi2 p = 0.00205`, `V = 0.042`).
    - `Strike%` cayó `-4.19 pp` vs V1 (`p = 0.044`) y `First-Pitch Strike%` cayó `-6.66 pp` (`47.24% -> 40.57%`, `p = 0.098`).
  - **Contraste con Mexicali en Playoffs (`n = 1,413` pitcheos):** Mexicali también tuvo `InZone% = 47.42%` (`p = 0.947` vs Yaquis), pero mantuvo mayor tasa de strikes globales (`41.40%` vs `39.59%`), menor `SD_X` (`30.75` vs `32.02`) y menos boletos (`4.71 BB/9` vs `5.77 BB/9`).

#### Rotación del staff y cuello de botella de fatiga (cierre de diciembre 2025)
1. **Éxodo de brazos entre V1 y Playoffs:** Yaquis perdió tras 1ra Vuelta a **Aríel Miranda** (`28.3 IP`), **Vladimir Gutiérrez** (`22.7 IP`, `1.19 WHIP`), **Saúl Vázquez** (`15.7 IP`, `10.91 K/9`), **Devin Sweet** (`15.0 IP`, `7 HLD`), y en diciembre perdió a **Brandon Brennan** (`36.0 IP` totales, último juego `2025-12-14`, `0 IP` en PO). En 2da Vuelta llegaron **Elián Leyva** (`13.0 IP`, `8.31 BB/9`, fuera de PO), **Luis Romero** (`7.0 IP`, fuera de PO) y **Raffi Vizcaíno** (`1.0 IP` V2 → `3.0 IP` en PO).
2. **Carga extrema en los últimos 14 días (`2025-12-18` a `2025-12-30`) antes del inicio de Playoffs (`2026-01-01`):**
   - **Fernando Sánchez**: `782` pitcheos en Regular (`49.0 IP`), pero acumuló **`252` pitcheos en 3 salidas en los últimos 14 días** (última el `2025-12-29`). En J3 (`2026-01-04`) otorgó **5 BB en 4.0 IP** (`53.2% Strike%`).
   - **Odrisamer Despaigne**: `73.3 IP` / `1,151` pitcheos en Regular (`206` en últimos 14d; `97` el `2025-12-26`). Abrió J1 y volvió con solo **3 días de descanso** en J4 (`102` pitcheos, `5 BB, 4 ER` en `5.0 IP`).
   - **Felipe González**: líder del equipo con `1,190` pitcheos (`71.3 IP`, `181` en últimos 14d hasta `2025-12-27`). Relegado al bullpen en Playoffs, explotó en J2 (`2.2 IP, 50 P, 6 H, 3 BB, 3 ER, L`).
   - **Orlando Lara**: `70.7 IP` / `1,133` pitcheos (`173` en últimos 14d hasta `2025-12-28`).
   - **Bullpen sin oxígeno:** **Manuel Chávez** sumó `40` juegos en Regular (`7` apariciones en últimos 14d hasta `12-30`, apenas `0.1 IP` en PO); **Efraín Contreras** (`29 G`, hasta `12-30`) y **Samuel Zazueta** (`28 G`, `5` apps en últimos 14d hasta `12-30`; Zazueta aun así lanzó en los 4 juegos de PO con `4.7 IP, 0 ER`).

#### Desglose exacto juego por juego de los 4 partidos de Playoffs (2025–26)
| Juego (`game_pk`) | Fecha / Sede | Marcador | Abridor Yaquis | Relevistas clave Yaquis | Abridor Mexicali y desenlace |
|---|---|---|---|---|---|
| **J1 (`825728`)** | `2026-01-01` Obregón | **MEX 3 - OBR 2** (10 inn) | **O. Despaigne**: `6.1 IP, 5 H, 2 ER, 3 BB, 1 K, 1 HR (81 P)` | Aro (`0.2 IP, 1 BB`), **E. Contreras** (`2.0 IP, 1 ER, L`), Zazueta (`0.1 IP`), Vizcaíno (`0.2 IP, 1/2 IRS`) | D. Reyes (`6.0 IP, 1 ER`); carrera ganadora ante Contreras/Vizcaíno en la 10ma. |
| **J2 (`825714`)** | `2026-01-02` Obregón | **MEX 10 - OBR 8** (12 inn) | **O. Lara**: `5.0 IP, 8 H, 3 ER, 2 BB, 2 K (82 P)` | **N. Gardewine** (`1.1 IP, 4 ER`, GS de A. Wilson en 8va); **F. González** (`2.2 IP, 6 H, 3 ER, 3 BB, 50 P, L`); Vizcaíno (`1.0 IP, 0 ER`) | G. Ponce (`3.2 IP, 3 ER`); OBR empató ante J. Sanchez (`4 ER, 2 HR`), pero cedió 3 en la 12da. |
| **J3 (`825718`)** | `2026-01-04` Mexicali | **OBR 1 - MEX 2** | **F. Sánchez**: `4.0 IP, 3 H, 1 ER, 5 BB, 3 K (77 P, L)` | Gardewine (`0.2 IP, 2 BB`), Aro (`1.0 IP, 1 ER`), Zazueta (`1.0 IP`), **R. Vizcaíno** (`1.1 IP, 4 K, 0/2 IRS`) | V. Bellozo (`4.2 IP, 0 ER, 4 K`); bullpen MEX cerró juego de 1 carrera. |
| **J4 (`825706`)** | `2026-01-05` Mexicali | **OBR 1 - MEX 4** | **O. Despaigne**: `5.0 IP, 4 H, 4 ER, 5 BB, 4 K, 1 HR (102 P, L)` | **S. Zazueta** (`3.0 IP, 1 H, 0 ER, 1 BB, 36 P`) | M. Simon (`5.0 IP, 1 ER`); Cruz/Sanchez/Robles/Heyer completaron barrida. |

---

### 2.3 Hipótesis del Jardín Izquierdo (`hit_location = '7'` y `fielding_game_stats`)

#### Desempeño por zona de jardín vs Mexicali y Liga LMP
| Etapa | Defensa | BIP a LF (`'7'`, excl. HR) | Outs en LF | DER% LF (IC 95% Wilson) | AVG perm. | XBH (`2B+3B`) | HR a LF |
|---|---|---:|---:|---:|---:|---:|---:|
| 1ra Vuelta | **Yaquis** | 153 | 76 | **49.7%** `[41.9%, 57.5%]` | .510 | 16 | 7 |
| 1ra Vuelta | Mexicali | 132 | 63 | 47.7% | .538 | 23 | 4 |
| 1ra Vuelta | LMP Resto | 1,210 | 549 | 45.4% | .555 | 200 | 60 |
| 2da Vuelta | **Yaquis** | 132 | 61 | **46.2%** `[37.9%, 54.7%]` | .538 | 16 | 11 |
| 2da Vuelta | Mexicali | 129 | 62 | 48.1% | .519 | 18 | 3 |
| 2da Vuelta | LMP Resto | 1,102 | 529 | 48.0% | .533 | 166 | 54 |
| **Regular Total** | **Yaquis** | **285** | **137** | **48.07%** `[42.3%, 53.9%]` | **.523** | **32** | **18** |
| Regular Total | LMP Resto | 2,573 | 1,203 | **46.75%** `[44.8%, 48.7%]` | .544 | 366 | 114 |
| **Playoffs** | **Yaquis** | **21** | **9** | **42.9%** `[24.5%, 63.5%]` | **.571** | **2** | **3** |
| Playoffs | Mexicali | 39 | 22 | 56.4% `[41.0%, 70.7%]` | .462 | 4 | 2 |

- **Pruebas estadísticas en LF (`'7'`, excl. HR):**
  - Regular Yaquis (`48.07%`) vs Resto LMP (`46.75%`): `Chi2 p = 0.673` (`V = 0.008`). **Yaquis defendió ligeramente mejor que el promedio de la liga.**
  - Yaquis V1 (`49.7%`) vs V2 (`46.2%`): `Chi2 p = 0.560` (`V = 0.035`).
  - Yaquis V2 (`46.2%`) vs LMP Reg (`46.75%`): `Chi2 p = 0.903`.
  - Yaquis PO (`42.9%`) vs Regular (`48.07%`): `Chi2 p = 0.644`; vs Mexicali PO (`56.4%`): `Chi2 p = 0.316`.
- **Comparación entre los 3 jardines de Yaquis (`1ra -> 2da -> PO`):** `CF ('8')` subió `54.3% -> 62.5% -> 64.0%`, `RF ('9')` subió `52.2% -> 55.7% -> 57.9%`, mientras `LF ('7')` fue `49.7% -> 46.2% -> 42.9%` (aunque en toda la LMP el LF siempre tiene el DER más bajo de los 3 jardines: `46.0%–51.3%`).
- **Jugadores reales en `LF` (`fielding_game_stats`):**
  - **1ra Vuelta:** **Miguel Guzmán** (`25 GS, 48 PO, 2 A, 0 E, 1.000 FPCT`), **Guillermo Williamson** (`7 GS, 20 PO, 1 A, 1 E, .9545`), **Andrew Navigato** (`5 GS, 5 PO, 5 A, 0 E`), **Braulio Cavero** (`1 GS, 4 PO, 0 E`).
  - **2da Vuelta (alta rotación):** **José Gaitán** (`18 GS, 37 PO, 0 A, 1 E, .9737`), **Zoilo Almonte** (`4 GS, 0 E`), **Taiki Sekine** (`3 GS, 0 E`), **Riley Unroe** (`3 GS, 0 E`), **Miguel Guzmán** (`3 GS, 0 E`), **Williamson** (`1 GS`).
  - **Playoffs:** **José Gaitán** (`3 G, 2 GS, 8 PO, 0 E, 1.000 FPCT`) y **Antonís Macías** (`1 G, 1 GS, 1 PO, 0 E, 1.000 FPCT`). **Cero errores en LF en Playoffs** (en 2da Vuelta, de hecho, Córdoba en CF y Elizalde en RF cometieron `3 E` cada uno frente a `1 E` total en LF).
- **Auditoría de los 24 batazos a LF contra Yaquis en Playoffs (incluyendo HR):**
  - `9` flyouts de out (`37.5%`), **`3` Home Runs** (Yadir Drake en J1 ante Despaigne, **Grand Slam** de Alexis Wilson en J2 ante Gardewine, y Alex D. Mejía en J4 ante Despaigne = `7` carreras), `2` dobles (Cade Gotta en J2, Wynton Bernard en J4) y `10` sencillos (`7` líneas, `3` rolas).
  - **Conclusión H3:** No hubo crisis defensiva de fildeo en LF; los `1.083 SLG` permitidos hacia LF en Playoffs reflejan **pitcheos elevados/en medio castigados con cuadrangulares y líneas limpias**, no pifias ni falta de alcance de Gaitán/Macías.

---

### 2.4 H2H, Localía y Contexto Histórico de 20 Años (2006–2026)

- **Localía 2025–26 Regular:** En Obregón `22-12` (`.647`, `3.03 ERA`, `1.29 WHIP`, `0.46 HR/9`, `.674 OPS`); de visita `18-16` (`.529`, `3.83 ERA`, `1.38 WHIP`, `.709 OPS`). El Estadio Yaquis suprimió carreras y cuadrangulares durante todo el rol regular, por lo que perder J1 (`2-3` en 10 inn) y J2 (`8-10` en 12 inn) en Obregón quebró la principal ventaja estructural del club.
- **H2H vs Mexicali 2025–26:** Regular `4-2` (`22-23` carreras: `2-1` en Obregón, `2-1` en Mexicali); Playoffs `0-4` (`12-19` carreras).
- **Contexto 2006–2026 (`21` temporadas en DB):**
  - **Temporadas de campeonato (`4` títulos):** `2007–08` (`39-28` `.582` Reg → `12-6` `.667` PO, `4-1` Final), `2010–11` (`38-30` `.559` Reg → `12-4` `.750` PO), `2011–12` (`37-31` `.544` Reg → `12-3` `.800` PO, `4-0` Final), `2012–13` (`37-30` `.544` Reg → `11-5` `.688` PO, `4-0` Final). Subcampeón en `2018–19` (`37-29` Reg → `9-11` PO, `2-4` Final).
  - **Máxima dominancia regular sin título:** `2019–20` (`44-22`, `.667`, `+95` Dif → cayó en Semis `3-4`, `7-5` PO, `Luck = -0.167`) y `2020–21` (`37-21`, `.638`, `+65` Dif → Semis `2-4`).
  - **Ubicación de `2025–26`:** **`40-28` (`.588`, `+42` Dif)** es la **3ra mejor temporada regular en 20 años**, pero su `0-4` en Cuartos (`Luck_Diff = -0.301`) es la **única barrida en primera ronda** del registro (peor que `2008` `1-4` y `2021` `1-4`).
  - **Desacople histórico (`2006–2025`):** En la serie histórica de `15` temporadas con postemporada, el `%` de victorias en temporada regular **no garantiza** éxito en series cortas: los 4 títulos llegaron desde campañas de `.544–.582`, mientras los picos de `.667` (`2019`), `.638` (`2020`) y `.588` (`2025`) terminaron eliminados antes de la final.

---

## 3. Arco Narrativo de Data Storytelling (`03_reporte_tecnico` Marimo → Jupyter)

Siguiendo la estructura de `data-storytelling` (**Setup → Conflict → Resolution** / **5 Actos**), el reporte técnico se organiza con encabezados orientados a hallazgo (*insight-led headlines*):

### Acto 1 — El Gancho (*Hook*): "40 victorias construidas en 75 días, demolidas en 96 horas"
- **Dato ancla:** Yaquis firmó su **3ra mejor temporada regular en 20 años (`40-28`, `.588`)**, venciendo `4-2` a Mexicali en el rol regular y jugando `.647` en Obregón (`3.03 ERA`). Cinco días después, cayó **barrido `0-4`** en Cuartos de Final (`3` de los `4` juegos perdidos por `1–2` carreras).
- **Pregunta central:** ¿Fue mala suerte en una serie corta, un hueco defensivo en el jardín izquierdo, o una factura acumulada de poder y comando?

### Acto 2 — El Contexto (*Context*): "Cómo ganaba Yaquis y la falacia de octubre-diciembre"
- **Visuales:** Línea histórica 2006–2026 (`%V Regular` vs alcance en Playoffs, destacando los 4 títulos `2007–2012` y el techo de `2019`) + dispersión `PCT Reg vs PCT PO` + comparativa Home/Away 2025–26.
- **Narrativa:** Históricamente, las coronas de Yaquis no nacieron de arrasar la temporada regular (`.544–.582`), sino de llegar con pitcheo fresco y poder oportuno a enero. En `2025–26`, Obregón ganó a base de defensa en casa, velocidad en 1ra Vuelta (`50 SB`) y un bloque de 4 abridores de alto volumen.

### Acto 3 — Acción Ascendente (*Rising Action*): "Desmontando dos mitos: la defensa en LF y la calidad de contacto"
- **Pilar A (Mito refutado — Jardín Izquierdo):** Mostrar los `285` BIP en LF (`48.07% DER%` vs `46.75%` LMP, `p=0.673`), la tabla de `0` errores de Gaitán y Macías en Playoffs, y el desglose de los `24` batazos en PO donde **`7` carreras llegaron por 3 HR sobre la barda**, no por bolas caídas.
- **Pilar B (El desgaste ofensivo silencioso):** Comparar la caída escalonada de OPS (`.703 -> .681 -> .667`) y SLG (`.357 -> .351 -> .322`, ISO `.074`), mostrando el éxodo de Paris/Navigato, el enfriamiento de Córdoba (`.947 -> .571 -> .596`) y Unroe (`.696 -> .426`), y el muro ante lanzadores derechos en PO (`.591 OPS, 0 HR` de derechos en `75 PA`), mientras se documenta honestamente que la muestra `n=4` impide atribuir la baja conversión de líneas (`.536`) a algo más que varianza + bajo poder crudo (`p >= 0.367`).

### Acto 4 — El Clímax (*Climax*): "La fractura física del comando: por qué el bullpen y la zona explotaron juntos"
- **Insight central:** La progresión **`BB/9` de abridores (`3.67 -> 4.83 -> 6.64`)**, **`InZone%` (`55.1% -> 54.1% -> 47.6%`, `p=0.0003`)** y **`SD_X` (`26.7 -> 27.7 -> 32.0`, Levene `p<1e-5`)**, conectada directamente con la curva de carga de los últimos 14 días de diciembre (`Fernando Sánchez 252 P`, `Despaigne 206 P` y regreso con 3 días de descanso en J4, `Felipe González 1,190 P` totales, `Chávez/Contreras/Zazueta` lanzando hasta el `12-30`).
- **Cierre dramático:** En una serie donde el margen fue mínimo (`2-3` 10 inn, `8-10` 12 inn, `1-2`, `1-4`), regalar `25` bases por bolas en `39.0 IP` (`5.77 BB/9`) y entregar 3 cuadrangulares al LF pesó más que cualquier error de fildeo.

### Acto 5 — Resolución y Plan de Acción (*Resolution & CTA*): "Tres ajustes para 2026–27"
1. **Gestión de carga en la última quincena de diciembre:** Limitar aperturas consecutivas sobre `90+` pitcheos entre el 18 y 30 de diciembre cuando el pase esté asegurado, evitando llegar a enero con la rotación en `>200` pitcheos/14d y evitando salidas con `3` días de descanso.
2. **Construcción de poder derecho para Playoffs:** Reforzar un bate derecho de alto ISO (en `2025–26` solo produjeron `.591 OPS` y `0 HR` ante RHP en postemporada).
3. **Saneamiento del pipeline ETL (`is_risp`):** Corregir `scraper/parser.py` para derivar corredores en base exclusivamente del estado *previo* al primer evento del turno y habilitar análisis real de situaciones de apremio (*clutch/RISP*).

---

## 4. Arquitectura de Dashboard Interactivo y Especificación Visual

### 4.1 Recomendación de Framework
- **Recomendación principal: Plotly Dash (`dash` + `dash-bootstrap-components` / CSS propio + `plotly.graph_objects`)**
  - **Por qué Dash sobre Streamlit:**
    1. **Control total de estética de marca ("Sonora Stadium Editorial"):** CSS variables nativas, tipografía personalizada y layout asimétrico de 12 columnas sin las restricciones de contenedores y re-renders completos de página de Streamlit.
    2. **Interactividad 2D nativa de nivel sabermétrico:** `clickData` y `hoverData` bidireccionales entre la **Zona de Strike 2D Gameday** y el **Spray Chart 2D**, con conmutación instantánea entre *Modo Aficionado* y *Modo Analista* sin recargar consultas pesadas (usando `dcc.Store` + caché en memoria sobre SQLite read-only `mode=ro`).
    3. **Visualizaciones beisboleras exactas:** Plotly nativo permite renderizar polígonos de campo de béisbol, elipses de dispersión `1-SD` de pitcheo y la zona de strike calibrada `X=[82.0, 134.3], Y=[115.9, 182.8]` en una sola capa coherente (evitando depender de librerías estáticas como `baseball-field-viz` que no integran tooltips interactivos por `game_pk` ni coordenadas Gameday px).
- **Rol del stack complementario en el portafolio:**
  - **Marimo → Jupyter (`03_reporte_tecnico.ipynb`):** Reporte técnico reproducible paso a paso con narrativa de 5 actos y pruebas estadísticas (ideal para GitHub / reclutadores de Data Science).
  - **Streamlit (alternativa rápida):** Válida únicamente si se prioriza desplegar un prototipo de 1 solo archivo en Streamlit Community Cloud, sacrificando control fino de CSS y eventos cross-filter 2D.

### 4.2 Dirección Estética e Identidad Visual (Basada en el Sitio Oficial de Yaquis)
- **Concepto estético:** **Yaquis Stadium Editorial + Scout Telemetry** (inspirado en el portal oficial de Yaquis de Cd. Obregón: azul marino institucional, blanco limpio, acentos azul cielo y rojo coral con cintillos inclinados de marcador).
- **Tokens CSS (`:root`)**:
  ```css
  :root {
    --bg-canvas: #F4F7FA;
    --bg-surface: #FFFFFF;
    --bg-navy: #003B73;          /* Navbar, tarjetas de marcador en vivo y cintillos */
    --brand-royal: #0057A8;      /* Botones primarios y encabezados */
    --brand-sky: #0095DA;        /* Badges de visita / serie activa */
    --brand-coral: #E6392F;      /* Alertas críticas, badge EN VIVO, CTA */
    --border-subtle: #DDE6F0;
    --text-primary: #0F172A;
    --text-secondary: #475569;
    --status-good: #16A34A;
    --status-warn: #D97706;
    --status-bad: #E6392F;
  }
  ```
- **Tipografía:**
  - Display / Titulares de pizarra: `'Barlow Condensed', sans-serif` (peso `700`, mayúsculas controladas para encabezados de sección y KPIs).
  - Cuerpo / Narrativa: `'Inter', system-ui, sans-serif` (`15px–16px`, lectura limpia en español).
  - Tablas y cifras sabermétricas: `'JetBrains Mono', monospace` con `font-variant-numeric: tabular-nums` y alineación a la derecha.

### 4.3 Arquitectura de Información Dual (Casual Fan vs Baseball Expert)
Un selector segmentado global en la barra superior (`[ Modo Aficionado | Modo Analista ]`) adapta la densidad sin duplicar rutas ni ocultar la navegación:

1. **Capa 1 — Modo Aficionado (Resumen Ejecutivo y Narrativa Visual):**
   - **4–5 KPI Cards de entrada** (límite estricto `kpi-dashboard-design`):
     1. *Récord 2025–26:* `40-28` (`.588`, 3ro en 20 años) | Playoffs: `0-4` vs MEX.
     2. *Producción Ofensiva:* `4.32 R/G` Regular → **`3.00 R/G`** Playoffs (`-1.32 R/G`).
     3. *Descontrol de Abridores:* `3.67 BB/9` (V1) → **`6.64 BB/9`** (PO, `+2.97`).
     4. *Mito del Jardín Izquierdo:* `48.1%` outs en LF (`46.8%` liga; `0` errores en PO).
     5. *Pulso 2026–27 YTD:* `15-14` (`.517`, Dif `+20` al `15 nov`).
   - **3 Visualizaciones claras con texto explicativo directo:** (a) Historia 2006–2026 y campeonatos, (b) Comparativo simple V1 vs V2 vs Playoffs (Carreras, Poder, Boletos), (c) Resumen de los 4 juegos vs Mexicali con veredicto en lenguaje llano.
2. **Capa 2 — Modo Analista (Sabermetría, Splits y Coordenadas 2D):**
   - Activa la barra completa de filtros (`Temporada 2006–2026`, `Etapa: 1ra Vuelta / 2da Vuelta / Playoffs`, `Rol: Abridor / Relevista`, `Mano bateador/lanzador`, `Jugador individual`) y 4 pestañas analíticas:
     - **Tab 1 — Ofensiva y Contacto:** Tabla sabermétrica individual (`PA>=50` / todos en PO), splits `bat_side x pitch_hand`, distribución de trayectorias y dureza (`AVG` condicional).
     - **Tab 2 — Comando y Fatiga 2D:** Zona de strike calibrada (`pitch_x`, `pitch_y`), métricas de dispersión (`SD_X`, `InZone%`, `FPS%`, Levene/MWU) y línea temporal de pitcheos acumulados (`rolling 14 días`).
     - **Tab 3 — Defensa y Spray Chart 2D:** Mapa de campo interactivo con los `9` sectores (`hit_location 1–9`), `DER%` con intervalos Wilson 95%, tabla de fildeo por jugador y auditoría de los 24 batazos a LF en Playoffs.
     - **Tab 4 — Contexto Histórico y H2H:** Matriz de `21` temporadas (`PCT` vs `Pyth_W%`), correlación Reg vs PO y detalle H2H vs Mexicali (`game_pk` inspectable).

---

### 4.4 Especificación Exacta Gráfica por Gráfica (7 Vistas Principales)

| ID | Título y Tipo (Plotly) | Audiencia | Tablas y Columnas SQLite exactas | Filtros Interactivos | Anotaciones Estadísticas y Salvedades |
|---|---|---|---|---|---|
| **G1** | **Trayectoria Histórica 2006–2026 & Paradoja 2025–26** (`Scatter + Lollipop / Dual-Bar`) | Ambos | `v_valid_games` (`season`, `game_stage`, `game_type`, `home/away_score`) para `team_id=680`. Calcula `PCT`, `Pyth_W%` (`exp=1.83`), `Diff`. | Rango de años (`2006–2026`); resaltar campeonatos (`2007, 2010–12`) o `2025–26`. | Comparativa `PCT Reg vs PCT PO` en las `15` temporadas con playoffs; marcar `2026` como **YTD parcial (`29 JJ`)**. |
| **G2** | **Embudo de Caída Ofensiva y Splits L/R** (`Slope Chart + Grouped Bar`) | Ambos (básico) / Analista (splits) | `batting_game_stats` (`plate_appearances`, `at_bats`, `hits`, `total_bases`, `walks`, `strikeouts`) + `plate_appearances` (`bat_side`, `pitch_hand`, `event_type`). | Etapa (`V1 / V2 / PO`), umbral `min_PA` (default `50` Reg / `1` PO), filtro `bat_side`. | Mostrar `SLG .357 -> .351 -> .322` e `ISO .097 -> .104 -> .074`; badge de **muestra pequeña (`n=4 JJ, 175 PA`)** en PO; **no mostrar `is_risp`**. |
| **G3** | **Calidad de Contacto Condicional** (`100% Stacked Bar + Dot Plot con IC Wilson`) | Analista | `plate_appearances` (`hit_trajectory`, `hit_hardness`, `event_type`, `batting_team_id`) unido a `v_valid_games` (`season=2025`). | Comparar `Yaquis vs Mexicali vs LMP`; seleccionar `Trayectoria` o `Dureza`. | Mostrar `AVG` sobre `line_drive` (`.724 -> .661 -> .536`) y `fly_ball` (`.185 -> .191 -> .118`) con IC Wilson 95% y `p_raw`; **banner obligatorio** indicando que `~95%` de BIP tienen etiqueta manual por defecto `"medium"`. |
| **G4** | **Zona de Strike 2D Calibrada y Dispersión de Comando** (`2D Density Contour / Scatter + Elipse 1-SD`) | Analista (versión simplificada en Aficionado) | `pitches` (`pitch_x`, `pitch_y`, `is_strike`, `is_ball`, `pitch_number`, `call_code`) + `plate_appearances` (`pitching_team_id`, `pitcher_id`) + `players`. | Etapa (`V1 / V2 / PO`), Pitcher individual o Staff, solo Abridores vs Relevistas, conteo (`1er pitcheo`, `2 strikes`). | Dibujar caja calibrada **`X=[82.0, 134.3], Y=[115.9, 182.8]`** (no `[-0.83, 0.83]` ft); anotar `InZone% 55.1% -> 54.1% -> 47.6% (p=0.0003)` y `SD_X 26.7 -> 32.0 (Levene p<1e-5)`. **Caveat:** coordenadas Gameday px manuales; **bloquear `2006–2010`**. |
| **G5** | **Timeline de Carga Acumulada y Descanso hacia Enero** (`Multi-Line + Stepped Area + Markers`) | Ambos | `pitching_game_stats` (`pitches_thrown`, `outs`, `games_started`, `walks`, `earned_runs`) + `v_valid_games.game_date`. | Pitcher (`Despaigne`, `González`, `Lara`, `Sánchez`, `Chávez`, etc.), ventana rolling (`7d` / `14d` / acumulada). | Línea vertical en `2025-12-30` (fin Regular) y `2026-01-01` (inicio PO); anotar `252 P/14d` de Sánchez y `102 P` con 3 días de descanso de Despaigne en J4 (`825706`). |
| **G6** | **Spray Chart 2D y Eficiencia Defensiva por Zona (`DER%` 1–9)** (`Custom Field Polygon + Scatter + Forest Plot IC`) | Ambos | `plate_appearances` (`hit_coord_x`, `hit_coord_y`, `hit_location`, `event_type`, `is_out`, `hit_trajectory`, `rbi`, `pitching_team_id`) + `fielding_game_stats` (`position='LF'`). | Defensa (`Yaquis` vs `Mexicali` vs `LMP`), zona (`7=LF`, `8=CF`, `9=RF`, Todas), excluir/incluir `HR`. | Forest plot con IC Wilson 95%: `Yaquis LF Reg 48.1% [42.3, 53.9]` vs `LMP 46.8% (p=0.673)`; en modo PO resaltar los **3 HR** y `0 E` de Gaitán/Macías en LF. Invertir eje Y si el canvas Gameday tiene `y=0` arriba (verificar orientación `home plate` en `(125, 200)` aprox). |
| **G7** | **Pizarra Serie Cuartos de Final (`OBR 0 - MEX 4`)** (`Small-Multiples Boxscore Cards + Leverage Timeline`) | Ambos | `v_valid_games` (`825728, 825714, 825718, 825706`), `pitching_game_stats`, `plate_appearances` (`inning`, `home_score_after`, `away_score_after`). | Clic en juego `J1..J4` para filtrar `G4` y `G6` al partido específico. | Destacar partidos decididos por 1–2 carreras (`J1 10 inn`, `J2 12 inn`, `J3 1-2`) y saldo total `25 BB` en `39 IP`. |

---

### 4.5 Layout Grid, Responsividad y Estados de UI (`build-ui` & `ui-states`)

#### Retícula Desktop (`1440px`) y Mobile (`390px`)
- **Desktop (`1440px`, 12 columnas, `gap: 16px`, `max-width: 1380px`):**
  - *Fila 1 (Sticky Header `64px`):* Logo/título `Yaquis LMP Analytics`, Selector de Audiencia (`Aficionado | Analista`), Selector de Temporada/Etapa, Botón `Metodología & Caveats`.
  - *Fila 2 (KPI Strip):* `4` o `5` tarjetas iguales (`grid-template-columns: repeat(5, 1fr)`), altura uniforme, delta con unidad explícita (`pp`, `BB/9`, `R/G`).
  - *Fila 3 (Foco Principal Asimétrico `7 + 5` cols):* Izquierda `G4` (Zona de Strike 2D / Oponente) o `G6` (Spray Chart); Derecha `G5` (Carga acumulada) o panel narrativo en Modo Aficionado.
  - *Fila 4 (Comparativo `6 + 6` cols):* `G2/G3` (Ofensiva y contacto) + `G1` (Contexto histórico 2006–2026).
  - *Fila 5 (Tabla de Drilldown `12` cols):* Encabezados fijos al hacer scroll (`position: sticky`), números alineados a la derecha, columna de acción por fila (`Inspeccionar jugador / juego`).
- **Mobile (`390px`, 1 columna):**
  - KPI strip en grid `2x2 + 1` ancho completo; gráficos apilados en columna única con altura fija `320px–360px` para evitar scroll infinito de Plotly; controles de filtro colapsados en un *drawer* o acordeón superior con objetivos táctiles **`>= 44px`**. Tablas con scroll horizontal contenido (`overflow-x: auto`) y primera columna fija (`Nombre`).

#### Estados de UI obligatorios (`ui-states`)
| Estado | Regla de implementación concreta |
|---|---|
| **1. First Use (Primer ingreso)** | Abre por defecto en **2025–26 (Comparativo V1 → V2 → Playoffs)** en *Modo Aficionado*, con un banner sutil de bienvenida explicando cómo alternar a *Modo Analista* y qué significa cada etiqueta. |
| **2. Empty / Filtered-to-Nothing** | Si una combinación de filtros arroja `0` filas (ej. `Yaquis Playoffs vs LHP`, donde hubo `0 PA`), nunca mostrar un lienzo Plotly en blanco: mostrar tarjeta contextual *"Sin apariciones ante lanzadores zurdos en Playoffs 2025–26 (`0 PA`)"* + botón directo **`Restablecer filtro de mano`**. |
| **3. Small-Sample Warning (`n < 30` o `Playoffs n=4`)** | Toda métrica calculada sobre los `4` juegos de Playoffs (o jugadores con `< 30 PA` / `< 20 BIP`) muestra un pill ámbar `--status-warn` (`Muestra corta: n=21 BIP · IC 95% [24.5%, 63.5%]`) y bloquea afirmaciones causales absolutas. |
| **4. Data-Caveat / Partial-Coverage State** | (a) Al seleccionar `2006–2010`, deshabilitar métricas de conteo de pitcheos (`Strike%`, `FPS%`) con aviso *"Tracking parcial (~1.6 pitcheos/PA); datos completos desde 2011"*. (b) Mostrar tooltip informativo permanente sobre coordenadas Gameday px (`no Statcast`) y `hit_hardness` (`~95% default medium`). (c) `is_risp` desactivado del catálogo de filtros hasta corrección del parser. |
| **5. Loading (Carga parcial)** | Skeletons con las dimensiones exactas de cada KPI y gráfico (evitando saltos de layout CLS); la carga de gráficos 2D pesados (`pitches`) usa `dcc.Loading` local por tarjeta sin bloquear el encabezado ni el resto de la página. |
| **6. Error / DB Unavailable** | Mensaje claro en español (*"No se pudo consultar la base analítica local en modo lectura"*), conservando filtros seleccionados y ofreciendo botón **`Reintentar consulta`** (sin exponer trazas SQL/Python crudas). |
| **7. Edge Content (Nombres largos y ceros)** | Nombres largos (`Kevin Villavicencio`, `Odrisamer Despaigne`) truncados con `text-overflow: ellipsis` y tooltip completo; valores `0` o `NaN` (ej. `ERA` con `0.0 IP` como Jesús Luna en V1) formateados explícitamente como `—` (`sin outs registrados`), nunca como `Infinity` o `NaN`. |

---

## 5. Próximos Pasos de Implementación
1. **Notebook técnico (`03_reporte_tecnico.ipynb` / Marimo):** Implementar las secciones y pruebas estadísticas verificadas siguiendo el Arco Narrativo de 5 actos (Sección 3).
2. **Aplicación Dash (`app/`):** Construir el dashboard modular bajo los tokens CSS de *Sonora Stadium Editorial* y los 7 gráficos especificados (Sección 4), verificando manualmente todos los estados (`390px` y `1440px`, navegación por teclado y contraste `>= 4.5:1`).
3. **Parche futuro opcional (fuera de este análisis read-only):** Corregir el cálculo de `is_risp` en `scraper/parser.py` para futuras ingestas incrementales.
