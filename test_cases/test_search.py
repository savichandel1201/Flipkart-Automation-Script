import pytest
from page.home_page import HomePage
from page.search_page import SearchPage
from utilities.read_testdata import ReadTestData
from utilities.logger import setup_logger
from utilities.screenshot import capture_screenshot

logger = setup_logger()

@pytest.mark.sanity
@pytest.mark.parametrize("data", ReadTestData.get_search_data())
class TestSearch:

    def test_search_product(self, setup, data):
        driver = setup
        logger.info(f"Searching for {data['product']}")

        hp = HomePage(driver)
        hp.close_popup_if_present()
        hp.search_product(data["product"])

        sp = SearchPage(driver)
        count = sp.get_product_count()

        if count > 0:
            logger.info("Search Passed")
            assert True
        else:
            logger.error("Search Failed")
            assert False