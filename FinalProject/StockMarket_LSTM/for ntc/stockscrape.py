from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import csv
import time

def scrape_page(driver):
    # Wait for the table to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "table-bordered")))
    
    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='table-bordered')
    
    data = []
    for row in table.find_all('tr')[1:]:  # Skip the header row
        cols = row.find_all('td')
        if len(cols) == 9:
            data.append([col.text.strip() for col in cols])
    
    return data

def main():
    url = "https://merolagani.com/CompanyDetail.aspx?symbol=NTC#0"
    driver = webdriver.Chrome()  
    driver.get(url)

    # Click the "Price History" button
    price_history_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_CompanyDetail1_lnkHistoryTab"))
    )
    price_history_button.click()
    time.sleep(2)  # Wait for the page to load

    all_data = []
    num_pages = 5  # Change this to the number of pages you want to scrape
    for page in range(1, num_pages + 1):
        print(f"Scraping page {page}")
        
        if page > 1:
            # Click on the next page
            next_page = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@title='Page {page}']"))
            )
            next_page.click()
            time.sleep(2)  # Wait for the page to load
        
        page_data = scrape_page(driver)
        all_data.extend(page_data)

    driver.quit()

    # Write data to CSV file
    with open('ntc_price_history.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['#', 'Date', 'LTP', '% Change', 'High', 'Low', 'Open', 'Qty.', 'Turnover'])
        writer.writerows(all_data)

    print(f"Data has been scraped and saved to ntc_price_history.csv")

if __name__ == "__main__":
    main()