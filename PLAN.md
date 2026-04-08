# SkillScraper — Plan Maestro

> Terminal-first skill manager para el ecosistema `antigravity-awesome-skills` y otros repositorios de skills. Librería local centralizada + targets configurables + TUI con slash commands.

**Autor del plan:** Daniel
**Fecha:** 2026-04-07
**Stack:** Python 3.11+ · Textual · Typer
**Estado:** Planificación cerrada, listo para implementar

---

## 1. Visión

SkillScraper es un programa híbrido (CLI + TUI) que funciona como **hub central de skills** para cualquier agente de IA. Su filosofía se resume en tres ideas:

1. **Library = Catálogo** — metadatos cacheados de skills disponibles en los repos (búsqueda offline)
2. **Collection = Contenido** — skills descargadas localmente para usar
3. **Targets = Proyección** — desde collection a donde cada agente las necesite (`.claude/skills/`, `.cursor/skills/`, etc.)

El repositorio principal de origen es [`sickn33/antigravity-awesome-skills`](https://github.com/sickn33/antigravity-awesome-skills) (1,381 skills en 9 categorías), pero el programa está diseñado para extenderse a **múltiples repositorios** en el futuro.

---

## 2. Arquitectura de datos

### 2.1 Estructura de `~/.skillscraper/`

```
~/.skillscraper/
├── library/                    ← CATÁLOGO (metadatos cacheados, sin SKILL.md local)
│   ├── index.json              ← Todos los metadatos de skills
│   └── _meta/                  ← metadata por skill
│       └── <skill-id>.json
│
├── collection/                 ← SKILLS DESCARGADAS (contenido real)
│   ├── brainstorming/
│   │   ├── SKILL.md
│   │   └── _meta.json
│   └── ...
│
├── repos/                           ← Repositorios configurados
│   └── sources.toml                 ← Lista de repos de donde scrapear skills
│
├── combos/                          ← Combos en YAML
│   ├── pm-planning.yaml             ← Combo precargado (ver §5)
│   └── (otros combos del usuario)
│
├── targets.toml                     ← Destinos de instalación
├── config.toml                      ← Preferencias generales
└── history.jsonl                    ← Log append-only de acciones
```

### 2.2 Library = Catálogo, Collection = Contenido

**Library** (catálogo):
- Se genera con `sync` → descarga metadatos a `library/index.json`
- Permite búsqueda offline (`search`, `show` de metadatos)
- No contiene archivos `SKILL.md` locales
- Cada entrada en `index.json` tiene flag `in_collection` y puede mostrar estado "tachado" si ya existe en collection

**Collection** (contenido):
- Directorio físico (`~/.skillscraper/collection/`) con las skills descargadas
- Cada skill tiene su `SKILL.md` + `_meta.json` local
- Es la fuente para proyectar a los targets

**Flujo**:
1. `sync` → fetch de índices de repos → se guardan en `library/index.json` (se reescribe completo)
2. `download`/`add` → copia la skill del repo a `collection/` y marca `in_collection: true` en el metadata
3. `library` muestra el catálogo con las skills de collection tachadas (pero legibles)

### 2.3 Metadata con flag `in_collection`

```json
// library/_meta/<skill-id>.json
{
  "id": "brainstorming",
  "name": "Brainstorming",
  "description": "Exploración previa a implementar",
  "category": "planning",
  "repo": "antigravity",
  "version": "1.0.0",
  "in_collection": true,
  "collection_path": "collection/brainstorming",
  "downloaded_at": "2026-04-07T10:00:00Z"
}
```

Flag `in_collection`: `true` si la skill está descargada en collection.

### 2.4 Offline Mode

| Comando | Requiere internet? |
|---|---|
| `search` | No (usa library/index.json) |
| `show <id>` (metadatos) | No |
| `library` | No |
| `collection` | No |
| `install` / `uninstall` | No (usa collection local) |
| `sync` | Sí |
| `download` | Sí |
| `repos scan` | Sí |

- `index.json` tiene timestamp de última actualización
- Si el índice tiene >7 días, warn en `sync --force` o al hacer `download`

### 2.5 Targets

`targets.toml` define destinos nombrados:

```toml
# Target global de Claude Code (siempre disponible)
[targets.claude-global]
path = "~/.claude/skills"
strategy = "symlink"
auto = true                    # auto-detectado al primer arranque

# Target del proyecto actual (relativo a cwd)
[targets.claude-local]
path = "./.claude/skills"
strategy = "symlink"
auto = true                    # registrado si existe .claude/ en cwd

# Cursor global
[targets.cursor-global]
path = "~/.cursor/skills"
strategy = "copy"

# Agente custom del usuario
[targets.mi-agente]
path = "~/agents/mi-bot/context/skills"
strategy = "symlink"
```

**Strategies:**
- `symlink` — una sola copia física en library, links en targets. Actualización viral. Default en macOS/Linux.
- `copy` — copia independiente en el target. Default en Windows (por issues de symlinks) o cuando el usuario quiere "congelar" una versión.

**Auto-detección al primer arranque:**
1. Si existe `~/.claude/skills/` → registra `claude-global`.
2. Si existe `./.claude/` en cwd → registra `claude-local`.
3. Si existe `~/.cursor/skills/` → registra `cursor-global`.
4. Si existe `~/.codex/` → registra `codex-global`.

El usuario puede agregar/remover targets con `/targets add` y `/targets remove`.

### 2.4 Multi-repo (`repos/sources.toml`)

A futuro, SkillScraper no dependerá solo del repo principal. Ejemplo:

```toml
[repos.antigravity]
url = "https://github.com/sickn33/antigravity-awesome-skills"
index_path = "skills_index.json"       # archivo con el índice
skills_path = "skills/"                  # carpeta con las skills
enabled = true
priority = 1

[repos.awesome-claude-skills]
url = "https://github.com/otro-user/awesome-claude-skills"
index_path = null                        # si no hay índice, se escanea
skills_path = "skills/"
enabled = true
priority = 2

[repos.mi-repo-personal]
url = "https://github.com/daniel/mis-skills"
type = "single-skill"                    # el repo entero ES una skill
enabled = true

[repos.carpeta-local]
path = "~/work/custom-skills"            # sin url, local
skills_path = "."
enabled = true
```

**Modos de detección de skills en un repo:**
1. **Con índice** — el repo trae un `skills_index.json` o similar.
2. **Auto-scan** — SkillScraper recorre el repo buscando carpetas con `SKILL.md`.
3. **Single-skill** — el repo entero se trata como una sola skill (el `SKILL.md` está en la raíz).

`/repos add <url>` agrega un repo. `/repos scan` hace sync de todos los repos habilitados. Skills con el mismo ID en diferentes repos se resuelven por `priority`.

---

## 3. Interfaz: slash commands al estilo OpenCode

### 3.1 Command palette

En la TUI, el usuario escribe `/` y aparece un dropdown con:
- Nombre del comando
- Descripción corta (1 línea)
- Autocompletado con Tab
- `?` después del comando muestra sintaxis completa

Ejemplo:
```
> /install ?
  /install <skill-id> [--target T] [--copy] [--all-targets]
  Instala una skill en uno o todos los targets configurados.
  Ejemplos:
    /install brainstorming --target claude-local
    /install pm-core --all-targets
```

### 3.2 Comandos completos

**Library y sync**

| Comando | Descripción |
|---|---|
| `/sync` | Actualiza el índice del catálogo en `library/index.json` desde los repos |
| `/sync --force` | Re-descarga todo aunque exista caché |
| `/download <skill-id>` | Descarga una skill a la collection (directorio físico) |
| `/download combo <nombre>` | Descarga todas las skills de un combo a collection |
| `/add <skill-id>` | Alias de `/download` — descarga una skill a collection |
| `/remove <skill-id>` | Elimina una skill de la collection (y de todos los targets) |
| `/library` | Muestra el catálogo de skills disponibles (metadatos de index.json) |
| `/collection` | Lista las skills descargadas en el directorio collection/ |

**Exploración**

| Comando | Descripción |
|---|---|
| `/browse` | Abre la TUI visual con paneles (categorías, lista, detalle) |
| `/search <query>` | Búsqueda fuzzy en nombre + descripción + ID |
| `/search <query> --category X --risk Y --platform P` | Con filtros |
| `/show <skill-id>` | Detalle completo de una skill |
| `/random` | 5 skills al azar (descubrimiento) |
| `/stats` | Estadísticas de library y collection |
| `/diff` | Skills nuevas desde el último `/sync` |

**Combos**

| Comando | Descripción |
|---|---|
| `/combo create <nombre>` | Crea un combo desde la colección actual |
| `/combo list` | Lista todos los combos guardados |
| `/combo show <nombre>` | Detalle de un combo |
| `/combo edit <nombre>` | Abre el YAML en `$EDITOR` |
| `/combo clone <a> <b>` | Duplica un combo |
| `/combo delete <nombre>` | Elimina un combo |
| `/combo install <nombre>` | Atajo: descarga + instala todas las skills del combo |

**Targets**

| Comando | Descripción |
|---|---|
| `/targets` | Lista targets configurados |
| `/targets add <nombre> <ruta>` | Registra un nuevo target |
| `/targets add <nombre> <ruta> --copy` | Target con strategy copy |
| `/targets remove <nombre>` | Elimina un target |
| `/targets scan` | Re-ejecuta la auto-detección |
| `/install <skill-id>` | Instala en el target default |
| `/install <skill-id> --target T` | Instala en un target específico |
| `/install <skill-id> --all-targets` | Instala en todos |
| `/uninstall <skill-id>` | Desinstala del target (la skill sigue en library) |
| `/installed` | Muestra qué está instalado en cada target |

**Repos (multi-repo)**

| Comando | Descripción |
|---|---|
| `/repos` | Lista repos configurados |
| `/repos add <url>` | Agrega un repo |
| `/repos add <url> --type single-skill` | Agrega como skill única |
| `/repos add --path <ruta>` | Agrega una carpeta local como repo |
| `/repos remove <nombre>` | Elimina un repo |
| `/repos enable <nombre>` / `disable` | Toggle |
| `/repos scan` | Re-escanea todos los repos habilitados |

**Ayuda y utilidades**

| Comando | Descripción |
|---|---|
| `/help` | Lista todos los comandos con su descripción |
| `/help <comando>` | Detalle y ejemplos de un comando |
| `/manual` | Abre el manual completo en el pager |
| `/config` | Edita `config.toml` en `$EDITOR` |
| `/version` | Versión del programa y del índice |
| `/quit` | Sale de la TUI |

### 3.3 CLI one-shot

Todo lo anterior también funciona desde la terminal sin entrar a la TUI:

```bash
skillscraper sync
skillscraper search "nextjs"
skillscraper install brainstorming --target claude-local
skillscraper combo install pm-planning --all-targets
skillscraper browse                # ← abre la TUI
```

Alias corto sugerido: `ss`. (Se define en `pyproject.toml` como entry point adicional.)

---

## 4. Targets por defecto con auto-detección

Al primer arranque de SkillScraper (o con `/targets scan`), el programa ejecuta esta lógica:

```
1. ¿Existe ~/.claude/skills/?
   → Registra target "claude-global" (symlink)

2. ¿Existe ./.claude/ en cwd?
   → Registra target "claude-local" (symlink, path relativo)

3. ¿Existe ~/.cursor/skills/?
   → Registra target "cursor-global" (copy por default de Cursor)

4. ¿Existe ~/.codex/ o ~/.config/codex/?
   → Registra target "codex-global"

5. En Windows: fuerza strategy = "copy" para todos los targets nuevos
```

El usuario puede definir un target "default" en `config.toml`:

```toml
[defaults]
target = "claude-local"         # usado cuando /install no especifica --target
strategy = "symlink"            # para nuevos targets
```

---

## 5. Combo precargado: `pm-planning`

Combo curado para desarrollo de sistemas complejos con automatizaciones. Dividido en tres sub-combos activables por fase del proyecto.

### 5.1 `pm-core` — always-on (6 skills)

El núcleo. Siempre activo durante un proyecto complejo.

| Skill | Rol |
|---|---|
| `brainstorming` | Exploración previa a implementar |
| `ask-questions-if-underspecified` | Fuerza clarificación de scope |
| `concise-planning` | Planes cortos y accionables |
| `goal-analyzer` | Descompone objetivos en sub-objetivos |
| `executing-plans` | Ejecuta planes validados sin re-planear |
| `context-management-context-save` | Persistencia entre sesiones |

### 5.2 `pm-architecture` — fase de diseño (5 skills)

Para definir la arquitectura del sistema.

| Skill | Rol |
|---|---|
| `architect-review` | Review de decisiones arquitectónicas |
| `architecture-decision-records` | Genera ADRs formales |
| `architecture-patterns` | Recomienda patrones según el problema |
| `blueprint` | Diseño de blueprints de proyecto |
| `ddd-strategic-design` | DDD estratégico (opcional según proyecto) |

### 5.3 `pm-automation` — fase de orquestación (6 skills)

Cuando el sistema necesita automatizaciones.

| Skill | Rol |
|---|---|
| `antigravity-skill-orchestrator` | Orquestador meta de skills |
| `antigravity-workflows` | Workflows prearmados del repo |
| `multi-agent-task-orchestrator` | Coordinación multi-agente |
| `dispatching-parallel-agents` | Paralelización de tareas |
| `closed-loop-delivery` | Ciclos cerrados plan→exec→validate→adjust |
| `github-workflow-automation` | Automatizaciones vía GitHub Actions |

### 5.4 Formato YAML del combo

```yaml
# ~/.skillscraper/combos/pm-planning.yaml
name: PM & Planning
description: Desarrollo de sistemas complejos con automatizaciones
version: 1.0.0
author: Daniel
created: 2026-04-07

sub_combos:
  core:
    description: Núcleo always-on
    always_active: true
    skills:
      - brainstorming
      - ask-questions-if-underspecified
      - concise-planning
      - goal-analyzer
      - executing-plans
      - context-management-context-save

  architecture:
    description: Fase de diseño arquitectónico
    always_active: false
    skills:
      - architect-review
      - architecture-decision-records
      - architecture-patterns
      - blueprint
      - ddd-strategic-design

  automation:
    description: Fase de orquestación y automatización
    always_active: false
    skills:
      - antigravity-skill-orchestrator
      - antigravity-workflows
      - multi-agent-task-orchestrator
      - dispatching-parallel-agents
      - closed-loop-delivery
      - github-workflow-automation
```

**Instalación del combo:**
```bash
skillscraper combo install pm-planning --sub core              # solo core
skillscraper combo install pm-planning --sub core,architecture # core + arch
skillscraper combo install pm-planning --all                   # todo
```

---

## 6. Stack técnico

| Componente | Herramienta | Motivo |
|---|---|---|
| Lenguaje | Python 3.11+ | Velocidad de iteración, ecosistema maduro |
| TUI | Textual | CSS-like styling, widgets ricos, mouse support |
| CLI args | Typer | Integra con Textual, ayuda auto-generada |
| Fuzzy search | rapidfuzz | Rápido, C-backed, simple |
| HTTP | httpx | Async, moderno, retries built-in |
| YAML | ruamel.yaml | Preserva comentarios al editar combos |
| TOML | tomllib (stdlib) + tomli-w | Lectura stdlib, escritura con tomli-w |
| Storage | YAML (combos) + TOML (config/targets) + JSON (index/collection) + JSONL (history) | Cada formato para lo que mejor sirve |
| Packaging | pyproject.toml + pipx | `pipx install skillscraper` |
| Tests | pytest + pytest-asyncio | Estándar |

---

## 7. Estructura del repositorio del programa

```
skillscraper/
├── pyproject.toml
├── README.md
├── LICENSE
├── docs/
│   ├── MANUAL.md                   ← Manual completo (ver §8)
│   ├── QUICKSTART.md
│   └── images/
│       └── architecture.png
│
├── src/
│   └── skillscraper/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py                  ← Typer entry point (one-shot)
│       ├── version.py
│       │
│       ├── tui/
│       │   ├── __init__.py
│       │   ├── app.py              ← App Textual principal
│       │   ├── command_palette.py  ← Slash commands parser + dropdown
│       │   ├── screens/
│       │   │   ├── browse.py
│       │   │   ├── detail.py
│       │   │   ├── combo_editor.py
│       │   │   └── help.py
│       │   └── widgets/
│       │       ├── skill_card.py
│       │       ├── category_tree.py
│       │       └── target_list.py
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── paths.py            ← ~/.skillscraper/ resolution
│       │   ├── library.py          ← Catálogo de metadatos (index.json + _meta/)
│       │   ├── collection.py       ← Skills descargadas (contenido real)
│       │   ├── repos.py            ← Multi-repo management
│       │   ├── sync.py             ← Fetch de índices desde repos
│       │   ├── targets.py          ← symlink/copy + auto-detección
│       │   ├── combos.py           ← CRUD de combos
│       │   ├── search.py           ← Fuzzy + filtros
│       │   └── history.py          ← Log JSONL
│       │
│       ├── models/
│       │   ├── skill.py
│       │   ├── combo.py
│       │   ├── target.py
│       │   └── repo.py
│       │
│       ├── commands/                ← Handlers de cada slash command
│       │   ├── sync.py
│       │   ├── download.py
│       │   ├── install.py
│       │   ├── search.py
│       │   ├── combo.py
│       │   ├── targets.py
│       │   ├── repos.py
│       │   └── help.py
│       │
│       └── data/
│           └── default_combos/
│               └── pm-planning.yaml
│
├── tests/
│   ├── test_library.py
│   ├── test_sync.py
│   ├── test_targets.py
│   ├── test_combos.py
│   └── fixtures/
│
└── .github/
    └── workflows/
        └── ci.yml
```

---

## 8. Contenido del manual (`docs/MANUAL.md`)

Estructura del manual, redactado en español:

1. **Quickstart** — Instalación, primer sync, primer install en 5 minutos.
2. **Conceptos clave**
   - Library vs Targets vs Collection vs Combos (con diagrama)
   - Symlink vs Copy: cuándo usar cada uno
   - Por qué separar "tener" de "instalar"
   - Multi-repo y prioridades
3. **Comandos** — Tabla completa + sintaxis + ejemplos de cada slash command.
4. **Workflows típicos**
   - Workflow A: "Explorar y crear mi primer combo"
   - Workflow B: "Nuevo proyecto, activar mi combo de PM"
   - Workflow C: "Agregar skills custom (no del repo principal) a la library"
   - Workflow D: "Compartir un combo con un colega"
   - Workflow E: "Scan de un repo nuevo encontrado en GitHub"
   - Workflow F: "Un repo completo que es una skill"
5. **Configuración** — `config.toml`, `targets.toml`, `sources.toml` comentados línea por línea.
6. **Integraciones**
   - Claude Code (global y por-proyecto)
   - Cursor
   - Codex CLI
   - Agente custom leyendo de la library directamente (con ejemplo Python)
7. **Troubleshooting**
   - Symlinks en Windows
   - Permisos
   - Caché obsoleto
   - Conflictos de ID entre repos
8. **Extensión**
   - Agregar skills manualmente a la library
   - Crear combos desde cero
   - Plantilla de repo compatible con SkillScraper

El manual también es accesible desde la TUI con `/manual`, y cada sección puede invocarse directo con `/manual <seccion>`.

---

## 9. Roadmap de implementación

### Fase 1 — MVP (v0.1)
- [ ] Scaffolding del proyecto con `pyproject.toml` y Typer
- [ ] `core/paths.py` + inicialización de `~/.skillscraper/` (library/ + collection/)
- [ ] `core/sync.py` — fetch de `skills_index.json` del repo principal a library/
- [ ] `core/library.py` — CRUD del catálogo (index.json + _meta/)
- [ ] `core/collection.py` — CRUD de skills descargadas (contenido real)
- [ ] `core/search.py` — búsqueda fuzzy básica (usa library)
- [ ] Comandos CLI: `sync`, `search`, `show`, `download`, `library`, `collection`
- [ ] Combo `pm-planning` precargado en `data/default_combos/`
- [ ] `docs/QUICKSTART.md`

### Fase 2 — Targets e instalación (v0.2)
- [ ] `core/targets.py` — auto-detección + symlink/copy (desde collection)
- [ ] Comandos: `install`, `uninstall`, `installed`, `targets`
- [ ] `targets.toml` con auto-detección al primer arranque
- [ ] Strategy fallback en Windows

### Fase 3 — Combos (v0.3)
- [ ] `core/combos.py`
- [ ] Comandos: `add`, `remove`, `combo *`
- [ ] Editor integration (`$EDITOR` para `/combo edit`)
- [ ] Instalación de sub-combos

### Fase 4 — TUI con Textual (v0.4)
- [ ] `tui/app.py` base
- [ ] Command palette con slash commands
- [ ] Screen de browse (categorías + lista + detalle)
- [ ] Screen de combo editor
- [ ] Screen de help

### Fase 5 — Multi-repo (v0.5)
- [ ] `core/repos.py` con `sources.toml`
- [ ] Scan automático de repos sin índice
- [ ] Soporte `single-skill` repos
- [ ] Resolución de conflictos por prioridad
- [ ] Comandos `/repos *`

### Fase 6 — Manual completo y polish (v1.0)
- [ ] `docs/MANUAL.md` completo
- [ ] Tests con pytest (cobertura >80%)
- [ ] CI con GitHub Actions
- [ ] Release en PyPI
- [ ] README con screenshots de la TUI

### Fase 7 — Ideas futuras (post-v1.0)
- Sync incremental con git shallow clone en lugar de HTTP
- `/watch` — daemon que sincroniza en background y notifica
- `/plan <objetivo>` — sugiere combo desde lenguaje natural (matching semántico)
- `/audit` — audita tu library buscando duplicados, riesgos mezclados, gaps
- Integración con MCP para que SkillScraper sea invocable desde otros agentes
- Marketplace de combos compartibles (gists firmados)

---

## 10. Decisiones cerradas

| Decisión | Valor |
|---|---|
| Nombre | **SkillScraper** (alias CLI: `ss`) |
| Modo | Híbrido (CLI one-shot + TUI interactiva) |
| Lenguaje | Python 3.11+ |
| TUI framework | Textual |
| CLI framework | Typer |
| Storage library | Catálogo de metadatos (`~/.skillscraper/library/`) |
| Storage collection | Directorio físico (`~/.skillscraper/collection/`) |
| Storage combos | YAML |
| Storage config | TOML |
| Strategy default | symlink (Linux/macOS) · copy (Windows) |
| Auto-detección targets | Sí (claude-global, claude-local, cursor, codex) |
| Combo precargado | `pm-planning` con 3 sub-combos (17 skills) |
| Multi-repo | Sí, desde v0.5 |
| Distribución | `pipx install skillscraper` |

---

## 11. Glosario

- **Library** — Catálogo cacheado de metadatos de skills disponibles en los repos configurados (`~/.skillscraper/library/index.json` + `_meta/`). Sin archivos SKILL.md locales.
- **Collection** — Directorio físico donde viven las skills descargadas (`~/.skillscraper/collection/`). Contiene SKILL.md real para usar.
- **Combo** — Agrupación nombrada y guardada de skills, con posibilidad de sub-combos.
- **Sub-combo** — División interna de un combo por fase, rol o contexto.
- **Target** — Destino físico donde SkillScraper proyecta (symlink o copia) skills desde la collection para que un agente específico las consuma.
- **Strategy** — Modo de proyección a un target: `symlink` (link simbólico) o `copy` (copia física).
- **Source repo** — Repositorio configurado desde donde SkillScraper extrae skills. Puede ser remoto (git) o local.
- **Single-skill repo** — Repo completo que es tratado como una única skill (su SKILL.md está en la raíz).
- **Auto-detección** — Lógica que al primer arranque registra automáticamente targets conocidos (`~/.claude/skills/`, etc.).

---

## 12. Lo que OpenCode debería hacer con este plan

Cuando abras OpenCode en la carpeta del proyecto y cargues este archivo como contexto, el agente tiene todo lo necesario para:

1. Crear el scaffolding inicial (`pyproject.toml`, estructura de carpetas, `__init__.py`s).
2. Implementar la Fase 1 (MVP) paso a paso.
3. Consultar este plan cada vez que tenga dudas arquitectónicas.
4. Escribir el `docs/MANUAL.md` siguiendo la estructura de §8.
5. Guardar el combo `pm-planning.yaml` con el contenido exacto de §5.4.

**Primera instrucción sugerida para OpenCode:**
> "Lee `SkillScraper-PLAN.md` como contexto. Arrancamos por la Fase 1 del roadmap. Empezá por el `pyproject.toml` y la estructura de carpetas. Seguí estrictamente los nombres y convenciones del plan."

---

## 13. Skills recomendadas para implementar SkillScraper

Skills ya disponibles en el ecosistema que se recomienda activar durante el desarrollo de este proyecto.

### 13.1 Orquestación y coordinación

| Skill | Rol en este proyecto |
|---|---|
| `antigravity-skill-orchestrator` | Meta-skill principal. Evalúa la complejidad de cada tarea y selecciona las skills necesarias del combo pm-planning |
| `multi-agent-task-orchestrator` | Coordinar tareas paralelas cuando haya múltiples features implementándose simultáneamente |
| `dispatching-parallel-agents` | Cuando haya bugs independientes en diferentes módulos, investigar en paralelo |

### 13.2 Desarrollo y calidad

| Skill | Rol en este proyecto |
|---|---|
| `closed-loop-delivery` | Ciclos completos de plan → implement → validate → adjust para cada feature |
| `acceptance-orchestrator` | Validación de criterios de aceptación antes de marcar tareas como completadas |
| `vercel-react-best-practices` | Si el proyecto evoluciona hacia una UI web con React/Next.js |

### 13.3 Combo activo recomendado

Durante el desarrollo de SkillScraper, mantener activas estas skills del combo `pm-planning`:

**Core (always-on):**
- `concise-planning` — Planes accionables para cada fase
- `brainstorming` — Antes de decisiones arquitectónicas importantes

**Arquitectura (activar al empezar Fase 1 y Fase 2):**
- `architecture-decision-records` — Documentar decisiones técnicas del proyecto
- `software-architecture` — Consultar para decisiones de diseño

**Automatización (activar cuando se alcancen las fases 3+):**
- `github-actions-templates` — CI/CD del proyecto
- `testing-patterns` — Si se agregan tests automatizados

### 13.4 Cómo activar

El agente debe cargar estas skills al inicio de cada sesión usando el patrón del orchestrator:

```markdown
Al empezar este proyecto, activa:
1. antigravity-skill-orchestrator como meta-skill
2. Las skills de orchestration según la fase actual
3. pm-planning sub-combos relevantes al scope de la sesión
```

---

*Plan cerrado. Listo para implementación.*