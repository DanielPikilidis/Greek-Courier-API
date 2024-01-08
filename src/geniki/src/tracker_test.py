import unittest, os

from tracker import Tracker

class TestProxy(unittest.IsolatedAsyncioTestCase):
    
    async def test_setup_proxies(self):
        tracker = Tracker()
        os.environ["USE_PROXY"] = "false"
        await tracker.startup()
        self.assertEqual(tracker.proxy_queue, None)
        await tracker.shutdown()


class TestTrack(unittest.IsolatedAsyncioTestCase):

    async def test_track_one(self):
        tracker = Tracker()
        await tracker.startup()

        invalid_id = "1111111111"

        result = await tracker.track_one(invalid_id)

        self.assertEqual(result[invalid_id].found, False)

        await tracker.shutdown()

    async def test_track_many(self):
        tracker = Tracker()
        await tracker.startup()

        invalid_ids = ["1111111111", "1111111112", "1111111113"]

        result = await tracker.track_many(invalid_ids)

        for id in invalid_ids:
            self.assertEqual(result[id].found, False)

        await tracker.shutdown()

if __name__ == '__main__':
    unittest.main()