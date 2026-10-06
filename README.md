# skills

Agent skills for Claude Code and Codex.

| Skill | What it does |
| --- | --- |
| [`designing-ui`](skills/designing-ui/SKILL.md) | Steps and rules for designing a screen: rank, grouping, spacing, type, colour tokens, component composition and states. Loads when a task builds or restyles UI, creates a theme, or reviews how a UI looks. |

The rules in `designing-ui` come from [docs/ui-design-principles.md](docs/ui-design-principles.md), which records the sources and the decisions behind them.

## Install

Pick one of the three ways below.

### 1. Skills CLI (Claude Code, Codex, Cursor and other agents)

Needs Node.js. Run it inside a project to install for that project:

```bash
npx skills add riolly/skills
```

The CLI asks which agents to install for. To install for every project on the machine, add `-g`. To skip the prompts:

```bash
npx skills add riolly/skills --skill designing-ui -g -a claude-code -y
```

Update or remove later:

```bash
npx skills update
npx skills remove designing-ui
```

### 2. Claude Code plugin

In your shell:

```bash
claude plugin marketplace add riolly/skills
claude plugin install riolly@riolly-skills
```

Or inside a Claude Code session:

```
/plugin marketplace add riolly/skills
/plugin install riolly@riolly-skills
```

Installed this way, the skill is named `riolly:designing-ui`. Update later with:

```bash
claude plugin marketplace update riolly-skills
claude plugin update riolly@riolly-skills
```

### 3. Manual copy (Claude Code)

```bash
git clone https://github.com/riolly/skills
mkdir -p ~/.claude/skills
cp -r skills/skills/designing-ui ~/.claude/skills/
```

Copy into a project's `.claude/skills/` instead to install it for that project only.

## Use

Claude Code loads the skill on its own when a task involves UI. To call it directly, type `/designing-ui`, or `/riolly:designing-ui` when installed as a plugin.
