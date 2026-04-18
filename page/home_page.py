from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage(BasePage):

    close_popup = (By.XPATH, "//button[contains(text(),'✕')] | //span[contains(text(),'✕')] | //button[@class='_2KpZ6l _2doB4z']")
    search_box = (By.NAME, "q")

    def close_popup_if_present(self):
        try:
            # Try finding the 'X' button and clicking it
            wait = WebDriverWait(self.driver, 3)
            btn = wait.until(EC.element_to_be_clickable(self.close_popup))
            btn.click()
            import time
            time.sleep(1)
        except:
            # Fallback to ESC key
            try:
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            except:
                pass

    def search_product(self, product):
        wait = WebDriverWait(self.driver, 15)
        # Robust locator for search box
        search_locators = [
            (By.NAME, "q"),
            (By.XPATH, "//input[@title='Search for products, brands and more']"),
            (By.XPATH, "//input[@name='q']"),
            (By.CLASS_NAME, "Pke_EE"),
            (By.CLASS_NAME, "Vy9RSP"),
            (By.CLASS_NAME, "_2SmNnR")
        ]

        element = None
        for locator in search_locators:
            try:
                # Wait for presence then check if it's the right one
                elements = self.driver.find_elements(*locator)
                for el in elements:
                    if el.is_displayed():
                        element = el
                        break
                if element: break
            except:
                continue

        if not element:
             # Take screenshot
             self.driver.save_screenshot("screenshots/search_box_not_found.png")
             raise Exception("Search box not found or not interactable")

        # Click and clear thoroughly
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        element.click()

        # Method 1: Ctrl+A and Backspace
        from selenium.webdriver.common.keys import Keys
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)

        # Method 2: JS fallback to ensure it's empty
        self.driver.execute_script("arguments[0].value = '';", element)

        # Small wait for the UI to register the clear
        import time
        time.sleep(1)

        # Send keys
        element.send_keys(product)
        time.sleep(1)
        element.send_keys(Keys.ENTER)

        # Wait for results to load (URL change or presence of products)
        time.sleep(2)