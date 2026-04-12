from selenium.webdriver.common.by import By
from base_package.base_page import BasePage
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage(BasePage):

    close_popup = (By.XPATH, "//button[text()='✕']")
    search_box = (By.NAME, "q")

    def close_popup_if_present(self):
        try:
            WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.close_popup)
            ).click()
        except:
            from selenium.webdriver.common.keys import Keys
            self.driver.find_element("tag name", "body").send_keys(Keys.ESCAPE)

    def search_product(self, product):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.search_box)
        )
        element.clear()
        element.send_keys(product + Keys.ENTER)