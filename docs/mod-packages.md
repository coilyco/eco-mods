# Eco mod packages

`publish-mods` publishes each directory under `mods/Mods/UserCode/` as a package on
every push to `main`: `bunwulf-agricultural`, `bunwulf-biochemical`,
`bunwulf-educational`, `bunwulf-hardware-co`, `direct-carbon-capture`, `eco-nil`,
`mines-quarries`, `shop-boat`, and `world-counter`. The files are GitHub Release assets
on a `mods-<first 12 of the source sha>` tag (COI-3122), replacing Forgejo's registry.

A package version combines the repository version from `mods/pyproject.toml` with the
source revision. It holds an install-ready ZIP rooted at `Mods/UserCode/<Mod>`, JSON
metadata, and a SHA-256 sidecar. A re-run skips an asset already present with the same
bytes and fails on one with different bytes.

## Git LFS boundary

The repository includes a full Unity project with source art and vendored assets in Git
LFS, and package jobs do not download it. Each matrix job pulls only its own
`mods/Mods/UserCode/<Mod>/**` tree, which holds the built runtime bundles.

The packager rejects any remaining LFS pointer before writing an archive, so a job never
publishes a text pointer where an Eco runtime bundle belongs. Unity asset production stays
a separate authoring step: CI never invokes Unity.

The first `publish-mods` run on GitHub (2026-11-01) pulled these trees from GitHub LFS
and published all nine packages, so the narrow pull works there. LFS content outside
`mods/Mods/UserCode/<Mod>/**` was not exercised (COI-3080).

## Credentials

The publish step uses the automatic `GITHUB_TOKEN` with `contents: write`, and no other
secret. The hosted `mods` job needs no egress proxy.

## Local commands

Set `MOD_NAME`, `MOD_PACKAGE_NAME`, and `MOD_SOURCE_REVISION`, then run `ward
exec package-mod`. `just test-mod-packages` runs the archive and publishing tests.
`just publish-mod` needs `gh`, `GITHUB_TOKEN`, `GITHUB_REPOSITORY` and `GITHUB_SHA`.
