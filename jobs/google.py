#company is google
#defines how it will scrape jobs from google's career page
import requests
from jobs.base import BaseJobScraper
from utils.logger import logger
from datetime import datetime, timezone

class GoogleJobScraper(BaseJobScraper):
    def fetch_jobs(self):
        url = "https://careers.google.com/api/v3/search/"
        params = {
            "distance": 50,
            "employment_type": "INTERN",
            "language": "en",
            "company": "Google",
            "page": 1
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        logger.info(f"Fetching Google jobs from API: {url}")

        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to retrieve jobs from API. Status code: {response.status_code}")
            return []

        try:
            data = response.json()
        except ValueError:
            logger.error("Invalid JSON response received.")
            return []

        job_results = data.get("jobs", [])
        today = datetime.now(timezone.utc).date()
        jobs = []

        for job in job_results:
            job_raw_id = job.get("id")  # format: "jobs/110690555461018310"
            if not job_raw_id or not job_raw_id.startswith("jobs/"):
                logger.warning("Skipping job with malformed ID.")
                continue

            posted_at = job.get("publish_date")
            if not posted_at:
                logger.debug(f"Skipping job due to missing publish_date: {job_raw_id}")
                continue

            try:
                post_date = datetime.fromisoformat(posted_at.rstrip("Z")).date()
                if post_date != today:
                    continue  # Skip if not posted today
            except Exception as e:
                logger.warning(f"Invalid publish_date format for job {job_raw_id}: {e}")
                continue

            job_id = f"google-{job_raw_id.split('/')[-1]}"
            title = job.get("title", "No title")
            apply_url = job.get("apply_url")

            if not apply_url or not posted_at:
                logger.debug(f"Skipping job due to missing apply_url or publish_date: {job_id}")
                continue

            job_entry = {
                "id": job_id,
                "title": title,
                "url": apply_url,
                "posted_at": posted_at
            }

            jobs.append(job_entry)

        logger.info(f"Found {len(jobs)} Google jobs from API.")
        return jobs