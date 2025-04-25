#company is google
#defines how it will scrape jobs from google's career page
import requests
from jobs.base import BaseJobScraper
from utils.logger import logger

class GoogleJobScraper(BaseJobScraper):
    def fetch_jobs(self):
        url = "https://careers.google.com/api/v3/search/"
        params = {
            "distance": 50,
            #"employment_type": "INTERN",
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

        data = response.json()
        job_results = data.get("jobs", [])
        jobs = []

        for job in job_results:
            job_id = f"google-{job.get('job_id')}"
            title = job.get('title')
            url = f"https://careers.google.com/jobs/results/{job.get('job_id')}/"
            posted_at = job.get('published_on')

            logger.debug(f"Job found: {title}")

            jobs.append({
                "id": job_id,
                "title": title,
                "url": url,
                "posted_at": posted_at
            })

        logger.info(f"Found {len(jobs)} Google jobs from API")
        return jobs