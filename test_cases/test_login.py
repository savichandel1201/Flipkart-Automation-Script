import pytest
import time
import os
from dotenv import load_dotenv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from page.home_page import HomePage
from page.login_page import LoginPage
from utilities.logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger()


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
        WebDriverWait(driver, 15).until(
            lambda d: "account" in d.current_url.lower() or "flipkart.com" in d.current_url.lower()
        )

        assert "account" in driver.current_url.lower() or "flipkart.com" in driver.current_url.lower()

        logger.info("Login Successful and Verified")