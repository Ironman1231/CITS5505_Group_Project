import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "user1"
TEST_PASSWORD = "123"


def dismiss_any_alert(driver, timeout=3):
    """Dismiss any alert that may be present."""
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        Alert(driver).accept()
    except Exception:
        pass


@pytest.fixture
def driver():
    """Set up a headless Edge browser for each test."""
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Edge(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


# ------------------------------------------------------------------ #
# Selenium Test: Login with valid credentials redirects to home #127  #
# ------------------------------------------------------------------ #
class TestLoginRedirect:

    def test_login_valid_credentials_redirects_to_home(self, driver):
        # Navigate to /login.html
        driver.get(f"{BASE_URL}/login.html")

        # Wait for the login form to be visible
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "login-username"))
        )

        # Fill in valid username and password
        driver.find_element(By.ID, "login-username").send_keys(TEST_USERNAME)
        driver.find_element(By.ID, "login-password").send_keys(TEST_PASSWORD)

        # Click the submit button
        driver.find_element(
            By.CSS_SELECTOR, "#login-form button[type='submit']"
        ).click()

        # Dismiss any alert that may appear on successful login
        dismiss_any_alert(driver)

        # Verify the URL no longer contains "login"
        WebDriverWait(driver, 10).until(
            lambda d: "login" not in d.current_url
        )
        assert "login" not in driver.current_url

        # Verify the user is on the home page
        assert driver.current_url == f"{BASE_URL}/" or "/index" in driver.current_url
