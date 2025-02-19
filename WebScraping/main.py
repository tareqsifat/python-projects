from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class PythonOrgScraper:
    def __init__(self, driver):
        """Initialize the scraper with a Selenium WebDriver instance."""
        self.driver = driver

    def open_homepage(self):
        """Navigate to the Python.org homepage."""
        self.driver.get("https://www.python.org/")

    def go_to_events_page(self):
        """Find and click on the 'Events' link."""
        events_link = self.driver.find_element(By.XPATH, "//li[@id='events']//a")
        events_link.click()

    def get_upcoming_events(self):
        """Retrieve and return the names of upcoming events."""
        upcoming_events = self.driver.find_elements(By.XPATH, "//ul[@class='list-recent-events menu']/li")
        return [event.find_element(By.TAG_NAME, "h3").text for event in upcoming_events]

    def close(self):
        """Close the browser."""
        self.driver.quit()

if __name__ == "__main__":
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (optional)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    scraper = PythonOrgScraper(driver)
    try:
        scraper.open_homepage()
        scraper.go_to_events_page()
        events = scraper.get_upcoming_events()
        for event in events:
            print(event)
    finally:
        scraper.close()
