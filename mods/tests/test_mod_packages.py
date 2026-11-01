from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock

from scripts import mod_packages


class ModPackagesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self.temp_dir.name)
        mods_root = self.repo_root / "mods"
        mods_root.mkdir()
        (mods_root / "pyproject.toml").write_text(
            '[project]\nname = "fixture"\nversion = "1.2.3"\n',
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _mod_dir(self) -> Path:
        mod_dir = self.repo_root / "mods" / "Mods" / "UserCode" / "SampleMod"
        mod_dir.mkdir(parents=True)
        return mod_dir

    def test_package_mod_creates_deterministic_install_archive(self) -> None:
        mod_dir = self._mod_dir()
        (mod_dir / "Sample.cs").write_text("public class Sample {}\n", encoding="utf-8")
        assets = mod_dir / "Assets"
        assets.mkdir()
        (assets / "Sample.unity3d").write_bytes(b"materialized unity bundle")
        output = self.repo_root / "packages"

        mod_packages.package_mod(
            self.repo_root, output, "SampleMod", "sample-mod", "abc123"
        )
        archive = output / "SampleMod-1.2.3.zip"
        first_digest = hashlib.sha256(archive.read_bytes()).hexdigest()

        mod_packages.package_mod(
            self.repo_root, output, "SampleMod", "sample-mod", "abc123"
        )

        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), first_digest)
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(
                package.namelist(),
                [
                    "Mods/UserCode/SampleMod/Assets/Sample.unity3d",
                    "Mods/UserCode/SampleMod/Sample.cs",
                ],
            )
        manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
        record = manifest["packages"][0]
        self.assertEqual(record["package_name"], "sample-mod")
        self.assertEqual(record["registry_version"], "1.2.3+abc123")
        self.assertEqual(
            record["lfs_assets"],
            ["mods/Mods/UserCode/SampleMod/Assets/Sample.unity3d"],
        )

    def test_package_mod_rejects_unmaterialized_lfs_pointer(self) -> None:
        mod_dir = self._mod_dir()
        (mod_dir / "Sample.unity3d").write_text(
            "version https://git-lfs.github.com/spec/v1\n"
            "oid sha256:0123456789abcdef\n"
            "size 1234\n",
            encoding="utf-8",
        )

        with self.assertRaisesRegex(ValueError, "Git LFS object is not materialized"):
            mod_packages.package_mod(
                self.repo_root,
                self.repo_root / "packages",
                "SampleMod",
                "sample-mod",
                "abc123",
            )

    def _package_dir(self) -> Path:
        package_dir = self.repo_root / "packages"
        package_dir.mkdir()
        record = {
            "archive": "SampleMod-1.2.3.zip",
            "metadata": "SampleMod-1.2.3.json",
            "checksum_file": "SampleMod-1.2.3.zip.sha256",
            "package_name": "sample-mod",
            "registry_version": "1.2.3+abc123",
        }
        for field in ("archive", "metadata", "checksum_file"):
            (package_dir / record[field]).write_bytes(field.encode())
        (package_dir / "manifest.json").write_text(
            json.dumps({"schema": 1, "packages": [record]}), encoding="utf-8"
        )
        return package_dir

    def test_publish_mod_uploads_archive_metadata_and_checksum(self) -> None:
        package_dir = self._package_dir()
        uploads: list[str] = []

        with (
            mock.patch.object(mod_packages, "_ensure_release") as ensure,
            mock.patch.object(
                mod_packages,
                "_upload_idempotently",
                side_effect=lambda path, _repo, _tag: uploads.append(path.name),
            ),
        ):
            mod_packages.publish_mod(
                package_dir, "coilyco/eco-mods", "mods-abc123", "a" * 40
            )

        ensure.assert_called_once_with("coilyco/eco-mods", "mods-abc123", "a" * 40)
        self.assertEqual(
            uploads,
            [
                "SampleMod-1.2.3.zip",
                "SampleMod-1.2.3.json",
                "SampleMod-1.2.3.zip.sha256",
            ],
        )

    def test_release_tag_is_the_short_revision(self) -> None:
        revision = "0123456789abcdef0123456789abcdef01234567"
        self.assertEqual(mod_packages.release_tag(revision), "mods-0123456789ab")

    def test_upload_skips_matching_asset_and_rejects_different_bytes(self) -> None:
        archive = self.repo_root / "SampleMod-1.2.3.zip"
        archive.write_bytes(b"zip")
        calls: list[tuple[str, ...]] = []
        remote = [b"zip"]

        def fake_gh_checked(*args: str) -> bytes:
            calls.append(args)
            if args[:2] == ("release", "view"):
                return json.dumps({"assets": [{"name": archive.name}]}).encode()
            return remote[0]

        with mock.patch.object(
            mod_packages, "_gh_checked", side_effect=fake_gh_checked
        ):
            mod_packages._upload_idempotently(
                archive, "coilyco/eco-mods", "mods-abc123"
            )
            self.assertFalse(any(call[:2] == ("release", "upload") for call in calls))

            remote[0] = b"other"
            with self.assertRaisesRegex(RuntimeError, "different bytes"):
                mod_packages._upload_idempotently(
                    archive, "coilyco/eco-mods", "mods-abc123"
                )

    def test_upload_sends_a_new_asset(self) -> None:
        archive = self.repo_root / "SampleMod-1.2.3.zip"
        archive.write_bytes(b"zip")
        calls: list[tuple[str, ...]] = []

        def fake_gh_checked(*args: str) -> bytes:
            calls.append(args)
            return json.dumps({"assets": []}).encode()

        with mock.patch.object(
            mod_packages, "_gh_checked", side_effect=fake_gh_checked
        ):
            mod_packages._upload_idempotently(
                archive, "coilyco/eco-mods", "mods-abc123"
            )

        self.assertEqual(
            calls[-1],
            (
                "release",
                "upload",
                "mods-abc123",
                str(archive),
                "--repo",
                "coilyco/eco-mods",
            ),
        )


if __name__ == "__main__":
    unittest.main()
