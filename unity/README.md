[![Eco by Strange Loop Games](https://cdn.cloudflare.steamstatic.com/steam/apps/382310/header.jpg)](https://store.steampowered.com/app/382310/Eco/)

<sub>Banner: Steam header for Eco by [Strange Loop Games](https://strangeloopgames.com/). Used here for attribution, not my artwork.</sub>

# unity

The Unity project that builds the asset bundles Kai's [Eco](https://play.eco/) mods load. This is a directory of `eco-mods`, not a repository of its own.

`Assets/`, `Packages/`, and `ProjectSettings/` are the usual Unity layout. `AssetBundles/` holds bundle output, and `Builds/Mods/UserCode/<Mod>/Assets/` holds the per-mod build that the sibling `mods/` tree consumes. The editor version is pinned in `ProjectSettings/ProjectVersion.txt`.

Point the Unity Hub at this directory, not at the repository root. `Library/` is generated and ignored, so a fresh checkout imports the whole tree on first open and that takes a while.

Build a bundle from the Editor with `ModKit > Build Current Bundle`, one scene at a time. Unity manages the `.meta` files, so do not edit them by hand.

`Assets/Scenes/Construction.unity` is unstarted work: 2D icons for a BunWulf Construction Worker skill that no C# under `../mods/` defines, so its build output is not committed. A running server advertises every bundle it booted with and clients fetch them at connect, so removing a shipped bundle from a server is stop, remove the folder, start, never while eco-server runs (COI-2690, COI-2798).

## Siblings

- `../mods/` - the C# mod source that loads these bundles.
- `../unity-embedded/` - icons, prefabs, and scenes the client loads directly rather than through a bundle.
- [StrangeLoopGames/EcoModKit](https://github.com/StrangeLoopGames/EcoModKit) - the upstream modkit, vendored under `Assets/EcoModKit/`.

## See also

- [AGENTS.md](AGENTS.md) - agent operating rules for this directory.
- [docs/FEATURES.md](docs/FEATURES.md) - inventory of what ships today.
- [.coily/coily.yaml](.coily/coily.yaml) - catalog metadata only.
