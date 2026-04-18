import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page.home_page import HomePage
from page.search_page import SearchPage
from page.product_page import ProductPage
from utilities.logger import setup_logger

logger = setup_logger()

@pytest.mark.buynow
class TestBuyNow:

    def test_buy_iphone_15(self, login_session):
        driver = login_session
        search_term = "iphone15"
        specific_product_name = "APPLE iPhone 15 (Black, 128 GB)"
        
        logger.info(f"--- Starting Buy Now test for product: {specific_product_name} ---")
        
        # 1. Clear other tabs
        if len(driver.window_handles) > 1:
            for window_handle in driver.window_handles[1:]:
                driver.switch_to.window(window_handle)
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Ensure we are on home page
        driver.get("https://www.flipkart.com")

        # 2. Search product
        hp = HomePage(driver)
        hp.close_popup_if_present()
        hp.search_product(search_term)

        # 3. Click specific product using provided XPath (No scrolling)
        try:
            product_xpath = '//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div/div/a/div[2]/div[1]/div/div/img'
            
            # Wait for the product image to be present
            wait = WebDriverWait(driver, 15)
            product_element = wait.until(EC.presence_of_element_located((By.XPATH, product_xpath)))
            
            # Capture current window handles before click
            old_handles = driver.window_handles
            
            # Click the product
            try:
                product_element.click()
            except:
                driver.execute_script("arguments[0].click();", product_element)
            logger.info("Clicked on product image using specific XPath")
            
            # Wait for and switch to new tab
            wait.until(lambda d: len(d.window_handles) > len(old_handles))
            for handle in driver.window_handles:
                if handle not in old_handles:
                    driver.switch_to.window(handle)
                    logger.info("Switched to product tab")
                    break
            
            # 4. Click Buy Now using ProductPage (which now includes your specific XPath)
            pp = ProductPage(driver)
            pp.click_buy_now()
            logger.info("Successfully clicked Buy Now using specific XPath")
            
        except Exception as e:
            logger.error(f"Failed during Buy Now test execution: {e}")
            pytest.fail(f"Test failed: {e}")

        time.sleep(5) # Wait to see the result
