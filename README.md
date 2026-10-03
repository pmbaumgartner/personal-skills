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
live at any particular path. Python 3 and Git are required.

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
skills update
```

Enable creates an absolute link in `~/.agents/skills`. Disable removes only a
link belonging to this checkout, never the skill source. Existing directories
and foreign links are protected. Activation is machine-local, not tracked.
Restart your agent session if its skill list does not refresh.

All source skills have a normal `SKILL.md`, even when disabled.
`disable-model-invocation: true` is a separate Claude Code setting: the skill is
manual-only, not disabled.

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

## Independent and third-party skills

`evidence-based-code-review` remains an independent checkout at
`~/projects/evidence-based-code-review`, preserving its own history, remote,
and local edits. Its source entry here is a relative symlink to that checkout.
On a new machine, clone it beside this repository, or adjust that source link.
Commit and pull its changes separately; `skills update` does not update it.

Third-party and externally synced skills remain outside this repository.
The activation tool leaves them alone. No submodules or automatic external
updates are used.

## Verification

```sh
python3 -m unittest discover -s tests -v
```
