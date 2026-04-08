---
name: deep-research
description: "Execute autonomous multi-step research using Google Gemini Deep Research Agent. Use for: market analysis, competitive landscaping, literature reviews, technical research, due diligence."
risk: safe
source: "https://github.com/sanjay3290/ai-skills/tree/main/skills/deep-research"
date_added: "2026-02-27"
---

# Gemini Deep Research Skill

Run autonomous research tasks that plan, search, read, and synthesize information into comprehensive reports.

## When to Use This Skill

Use this skill when:
- Performing market analysis
- Conducting competitive landscaping
- Creating literature reviews
- Doing technical research
- Performing due diligence
- Need detailed, cited research reports

## Requirements

- Python 3.8+
- httpx: `pip install -r requirements.txt`
- GEMINI_API_KEY environment variable

## Setup

1. Get a Gemini API key from Google AI Studio
2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY=your-api-key-here
   ```
   Or create a `.env` file in the skill directory.

## Usage

### Start a research task
```bash
python3 scripts/research.py --query "Research the history of Kubernetes"
```

### With structured output format
```bash
python3 scripts/research.py --query "Compare Python web frameworks" \
  --format "1. Executive Summary\n2. Comparison Table\n3. Recommendations"
```

### Stream progress in real-time
```bash
python3 scripts/research.py --query "Analyze EV battery market" --stream
```

### Check status of running research
```bash
python3 scripts/research.py --status <interaction_id>
```

### Continue from previous research
```bash
python3 scripts/research.py --query "Elaborate on point 2" --continue <interaction_id>
```

## Output Formats

- **Default**: Human-readable markdown report
- **JSON** (`--json`): Structured data for programmatic use
- **Raw** (`--raw`): Unprocessed API response

## Cost & Time

| Metric | Value |
|--------|-------|
| Time | 2-10 minutes per task |
| Cost | $2-5 per task (varies by complexity) |
| Token usage | ~250k-900k input, ~60k-80k output |

## Best Use Cases

- Market analysis and competitive landscaping
- Technical literature reviews
- Due diligence research
- Historical research and timelines
- Comparative analysis (frameworks, products, technologies)