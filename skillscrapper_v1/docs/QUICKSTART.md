# SkillScraper Quickstart

SkillScraper is a CLI/TUI tool for managing AI agent skills.

## Installation
Install the project in development mode:
```bash
pip install -e .
```

## Basic Workflow

### 1. Initialize the Catalog
Sync the local library with the remote repositories to discover available skills:
```bash
skillscraper sync
```

### 2. Explore Skills
Search for skills related to a specific topic:
```bash
skillscraper search "planning"
```
View details of a specific skill:
```bash
skillscraper show brainstorming
```

### 3. Build your Collection
Download a skill to your local collection:
```bash
skillscraper download brainstorming
```
List all skills you have downloaded:
```bash
skillscraper collection
```

## Next Steps
The full manual is available in `docs/MANUAL.md` (coming soon).
