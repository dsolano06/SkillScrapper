# SkillScraper

Python CLI/TUI for managing AI agent skills. Located at `C:\Users\dsola\Documents\Dev_Projects\SkillScraper`.

## Project Status

- **Stage**: Pre-implementation (empty `skillscraper/` directory)
- **Reference**: Full plan in `PLAN.md`

## Stack

- Python 3.11+
- Textual (TUI)
- Typer (CLI)
- pytest + pytest-asyncio

## Development

```bash
# Install in dev mode
pip install -e .

# Run CLI
skillscraper --help
ss --help    # alias
```

## Architecture (from PLAN.md)

- **Library**: `~/.skillscraper/library/` - central skill storage
- **Targets**: agent-specific destinations (`.claude/skills/`, `.cursor/skills/`, etc.)
- **Combos**: skill groupings in YAML
- **Strategy**: `symlink` (Linux/macOS) or `copy` (Windows)

## Key Files

- `PLAN.md` - complete project specification
- `.agents/skills/` - installed skills (see `skills-lock.json`)
- `skillscraper/` - source code (empty, to be created per PLAN.md)

## Skills Available

Pre-installed via `skills-lock.json`:
- `vercel-react-best-practices` - React/Next.js optimization rules

## Commands to Implement (from PLAN.md)

1. **Phase 1 (MVP)**: sync, search, show, download, library, pm-planning combo
2. **Phase 2**: install, uninstall, targets, targets scan
3. **Phase 3**: add, remove, collection, combo commands
4. **Phase 4**: TUI with slash commands

Run `skillscraper browse` to open the TUI after implementation.

## Notes

- Follow PLAN.md section 7 for exact directory structure
- Windows: force `copy` strategy for targets (symlink limitations)
- Auto-detect targets: `~/.claude/skills/`, `./.claude/`, `~/.cursor/skills/`, `~/.codex/`