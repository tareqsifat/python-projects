from selenium import webdriver
from selenium.webdriver.common.by import By

# Specify the path to your ChromeDriver executable
driver_path = "/usr/bin/chromedriver"

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(executable_path=driver_path)

# Navigate to the Python website
driver.get("https://www.python.org/")

# Find the "Events" link and click on it
events_link = driver.find_element(By.XPATH, "//li[@id='events']//a")
events_link.click()

# Find and print the names of upcoming events
upcoming_events = driver.find_elements(By.XPATH, "//ul[@class='list-recent-events menu']/li")
for event in upcoming_events:
    event_name = event.find_element(By.TAG_NAME, "h3").text
    print(event_name)

# Close the browser
driver.quit()
