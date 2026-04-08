# Manual de Usuario — SkillScraper v1

Bienvenido a SkillScraper, el hub central para gestionar las capacidades (skills) de tus agentes de IA. SkillScraper te permite descubrir, organizar y desplegar instrucciones especializadas en múltiples agentes y proyectos de forma eficiente.

---

## 1. Quickstart: De 0 a 100 en 5 minutos

Sigue estos pasos para empezar a potenciar tus agentes:

1. **Instalación**:
   Instala SkillScraper globalmente usando `pipx` (recomendado):
   ```bash
   pipx install skillscraper
   ```

2. **Sincronización Inicial**:
   Actualiza el catálogo de skills disponibles desde los repositorios remotos:
   ```bash
   skillscraper sync
   # O dentro de la TUI: /sync
   ```

3. **Descubrimiento**:
   Busca una skill que necesites (ej. "planning"):
   ```bash
   skillscraper search "planning"
   # O dentro de la TUI: /search "planning"
   ```

4. **Instalación**:
   Instala la skill en tu target por defecto (ej. Claude Code local):
   ```bash
   skillscraper install brainstorming
   # O dentro de la TUI: /install brainstorming
   ```

¡Listo! Tu agente ahora tiene acceso a la skill `brainstorming`.

---

## 2. Conceptos Clave

Para dominar SkillScraper, es fundamental entender cómo fluyen las skills:

### Library $\rightarrow$ Collection $\rightarrow$ Targets

- **Library (Catálogo)**: Es una caché de metadatos (`~/.skillscraper/library/index.json`). No contiene el código de la skill, solo sabe que existe, qué hace y dónde descargarla. Permite búsquedas instantáneas offline.
- **Collection (Contenido)**: Son las skills que has decidido descargar físicamente a tu máquina (`~/.skillscraper/collection/`). Aquí reside el archivo `SKILL.md` real.
- **Targets (Proyección)**: Son los destinos donde el agente de IA busca sus skills (ej. `.claude/skills/`, `.cursor/skills/`). SkillScraper "proyecta" la skill desde tu *Collection* hacia el *Target*.
- **Combos**: Agrupaciones nombradas de skills (definidas en YAML) para activar roles completos (ej. un combo de "Project Manager" que incluye 10 skills de planning y arquitectura).

### Symlink vs Copy

SkillScraper utiliza dos estrategias para proyectar skills a los targets:
- **Symlink (Enlace Simbólico)**: Crea un acceso directo. Si actualizas la skill en tu *Collection*, el cambio se refleja instantáneamente en todos los targets. (Default en macOS/Linux).
- **Copy (Copia Física)**: Copia el archivo. Útil para "congelar" una versión de la skill en un proyecto específico o en Windows donde los symlinks requieren permisos elevados. (Default en Windows).

### Filosofía: "Tener" vs "Instalar"
- **Tener en Library**: Saber que la skill existe en el ecosistema.
- **Tener en Collection**: Haber descargado la skill para uso personal.
- **Instalar en Target**: Haber hecho que un agente específico pueda leer la skill.

### Multi-repo y Prioridades
SkillScraper puede scrapear múltiples fuentes (`sources.toml`). Si dos repositorios ofrecen una skill con el mismo ID, SkillScraper utiliza la propiedad `priority` para decidir cuál prevalece.

---

## 3. Referencia de Comandos

Puedes usar estos comandos directamente en la CLI (`skillscraper <comando>`) o dentro de la TUI interactiva (`/comando`).

### Gestión de Librería y Sync
| Comando | Sintaxis | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `/sync` | `sync [--force]` | Actualiza el catálogo desde los repos | `/sync --force` |
| `/download` | `download <id>` | Descarga skill a la collection | `/download brainstorming` |
| `/add` | `add <id>` | Alias de `/download` | `/add concise-planning` |
| `/remove` | `remove <id>` | Elimina skill de collection y targets | `/remove brainstorming` |
| `/library` | `library` | Muestra el catálogo completo | `/library` |
| `/collection` | `collection` | Lista skills descargadas localmente | `/collection` |

### Exploración
| Comando | Sintaxis | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `/browse` | `browse` | Abre la interfaz visual de navegación | `/browse` |
| `/search` | `search <query> [filtros]` | Búsqueda fuzzy en catálogo | `/search "nextjs" --category web` |
| `/show` | `show <id>` | Muestra detalles completos de una skill | `/show goal-analyzer` |
| `/random` | `random` | Sugiere 5 skills al azar para descubrir | `/random` |
| `/stats` | `stats` | Estadísticas de library y collection | `/stats` |

### Combos
| Comando | Sintaxis | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `/combo create` | `combo create <nombre>` | Crea combo desde la collection actual | `/combo create mi-set-dev` |
| `/combo list` | `combo list` | Lista todos los combos guardados | `/combo list` |
| `/combo show` | `combo show <nombre>` | Muestra contenido de un combo | `/combo show pm-planning` |
| `/combo edit` | `combo edit <nombre>` | Edita el YAML en tu editor externo | `/combo edit pm-planning` |
| `/combo install`| `combo install <nombre>` | Descarga e instala todas las skills | `/combo install pm-planning` |

### Targets e Instalación
| Comando | Sintaxis | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `/targets` | `targets` | Lista targets configurados | `/targets` |
| `/targets add` | `targets add <nom> <ruta> [--copy]` | Registra nuevo destino | `/targets add my-bot ~/bot/skills` |
| `/targets remove`| `targets remove <nom>` | Elimina un target | `/targets remove old-bot` |
| `/targets scan` | `targets scan` | Re-detecta targets comunes | `/targets scan` |
| `/install` | `install <id> [--target T]` | Instala skill en target específico | `/install brainstorming --target claude-local` |
| `/uninstall` | `uninstall <id>` | Quita skill del target | `/uninstall brainstorming` |
| `/installed` | `installed` | Muestra qué hay en cada target | `/installed` |

### Repositorios
| Comando | Sintaxis | Descripción | Ejemplo |
| :--- | :--- | :--- | :--- |
| `/repos` | `repos` | Lista repos configurados | `/repos` |
| `/repos add` | `repos add <url> [--type T]` | Agrega nueva fuente de skills | `/repos add https://github.com/user/repo` |
| `/repos scan` | `repos scan` | Sincroniza todos los repos habilitados | `/repos scan` |

---

## 4. Workflows Típicos

### Workflow A: Explorar y crear mi primer combo
1. `/search "architecture"` $\rightarrow$ Encuentras 3 skills interesantes.
2. `/download <id>` $\rightarrow$ Descargas las 3 a tu *Collection*.
3. `/combo create "mi-arquitecto"` $\rightarrow$ SkillScraper crea un combo con esas 3 skills.
4. `/combo install "mi-arquitecto" --all-targets` $\rightarrow$ Las despliegas en todos tus agentes.

### Workflow B: Nuevo proyecto, activar combo de PM
1. Abres tu terminal en la carpeta del proyecto.
2. `/targets scan` $\rightarrow$ SkillScraper detecta la carpeta `./.claude/` y crea el target `claude-local`.
3. `/combo install pm-planning --sub core` $\rightarrow$ Instalas solo el núcleo esencial de gestión para empezar.

### Workflow C: Agregar skills custom a la library
1. `/repos add --path ~/mis-notas/skills` $\rightarrow$ Agregas una carpeta local como fuente.
2. `/repos scan` $\rightarrow$ SkillScraper indexa tus archivos `.md` locales.
3. Ahora aparecen en `/library` y puedes instalarlas como cualquier otra.

### Workflow D: Compartir un combo con un colega
1. Localiza el archivo en `~/.skillscraper/combos/mi-combo.yaml`.
2. Envía el archivo YAML a tu colega.
3. Tu colega copia el archivo en su carpeta `combos/` y ejecuta `/combo install mi-combo`.

### Workflow E: Scan de un repo nuevo en GitHub
1. Encuentras un repo con skills: `/repos add https://github.com/someone/awesome-skills`.
2. `/repos scan` $\rightarrow$ SkillScraper busca el `skills_index.json` o escanea carpetas con `SKILL.md`.
3. Las nuevas skills aparecen inmediatamente en tu `/library`.

### Workflow F: Un repo completo que es una skill
1. Algunos repos son una sola skill gigante: `/repos add <url> --type single-skill`.
2. SkillScraper trata la raíz del repo como la carpeta de la skill y usa el `SKILL.md` principal.

---

## 5. Configuración

SkillScraper utiliza archivos TOML para su configuración. Se encuentran en `~/.skillscraper/`.

### `config.toml` (Preferencias)
```toml
[defaults]
target = "claude-local"   # Target usado si no se especifica --target en /install
strategy = "symlink"      # Estrategia default para nuevos targets (symlink o copy)
editor = "vim"            # Editor usado por /combo edit
```

### `targets.toml` (Destinos)
```toml
[targets.claude-global]
path = "~/.claude/skills"
strategy = "symlink"
auto = true               # Indica que fue detectado automáticamente

[targets.cursor-global]
path = "~/.cursor/skills"
strategy = "copy"         # Forzamos copia para Cursor
```

### `sources.toml` (Fuentes de datos)
```toml
[repos.antigravity]
url = "https://github.com/sickn33/antigravity-awesome-skills"
index_path = "skills_index.json"
skills_path = "skills/"
enabled = true
priority = 1              # Menor número = Mayor prioridad
```

---

## 6. Integraciones

### Claude Code
- **Global**: Proyecta a `~/.claude/skills/`. Todas tus sesiones de Claude Code tendrán estas skills.
- **Local**: Proyecta a `./.claude/skills/`. Solo el proyecto actual tendrá estas skills.

### Cursor
- Proyecta a `~/.cursor/skills/`. Recomendamos usar `strategy = "copy"` ya que Cursor a veces tiene problemas con enlaces simbólicos profundos.

### Codex CLI
- Proyecta a `~/.codex/` o `~/.config/codex/`.

### Agentes Custom (Python)
Si estás programando tu propio agente, puedes hacer que lea directamente de la *Collection* de SkillScraper:
```python
import os
from pathlib import Path

def load_skill(skill_id):
    path = Path.home() / ".skillscraper" / "collection" / skill_id / "SKILL.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None
```

---

## 7. Troubleshooting

### Symlinks en Windows
Si recibes errores de "Permisos insuficientes" al usar `symlink` en Windows:
- **Solución A**: Activa el "Modo de Desarrollador" en la configuración de Windows.
- **Solución B**: Ejecuta tu terminal como Administrador.
- **Solución C**: Cambia la estrategia a `copy` en `config.toml` o al crear el target (`/targets add <nom> <ruta> --copy`).

### Caché Obsoleto
Si sabes que un repositorio se actualizó pero no ves los cambios:
- Ejecuta `/sync --force` para ignorar el caché y re-descargar todo el índice.

### Conflictos de ID
Si dos repositorios tienen una skill llamada `planning`:
- SkillScraper usará la del repositorio con la `priority` más baja (ej. priority 1 gana a priority 2) definida en `sources.toml`.

---

## 8. Extensión

### Agregar skills manualmente
Si tienes una skill que no está en ningún repo:
1. Crea una carpeta en `~/.skillscraper/collection/<mi-skill>/`.
2. Añade el archivo `SKILL.md` con las instrucciones.
3. Crea un archivo `_meta.json` básico:
   ```json
   { "id": "mi-skill", "name": "Mi Skill", "description": "Descripción", "category": "custom" }
   ```

### Plantilla de Repo Compatible
Para que tu repositorio de skills sea compatible con SkillScraper, sigue este esquema:
- **Opción A (Con Índice)**: Incluye un archivo `skills_index.json` en la raíz que liste las skills, sus IDs y rutas.
- **Opción B (Auto-scan)**: Crea una carpeta `skills/` y dentro de ella subcarpetas por cada skill, cada una con su propio `SKILL.md`.
- **Opción C (Single-Skill)**: Pon el `SKILL.md` directamente en la raíz del repositorio.
