#!/usr/bin/env python3
"""Asset and recipe tooling for eco-mods.

Subcommands mirror what used to live in tasks.py. Ward exposes them through
the repository command catalog. See ../justfile.

push-asset has moved out of Python entirely: zip-assets is now a Ward helper,
and the actual upload lives in `coily gaming eco mod push`. This script
keeps the Python-heavy verbs (copy-assets, bunwulf-*) and the cleaner
zip helpers shared by copy-assets.
"""

import argparse
import os
import shutil
import stat
import sys

import jinja2
import regex
import yaml

MODS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, MODS_DIR)
import util  # noqa: E402


# The generated UserCode and the source Unity project both live in this
# repository now. USERCODE_PATH resolves against the script, and copy_assets
# reads the sibling unity/ tree rather than cloning the retired
# eco-mods-assets remote.
USERCODE_PATH = os.path.join(MODS_DIR, "Mods", "UserCode")
UNITY_USERCODE = os.path.join(MODS_DIR, os.pardir, "unity", "Builds", "Mods", "UserCode")


class RemovalException(Exception):
    pass


def handle_remove_readonly(func, path, _):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise RemovalException("could not handle path")


def copy_paths(origin_path, target_path):
    if not os.path.isdir(origin_path):
        return
    if os.path.exists(target_path) and os.path.isdir(target_path):
        print(f"\tRemoving {target_path}")
        shutil.rmtree(target_path, ignore_errors=False, onerror=handle_remove_readonly)
    if os.path.isdir(origin_path):
        print(f"\tCopying {origin_path} to {target_path}")
        shutil.copytree(origin_path, target_path)


def copy_assets():
    print("Copying Unity assets from the in-tree unity project")
    for build in os.listdir(UNITY_USERCODE):
        origin_path = os.path.join(UNITY_USERCODE, build, "Assets")
        target_path = os.path.join(USERCODE_PATH, build, "Assets")
        copy_paths(origin_path, target_path)


def bunwulf_agricultural():
    plants = os.path.join(util.AUTOGEN_PATH, "Plant")
    plant = os.listdir(plants)

    plant_entity_pattern = r".*public partial class (\w+) : PlantEntity.*"
    plant_species_pattern = r".*public partial class (\w+) : PlantSpecies.*"
    tree_species_pattern = r".*public partial class (\w+) : TreeSpecies.*"

    templates = jinja2.Environment(loader=jinja2.FileSystemLoader("templates/"))
    template = templates.get_template("plant.template")

    for p in plant:
        with open(os.path.join(plants, p), "r", encoding="utf-8") as f:
            data = f.read()

        if "PlantFibersItem" in data:
            continue

        if regex.match(tree_species_pattern, data, regex.DOTALL):
            continue

        plant_entity = regex.search(plant_entity_pattern, data, regex.DOTALL).group(1)
        plant_species = regex.search(
            plant_species_pattern, data, regex.DOTALL
        ).group(1)

        print(f"Writing {plant_entity} to BunWulfAgricultural")
        content = template.render(
            plant_entity=plant_entity, plant_species=plant_species
        )
        with open(
            os.path.join(USERCODE_PATH, "BunWulfAgricultural", "Plant", p),
            "w",
            encoding="utf-8",
        ) as f:
            f.write(content)


def bunwulf_structural():
    with open("recipes.yml", "r", encoding="utf-8") as recipes:
        recipe_data = yaml.safe_load(recipes)["BunWulfStructural"]

    util.process_recipes(
        recipe_data, os.path.join(USERCODE_PATH, "BunWulfStructural", "Recipes")
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "copy-assets",
        help="Refresh Mods/UserCode assets from the in-tree unity project.",
    )

    sub.add_parser(
        "bunwulf-agricultural",
        help="Regenerate BunWulfAgricultural plants from templates.",
    )
    sub.add_parser(
        "bunwulf-structural",
        help="Regenerate BunWulfStructural recipes from recipes.yml.",
    )

    args = parser.parse_args()

    if args.cmd == "copy-assets":
        copy_assets()
    elif args.cmd == "bunwulf-agricultural":
        bunwulf_agricultural()
    elif args.cmd == "bunwulf-structural":
        bunwulf_structural()


if __name__ == "__main__":
    main()
