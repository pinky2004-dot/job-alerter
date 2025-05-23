#base scraper class that other scraper classes will inherit from
class BaseJobScraper: #abstract class
    def fetch_jobs(self):
        """
        Fetch job postings from the company's career page.
        This method should be overridden in child classes (e.g., GoogleJobScraper).
        """
        raise NotImplementedError("Subclasses should implement this method")