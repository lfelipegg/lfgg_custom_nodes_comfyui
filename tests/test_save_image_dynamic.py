import importlib
import os
import sys
import tempfile
import time
import types
import unittest


def _install_fake_comfy_modules(output_dir):
    folder_paths = types.SimpleNamespace(get_output_directory=lambda: output_dir)
    comfy_args = types.SimpleNamespace(disable_metadata=False)
    comfy_cli_args = types.SimpleNamespace(args=comfy_args)
    comfy = types.SimpleNamespace(cli_args=comfy_cli_args)

    sys.modules["folder_paths"] = folder_paths
    sys.modules["comfy"] = comfy
    sys.modules["comfy.cli_args"] = comfy_cli_args


def _reload_module(output_dir):
    _install_fake_comfy_modules(output_dir)
    sys.modules.pop("save_image_dynamic", None)
    return importlib.import_module("save_image_dynamic")


class SaveImageDynamicTests(unittest.TestCase):
    def tearDown(self):
        for module_name in ("save_image_dynamic", "folder_paths", "comfy", "comfy.cli_args"):
            sys.modules.pop(module_name, None)

    def test_expand_template_supports_brace_and_percent_tokens(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module = _reload_module(tmpdir)

            expanded = module._expand_template(
                "{model}/%date%/{width}x%height%/{batch}-%counter%-%time%",
                {
                    "model": "juggernaut",
                    "date": "2026-06-03",
                    "time": "14-05-09",
                    "width": "512",
                    "height": "768",
                    "batch": "2",
                    "counter": "00007",
                },
            )

        self.assertEqual(expanded, "juggernaut/2026-06-03/512x768/2-00007-14-05-09")

    def test_blank_model_name_falls_back_to_unknown_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module = _reload_module(tmpdir)

            self.assertEqual(module._normalize_model_name("   "), "unknown_model")

    def test_sanitize_filename_component_removes_windows_unsafe_characters(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module = _reload_module(tmpdir)

            self.assertEqual(
                module._sanitize_filename_component('bad<model>:"name"|?*'),
                "bad_model_name",
            )

    def test_resolve_output_subfolder_rejects_path_traversal(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module = _reload_module(tmpdir)

            with self.assertRaises(ValueError):
                module._resolve_output_folder(tmpdir, "../escape")

    def test_save_images_returns_absolute_paths_and_ui_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module = _reload_module(tmpdir)
            module._local_time = lambda: time.struct_time((2026, 6, 3, 14, 5, 9, 2, 154, -1))
            module._save_png_image = lambda image, path, metadata, compress_level: open(path, "wb").close()
            node = module.SaveImageDynamic()
            images = [
                types.SimpleNamespace(shape=(3, 4, 3)),
                types.SimpleNamespace(shape=(3, 4, 3)),
            ]

            result = node.save_images(
                images=images,
                path_template="runs/{model}/{date}",
                filename_template="{model}_{width}x{height}_{batch}",
                model_name='my<model>:"bad"',
                compress_level=1,
                prompt={"1": {"inputs": {}}},
                extra_pnginfo={"workflow": {"nodes": []}},
            )

            saved_paths = result["result"][0].splitlines()
            ui_images = result["ui"]["images"]

            self.assertEqual(len(saved_paths), 2)
            self.assertTrue(all(os.path.isabs(path) for path in saved_paths))
            self.assertTrue(all(os.path.exists(path) for path in saved_paths))
            self.assertTrue(saved_paths[0].endswith("my_model_bad_4x3_0_00001_.png"))
            self.assertTrue(saved_paths[1].endswith("my_model_bad_4x3_1_00002_.png"))
            self.assertEqual(ui_images[0]["filename"], "my_model_bad_4x3_0_00001_.png")
            self.assertEqual(ui_images[0]["subfolder"], "runs/my_model_bad/2026-06-03")
            self.assertEqual(ui_images[0]["type"], "output")


if __name__ == "__main__":
    unittest.main()
