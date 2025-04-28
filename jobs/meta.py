# company is meta
# defines how it will scrape jobs from Meta's career page
import requests
from jobs.base import BaseJobScraper
from utils.logger import logger
from datetime import datetime, timezone
from seleniumwire import webdriver
from seleniumwire.utils import decode
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json

class MetaJobScraper(BaseJobScraper):
    def fetch_jobs(self):
        url = "https://www.metacareers.com/jobs/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        logger.info(f"Fetching Meta jobs from API: {url}")

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            # Wait for requests to populate
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            jobs = []

            for request in driver.requests:
                if request.response and "graphql" in request.url:
                    body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                    logger.info(f"Response body: {body}")

                    try:
                        parsed = json.loads(body).get("data", {})

                        # Check for job results in multiple places
                        job_results = (
                            parsed.get("job_search_with_featured_jobs", {}).get("all_jobs", []) or
                            parsed.get("job_search", {}).get("all_jobs", []) or
                            []
                        )

                        today = datetime.now(timezone.utc).date()

                        for job in job_results:
                            job_raw_id = job.get("id")
                            if not job_raw_id:
                                logger.warning("Skipping job with missing ID.")
                                continue

                            posted_at = job.get("posted_at")
                            if not posted_at:
                                logger.debug(f"Skipping job due to missing posted_at: {job_raw_id}")
                                continue

                            try:
                                post_date = datetime.fromisoformat(posted_at.rstrip("Z")).date()
                                if post_date != today:
                                    continue  # Only consider jobs posted today
                            except ValueError as e:
                                logger.warning(f"Invalid posted_at format for job {job_raw_id}: {e}")
                                continue

                            title = job.get("title", "No title")
                            apply_url = f"https://www.metacareers.com/jobs/{job_raw_id}"
                            location = job.get("locations", ["N/A"])[0]

                            job_entry = {
                                "id": f"meta-{job_raw_id}",
                                "title": title,
                                "url": apply_url,
                                "posted_at": posted_at,
                                "location": location
                            }

                            jobs.append(job_entry)

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error while parsing jobs: {e}")

            driver.quit()
            logger.info(f"Found {len(jobs)} Meta jobs posted today.")
            return jobs

        except Exception as e:
            logger.error(f"Error while fetching Meta jobs: {e}")
            driver.quit()
            return []