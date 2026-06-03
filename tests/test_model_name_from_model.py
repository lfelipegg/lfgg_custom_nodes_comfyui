import unittest

from model_name_from_model import (
    UNKNOWN_MODEL_NAME,
    _normalize_model_source_name,
    _resolve_model_name_from_graph,
)


class FakeDynamicPrompt:
    def __init__(self, nodes):
        self._nodes = nodes

    def get_node(self, node_id):
        return self._nodes[node_id]


class ResolveModelNameFromGraphTests(unittest.TestCase):
    def test_normalize_model_source_name_returns_filename_stem(self):
        self.assertEqual(
            _normalize_model_source_name(r"sdxl\models\juggernaut.safetensors"),
            "juggernaut",
        )

    def test_resolve_model_name_from_graph_traces_through_model_modifier(self):
        dynprompt = FakeDynamicPrompt(
            {
                "target": {
                    "class_type": "LfggModelNameFromModel",
                    "inputs": {"model": ["modifier", 0]},
                },
                "modifier": {
                    "class_type": "LoraLoader",
                    "inputs": {
                        "model": ["loader", 0],
                        "clip": ["clip_loader", 0],
                    },
                },
                "loader": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "sdxl/juggernaut.safetensors"},
                },
            }
        )

        self.assertEqual(
            _resolve_model_name_from_graph(dynprompt, "target"),
            "juggernaut",
        )

    def test_resolve_model_name_from_graph_supports_unet_loader(self):
        dynprompt = FakeDynamicPrompt(
            {
                "target": {
                    "class_type": "LfggModelNameFromModel",
                    "inputs": {"model": ["loader", 0]},
                },
                "loader": {
                    "class_type": "UNETLoader",
                    "inputs": {"unet_name": "flux\\dev\\flux1-dev.sft"},
                },
            }
        )

        self.assertEqual(
            _resolve_model_name_from_graph(dynprompt, "target"),
            "flux1-dev",
        )

    def test_resolve_model_name_from_graph_returns_unknown_for_unsupported_root(self):
        dynprompt = FakeDynamicPrompt(
            {
                "target": {
                    "class_type": "LfggModelNameFromModel",
                    "inputs": {"model": ["unsupported", 0]},
                },
                "unsupported": {
                    "class_type": "ModelMergeSimple",
                    "inputs": {"ratio": 0.5},
                },
            }
        )

        self.assertEqual(
            _resolve_model_name_from_graph(dynprompt, "target"),
            UNKNOWN_MODEL_NAME,
        )

    def test_resolve_model_name_from_graph_returns_unknown_for_ambiguous_sources(self):
        dynprompt = FakeDynamicPrompt(
            {
                "target": {
                    "class_type": "LfggModelNameFromModel",
                    "inputs": {"model": ["merge", 0]},
                },
                "merge": {
                    "class_type": "ModelMergeSimple",
                    "inputs": {
                        "model1": ["loader_a", 0],
                        "model2": ["loader_b", 0],
                    },
                },
                "loader_a": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "models/a.safetensors"},
                },
                "loader_b": {
                    "class_type": "CheckpointLoaderSimple",
                    "inputs": {"ckpt_name": "models/b.safetensors"},
                },
            }
        )

        self.assertEqual(
            _resolve_model_name_from_graph(dynprompt, "target"),
            UNKNOWN_MODEL_NAME,
        )


if __name__ == "__main__":
    unittest.main()
