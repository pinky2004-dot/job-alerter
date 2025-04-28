# company is glassdoor
# defines how it will scrape jobs from glassdoor's career page
import requests
from bs4 import BeautifulSoup
import hashlib
from datetime import datetime
from datetime import timedelta
import time  # Import the time module
from utils.logger import logger  # Import the logger

class GlassdoorJobScraper:
    def __init__(self):
        self.base_url = "https://www.glassdoor.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.6422.141 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        self.max_retries = 3
        self.retry_delay = 5

    def fetch_jobs(self, job_title="Software Engineer", location="United States", num_pages=5):
        """
        Fetches job listings from Glassdoor for a given job title and location.

        Args:
            job_title (str): The job title to search for.
            location (str): The location to search in.
            num_pages (int): The number of pages to scrape.  Glassdoor limits this.

        Returns:
            list: A list of dictionaries, where each dictionary represents a job listing.
                    Returns an empty list on error.
        """
        all_jobs = []
        for page in range(1, num_pages + 1):
            url = f"{self.base_url}/Job/jobs.htm?sc.keyword={job_title.replace(' ', '+')}&locT=C&locId=1&page={page}"  # US
            if location != "United States":  # add support for other locations.
                url = f"{self.base_url}/Job/jobs.htm?sc.keyword={job_title.replace(' ', '+')}&locT=C&locId=1&page={page}"

            logger.info(f"Fetching Glassdoor jobs from: {url}")
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(url, headers=self.headers)
                    if response.status_code == 200:
                        soup = BeautifulSoup(
                            response.content, 'html.parser')
                        job_listings = self.extract_job_listings(soup)
                        if not job_listings:
                            logger.info("No more job listings found on this page.")
                            break
                        all_jobs.extend(job_listings)
                        break
                    else:
                        logger.error(
                            f"Failed to retrieve jobs from Glassdoor. Status code: {response.status_code}")
                        if attempt < self.max_retries - 1:
                            logger.info(
                                f"Retrying in {self.retry_delay} seconds...")
                            time.sleep(self.retry_delay)
                            self.retry_delay *= 2
                        else:
                            logger.error(
                                "Max retries reached. Skipping this page.")
                            return all_jobs
                except requests.exceptions.RequestException as e:
                    logger.error(f"Error making request: {e}")
                    if attempt < self.max_retries - 1:
                        logger.info(
                            f"Retrying in {self.retry_delay} seconds...")
                        time.sleep(self.retry_delay)
                        self.retry_delay *= 2
                    else:
                        logger.error("Max retries reached. Skipping this page.")
                        return []
            self.retry_delay = 5
        return all_jobs

    def extract_job_listings(self, soup):
        """
        Extracts job listings from a Glassdoor search results page.

        Args:
            soup (BeautifulSoup): The parsed HTML of the search results page.

        Returns:
            list: A list of job dictionaries, or an empty list if no jobs are found.
        """
        job_list = []
        try:
            job_cards = soup.find_all('li', class_='react-job-listing')
            if not job_cards:
                return []
            for card in job_cards:
                try:
                    title_element = card.find('a', class_='jobLink')
                    title = title_element.text.strip() if title_element else "N/A"
                    job_url = self.base_url + \
                        title_element['href'] if title_element and title_element.has_attr(
                            'href') else "N/A"
                    company_name_element = card.find(
                        'div', class_='employerName')
                    company_name = company_name_element.text.strip() if company_name_element else "N/A"
                    location_element = card.find('div', class_='location')
                    location = location_element.text.strip() if location_element else "N/A"
                    date_posted_element = card.find(
                        'span', attrs={'data-test': 'job-age'})
                    date_posted = date_posted_element.text.strip() if date_posted_element else "N/A"
                    posted_at = self.convert_relative_date(date_posted)
                    job_id = hashlib.md5(job_url.encode()).hexdigest()
                    job_entry = {
                        "id": job_id,
                        "title": title,
                        "company_name": company_name,
                        "location": location,
                        "url": job_url,
                        "posted_at": posted_at,
                    }
                    job_list.append(job_entry)
                except AttributeError as e:
                    logger.warning(
                        f"Skipping a job listing due to missing data: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting job listings: {e}")
            return []
        return job_list

    def convert_relative_date(self, relative_date):
        """
        Converts a relative date string (e.g., "1d", "2h", "3w") to an ISO 8601 datetime string.

        Args:
            relative_date (str): The relative date string.

        Returns:
            str: An ISO 8601 datetime string, or "N/A" if conversion fails.
        """
        if relative_date == "Just now" or relative_date == "Today":
            return datetime.now().isoformat()
        elif "h" in relative_date:
            hours = int(relative_date.replace("h", ""))
            return (datetime.now() - timedelta(hours=hours)).isoformat()
        elif "d" in relative_date:
            days = int(relative_date.replace("d", ""))
            return (datetime.now() - timedelta(days=days)).isoformat()
        elif "w" in relative_date:
            weeks = int(relative_date.replace("w", ""))
            return (datetime.now() - timedelta(weeks=weeks)).isoformat()
        elif "m" in relative_date:
            months = int(relative_date.replace("m", ""))
            return (datetime.now() - timedelta(weeks=weeks*4)).isoformat()
        else:
            return "N/A"