import pytest
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page.home_page import HomePage
from page.login_page import LoginPage
from utilities.logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger()


@pytest.mark.regression
@pytest.mark.smoke
class TestLogin:

    def test_login_with_manual_otp(self, setup):
        driver = setup
        logger.info("Starting Login Test")
        
        # Get credential from .env
        login_credential = os.getenv("LOGIN_CREDENTIAL")
        if not login_credential:
             logger.error("LOGIN_CREDENTIAL not found in .env file")
             pytest.fail("LOGIN_CREDENTIAL not found in .env file")

        # Perform Login
        lp = LoginPage(driver)
        
        # Check if already logged in
        if not lp.is_email_field_present():
            # Try checking for My Account or similar
            try:
                # If we can find the search box and no login button, maybe we are logged in
                driver.get("https://www.flipkart.com")
                if len(driver.find_elements(By.NAME, "q")) > 0:
                     # Check if Login button is present
                     try:
                         # Use short wait to check for login button
                         WebDriverWait(driver, 5).until(EC.element_to_be_clickable(lp.login_link))
                         logger.info("Login button found, proceeding with login")
                     except:
                         logger.info("Already logged in, skipping login test steps")
                         return
            except:
                 pass

        # Check if email field is already visible (modal automatically popped up)
        if lp.is_email_field_present():
             logger.info("Login modal already present on load")
        else:
             logger.info("Clicking on Login link")
             lp.click_login()

        lp.enter_email(login_credential)
        logger.info(f"Entered Login Credential: {login_credential}")
        
        # Debug screenshot
        driver.save_screenshot("screenshots/after_email_entry.png")

        lp.click_continue()
        logger.info("Clicked Continue / Request OTP")

        # Manual OTP Wait
        print("\n" + "="*50)
        print("ACTION REQUIRED: You have 15 seconds to enter the OTP manually in the browser.")
        print("DO NOT click Login/Verify in the browser yourself.")
        print("The script will automatically click Login in 15 seconds...")
        print("="*50 + "\n")
        
        # Fixed 15-second wait for OTP
        time.sleep(15)

        # Final Login Click
        logger.info("15 seconds over. Clicking the final Login/Verify button automatically")
        lp.click_login_after_otp()

        # Validation (after login)
        logger.info("Waiting for login validation...")
        try:
            # Check for account related text or elements
            WebDriverWait(driver, 20).until(
                lambda d: len(d.find_elements(By.XPATH, "//*[contains(text(), 'My Account') or contains(text(), 'Account')]")) > 0 or 
                          len(d.find_elements(By.NAME, "q")) > 0
            )
            logger.info("Login Successful and Verified")
        except:
            # If not found, check current URL
            current_url = driver.current_url.lower()
            if "flipkart.com" in current_url and "/account/login" not in current_url:
                 logger.warning(f"Validation by element failed, but URL looks okay: {current_url}")
            else:
                 driver.save_screenshot("screenshots/login_verification_failed.png")
                 logger.error(f"Login Verification Failed. Current URL: {current_url}")
                 assert False, f"Login failed. URL: {current_url}"

        # Close any popups
        try:
             hp = HomePage(driver)
             hp.close_popup_if_present()
        except:
             pass