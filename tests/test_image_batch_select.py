import importlib
import sys
import unittest


class FakeImageBatch:
    def __init__(self, frames, shape=None, cloned=False):
        self.frames = frames
        self.cloned = cloned
        self.shape = shape or (len(frames), 2, 2, 3)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return FakeImageBatch(
                self.frames[item],
                shape=(len(self.frames[item]), *self.shape[1:]),
            )
        return self.frames[item]

    def clone(self):
        copied_frames = [
            frame.copy() if hasattr(frame, "copy") else frame
            for frame in self.frames
        ]
        return FakeImageBatch(copied_frames, shape=self.shape, cloned=True)


def _reload_module():
    sys.modules.pop("image_batch_select", None)
    return importlib.import_module("image_batch_select")


class ImageBatchSelectTests(unittest.TestCase):
    def test_first_mode_selects_first_image_and_preserves_batch_dimension(self):
        module = _reload_module()
        images = FakeImageBatch([{"id": "first"}, {"id": "last"}])

        selected = module.ImageBatchSelect().select_image(images, "first", 0)[0]

        self.assertEqual(selected.shape, (1, 2, 2, 3))
        self.assertEqual(selected.frames, [{"id": "first"}])

    def test_last_mode_selects_last_image(self):
        module = _reload_module()
        images = FakeImageBatch([{"id": "first"}, {"id": "middle"}, {"id": "last"}])

        selected = module.ImageBatchSelect().select_image(images, "last", 0)[0]

        self.assertEqual(selected.shape, (1, 2, 2, 3))
        self.assertEqual(selected.frames, [{"id": "last"}])

    def test_index_mode_selects_middle_image(self):
        module = _reload_module()
        images = FakeImageBatch([{"id": "first"}, {"id": "middle"}, {"id": "last"}])

        selected = module.ImageBatchSelect().select_image(images, "index", 1)[0]

        self.assertEqual(selected.shape, (1, 2, 2, 3))
        self.assertEqual(selected.frames, [{"id": "middle"}])

    def test_index_mode_clamps_large_index_to_last_image(self):
        module = _reload_module()
        images = FakeImageBatch([{"id": "first"}, {"id": "last"}])

        selected = module.ImageBatchSelect().select_image(images, "index", 99)[0]

        self.assertEqual(selected.shape, (1, 2, 2, 3))
        self.assertEqual(selected.frames, [{"id": "last"}])

    def test_selection_is_cloned_when_input_supports_clone(self):
        module = _reload_module()
        original_frame = {"id": "first"}
        images = FakeImageBatch([original_frame, {"id": "last"}])

        selected = module.ImageBatchSelect().select_image(images, "first", 0)[0]
        original_frame["id"] = "changed"

        self.assertTrue(selected.cloned)
        self.assertEqual(selected.frames, [{"id": "first"}])

    def test_empty_batch_raises_value_error(self):
        module = _reload_module()
        images = FakeImageBatch([], shape=(0, 2, 2, 3))

        with self.assertRaises(ValueError):
            module.ImageBatchSelect().select_image(images, "last", 0)

    def test_non_4d_image_input_raises_value_error(self):
        module = _reload_module()
        images = FakeImageBatch([{"id": "bad"}], shape=(1, 2, 2))

        with self.assertRaises(ValueError):
            module.ImageBatchSelect().select_image(images, "first", 0)

    def test_node_metadata_follows_lfgg_conventions(self):
        module = _reload_module()

        self.assertEqual(module.ImageBatchSelect.RETURN_TYPES, ("IMAGE",))
        self.assertEqual(module.ImageBatchSelect.RETURN_NAMES, ("image",))
        self.assertEqual(module.ImageBatchSelect.FUNCTION, "select_image")
        self.assertEqual(module.ImageBatchSelect.CATEGORY, "LFGG / Image")
        self.assertEqual(
            module.NODE_CLASS_MAPPINGS,
            {"LfggImageBatchSelect": module.ImageBatchSelect},
        )
        self.assertEqual(
            module.NODE_DISPLAY_NAME_MAPPINGS,
            {"LfggImageBatchSelect": "LFGG Image Batch Select"},
        )
        self.assertIn("ImageBatchSelect", module.__all__)

    def test_input_metadata_uses_expected_controls(self):
        module = _reload_module()

        input_types = module.ImageBatchSelect.INPUT_TYPES()["required"]

        self.assertEqual(input_types["images"][0], "IMAGE")
        self.assertEqual(input_types["mode"][0], ("last", "first", "index"))
        self.assertEqual(input_types["mode"][1]["default"], "last")
        self.assertEqual(input_types["batch_index"][0], "INT")
        self.assertEqual(input_types["batch_index"][1]["default"], 0)
        self.assertEqual(input_types["batch_index"][1]["min"], 0)
        self.assertEqual(input_types["batch_index"][1]["max"], 4095)


if __name__ == "__main__":
    unittest.main()
