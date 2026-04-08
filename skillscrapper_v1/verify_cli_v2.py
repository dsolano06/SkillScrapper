import asyncio
from skillscraper.cli import app
from typer.testing import CliRunner

runner = CliRunner()

commands = [
    ['sync'],
    ['search', 'planning'],
    ['installed'],
    ['collection'],
    ['combo', 'list'],
    ['repos', 'list'],
    ['repos', 'scan']
]

for cmd in commands:
    print(f'Testing command: { \" \".join(cmd) }')
    result = runner.invoke(app, cmd)
    if result.exit_code != 0:
        print(f'FAILED: {result.exception}')
    else:
        print('PASSED')
