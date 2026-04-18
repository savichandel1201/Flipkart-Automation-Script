from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utilities.logger import setup_logger

logger = setup_logger()


class SearchPage(BasePage):

    products = (By.XPATH, "//div[@data-id] | //div[contains(@class, 'cPHDOP')] | //div[contains(@class, 'sl-so-search-result')] | //div[contains(@class, '_75_9eb')] | //div[contains(@class, '_1AtVbE')] | //div[contains(@class, '_4ddWXP')]")

    def get_product_count(self):
        try:
            # Wait for at least one product
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located(self.products))
            elements = self.driver.find_elements(*self.products)
            
            # Filter for visible elements
            count = 0
            for el in elements:
                if el.is_displayed():
                    # If it's visible and matches our broad locators, we count it
                    count += 1
            return count
        except:
            return 0

    def click_first_product(self):
        # Wait for products to be present
        wait = WebDriverWait(self.driver, 15)
        elements = wait.until(EC.presence_of_all_elements_located(self.products))
        
        target = None
        for el in elements:
            try:
                if el.is_displayed():
                    target = el
                    break
            except:
                continue
        
        if target:
            # Scroll to it
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
            import time
            time.sleep(2)
            
            # Click the first product and switch to the new window/tab
            old_handles = self.driver.window_handles
            
            # Use both normal click and JS click if needed
            try:
                target.click()
            except:
                self.driver.execute_script("arguments[0].click();", target)
            
            # Wait for the new window/tab to open
            try:
                wait.until(lambda d: len(d.window_handles) > len(old_handles))
                new_handles = self.driver.window_handles
                for handle in new_handles:
                    if handle not in old_handles:
                        self.driver.switch_to.window(handle)
                        logger.info("Switched to new product tab")
                        break
            except:
                logger.warning("No new tab detected after clicking product")
        else:
            raise Exception("No visible products found to click")

    def click_product_by_name(self, product_name):
        # Wait for products to be present
        wait = WebDriverWait(self.driver, 15)
        wait.until(EC.presence_of_all_elements_located(self.products))

        # Scroll down to find the product
        found = False
        import time

        # Create variations of the name for better matching
        search_terms = [product_name]
        if "(" in product_name:
            search_terms.append(product_name.split("(")[0].strip())
        if "," in product_name:
            search_terms.append(product_name.split(",")[0].strip())

        logger.info(f"Searching for product with terms: {search_terms}")

        for i in range(10): # Scroll 10 times
            for term in search_terms:
                try:
                    # Specific Flipkart product name locators
                    locators = [
                        f"//div[contains(text(), '{term}')]",
                        f"//a[contains(., '{term}')]",
                        f"//*[normalize-space(text())='{term}']",
                        f"//div[contains(@class, 'KzDlHZ') and contains(text(), '{term}')]", # Common Flipkart class for titles
                        f"//a[contains(@class, 'w_U_Wb') and contains(., '{term}')]"
                    ]

                    for xpath in locators:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        for element in elements:
                            if element.is_displayed():
                                logger.info(f"Found product element with XPath: {xpath}")
                                # Scroll into view
                                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                time.sleep(2)

                                original_window = self.driver.current_window_handle
                                old_handles = self.driver.window_handles

                                # Click the product
                                try:
                                    element.click()
                                except:
                                    self.driver.execute_script("arguments[0].click();", element)

                                # Wait and switch to new window
                                try:
                                    WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > len(old_handles))
                                    for window_handle in self.driver.window_handles:
                                        if window_handle not in old_handles:
                                            self.driver.switch_to.window(window_handle)
                                            logger.info("Switched to new product tab")
                                            break
                                    found = True
                                    break
                                except:
                                    # If no new window, maybe it's in the same tab
                                    logger.warning("No new window opened, continuing in same tab")
                                    found = True
                                    break
                        if found: break
                    if found: break
                except Exception as e:
                    continue

            if found: break

            # Scroll down
            logger.info(f"Product not found in view, scrolling down (Attempt {i+1}/10)...")
            self.driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)

        if not found:
            raise Exception(f"Product matching '{product_name}' not found on search results page after exhaustive scrolling")