import unittest, os

from tracker import Tracker

class TestProxy(unittest.IsolatedAsyncioTestCase):
    
    async def test_setup_proxies(self):
        tracker = Tracker(max_pages=1)
        os.environ["USE_PROXY"] = "false"
        await tracker.startup()
        self.assertEqual(tracker.proxy, None)
        await tracker.shutdown()


class TestTrack(unittest.IsolatedAsyncioTestCase):

    async def test_track_one(self):
        tracker = Tracker(max_pages=1)
        await tracker.startup()

        valid_id = "7581129625"
        invalid_id = "7581129626"

        result = await tracker.track_one(valid_id)

        self.assertEqual(result[valid_id].found, True)

        result = await tracker.track_one(invalid_id)

        self.assertEqual(result[invalid_id].found, False)

        await tracker.shutdown()

    async def test_track_many(self):
        tracker = Tracker(max_pages=1)
        await tracker.startup()

        valid_ids = ["7581129625", "7581124014", "7581121041"]
        invalid_ids = ["7581129626", "7581129627", "7581129628"]

        result = await tracker.track_many(valid_ids)

        for id in valid_ids:
            self.assertEqual(result[id].found, True)

        result = await tracker.track_many(invalid_ids)

        for id in invalid_ids:
            self.assertEqual(result[id].found, False)

        await tracker.shutdown()

if __name__ == '__main__':
    unittest.main()