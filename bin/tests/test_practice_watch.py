"""Feed parsing for bin/practice-watch, run offline."""
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parent.parent / "practice-watch"
loader = importlib.machinery.SourceFileLoader("practice_watch", str(SCRIPT))
spec = importlib.util.spec_from_loader("practice_watch", loader)
watch = importlib.util.module_from_spec(spec)
loader.exec_module(watch)

ATOM = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>yt:video:abc</id>
<title>Video</title><link rel="related" href="https://example.com/related"/>
<link rel="alternate" href="https://www.youtube.com/watch?v=abc"/>
<published>2026-11-18T17:01:17+00:00</published></entry></feed>"""
RSS = b"""<rss><channel><item><guid>p1</guid><title>Post</title>
<link>https://example.com/p1</link><pubDate>Tue, 18 Nov 2026 09:00:00 -0800</pubDate>
</item></channel></rss>"""


class ParseFeed(unittest.TestCase):
    def test_atom_prefers_the_alternate_link(self):
        # WHY: an Element with no children is falsy, so `find(alternate) or
        # find(link)` fell through to the first link of any rel.
        [item] = watch.parse_feed(ATOM)
        self.assertEqual(item["url"], "https://www.youtube.com/watch?v=abc")

    def test_rss_dates_become_comparable_utc(self):
        # WHY: the age filter compares strings; RFC 822 dates never compared
        # correctly against the ISO cutoff before normalisation.
        [item] = watch.parse_feed(RSS)
        self.assertEqual(item["published"], "2026-11-18T17:00:00Z")
        self.assertLess("2026-11-04T00:00:00Z", item["published"])

    def test_unparseable_date_is_empty_not_an_error(self):
        self.assertEqual(watch.iso_utc("sometime last week"), "")


if __name__ == "__main__":
    unittest.main()
