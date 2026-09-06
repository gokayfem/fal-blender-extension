"""Run with Blender --background --factory-startup --python this_file."""
import importlib.util
import json
import queue
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bpy

root = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("fal_ai", root / "__init__.py", submodule_search_locations=[str(root)])
addon = importlib.util.module_from_spec(spec)
sys.modules["fal_ai"] = addon
spec.loader.exec_module(addon)
from fal_ai import live_preview as live
from fal_ai import live_stream as stream
from fal_ai.stream_buffer import ClipBuffer


class LiveTests(unittest.TestCase):
    def test_paired_base64(self):
        payload = live.build_payload(b"first", "motion", "480P", b"last")
        self.assertEqual(payload["image_url"], "data:image/png;base64,Zmlyc3Q=")
        self.assertEqual(payload["end_image_url"], "data:image/png;base64,bGFzdA==")

    def test_buffer_preserves_order_and_waits_for_prefill(self):
        buffer = ClipBuffer(2)
        buffer.put(1, "second")
        self.assertIsNone(buffer.pop())
        buffer.put(0, "first")
        self.assertEqual(buffer.pop(), "first")
        self.assertEqual(buffer.pop(), "second")
        self.assertIsNone(buffer.pop())
        buffer.put(3, "fourth")
        self.assertIsNone(buffer.pop())
        buffer.put(2, "third")
        self.assertEqual(buffer.pop(), "third")
        self.assertEqual(buffer.pop(), "fourth")

    def test_short_stream_can_drain_and_rejects_duplicates(self):
        buffer = ClipBuffer(2)
        buffer.put(0, "one")
        self.assertIsNone(buffer.pop())
        self.assertEqual(buffer.pop(final=True), "one")
        with self.assertRaises(ValueError): buffer.put(0, "duplicate")

    def test_pair_reuses_boundary_and_restores_timeline(self):
        scene = bpy.context.scene
        scene.frame_set(42)
        session = {"scene": scene}
        with patch.object(live, "_capture", side_effect=[b"first", b"boundary", b"last"]) as capture:
            first, last, _ = stream.capture_pair(session, 1, 121)
            second_first, second_last, _ = stream.capture_pair(session, 121, 241)
        self.assertEqual(capture.call_count, 3)
        self.assertEqual(last, second_first)
        self.assertEqual(scene.frame_current, 42)
        with patch.object(live, "_capture", side_effect=RuntimeError("capture failed")):
            with self.assertRaises(RuntimeError): stream.capture_pair(session, 241, 361)
        self.assertEqual(scene.frame_current, 42)

    def test_registration_and_defaults(self):
        addon.register()
        self.assertEqual(bpy.context.scene.fal_h3_live.resolution, "480P")
        self.assertTrue(bpy.app.timers.is_registered(live._tick))
        addon.unregister()
        self.assertFalse(hasattr(bpy.types.Scene, "fal_h3_live"))
        self.assertFalse(bpy.app.timers.is_registered(live._tick))

    def test_payload_and_validation(self):
        payload = live.build_payload(b"png", " test motion ", "480P")
        self.assertEqual(payload["image_url"], "data:image/png;base64,cG5n")
        self.assertEqual(payload["duration"], 5)
        self.assertNotIn("aspect_ratio", payload)
        self.assertTrue(payload["enable_safety_checker"])
        with self.assertRaises(ValueError):
            live.build_payload(b"png", "", "480P")

    def test_network_failure_never_retries_or_exposes_key(self):
        events = queue.Queue()
        with patch.object(live.urllib.request, "urlopen", side_effect=TimeoutError("SECRET")) as call:
            live.generate("SECRET", {}, tempfile.gettempdir(), events, "token", 0)
        self.assertEqual(call.call_count, 1)
        token, kind, message = events.get_nowait()
        self.assertEqual(kind, "error")
        self.assertNotIn("SECRET", message)

    def test_worker_saves_timing_and_result(self):
        class Response:
            headers = {"x-fal-request-id": "test-request"}
            def __init__(self, data): self.data = data
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return self.data
        events = queue.Queue()
        result = {"video": {"url": "https://example.com/test.mp4"}, "timings": {"inference": 0.49}}
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(live.urllib.request, "urlopen", side_effect=[Response(json.dumps(result).encode()), Response(b"movie")]):
                live.generate("SECRET", live.build_payload(b"png", "motion", "480P"), folder, events, "token", 0.1)
            events.get_nowait()
            _, kind, data = events.get_nowait()
            self.assertEqual(kind, "complete")
            self.assertEqual(Path(data["video_path"]).read_bytes(), b"movie")
            self.assertEqual(data["provider_timings"]["inference"], 0.49)
            self.assertNotIn("SECRET", Path(data["video_path"]).with_suffix(".json").read_text())


suite = unittest.defaultTestLoader.loadTestsFromTestCase(LiveTests)
result = unittest.TextTestRunner(verbosity=2).run(suite)
if not result.wasSuccessful():
    raise RuntimeError("H3 Live tests failed")
