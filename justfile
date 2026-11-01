# Per-repo task manifest. Run `just` (or `just --list`) to see every verb.
#
# Recipes take trailing arguments directly: `just <verb> a b`, where the
# retired form was `ward exec <verb> -- a b`.
#
# One line of comment per recipe on purpose: just reads only the LAST comment
# line above a recipe, so a wrapped description silently truncates to its tail.
#
# `ward exec` is retired, and so is the `.ward/ward.yaml` that outlived it.

set positional-arguments

# Default target: list every available recipe.
default:
    @just --list --unsorted

# Type-check all server mods against Eco.ReferenceAssemblies.
build-mods *ARGS:
    @bash mods/scripts/ward-command.sh build "$@"

# Refresh the locked Python environment for mod tooling.
lock-mods *ARGS:
    @uv lock --project mods "$@"

# Test deterministic per-mod packaging and release-asset publishing.
test-mod-packages *ARGS:
    @bash mods/scripts/ward-command.sh test-packages "$@"

# Lint and format-check the mod package tooling.
lint-mod-packages *ARGS:
    @bash mods/scripts/ward-command.sh lint-packages "$@"

# Format the mod package tooling.
format-mod-packages *ARGS:
    @bash mods/scripts/ward-command.sh format-packages "$@"

# Compile the Python tooling to catch syntax errors.
python-syntax *ARGS:
    @uv run --project mods python -m compileall -q mods "$@"

# Parse the CI workflow as YAML.
validate-ci *ARGS:
    @uv run --project mods python mods/scripts/validate_workflow.py "$@"

# Run both offline trufflehog hooks without the broken layout hooks.
secret-scan *ARGS:
    @pre-commit run trufflehog --all-files --config mods/.pre-commit-config.yaml "$@"

# Package MOD_NAME under .build/mod-package for MOD_SOURCE_REVISION.
package-mod *ARGS:
    @bash mods/scripts/ward-command.sh package-mod "$@"

# Publish .build/mod-package as GitHub Release assets. Needs gh, GITHUB_TOKEN, GITHUB_REPOSITORY, GITHUB_SHA.
publish-mod *ARGS:
    @bash mods/scripts/ward-command.sh publish-mod "$@"

# Refresh the assets folder from eco-mods-assets. Pass optional --branch NAME after `--`.
copy-assets *ARGS:
    @bash mods/scripts/ward-command.sh copy-assets "$@"

# Zip Mods/UserCode/<name> into <name>.zip. Pass NAME after `--`.
zip-assets *ARGS:
    @bash mods/scripts/ward-command.sh zip-assets "$@"

# Zip a UserCode mod and deploy the archive to the Eco server. Pass NAME after `--`.
push-asset *ARGS:
    @bash mods/scripts/ward-command.sh push-asset "$@"

# Regenerate BunWulfAgricultural plants from templates.
bunwulf-agricultural *ARGS:
    @bash mods/scripts/ward-command.sh bunwulf-agricultural "$@"

# Regenerate BunWulfStructural recipes from recipes.yml.
bunwulf-structural *ARGS:
    @bash mods/scripts/ward-command.sh bunwulf-structural "$@"
