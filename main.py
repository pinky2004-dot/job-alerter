#entry point
import yaml
from jobs.google import GoogleJobScraper
from storage.file_store import load_jobs, save_jobs
from notifications.email import send_email
from utils.logger import logger

#maps company names to scraper classes
def get_scraper(company_name):
    if company_name == 'google':
        return GoogleJobScraper()
    # You can add more scrapers here
    return None

#filters by keywords
def filter_jobs(jobs, keywords):
    return [
        job for job in jobs
        if any(keyword.lower() in job['title'].lower() for keyword in keywords)
    ]

#builds the pipeline
def main():
    logger.info("Starting Job Alerter...") #logs to console/file

    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    stored_jobs = load_jobs()
    new_jobs_total = []

    for company in config['companies']:
        name = company['name']
        keywords = company['keywords']
        logger.info(f"Checking jobs for {name}...")

        scraper = get_scraper(name)
        if not scraper:
            logger.warning(f"No scraper found for {name}")
            continue

        fetched_jobs = scraper.fetch_jobs()
        seen_jobs = stored_jobs.get(name, [])

        seen_ids = {job['id'] for job in seen_jobs}
        new_jobs = [job for job in fetched_jobs if job['id'] not in seen_ids]
        filtered = filter_jobs(new_jobs, keywords)

        if filtered:
            logger.info(f"Found {len(filtered)} new jobs for {name}")
            message = "\n\n".join(f"{job['title']} - {job['url']}" for job in filtered)
            send_email(f"New {name.capitalize()} Jobs Found!", message) #sends notification
            seen_jobs.extend(filtered)
            stored_jobs[name] = seen_jobs
            new_jobs_total.extend(filtered)

    save_jobs(stored_jobs) #saves new jobs to file
    logger.info(f"Job Alerter completed. {len(new_jobs_total)} new jobs sent.")

if __name__ == "__main__":
    main()