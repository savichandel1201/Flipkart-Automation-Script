from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SearchPage(BasePage):

    products = (By.XPATH, "//div[@data-id]")

    def get_product_count(self):
        elements = WebDriverWait(self.driver, 5).until(
            EC.presence_of_all_elements_located(self.products)
        )
        return len(elements)