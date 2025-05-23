import unittest
from jobs.google import GoogleJobScraper

class TestGoogleScraper(unittest.TestCase):
    def test_fetch_jobs(self):
        scraper = GoogleJobScraper()
        jobs = scraper.fetch_jobs()

        self.assertIsInstance(jobs, list)
        if jobs:
            job = jobs[0]
            self.assertIn('id', job)
            self.assertIn('title', job)
            self.assertIn('url', job)
            self.assertIn('posted_at', job)

if __name__ == '__main__':
    unittest.main()