import unittest, os

from tracker import Tracker

class TestProxy(unittest.IsolatedAsyncioTestCase):
    
    async def test_setup_proxies(self):
        tracker = Tracker()
        os.environ["USE_PROXY"] = "false"
        await tracker.startup()
        self.assertEqual(tracker.proxies, None)
        await tracker.shutdown()

class TestTrack(unittest.IsolatedAsyncioTestCase):

    async def test_track_one(self):
        tracker = Tracker()
        await tracker.startup()

        valid_id = "043510001997"
        invalid_id = "043510001998"

        result = await tracker.track_one(valid_id)

        self.assertEqual(result[valid_id].found, True)

        result = await tracker.track_one(invalid_id)

        self.assertEqual(result[invalid_id].found, False)

        await tracker.shutdown()

    async def test_track_many(self):
        tracker = Tracker()
        await tracker.startup()

        valid_ids = ["043510007024", "043510008212", "043510003174"]
        invalid_ids = ["043510007025", "043510007026", "043510007027"]

        result = await tracker.track_many(valid_ids)

        for id in valid_ids:
            self.assertEqual(result[id].found, True)

        result = await tracker.track_many(invalid_ids)

        for id in invalid_ids:
            self.assertEqual(result[id].found, False)

        await tracker.shutdown()

if __name__ == '__main__':
    unittest.main()