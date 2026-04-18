import pytest
import time
import os
from dotenv import load_dotenv
from selenium import webdriver
from utilities.read_config import ReadConfig
from utilities.screenshot import capture_screenshot
from page.login_page import LoginPage
from utilities.logger import setup_logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Load environment variables
load_dotenv()
logger = setup_logger()

@pytest.fixture(scope="session")
def setup():
    browser = ReadConfig.get_browser()

    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        
        # PERSISTENT PROFILE:
        # Create a local folder for the Chrome profile
        profile_path = os.path.join(os.getcwd(), "chrome_profile")
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        
        # Using a fixed user data directory will allow Chrome to save cookies and session info.
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        
        # options.add_argument("--headless") # Optional - PERSISTENT PROFILE IS HARD IN HEADLESS
        driver = webdriver.Chrome(options=options)
    elif browser == "firefox":
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Chrome()

    driver.maximize_window()
    driver.get(ReadConfig.get_base_url())

    yield driver

    try:
        driver.quit()
    except:
        pass

@pytest.fixture(scope="session")
def login_session(setup):
    driver = setup
    logger.info("Starting Persistent Login Session")
    
    # Get credential from .env
    login_credential = os.getenv("LOGIN_CREDENTIAL")
    if not login_credential:
         logger.error("LOGIN_CREDENTIAL not found in .env file")
         pytest.fail("LOGIN_CREDENTIAL not found in .env file")

    lp = LoginPage(driver)

    # Check if login is needed
    try:
        # Better check for login: if 'My Account' or Search box is there and Login button is NOT
        driver.get("https://www.flipkart.com")
        time.sleep(3)
        
        # Check if Search box is present
        search_box = driver.find_elements(By.NAME, "q")
        
        # Check if Login button/link is present
        login_elements = driver.find_elements(*lp.login_link)
        is_login_button_present = any(el.is_displayed() for el in login_elements)
        
        if len(search_box) > 0 and not is_login_button_present:
            logger.info("Already logged in (Search box present and Login button NOT visible)")
            return driver
            
        if lp.is_email_field_present():
            logger.info("Login modal already present on home page")
        elif is_login_button_present:
            logger.info("Clicking on Login link to open modal")
            lp.click_login()
        else:
            # Maybe we are logged in but could not find Search box or Login button. 
            # Let's try to check for email field one more time as a fallback
            if not lp.is_email_field_present():
                logger.info("Assuming already logged in as no login button or email field found")
                return driver
    except Exception as e:
        logger.warning(f"Error during login check: {e}")
        pass

    # If we reached here, we need to perform login
    try:
        lp.enter_email(login_credential)
        lp.click_continue()
        
        # Manual OTP Wait
        logger.info("ACTION REQUIRED: You have 15 seconds to enter the OTP manually in the browser.")
        time.sleep(15)
        lp.click_login_after_otp()

        # Validation
        logger.info("Waiting for login validation...")
        WebDriverWait(driver, 30).until(
            lambda d: ("/account/login" not in d.current_url.lower()) and 
                     (len(d.find_elements(By.XPATH, "//*[contains(text(), 'My Account') or contains(text(), 'Account')]")) > 0 or 
                      len(d.find_elements(By.NAME, "q")) > 0)
        )
        logger.info("Login Successful and Session Established")
    except Exception as e:
        logger.error(f"Login session failed or timed out: {e}")
        driver.save_screenshot("screenshots/login_session_failed.png")
        # If it failed, maybe we are still okay to continue if some elements are found
        pass

    return driver



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Take screenshot only if test failed
    if rep.when == "call" and rep.failed:
        # Check for both 'setup' and 'login_session' fixtures
        driver = item.funcargs.get("setup") or item.funcargs.get("login_session")

        if driver:
            try:
                capture_screenshot(driver, item.name)
            except Exception as e:
                print(f"Screenshot failed for {item.name}: {e}")