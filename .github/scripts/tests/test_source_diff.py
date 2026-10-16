import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).parents[1] / "source_diff.py"
spec = importlib.util.spec_from_file_location("source_diff", SCRIPT)
diff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diff)


def rpm_sources(items):
    return {"org.osbuild.curl": {"items": items}}


class SourceDiffTests(unittest.TestCase):
    def test_package_update_addition_and_removal_are_readable(self):
        published = rpm_sources({
            "sha256:old": {"url": "https://repo/systemd-260-1.fc46.aarch64.rpm"},
            "sha256:removed": "https://repo/old-package-1-1.fc46.noarch.rpm",
        })
        current = rpm_sources({
            "sha256:new": {"url": "https://repo/systemd-260-2.fc46.aarch64.rpm"},
            "sha256:added": "https://repo/new-package-1-1.fc46.noarch.rpm",
        })
        report = diff.source_diff(published, current)
        self.assertIn('-org.osbuild.curl "systemd-260-1.fc46.aarch64.rpm"', report)
        self.assertIn('+org.osbuild.curl "systemd-260-2.fc46.aarch64.rpm"', report)
        self.assertIn('-org.osbuild.curl "old-package-1-1.fc46.noarch.rpm"', report)
        self.assertIn('+org.osbuild.curl "new-package-1-1.fc46.noarch.rpm"', report)

    def test_checksum_only_change_is_reported_even_for_identical_filenames(self):
        url = {"url": "https://repo/pkg-1-1.noarch.rpm"}
        report = diff.source_diff(rpm_sources({"sha256:old": url}),
                                  rpm_sources({"sha256:new": url}))
        self.assertIn('-org.osbuild.curl "pkg-1-1.noarch.rpm": sha256:old', report)
        self.assertIn('+org.osbuild.curl "pkg-1-1.noarch.rpm": sha256:new', report)

    def test_librepo_package_paths_are_labeled_and_mirror_changes_are_reported(self):
        def sources(version, mirror):
            return {"org.osbuild.librepo": {
                "items": {f"sha256:{version}": {
                    "path": f"Packages/s/systemd-{version}-1.fc46.aarch64.rpm",
                    "mirror": "fedora",
                }},
                "options": {"mirrors": {"fedora": {"url": mirror, "type": "baseurl"}}},
            }}

        report = diff.source_diff(sources("260", "https://old/"),
                                  sources("261", "https://new/"))
        self.assertIn('-org.osbuild.librepo "systemd-260-1.fc46.aarch64.rpm"', report)
        self.assertIn('+org.osbuild.librepo "systemd-261-1.fc46.aarch64.rpm"', report)
        self.assertIn("https://old/", report)
        self.assertIn("https://new/", report)

    def test_url_and_source_option_changes_are_not_hidden(self):
        published = rpm_sources({"sha256:same": {"url": "https://old/pkg.rpm"}})
        current = rpm_sources({"sha256:same": {"url": "https://new/pkg.rpm"}})
        current["org.osbuild.curl"]["options"] = {"insecure": True}
        report = diff.source_diff(published, current)
        self.assertIn("https://old/pkg.rpm", report)
        self.assertIn("https://new/pkg.rpm", report)
        self.assertIn('"insecure": true', report)

    def test_container_and_other_source_changes_are_reported(self):
        published = {
            "org.osbuild.skopeo": {"items": {"sha256:old": {
                "image": {"name": "registry/fedora:46", "digest": "sha256:old"},
            }}},
            "org.osbuild.containers-storage": {"items": {"sha256:storage": {}}},
        }
        current = {
            "org.osbuild.skopeo": {"items": {"sha256:new": {
                "image": {"name": "registry/fedora:46", "digest": "sha256:new"},
            }}},
            "org.osbuild.inline": {"items": {"sha256:inline": {"data": "hello"}}},
        }
        report = diff.source_diff(published, current)
        self.assertIn('-org.osbuild.skopeo "registry/fedora:46": sha256:old', report)
        self.assertIn('+org.osbuild.skopeo "registry/fedora:46": sha256:new', report)
        self.assertIn('-org.osbuild.containers-storage', report)
        self.assertIn('+org.osbuild.inline', report)

    def test_ordering_does_not_affect_report(self):
        first = rpm_sources({"b": {"url": "https://repo/b.rpm", "insecure": True},
                             "a": "https://repo/a.rpm"})
        second = rpm_sources({"a": "https://repo/a.rpm",
                              "b": {"insecure": True, "url": "https://repo/b.rpm"}})
        self.assertEqual(diff.source_lines(first), diff.source_lines(second))
        self.assertEqual(diff.source_diff(first, second), "No source changes.\n")

    def test_cli_ignores_pipeline_and_image_version_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("published.json", "current.json")]
            for index, path in enumerate(paths):
                path.write_text(json.dumps({"sources": rpm_sources({}),
                                            "pipelines": [{"name": str(index)}]}))
            result = subprocess.run([sys.executable, str(SCRIPT), *map(str, paths)],
                                    capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout, "No source changes.\n")

    def test_missing_or_invalid_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            for manifest in ({}, {"sources": None}, {"sources": []}):
                path.write_text(json.dumps(manifest))
                with self.assertRaisesRegex(ValueError, "sources must be an object"):
                    diff.sources_from_manifest(path)


if __name__ == "__main__":
    unittest.main()
