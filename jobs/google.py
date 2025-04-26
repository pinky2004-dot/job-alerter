#company is google
#defines how it will scrape jobs from google's career page
import requests
from jobs.base import BaseJobScraper
from utils.logger import logger
from datetime import datetime, timezone

class GoogleJobScraper(BaseJobScraper):
    def fetch_jobs(self):
        url = "https://careers.google.com/api/v3/search/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        today = datetime.now(timezone.utc).date()
        all_jobs = []
        page = 1

        while True:
            params = {
                "language": "en",
                "page": page
            }

            logger.info(f"Fetching Google jobs from API: {url} (page {page})")

            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                logger.error(f"Failed to retrieve jobs from API. Status code: {response.status_code}")
                break

            try:
                data = response.json()
            except ValueError:
                logger.error("Invalid JSON response received.")
                break

            job_results = data.get("jobs", [])
            if not job_results:
                logger.info("No more jobs found, ending pagination.")
                break  # no more jobs -> stop looping

            for job in job_results:
                job_raw_id = job.get("id")
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

                all_jobs.append(job_entry)

            page += 1  # go to next page

        logger.info(f"Found {len(all_jobs)} Google jobs posted today from API.")
        return all_jobs