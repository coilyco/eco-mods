# Features

Repository-level inventory for `eco-mods`.

## Forgejo CI

- `.forgejo/workflows/ci.yml` runs on pushes to `main`, pull requests, and
  guarded manual dispatches.
- The gate covers root hygiene, package-tool tests, the proxy-backed `mods/`
  C# build, and repo-level secret scanning.
- Main and manual runs publish nine independent, install-ready Forgejo generic
  packages. Each job fetches only its mod's committed Git LFS runtime assets and
  fails closed on unmaterialized pointers. See [mod-packages.md](mod-packages.md).
- Unity build pipelines are intentionally out of scope for this first pass.
- The legacy GitHub-only TruffleHog workflow was replaced with Forgejo-native coverage.

## See also

- [README.md](../README.md) - human-facing intro.
- [AGENTS.md](../AGENTS.md) - operating rules.
- [justfile](../justfile) - dev verbs.
- [mods/docs/FEATURES.md](../mods/docs/FEATURES.md) and
  [unity/docs/FEATURES.md](../unity/docs/FEATURES.md) - per-subtree inventories.
