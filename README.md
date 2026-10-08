# skills

Agent skills for Claude Code and Codex.

| Skill | What it does |
| --- | --- |
| [`designing-ui`](skills/designing-ui/SKILL.md) | Steps and rules for designing a screen: rank, grouping, spacing, type, colour tokens, component composition and states. Loads when a task builds or restyles UI, creates a theme, or reviews how a UI looks. |
| [`feature-walkthrough`](skills/feature-walkthrough/SKILL.md) | Record real browser workflows with spoken narration, matching captions, circles, rectangles and pointer gestures. Compare verified app versions in labelled chapters or side by side, and include terminal output. |

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

Install the video walkthrough skill for both Claude Code and Codex:

```bash
npx skills add riolly/skills --skill feature-walkthrough -g -a claude-code -a codex -y
```

Search the public skills index or list the repository directly:

```bash
npx skills find feature-walkthrough --owner riolly
npx skills add riolly/skills --list
```

`find` uses the skills.sh index, so a newly merged skill may take time to appear. Direct `add` discovers the repository's `SKILL.md` files without waiting for the search index. The [skills.sh FAQ](https://skills.sh/docs/faq) explains how installations feed discovery.

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

Installed this way, the skills are named `riolly:designing-ui` and `riolly:feature-walkthrough`. Update later with:

```bash
claude plugin marketplace update riolly-skills
claude plugin update riolly@riolly-skills
```

### 3. Manual copy (Claude Code)

```bash
git clone https://github.com/riolly/skills
mkdir -p ~/.claude/skills
cp -r skills/skills/designing-ui ~/.claude/skills/
cp -r skills/skills/feature-walkthrough ~/.claude/skills/
```

Copy into a project's `.claude/skills/` instead to install it for that project only.

## Use

Claude Code loads the skill on its own when a task involves UI. To call it directly, type `/designing-ui`, or `/riolly:designing-ui` when installed as a plugin.

For a feature report, ask for a short narrated walkthrough or invoke `/feature-walkthrough` in Claude Code, `/riolly:feature-walkthrough` through the plugin, or `$feature-walkthrough` in Codex. It explains what changed, demonstrates the actual result, and gives you steps to try.

Existing recording preferences, including `AGENTS.md` instructions, take precedence. Otherwise, the skill gives written steps for changes that are obvious to check and asks once about a recording for harder ones. In Codex, the written result arrives as a progress update before recording, and the final response includes the verified video or a recording limitation. A recording subagent is preferred when available and allowed; T3 uses its shared preview recorder with or without subagents. Delivery after the turn ends requires a client that explicitly supports automatic resumption.

The skill files install through `npx`; recording dependencies are separate. T3 Code uses its shared preview recorder with native framing checked for sharp text. Other environments can use the bundled Playwright recorder at 1920×1080. Install `uv`, then follow [portable recording](skills/feature-walkthrough/references/portable.md) for browser setup and [narration](skills/feature-walkthrough/references/narration.md) for the default local voice. Exports preserve source resolution and add a separate title and compact captions. [Export quality](skills/feature-walkthrough/references/quality.md) covers NVIDIA encoding, playback, and downloaded-copy checks. Terminal clips additionally need asciinema and agg. No paid speech API is required. Terminal clients receive a local MP4 path; T3 can embed the video.

## Verify the walkthrough helpers

After the pinned browser setup in the portable recording guide:

```bash
uv run --python 3.12 tests/test_feature_walkthrough.py
```

The integration checks record real actions against a temporary test page, verify annotations and titles, preserve full-resolution composition, decode portable MP4 exports, and reject failed workflows or accidental overwrites. They also cover marks over modal dialogs and under a strict content security policy, recordings without a duration header, compact caption bands, and reported NVIDIA fallback. Narration checks run when the local voice is installed; terminal checks need asciinema and agg. Set `WALKTHROUGH_TEST_NVENC=1` to require a real NVIDIA export on a capable machine.
