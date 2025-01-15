def visit_website(url: str):
  """
  Open a specific website with the default browser.
  
  Args:
    url: The website URL to visit.
  
  Returns:
    A string that says the website has been opened.
  """
  import subprocess
  import platform

  print(f'🤵🏻 Opening your browser and visiting {url}...\n')

  if platform.system() == 'Darwin':  # macOS
    subprocess.run(["open", url])
  elif platform.system() == 'Windows':  # Windows
    subprocess.run(["start", url], shell=True)
  else:  # Linux and others
    subprocess.run(["xdg-open", url])

  return f"I have opened {url}."

def scrape_source(url: str):
  """
  Scrape the source of a given website.
  
  Args:
    url: The website URL to scrape.
  
  Returns:
    A string containing the path to the website source, or if it fails, a string that says it failed.
  """
  import requests
  from bs4 import BeautifulSoup

  print(f'🤵🏻 Scraping the web source of {url}...\n')

  response = requests.get(url)
  if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    with open("temp/temp.html", "w") as temp_file:
      temp_file.write(soup.prettify())
    return "temp/temp.html"
  else:
    return "Failed to scrape the website source."
    
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def scrape_dynamic_source(url: str):
  """
  Scrape the source of a dynamically loaded website using Selenium.
  
  Args:
    url: The website URL to scrape.
  
  Returns:
    A string containing the path to the website source, or if it fails, a string that says it failed.
  """

  print(f'🤵🏻 Scraping the web source of {url} with Selenium...\n')

  try:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize Chrome driver with webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    
    # Allow time for dynamic content to load
    time.sleep(5)
    
    # Get the page source after JavaScript execution
    page_source = driver.page_source
    
    # Save to a temporary file
    output_path = "temp/temp.html"
    with open(output_path, "w") as temp_file:
        temp_file.write(page_source)
    
    driver.quit()
    return output_path
  except Exception as e:
    return f"Failed to scrape the dynamic website source. Error: {e}"