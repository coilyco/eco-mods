---
ward:
  workflow: pull-request-and-merge
---
# Agent instructions

## Scope

This repository owns Kai's public Eco mod source, retained Unity assets,
package tooling, and package publication workflows.

## Project shape

`mods/` holds the C# mod projects and the public listing copy that ships to
mod.io, `unity/` vendors the EcoModKit SDK and retained Unity assets, and
`unity-embedded/` holds the embedded variants. `scripts/` holds the shell that
CI steps invoke on one line.

## Repo boundaries

Server configuration and installed third-party mods live in
`coilyco-gaming/eco-ops`. Deployment lives in `coilyco-bridge/deploy`. Keep
those operational concerns out of this source repository.

## Commands

Route development through the [`justfile`](justfile) (`just <verb>`). Use the
focused build, lint, format, package, and validation verbs for the mod being
changed.

## Validation

Run the applicable validation and packaging verbs. Preserve Git LFS
assets and never bypass secret scanning.

## Safety

Package publication needs `FORGEJO_PACKAGE_TOKEN` with `write:package`, held as
an Actions secret and never in the tree. Never bypass secret scanning, and
preserve Git LFS pointers rather than committing materialized assets.

## Cross-repo contracts

Server configuration and installed third-party mods live in
`coilyco-gaming/eco-ops`, and deployment in `coilyco-bridge/deploy`. The
catalog pre-commit hooks are authored in agentic-os and consumed here by
upstream rev, never forked.

## Agent rules

<!-- BEGIN managed by agentic-os/scripts/apply-git-workflow.py -->
### Git workflow

**This repo runs the `pull-request-and-merge` lane**, declared as `ward.workflow` in this file's frontmatter. The agent commits to a task branch, pushes it, opens a Forgejo pull request, and **merges that pull request itself** once it is green. The author of the code is the one who merges it. Opening the pull request is a step, never the stopping point.

The fleet runs one lane, and it authorizes the agent end to end. Pushing straight to `main` is over: `merge-remote-main` is retired, so no repo can declare its way back to one.

* `pull-request-and-merge` - the agent commits to a task branch, pushes it, opens a pull request, and merges that pull request itself once it is green.

**Every lane slug names what the AGENT does, never what someone else does.** `pull-request-and-merge` carries the merge because the agent that authored the code merges its own pull request. `pull-request` drops `-and-merge` because the author stops at the pull request and the director merge lane takes over. Reading `pull-request-and-merge` as "someone else merges it later" inverts the two and leaves finished work sitting unmerged.

**These actions are pre-authorized on every lane, and the agent MUST take them without asking first.** Committing, creating a branch, pushing a branch, pushing the lane's own destination, and opening a pull request are ordinary reversible work, not the destructive wall that earns a question. Stopping to ask is how a turn ends with the work stranded in a dirty worktree.

* **ALWAYS commit** in-scope work and **ALWAYS push** it to the canonical remote before pausing, reporting a checkpoint, handing off, or ending a turn. A local-only commit is not a checkpoint.
* **ALWAYS open the pull request** in the same turn as the branch's first push, on every lane except `remote-branch-only`. A pushed branch with no pull request is litter nobody reviews.
* **NEVER `--no-verify`** and **NEVER force-push**. Those two are the real walls, and they stay closed.
* **ALWAYS merge your own pull request on `pull-request-and-merge`**, in the same turn, as soon as it is green. Reporting it as open and awaiting someone is the failure this lane exists to prevent.
* **NEVER merge on `pull-request` or `remote-branch-only`.** Those two stop where they stop, and the director merge lane carries a `pull-request` from there.
<!-- END managed by agentic-os/scripts/apply-git-workflow.py -->

Use she/her for Kai. No em dashes, italics, or semicolons in prose. Name the
actor in every action sentence.

## Release

Canonical work lands on Forgejo `main`. CI publishes independent,
install-ready generic packages from committed sources and materialized assets.

## Checkout residency

This repo belongs on disk, whether or not Agent Compose's `repository-plan.yaml`
lists it. On a native Windows host it is worked in the canonical checkout under
the projects root, never in a session shadow, a linked worktree, or a temporary
clone. The governing rule is `Serialized checkouts on native Windows` in
agentic-os AGENTS.md, which covers eco-app, eco-mods, and eco-ops together.

These three take one writer at a time, because the Unity assets and the Eco
server state they drive corrupt on a second checkout rather than isolating.
Before the first mutation, confirm that no other agent and no open Unity Editor
holds the checkout, and stop and report when one does rather than branching
around it.

Commit and push before pausing, switching tasks, or ending a session. That still
holds, though now because the remote is the shared record and not because a
temporary root could be purged.

## See also

* [README.md](README.md) - repository orientation.
* [docs/FEATURES.md](docs/FEATURES.md) - current package and CI inventory.
* [`justfile`](justfile) - the dev verbs.
