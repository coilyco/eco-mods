#!/usr/bin/env python3
"""Create and publish deterministic, install-ready Eco mod archives."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tomllib
import zipfile
from pathlib import Path

SCHEMA_VERSION = 1
REVISION_PATTERN = re.compile(r"^[A-Za-z0-9._+-]+$")
MOD_PATTERN = re.compile(r"^[A-Za-z0-9]+$")
PACKAGE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9.-]*$")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1\n"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_version(repo_root: Path) -> str:
    metadata = tomllib.loads(
        (repo_root / "mods" / "pyproject.toml").read_text(encoding="utf-8")
    )
    version = str(metadata["project"]["version"])
    if not REVISION_PATTERN.fullmatch(version):
        raise ValueError(f"invalid project version: {version!r}")
    return version


def _prepare_output(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    for path in output.iterdir():
        if not path.is_file():
            raise ValueError(f"refusing to replace unexpected directory: {path}")
        path.unlink()


def _mod_files(mod_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(mod_dir.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"mod package input must not contain symlinks: {path}")
        if not path.is_file():
            continue
        with path.open("rb") as source:
            prefix = source.read(len(LFS_POINTER_PREFIX))
        if prefix == LFS_POINTER_PREFIX:
            relative = path.relative_to(mod_dir)
            raise ValueError(
                f"Git LFS object is not materialized for {relative}. "
                "Run git lfs pull for this mod before packaging."
            )
        files.append(path)
    if not files:
        raise ValueError(f"mod package input is empty: {mod_dir}")
    return files


def _write_archive(mod: str, mod_dir: Path, files: list[Path], archive: Path) -> None:
    with zipfile.ZipFile(
        archive,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as package:
        for source in files:
            relative = source.relative_to(mod_dir)
            destination = Path("Mods") / "UserCode" / mod / relative
            info = zipfile.ZipInfo(destination.as_posix(), ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o644 << 16
            package.writestr(info, source.read_bytes())


def package_mod(
    repo_root: Path,
    output: Path,
    mod: str,
    package_name: str,
    revision: str,
) -> None:
    if not MOD_PATTERN.fullmatch(mod):
        raise ValueError(f"invalid mod directory name: {mod!r}")
    if not PACKAGE_PATTERN.fullmatch(package_name):
        raise ValueError(f"invalid package name: {package_name!r}")
    if not REVISION_PATTERN.fullmatch(revision):
        raise ValueError(f"invalid source revision: {revision!r}")

    mod_dir = repo_root / "mods" / "Mods" / "UserCode" / mod
    if not mod_dir.is_dir():
        raise ValueError(f"unknown mod directory: {mod_dir}")

    files = _mod_files(mod_dir)
    version = _repo_version(repo_root)
    _prepare_output(output)

    archive_name = f"{mod}-{version}.zip"
    archive = output / archive_name
    _write_archive(mod, mod_dir, files, archive)
    checksum = _sha256(archive)
    registry_version = f"{version}+{revision}"
    metadata_name = f"{mod}-{version}.json"
    checksum_name = f"{archive_name}.sha256"
    lfs_assets = [
        path.relative_to(repo_root).as_posix()
        for path in files
        if path.suffix.lower() in {".unity3d", ".bundle"}
    ]
    record: dict[str, object] = {
        "archive": archive_name,
        "checksum": checksum,
        "checksum_file": checksum_name,
        "file_count": len(files),
        "lfs_assets": lfs_assets,
        "metadata": metadata_name,
        "mod": mod,
        "mod_version": version,
        "package_name": package_name,
        "registry_version": registry_version,
        "size": archive.stat().st_size,
        "source_directory": mod_dir.relative_to(repo_root).as_posix(),
        "source_revision": revision,
    }
    (output / metadata_name).write_text(
        json.dumps(
            {"schema": SCHEMA_VERSION, "package": record}, indent=2, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )
    (output / checksum_name).write_text(
        f"{checksum}  {archive_name}\n",
        encoding="utf-8",
    )
    (output / "manifest.json").write_text(
        json.dumps(
            {
                "schema": SCHEMA_VERSION,
                "source_revision": revision,
                "packages": [record],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"packaged {mod} as {package_name} {registry_version}: {archive}")


GH_TIMEOUT_SECONDS = 300


def release_tag(revision: str) -> str:
    """One release per source revision holds every mod built from it."""
    return f"mods-{revision[:12]}"


def _gh(*args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["gh", *args], check=False, capture_output=True, timeout=GH_TIMEOUT_SECONDS
    )


def _gh_checked(*args: str) -> bytes:
    result = _gh(*args)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"gh {' '.join(args[:2])} failed: {detail}")
    return result.stdout


def _ensure_release(repo: str, tag: str, target: str) -> None:
    """Create the release at the source commit, tolerating a parallel job that won the race."""
    if _gh("release", "view", tag, "--repo", repo).returncode == 0:
        return
    created = _gh(
        "release",
        "create",
        tag,
        "--repo",
        repo,
        "--target",
        target,
        "--title",
        tag,
        "--notes",
        f"Install-ready Eco mod archives built from {target}.",
        "--latest=false",
    )
    if (
        created.returncode != 0
        and _gh("release", "view", tag, "--repo", repo).returncode != 0
    ):
        detail = created.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(f"could not create release {tag}: {detail}")


def _upload_idempotently(path: Path, repo: str, tag: str) -> None:
    data = path.read_bytes()
    listing = _gh_checked("release", "view", tag, "--repo", repo, "--json", "assets")
    names = {asset["name"] for asset in json.loads(listing)["assets"]}
    if path.name in names:
        remote = _gh_checked(
            "release",
            "download",
            tag,
            "--repo",
            repo,
            "--pattern",
            path.name,
            "--output",
            "-",
        )
        if hashlib.sha256(remote).digest() != hashlib.sha256(data).digest():
            raise RuntimeError(
                f"release {tag} already has {path.name} with different bytes"
            )
        print(f"already published with matching checksum: {path.name}")
        return
    _gh_checked("release", "upload", tag, str(path), "--repo", repo)
    print(f"published {path.name}")


def publish_mod(package_dir: Path, repo: str, tag: str, target: str) -> None:
    manifest = json.loads((package_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema") != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported package manifest schema: {manifest.get('schema')!r}"
        )
    records = manifest.get("packages", [])
    if len(records) != 1:
        raise ValueError("a per-mod publish directory must contain exactly one package")

    _ensure_release(repo, tag, target)
    record = records[0]
    for field in ("archive", "metadata", "checksum_file"):
        _upload_idempotently(package_dir / record[field], repo, tag)


def _required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} is required")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser(
        "package", help="create one deterministic mod ZIP"
    )
    package_parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    package_parser.add_argument("--output", type=Path, required=True)
    package_parser.add_argument("--mod", required=True)
    package_parser.add_argument("--package-name", required=True)
    package_parser.add_argument("--revision", required=True)

    publish_parser = subparsers.add_parser(
        "publish", help="upload one mod as GitHub Release assets"
    )
    publish_parser.add_argument(
        "--input",
        type=Path,
        default=Path(os.environ.get("MOD_PACKAGE_DIR", ".build/mod-package")),
    )
    publish_parser.add_argument(
        "--tag", default=os.environ.get("MOD_RELEASE_TAG") or None, help="release tag"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "package":
            package_mod(
                args.repo_root.resolve(),
                args.output.resolve(),
                args.mod,
                args.package_name,
                args.revision,
            )
        else:
            target = _required_env("GITHUB_SHA")
            publish_mod(
                args.input.resolve(),
                _required_env("GITHUB_REPOSITORY"),
                args.tag or release_tag(target),
                target,
            )
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"mod packages: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
