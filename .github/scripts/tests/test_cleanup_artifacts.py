import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location(
    "cleanup_artifacts", Path(__file__).parents[1] / "cleanup_artifacts.py"
)
cleanup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cleanup)


def build_keys(bucket, version, prefix="main/46/aarch64/teamsbc-makalu-virt/"):
    image_type = prefix.rstrip("/").rsplit("/", 1)[1]
    stem = f"{image_type}-{version}"
    suffixes = {
        "teamsbc-artifacts": [".raw.xz"],
        "teamsbc-updates": [".usr.raw.xz", ".efi"],
        "teamsbc-extensions": [".debug.sysext.erofs", ".tools.sysext.erofs"],
    }[bucket]
    files = [f"{prefix}{stem}{suffix}" for suffix in suffixes]
    files.append(f"{prefix}meta/{stem}.json")
    return files + [f"{key}.sha256" for key in files]


class RetentionTests(unittest.TestCase):
    def test_keeps_three_versions_and_removes_whole_older_builds_in_every_bucket(self):
        for bucket in cleanup.BUCKETS:
            with self.subTest(bucket=bucket):
                builds = {f"46.202610{day:02d}.0": build_keys(bucket, f"46.202610{day:02d}.0")
                          for day in range(1, 6)}
                keys = [key for files in builds.values() for key in files]
                retained, deleted = cleanup.retention_plan(bucket, reversed(keys))
                self.assertEqual(list(retained.values()), [[
                    "46.20261005.0", "46.20261004.0", "46.20261003.0",
                ]])
                self.assertEqual(set(deleted), set(builds["46.20261001.0"] + builds["46.20261002.0"]))

    def test_branch_major_architecture_and_image_type_have_independent_retention(self):
        prefixes = [
            "main/46/aarch64/teamsbc-makalu-virt/",
            "main/46/x86_64/teamsbc-makalu-virt/",
            "main/46/aarch64/teamsbc-lhotse-virt/",
            "main/46/aarch64/teamsbc-makalu-rpi5/",
            "main/45/aarch64/teamsbc-makalu-virt/",
            "feature/testing/46/aarch64/teamsbc-makalu-virt/",
        ]
        keys, expected = [], []
        for prefix in prefixes:
            major = prefix.split("/")[-4]
            for day in range(1, 5):
                files = build_keys("teamsbc-artifacts", f"{major}.202610{day:02d}.0", prefix)
                keys.extend(files)
                if day == 1:
                    expected.extend(files)
        retained, deleted = cleanup.retention_plan("teamsbc-artifacts", keys)
        self.assertEqual(set(retained), set(prefixes))
        self.assertTrue(all(len(versions) == 3 for versions in retained.values()))
        self.assertEqual(set(deleted), set(expected))

    def test_revision_is_sorted_numerically_and_not_by_upload_time_or_key_order(self):
        versions = ["46.20261013.9", "46.20261013.10", "46.20261013.2", "46.20261012.99"]
        keys = [key for version in versions for key in build_keys("teamsbc-updates", version)]
        retained, deleted = cleanup.retention_plan("teamsbc-updates", keys)
        self.assertEqual(list(retained.values()), [versions[:2][::-1] + [versions[2]]])
        self.assertEqual(set(deleted), set(build_keys("teamsbc-updates", versions[3])))

    def test_unknown_files_indexes_and_legacy_layouts_are_preserved(self):
        prefix = "main/46/aarch64/teamsbc-makalu-virt/"
        unrelated = [
            "index.html", f"{prefix}index.html", f"{prefix}SHA256SUMS",
            f"{prefix}SHA256SUMS.sig", f"{prefix}SHA256SUMS.asc", f"{prefix}SHA256SUMS.gpg",
            f"{prefix}meta/index.html", f"{prefix}meta/SHA256SUMS",
            f"{prefix}teamsbc-other-46.20261001.0.raw.xz",
            f"{prefix}teamsbc-makalu-virt-45.20261001.0.raw.xz",
            f"{prefix}teamsbc-makalu-virt-46.20261001.0.notes.txt",
            f"{prefix}teamsbc-makalu-virt-46.20261001.0.json",
            f"{prefix}nested/teamsbc-makalu-virt-46.20261001.0.raw.xz",
            f"{prefix}meta/teamsbc-makalu-virt-46.20261001.0.efi",
            "main/2026.01.01/46/aarch64/teamsbc-makalu-virt/image.raw.xz",
        ]
        keys = unrelated + [key for day in range(1, 5)
                            for key in build_keys("teamsbc-artifacts", f"46.202610{day:02d}.0")]
        _, deleted = cleanup.retention_plan("teamsbc-artifacts", keys)
        self.assertEqual(set(deleted), set(build_keys("teamsbc-artifacts", "46.20261001.0")))
        self.assertTrue(set(deleted).isdisjoint(unrelated))

    def test_empty_and_small_groups_need_no_deletion(self):
        self.assertEqual(cleanup.retention_plan("teamsbc-artifacts", []), ({}, []))
        for count in (1, 2, 3):
            keys = [key for day in range(1, count + 1)
                    for key in build_keys("teamsbc-artifacts", f"46.202610{day:02d}.0")]
            self.assertEqual(cleanup.retention_plan("teamsbc-artifacts", keys)[1], [])

    def test_invalid_retention_is_rejected(self):
        for keep in (0, -1):
            with self.assertRaises(ValueError):
                cleanup.retention_plan("teamsbc-artifacts", [], keep)


class StorageTests(unittest.TestCase):
    @patch.object(cleanup.subprocess, "check_output")
    def test_listing_uses_cli_pagination_and_handles_empty_buckets(self, check_output):
        keys = [f"key-{i}" for i in range(1100)]
        check_output.return_value = json.dumps({"Contents": [{"Key": key} for key in keys]}).encode()
        self.assertEqual(cleanup.list_keys("teamsbc-artifacts"), keys)
        command = check_output.call_args.args[0]
        self.assertIn("list-objects-v2", command)
        self.assertNotIn("--no-paginate", command)
        self.assertNotIn("--max-items", command)
        check_output.return_value = b"{}"
        self.assertEqual(cleanup.list_keys("teamsbc-artifacts"), [])

    @patch.object(cleanup, "delete_keys")
    @patch.object(cleanup, "list_keys")
    def test_default_dry_run_lists_deletions_without_mutating_storage(self, list_keys, delete_keys):
        list_keys.return_value = [key for day in range(1, 5)
                                 for key in build_keys("teamsbc-artifacts", f"46.202610{day:02d}.0")]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            cleanup.cleanup(["teamsbc-artifacts"])
        delete_keys.assert_not_called()
        self.assertIn("Would delete", output.getvalue())
        self.assertIn("Dry run", output.getvalue())

    @patch.object(cleanup, "delete_keys")
    @patch.object(cleanup, "list_keys")
    def test_listing_failure_in_any_bucket_prevents_all_deletion(self, list_keys, delete_keys):
        list_keys.side_effect = [build_keys("teamsbc-artifacts", "46.20261001.0"),
                                subprocess.CalledProcessError(1, "aws")]
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(subprocess.CalledProcessError):
            cleanup.cleanup(cleanup.BUCKETS, apply=True)
        delete_keys.assert_not_called()

    @patch.object(cleanup, "aws_json")
    def test_apply_deletes_only_the_planned_objects_after_all_listings(self, aws_json):
        calls = []
        expected = {}

        def aws(*args):
            operation, _, bucket = args[:3]
            calls.append(operation)
            if operation == "list-objects-v2":
                keys = [key for day in range(1, 5)
                        for key in build_keys(bucket, f"46.202610{day:02d}.0")]
                expected[bucket] = set(build_keys(bucket, "46.20261001.0"))
                return {"Contents": [{"Key": key} for key in keys]}
            request = json.loads(Path(args[4].removeprefix("file://")).read_text())
            self.assertEqual({item["Key"] for item in request["Objects"]}, expected[bucket])
            return {}

        aws_json.side_effect = aws
        with contextlib.redirect_stdout(io.StringIO()):
            cleanup.cleanup(cleanup.BUCKETS, apply=True)
        self.assertEqual(calls, ["list-objects-v2"] * 3 + ["delete-objects"] * 3)

    @patch.object(cleanup, "aws_json")
    def test_deletes_in_batches_of_at_most_1000_and_checks_individual_errors(self, aws_json):
        batches = []

        def delete(*args):
            request = json.loads(Path(args[4].removeprefix("file://")).read_text())
            batches.append(request["Objects"])
            self.assertTrue(request["Quiet"])
            return {}

        aws_json.side_effect = delete
        cleanup.delete_keys("teamsbc-artifacts", [f"key-{i}" for i in range(2001)])
        self.assertEqual([len(batch) for batch in batches], [1000, 1000, 1])
        aws_json.reset_mock()
        cleanup.delete_keys("teamsbc-artifacts", [])
        aws_json.assert_not_called()
        aws_json.side_effect = None
        aws_json.return_value = {"Errors": [{"Key": "old", "Code": "AccessDenied"}]}
        with self.assertRaisesRegex(RuntimeError, "AccessDenied"):
            cleanup.delete_keys("teamsbc-artifacts", ["old"])


if __name__ == "__main__":
    unittest.main()
