# Personal skills

Custom agent skills, with local activation managed by symlinks.
This repository continues the history of `kata-workflow`.

## Local setup

Clone this repository wherever you keep projects, then:

```sh
mkdir -p ~/.local/bin ~/.agents/skills
ln -s "$PWD/bin/skills" ~/.local/bin/skills
skills list
skills enable grug-consult
```

Run the setup commands from the repository root. Do not overwrite an existing
`skills` command or skill directory: inspect and reconcile it first.
The script finds its checkout through its own symlink, so the checkout need not
live at any particular path. uv and Git are required; uv manages Python for the script.

Claude Code shares the active collection through
`~/.claude/skills -> ~/.agents/skills`. On a new machine, create that link only
if `~/.claude/skills` does not already exist. Other agents need to be configured
to discover the shared collection; their separate skill directories are not
changed by this tool.

## Commands

```sh
skills list
skills enable thermo-nuclear-code-quality-review
skills disable thermo-nuclear-code-quality-review
skills invocation thermo-nuclear-code-quality-review
skills invocation thermo-nuclear-code-quality-review manual
skills update
```

Enable creates an absolute link in `~/.agents/skills`. Disable removes only a
link belonging to this checkout, never the skill source. Existing directories
and foreign links are protected. Activation is machine-local, not tracked.
Restart your agent session if its skill list does not refresh.

All source skills have a normal `SKILL.md`, even when disabled.
Invocation is a separate, tracked setting of each skill: `auto` lets agents
choose the skill on their own, while `manual` runs it only when explicitly
invoked. Enabling a skill does not change its invocation setting.
`skills invocation <name>` shows the setting and reports when agents disagree;
`skills invocation <name> manual|auto` sets it for every agent at once, through
`disable-model-invocation` in `SKILL.md` (Claude Code and Pi) and
`policy.allow_implicit_invocation` in `agents/openai.yaml` (Codex).

Invoke an enabled skill explicitly, whatever its invocation setting:

- Claude Code: `/grug-consult`
- Pi: `/skill:grug-consult`
- Codex: `$grug-consult`

## Editing and updating

Edit files under `skills/`, try them in your agent, then commit and push.
Edits are live immediately for enabled skills. `skills update` runs
`git pull --ff-only` and refuses to run with uncommitted changes.

The initial local migration deliberately does not reuse the old
`kata-workflow` GitHub remote. After creating your new remote, configure it:

```sh
git remote add origin <your-personal-skills-repository-url>
git push -u origin HEAD
```

The old GitHub repository is not renamed or modified by this setup.

## External skills

Sync the two upstream collections explicitly from the repository root:

```sh
bin/sync-external-skills
bin/sync-external-skills --check  # no writes; exit 1 when updates are available
```

The script requires uv and Git. It fetches `main` from:

- [Cursor team kit](https://github.com/cursor/plugins/tree/main/cursor-team-kit/skills/thermo-nuclear-code-quality-review):
  copies `thermo-nuclear-code-quality-review` without changing its prompt or frontmatter.
- [Roborev analysis prompts](https://github.com/kenn-io/roborev/tree/main/internal/prompt/analyze):
  wraps each `.txt` prompt in a `roborev-analyze-<type>/SKILL.md`, converting
  underscores to hyphens (for example, `roborev-analyze-api-design`). The wrapper
  adds a description, scope guidance, and source link; the prompt is preserved.

Upstream licenses are included with each skill. `external-skills.lock.json`
records source commits and generated-file hashes. Review and commit the resulting
changes; `skills update` still only pulls this repository and does not sync upstreams.

Sync refuses to overwrite local edits or conflicting files. Review those changes
before using `--force`, which replaces them with upstream content. Removed upstream
prompts have their unchanged generated files removed; unrelated files, including
existing `agents/openai.yaml` settings, are left alone. Changes to managed
`SKILL.md` invocation flags count as local edits too.

Sync does not enable skills or change active skill links. Use `skills enable <name>`
after syncing. Skills installed outside this checkout are untouched.

## Verification

```sh
uv run --python '>=3.9' -m unittest discover -s tests -v
```
