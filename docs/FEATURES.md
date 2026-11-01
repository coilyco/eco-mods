# Features

Repository-level inventory for `eco-mods`.

## GitHub CI

- `.github/workflows/ci.yml` runs on pushes to `main`, pull requests, and manual
  dispatches, on hosted runners (COI-3102).
- The gate covers root hygiene, package-tool tests, the `mods/` C# build, and
  repo-level secret scanning.
- `.github/workflows/publish-mods.yml` publishes nine independent, install-ready
  packages from main as release assets on a `mods-<sha>` tag (COI-3122). See
  [mod-packages.md](mod-packages.md).
- `.github/workflows/eco-boot.yml` boots `Mods/UserCode` with coilyco/eco-ops
  main on the pinned Eco server, failing on a compile error or start abort the
  type-check cannot see. Dispatch-only until a dispatched run is green, then on
  UserCode PRs. The harness lives in eco-ops.
- Unity build pipelines are intentionally out of scope for this first pass.

## See also

- [README.md](../README.md) - human-facing intro.
- [AGENTS.md](../AGENTS.md) - operating rules.
- [justfile](../justfile) - dev verbs.
- [mods/docs/FEATURES.md](../mods/docs/FEATURES.md) and
  [unity/docs/FEATURES.md](../unity/docs/FEATURES.md) - per-subtree inventories.
