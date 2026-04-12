import pytest
from selenium import webdriver
from utilities.read_config import ReadConfig
from utilities.screenshot import capture_screenshot


@pytest.fixture()
def setup():
    browser = ReadConfig.get_browser()

    if browser == "chrome":
        driver = webdriver.Chrome()
    elif browser == "firefox":
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Chrome()

    driver.maximize_window()
    driver.get(ReadConfig.get_base_url())

    yield driver

    driver.quit()



@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    # Take screenshot only if test failed
    if rep.when == "call" and rep.failed:
        driver = item.funcargs.get("setup")

        if driver:
            try:
                capture_screenshot(driver, item.name)
            except Exception as e:
                print("Screenshot failed:", e)