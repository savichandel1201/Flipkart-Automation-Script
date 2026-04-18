import pytest
import time
from page.home_page import HomePage
from page.search_page import SearchPage
from page.product_page import ProductPage
from page.cart_page import CartPage
from utilities.logger import setup_logger
from utilities.excel_utils import ExcelUtils

logger = setup_logger()

@pytest.mark.regression
@pytest.mark.sanity
class TestAddToCart:

    # Read product data from Excel
    excel_file = "test_data/data.xlsx"
    sheet_name = "Products"
    products_to_add = ExcelUtils.get_data_from_excel(excel_file, sheet_name)

    @pytest.mark.parametrize("product", products_to_add)
    def test_add_to_cart(self, login_session, product):
        driver = login_session
        logger.info(f"--- Adding {product} from Excel to cart ---")
        
        # 1. Clear other tabs and go to home page
        if len(driver.window_handles) > 1:
            for window_handle in driver.window_handles[1:]:
                driver.switch_to.window(window_handle)
                driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Ensure we are on a page with the search box
        driver.get("https://www.flipkart.com")

        # 2. Search product
        hp = HomePage(driver)
        hp.close_popup_if_present()
        hp.search_product(product)

        # 3. Select first product
        sp = SearchPage(driver)
        
        # Try specific XPath first if it's iphone 15
        if "iphone 15" in product.lower():
            try:
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                product_xpath = '//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div/div/a/div[2]/div[1]/div/div/img'
                wait = WebDriverWait(driver, 10)
                product_element = wait.until(EC.presence_of_element_located((By.XPATH, product_xpath)))
                
                old_handles = driver.window_handles
                driver.execute_script("arguments[0].click();", product_element)
                
                wait.until(lambda d: len(d.window_handles) > len(old_handles))
                for handle in driver.window_handles:
                    if handle not in old_handles:
                        driver.switch_to.window(handle)
                        break
                logger.info("Clicked iphone 15 using specific XPath")
                time.sleep(3) # Allow tab to load fully
            except:
                logger.info("Specific XPath failed, falling back to click_first_product")
                sp.click_first_product()
                time.sleep(3) # Allow tab to load fully
        else:
            sp.click_first_product()
            time.sleep(3) # Allow tab to load fully
            
        # 4. Add to Cart
        pp = ProductPage(driver)
        
        # Capture dynamic HTML as requested for verification
        try:
            timestamp = int(time.time())
            html_file = f"screenshots/product_page_{product.replace(' ', '_')}_{timestamp}.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            logger.info(f"Captured dynamic HTML for {product} at: {html_file}")
        except Exception as e:
            logger.warning(f"Failed to capture HTML: {e}")

        try:
            status = pp.click_add_to_cart()
            if status == "Product is already present in the cart section":
                logger.info(f"MESSAGE: {product} is already present in the cart section")
            else:
                logger.info(f"Successfully added {product} to cart")
            time.sleep(2) # Stability wait
        except Exception as e:
            logger.error(f"Failed to add {product} to cart: {e}")
            pytest.fail(f"Failed to add {product} to cart")

        time.sleep(2)

    def test_verify_final_cart(self, login_session):
        driver = login_session
        logger.info("--- Final Verification in Cart ---")
        
        # Go to cart page explicitly
        driver.get("https://www.flipkart.com/viewcart")
        time.sleep(5) # Let it load
        
        cp = CartPage(driver)
        count = cp.get_cart_items_count()
        
        # Output the count prominently
        print(f"\nTOTAL PRODUCTS IN CART: {count}")
        logger.info(f"VERIFICATION: Total items currently present in cart: {count}")
        
        # Simple check to ensure we are actually on the cart page
        assert "viewcart" in driver.current_url.lower() or "cart" in driver.current_url.lower()
        logger.info("Cart page access verified successfully")
