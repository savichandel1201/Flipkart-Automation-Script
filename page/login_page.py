from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage(BasePage):
    login_link = (By.XPATH, "//a[contains(@href, '/account/login')] | //a[text()='Login'] | //span[text()='Login'] | //a[@title='Login']")
    # Updated locators based on common Flipkart structures
    email_input = (By.XPATH, "//input[contains(@class, 'yXUQVt') or contains(@class, 'c3Bd2c') or contains(@class, '_2IX_2-') or contains(@class, 'V03791') or (@type='text' and not(@name='q'))]")
    # Updated Request OTP button locator
    continue_btn = (By.XPATH, "//button[contains(text(),'Request OTP') or contains(., 'Request OTP') or contains(text(), 'CONTINUE') or contains(., 'CONTINUE')]")
    # Updated Verify/Login button locator
    otp_login_btn = (By.XPATH, "//button[@type='submit'] | //button[contains(., 'Verify') or contains(., 'Login')]")

    def click_login(self):
        wait = WebDriverWait(self.driver, 15)
        # Wait for page load
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        try:
            # Try to find login button
            login_btn = wait.until(EC.element_to_be_clickable(self.login_link))
            # Scroll to it first
            self.driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
            import time
            time.sleep(1)
            self.driver.execute_script("arguments[0].click();", login_btn)
        except Exception as e:
            # If fail, try to see if modal is already there (sometimes it is)
            if not self.is_email_field_present():
                # Take screenshot for debugging if it fails
                self.driver.save_screenshot("screenshots/login_click_failed.png")
                raise e

        # Wait for email field to be visible
        try:
            wait.until(EC.visibility_of_element_located(self.email_input))
        except:
            # Maybe the click didn't work, try clicking by text as fallback
            try:
                fallback = self.driver.find_element(By.XPATH, "//*[text()='Login']")
                self.driver.execute_script("arguments[0].click();", fallback)
                wait.until(EC.visibility_of_element_located(self.email_input))
            except:
                raise Exception("Could not find email input after clicking login")

    def is_email_field_present(self):
        try:
            elements = self.driver.find_elements(*self.email_input)
            for el in elements:
                if el.is_displayed():
                    return True
            return False
        except:
            return False

    def enter_email(self, email):
        wait = WebDriverWait(self.driver, 15)
        # Find the visible email field
        email_field = None
        try:
            elements = wait.until(EC.presence_of_all_elements_located(self.email_input))
            for el in elements:
                if el.is_displayed():
                    email_field = el
                    break
        except:
            pass
            
        if not email_field:
             raise Exception("Visible email input field not found")

        import time
        time.sleep(1)

        # Click and clear
        email_field.click()
        email_field.clear()

        # Send keys
        email_field.send_keys(email)

    def click_continue(self):
        wait = WebDriverWait(self.driver, 15)
        btn = wait.until(
            EC.element_to_be_clickable(self.continue_btn)
        )
        import time
        time.sleep(1)
        self.driver.execute_script("arguments[0].click();", btn)

    def click_login_after_otp(self):
        """Clicks the final Login/Verify button after OTP is entered. Ignores timeout if auto-submitted."""
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.otp_login_btn)
            )
            btn.click()
        except:
            # Form likely auto-submitted or button is hidden/different
            pass