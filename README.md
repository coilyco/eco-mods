[![Eco by Strange Loop Games](https://cdn.cloudflare.steamstatic.com/steam/apps/382310/header.jpg)](https://store.steampowered.com/app/382310/Eco/)

<sub>Banner: Steam header for Eco by [Strange Loop Games](https://strangeloopgames.com/). Used here for attribution, not my artwork.</sub>

# eco-mods

Nine public C# gameplay mods for [Eco](https://play.eco/), plus the Unity
assets and packaging that ship them. CI publishes each as an independent,
install-ready package.

## The mods

The **BunWulf** family extends farming and professions. Agricultural adds crop
variety, Biochemical adds a plant-based Biochemist as an alternative to the
petrochemical oil path, Educational adds a Librarian who can craft skill books
across every discipline, and HardwareCo adds specialty hardware items.

Standalone: **DirectCarbonCapture** for late-game CO2 mitigation, **EcoNil**
for weather and moisture, **MinesQuarries** for infinite but expensive
extraction built around vertical integration, **ShopBoat** for a mobile shop
object, and **WorldCounter** for world statistics.

Each mod under [`mods/Mods/UserCode/`](mods/Mods/UserCode) carries its own
README, which is the copy that renders as its mod.io store page.

## Install and build

Every push to `main` publishes nine packages as release assets on a `mods-<sha>` tag,
each fetching only its own Git LFS runtime assets and failing closed on an
unmaterialized pointer (COI-3122). Archive layout and the LFS boundary are in
[docs/mod-packages.md](docs/mod-packages.md).

Mods target `Eco.ReferenceAssemblies` 0.13.0-beta. Dev verbs are recipes in the
[`justfile`](justfile), and [`mods/README.md`](mods/README.md) covers layout,
code generation, and conventions.

## See also

- [AGENTS.md](AGENTS.md) - repository boundaries and operating rules.
- [docs/FEATURES.md](docs/FEATURES.md) - the shipped inventory.
- [eco-app](https://github.com/coilyco/eco-app) - the companion service and its server-side mods.
- [justfile](justfile) - the dev verbs.
