from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CartPage(BasePage):
    # More specific and updated Flipkart cart item selectors
    cart_items = (By.XPATH, (
        "//div[contains(@class, 'V6899x')] | "
        "//div[contains(@class, 'c2Y_vV')] | "
        "//div[@class='_2n9Y98'] | "
        "//a[contains(@href, '/p/')] | "
        "//div[contains(@class, 'ov_t6e')] | " # New class for cart items
        "//div[contains(@class, 'fS7688')] | " # Another possible class
        "//div[contains(@class, '_1AtVbE') and .//button[text()='Remove']] | " # Items with Remove button
        "//div[contains(@class, 'idDDkQ')] | " # Fashion item class
        "//div[contains(@class, 'row') and .//a[contains(@href, '/p/')]]" # Row containing product link
    ))
    
    empty_cart_msg = (By.XPATH, "//div[contains(text(), 'Your cart is empty') or contains(text(), 'Missing Cart items')]")

    def get_cart_items_count(self):
        try:
            import time
            # Increased stabilization wait
            time.sleep(5)
            
            # Check for empty cart first
            empty_elements = self.driver.find_elements(*self.empty_cart_msg)
            if any(el.is_displayed() for el in empty_elements):
                from utilities.logger import setup_logger
                setup_logger().info("Empty cart message detected")
                return 0

            # Wait for at least one item
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(self.cart_items)
                )
            except:
                pass
            
            elements = self.driver.find_elements(*self.cart_items)
            
            unique_items = set()
            for el in elements:
                try:
                    if not el.is_displayed():
                        continue
                        
                    href = el.get_attribute("href")
                    if href and '/p/' in href:
                        # Normalize product links
                        unique_items.add(href.split('?')[0])
                    else:
                        # Use text of the product title
                        text = el.text.strip()
                        if text and len(text) > 10:
                            # Avoid generic texts
                            if "Remove" not in text and "Save for later" not in text:
                                unique_items.add(text[:100]) 
                except:
                    continue
            
            count = len(unique_items)
            
            # If unique filtering is too aggressive but we have elements
            if count == 0 and len(elements) > 0:
                # Count visible divs that look like items
                visible_elements = [e for e in elements if e.is_displayed()]
                return len(visible_elements)
                
            return count
        except Exception as e:
            from utilities.logger import setup_logger
            setup_logger().error(f"Error getting cart items count: {e}")
            return 0
