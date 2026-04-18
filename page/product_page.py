from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utilities.logger import setup_logger
import time
import os

logger = setup_logger()

class ProductPage(BasePage):
    # Robust Add to Cart locators
    add_to_cart_btn = (By.XPATH, (
        '//*[@id="slot-list-container"]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div[19]/div/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[2]/div | '
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')] | "
        "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'add to cart')] | "
        "//button[contains(.,'Add to Cart')] | "
        "//button[contains(.,'ADD TO CART')] | "
        "//button[contains(.,'Add to cart')] | "
        "//button[@aria-label='Add to Cart'] | "
        "//*[contains(@class, 'QqFHMw')]//button | "
        "//button[contains(@class, 'QqFHMw') or contains(@class, 'vS779D') or contains(@class, 'AT0mb0') or (contains(@class, '_2KpZ6l') and (contains(., 'CART') or contains(., 'Cart')))]"
    ))
    go_to_cart_btn = (By.XPATH, (
        "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'go to cart')] | "
        "//button[contains(.,'Go to Cart')] | "
        "//button[contains(.,'GO TO CART')] | "
        "//button[text()='Go to cart'] | "
        "//button[@aria-label='Go to Cart'] | "
        "//button[@aria-label='GO TO CART'] | "
        "//button[contains(@class, 'QqFHMw') and (contains(., 'CART') or contains(., 'Cart'))] | "
        "//button[contains(@class, 'L_V696')]"
    ))
    out_of_stock = (By.XPATH, "//*[contains(text(), 'OUT OF STOCK') or contains(text(), 'Sold Out') or contains(text(), 'NOTIFY ME')]")
    buy_now_btn = (By.XPATH, (
        '//*[@id="slot-list-container"]/div/div[2]/div/div/div/div[1]/div/div[2]/div/div[19]/div/div/div/div/div/div/div/div/div/div[2]/div[2]/div/div/div/div[1]/div | '
        "//button[contains(.,'Buy Now')] | "
        "//button[contains(.,'BUY NOW')] | "
        "//button[text()='Buy now'] | "
        "//button[@aria-label='Buy Now'] | "
        "//button[@aria-label='BUY NOW'] | "
        "//button[contains(@class, 'QqFHMw') and (contains(., 'BUY') or contains(., 'Buy'))] | "
        "//button[contains(@class, 'p8d96r')] | "
        "//button[contains(@class, 'L_V696')] | "
        "//button[contains(@class, '_2KpZ6l') and contains(@class, '_2U9u47')] | "
        "//button[contains(@class, '_2KpZ6l') and contains(@class, '_3A98W2')]"
    ))

    # Common Flipkart selectors for sizes/variations
    size_options = (By.XPATH, "//ul[contains(@class, '_1q8A91')]//li | //div[contains(@class, '_30_8By')] | //a[contains(@class, '_1f332o')] | //div[contains(text(), 'Select Size')]/..//li")

    def _find_button_dynamically(self, keywords):
        """Find a button on the page that contains any of the keywords in text or attributes."""
        # Check main content first
        all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
        all_links = self.driver.find_elements(By.TAG_NAME, "a")
        
        for el in (all_buttons + all_links):
            try:
                if not el.is_displayed():
                    continue
                
                # Check text, aria-label, and classes
                content = (el.text + " " + 
                          (el.get_attribute("aria-label") or "") + " " + 
                          (el.get_attribute("class") or "")).lower()
                
                if any(kw.lower() in content for keywords_list in keywords for kw in keywords_list):
                    # For Add to Cart, avoid "Go to Cart"
                    if "add" in keywords[0] and "go to" in content:
                        continue
                    return el
            except:
                continue
        
        # If not found, try recursive frame search with keywords
        return self._search_in_frames_by_keywords(keywords)

    def _search_in_frames_by_keywords(self, keywords):
        frames = self.driver.find_elements(By.TAG_NAME, "iframe") + \
                 self.driver.find_elements(By.TAG_NAME, "frame")
        
        for frame in frames:
            try:
                self.driver.switch_to.frame(frame)
                time.sleep(1)
                
                all_els = self.driver.find_elements(By.TAG_NAME, "button") + \
                          self.driver.find_elements(By.TAG_NAME, "a")
                
                for el in all_els:
                    if el.is_displayed():
                        content = (el.text + " " + 
                                  (el.get_attribute("aria-label") or "") + " " + 
                                  (el.get_attribute("class") or "")).lower()
                        if any(kw.lower() in content for keywords_list in keywords for kw in keywords_list):
                            if "add" in keywords[0] and "go to" in content:
                                continue
                            return el
                
                res = self._search_in_frames_by_keywords(keywords)
                if res: return res
                
                self.driver.switch_to.parent_frame()
            except:
                try: self.driver.switch_to.parent_frame()
                except: self.driver.switch_to.default_content()
        return None

    def click_add_to_cart(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        try:
            # 1. Out of Stock check
            out_elements = self.driver.find_elements(*self.out_of_stock)
            if any(el.is_displayed() for el in out_elements):
                logger.warning("Product OUT OF STOCK")
                return "OUT OF STOCK"

            # 2. Already in cart check
            go_to = self._find_button_dynamically([["go to cart", "go to bag"]])
            if go_to:
                logger.info("Product already in cart")
                return "Product is already present in the cart section"
            
            # 3. Size selection
            sizes = self.driver.find_elements(*self.size_options)
            visible_sizes = [s for s in sizes if s.is_displayed()]
            if visible_sizes:
                logger.info(f"Selecting size...")
                try: visible_sizes[0].click()
                except: self.driver.execute_script("arguments[0].click();", visible_sizes[0])
                time.sleep(2)

            # 4. Find Add button
            btn = self._find_button_dynamically([["add to cart", "add to bag", "add to basket"]])
            
            if not btn:
                # Last resort fallback to specific XPaths
                try:
                    btn = wait.until(EC.element_to_be_clickable(self.add_to_cart_btn))
                except:
                    pass

            if not btn:
                raise Exception("Could not find Add to Cart/Bag button dynamically")

            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
            time.sleep(1)
            try: btn.click()
            except: self.driver.execute_script("arguments[0].click();", btn)
            
            logger.info("Clicked Add button")
            self.driver.switch_to.default_content()
            time.sleep(5)
            return "SUCCESS"
            
        except Exception as e:
            self.driver.switch_to.default_content()
            ts = int(time.time())
            self.driver.save_screenshot(f"screenshots/add_failed_{ts}.png")
            logger.error(f"Add to Cart failed: {e}")
            raise e

    def click_buy_now(self):
        wait = WebDriverWait(self.driver, 10)
        
        # Ensure page is loaded
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        
        try:
            # 1. Check if Out of Stock
            try:
                out_elements = self.driver.find_elements(*self.out_of_stock)
                for el in out_elements:
                    if el.is_displayed():
                        logger.warning("Product is OUT OF STOCK or NOT AVAILABLE")
                        return
            except:
                pass
            
            # 2. Try finding Buy Now button in main content (shorter wait)
            btn = None
            try:
                temp_wait = WebDriverWait(self.driver, 5)
                elements = temp_wait.until(EC.presence_of_all_elements_located(self.buy_now_btn))
                for el in elements:
                    if el.is_displayed():
                        btn = el
                        break
            except:
                logger.info("Buy Now button not found in main content, searching in frames...")

            # 3. If not found, search in all frames (recursive)
            if not btn:
                btn = self._search_in_frames_recursive(self.buy_now_btn)

            if not btn:
                # Final attempt: scroll and try again
                self.driver.switch_to.default_content()
                self.driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                elements = self.driver.find_elements(*self.buy_now_btn)
                for el in elements:
                    if el.is_displayed():
                        btn = el
                        break

            if not btn:
                raise Exception("Buy Now button not found on product page even after searching frames")

            # Ensure it's in view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", btn)
            time.sleep(1)
            
            # Click using JavaScript
            self.driver.execute_script("arguments[0].click();", btn)
            logger.info("Clicked Buy Now button")
            
            # Switch back to default content
            self.driver.switch_to.default_content()
            
            # Wait for transition
            time.sleep(3)
            
        except Exception as e:
            self.driver.switch_to.default_content()
            timestamp = int(time.time())
            self.driver.save_screenshot(f"screenshots/buy_now_failed_{timestamp}.png")
            # Save HTML source for debugging
            with open(f"screenshots/buy_now_failed_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            logger.error(f"Error clicking Buy Now: {e}")
            raise e

    def _search_in_frames_recursive(self, locator):
        """Helper to search for an element in all frames recursively."""
        # Get all frames in current context
        frames = self.driver.find_elements(By.TAG_NAME, "iframe") + \
                 self.driver.find_elements(By.TAG_NAME, "frame")
        
        for frame in frames:
            try:
                self.driver.switch_to.frame(frame)
                # Small wait for frame content
                time.sleep(1)
                
                # Check for button in this frame
                btns = self.driver.find_elements(*locator)
                for b in btns:
                    if b.is_displayed():
                        frame_info = "unnamed"
                        try:
                            frame_info = frame.get_attribute('id') or frame.get_attribute('name') or "unnamed"
                        except:
                            pass
                        logger.info(f"Found button in frame: {frame_info}")
                        return b
                
                # Recursive search in sub-frames
                btn = self._search_in_frames_recursive(locator)
                if btn:
                    return btn
                
                # Go back to parent context for next sibling frame
                self.driver.switch_to.parent_frame()
            except:
                # On error, try to get back to parent
                try:
                    self.driver.switch_to.parent_frame()
                except:
                    self.driver.switch_to.default_content()
                    return None
        
        return None

