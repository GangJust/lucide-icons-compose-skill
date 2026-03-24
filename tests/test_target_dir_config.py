import json
import tempfile
import unittest
from pathlib import Path

from engine.cli import load_config, resolve_target_dir
from engine.scripts.run_skill_backend import is_valid_generation_config


class TargetDirConfigTests(unittest.TestCase):
    def test_resolve_target_dir_keeps_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_path = root / "config.json"
            absolute_target_dir = root / "out"

            resolved = resolve_target_dir(str(absolute_target_dir), config_path)

            self.assertEqual(resolved, absolute_target_dir.resolve())

    def test_load_config_resolves_relative_target_dir_from_config_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            config_dir = root / "project" / ".codex"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "lucide-icons-compose.json"
            package_name = "io.github.lucide.icons"
            config_path.write_text(
                json.dumps(
                    {
                        "target_dir": "../src/commonMain/kotlin",
                        "package": package_name,
                        "object_class_extension": "Icons.kt",
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(config_path)
            expected_target_dir = (config_dir / "../src/commonMain/kotlin").resolve()
            expected_package_dir = expected_target_dir.joinpath(*package_name.split("."))

            self.assertEqual(config.target_dir, expected_target_dir)
            self.assertEqual(config.output_dir, expected_package_dir)
            self.assertEqual(config.object_file, expected_package_dir / "Icons.kt")

    def test_helper_accepts_relative_target_dir_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "target_dir": "src/commonMain/kotlin",
                        "package": "io.github.lucide.icons",
                        "object_class_extension": "Icons.kt",
                    }
                ),
                encoding="utf-8",
            )

            self.assertTrue(is_valid_generation_config(config_path))


if __name__ == "__main__":
    unittest.main()
