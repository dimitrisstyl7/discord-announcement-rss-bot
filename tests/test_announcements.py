import importlib.util
import logging
import os
import requests
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

SCRIPT = Path(__file__).resolve().parents[1] / "app" / "announcements-bot.py"
spec = importlib.util.spec_from_file_location("announcements_bot", SCRIPT)
bot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bot)


def entry(announcement_id):
    return SimpleNamespace(
        link=f"https://example.com/?an_id={announcement_id}",
        title=f"Announcement {announcement_id}",
        description="Content",
        published_parsed=None,
    )


class AnnouncementTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        bot.LAST_ANNOUNCEMENT_ID_FILE = os.path.join(self.directory.name, "last_announcement_id.txt")
        bot.RSS_URL = "https://example.com/feed"
        bot.ANNOUNCEMENTS_WEBHOOK_URL = "https://example.com/announcements"
        bot.ERRORS_WEBHOOK_URL = "https://example.com/errors"
        bot.logger = logging.getLogger("test")
        Path(bot.LAST_ANNOUNCEMENT_ID_FILE).write_text("1")

    @patch.object(bot.time, "sleep")
    @patch.object(bot.feedparser, "parse")
    @patch.object(bot.requests, "get")
    @patch.object(bot.requests, "post")
    def test_partial_failure_checkpoints_sent_messages_and_retries(self, post, get, parse, sleep):
        get.return_value = Mock(content=b"feed")
        parse.return_value = SimpleNamespace(entries=[entry("3"), entry("2"), entry("1")])
        post.side_effect = [Mock(), requests.exceptions.ConnectionError("failed"), Mock()]

        with self.assertRaises(requests.exceptions.ConnectionError):
            bot.fetch_announcements()

        self.assertEqual(Path(bot.LAST_ANNOUNCEMENT_ID_FILE).read_text(), "2")
        self.assertIn("Announcement 2", post.call_args_list[0].kwargs["json"]["content"])
        self.assertIn("Announcement 3", post.call_args_list[1].kwargs["json"]["content"])
        self.assertEqual(post.call_args_list[2].args[0], bot.ERRORS_WEBHOOK_URL)

        post.reset_mock(side_effect=True)
        post.return_value = Mock()
        bot.fetch_announcements()

        self.assertEqual(Path(bot.LAST_ANNOUNCEMENT_ID_FILE).read_text(), "3")
        self.assertEqual(post.call_count, 1)
        self.assertIn("Announcement 3", post.call_args.kwargs["json"]["content"])

    @patch.object(bot.time, "sleep")
    @patch.object(bot.feedparser, "parse")
    @patch.object(bot.requests, "get")
    @patch.object(bot.requests, "post")
    def test_failed_first_message_does_not_advance_checkpoint(self, post, get, parse, sleep):
        get.return_value = Mock(content=b"feed")
        parse.return_value = SimpleNamespace(entries=[entry("2"), entry("1")])
        post.side_effect = [requests.exceptions.ConnectionError("failed"), Mock()]

        with self.assertRaises(requests.exceptions.ConnectionError):
            bot.fetch_announcements()

        self.assertEqual(Path(bot.LAST_ANNOUNCEMENT_ID_FILE).read_text(), "1")

    def test_script_fetches_once_and_exits(self):
        with patch.dict(
                os.environ, {
                    "LAST_ANNOUNCEMENT_ID_DIR": self.directory.name,
                    "RSS_URL": "https://example.com/feed",
                },
        ), patch("requests.get") as get, \
                patch("feedparser.parse", return_value=SimpleNamespace(entries=[])):
            get.return_value = Mock(content=b"feed")
            runpy.run_path(str(SCRIPT), run_name="__main__")

        get.assert_called_once()

    def test_script_propagates_fetch_failure(self):
        with patch.dict(
                os.environ, {
                    "LAST_ANNOUNCEMENT_ID_DIR": self.directory.name,
                    "RSS_URL": "https://example.com/feed",
                },
        ), patch("requests.get", side_effect=requests.exceptions.ConnectionError("failed")), \
                patch("requests.post", return_value=Mock()):
            with self.assertRaises(requests.exceptions.ConnectionError):
                runpy.run_path(str(SCRIPT), run_name="__main__")


if __name__ == "__main__":
    unittest.main()
