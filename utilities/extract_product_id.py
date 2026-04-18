import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page.home_page import HomePage
from page.search_page import SearchPage
from utilities.read_config import ReadConfig
import time

def extract_id():
    product_name = "APPLE iPhone 15 (Black, 128 GB)"
    print(f"Searching for: {product_name}")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--start-maximized")
    options.add_argument("--headless") # Running headless for extraction
    
    profile_path = os.path.join(os.getcwd(), "chrome_profile")
    options.add_argument(f"--user-data-dir={profile_path}")
    
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get(ReadConfig.get_base_url())
        
        hp = HomePage(driver)
        hp.close_popup_if_present()
        hp.search_product(product_name)
        
        # Wait for search results
        wait = WebDriverWait(driver, 15)
        # Search for the product element by its text
        product_xpath = f"//*[contains(text(), '{product_name}')]"
        wait.until(EC.presence_of_element_located((By.XPATH, product_xpath)))
        
        # Find the parent div with 'data-id'
        # On Flipkart, usually the parent or grandparent of the title has data-id
        elements = driver.find_elements(By.XPATH, f"{product_xpath}/ancestor::div[@data-id]")
        
        if elements:
            pid = elements[0].get_attribute("data-id")
            print(f"\nSUCCESS: Unique ID (PID) for '{product_name}' is: {pid}")
            return pid
        else:
            # Try a broader search if ancestor didn't work
            print("Ancestor with data-id not found, trying broader search...")
            all_products = driver.find_elements(By.XPATH, "//div[@data-id]")
            for p in all_products:
                if product_name.lower() in p.text.lower():
                    pid = p.get_attribute("data-id")
                    print(f"\nSUCCESS: Unique ID (PID) found in broader search: {pid}")
                    return pid
            
            print("Could not find the specific product ID.")
            return None
            
    except Exception as e:
        print(f"Error extracting ID: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    extract_id()
