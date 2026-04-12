from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage(BasePage):
    login_link = (By.XPATH, "//a[contains(@href, '/account/login')] | //a[text()='Login'] | //span[text()='Login']")
    # Updated locators based on the current HTML structure (class yXUQVt and c3Bd2c) or any text input not named 'q' (search)
    email_input = (By.XPATH, "//input[contains(@class, 'yXUQVt') or contains(@class, 'c3Bd2c') or (@type='text' and not(@name='q'))]")
    # Updated Request OTP button locator
    continue_btn = (By.XPATH, "//button[text()='Request OTP' or contains(., 'Request OTP')]")
    # Updated Verify/Login button locator (just use the submit button)
    otp_login_btn = (By.XPATH, "//button[@type='submit'] | //button[contains(., 'Verify') or contains(., 'Login')]")

    def click_login(self):
        wait = WebDriverWait(self.driver, 10)
        # Wait for page load
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")

        try:
            # Try to find login button
            login_btn = wait.until(EC.element_to_be_clickable(self.login_link))
            self.driver.execute_script("arguments[0].click();", login_btn)
        except Exception as e:
            # If fail, try to see if modal is already there (sometimes it is)
            if not self.is_email_field_present():
                raise e

        # Wait for email field to be visible
        wait.until(EC.visibility_of_element_located(self.email_input))

    def is_email_field_present(self):
        try:
            return self.driver.find_element(*self.email_input).is_displayed()
        except:
            return False

    def enter_email(self, email):
        wait = WebDriverWait(self.driver, 15)
        email_field = wait.until(
            EC.visibility_of_element_located(self.email_input)
        )
        # Small delay to ensure stability
        import time
        time.sleep(2)

        # Click and clear
        email_field.click()
        email_field.clear()

        # Send keys character by character for reliability or directly
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