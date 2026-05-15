import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "user1"
TEST_PASSWORD = "123"
SAMPLE_IMAGE_PATH = os.path.abspath("tests/Funny_dogs_2.jpg")

def dismiss_any_alert(driver, timeout=3):
    """Dismiss any alert that may be present."""
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        Alert(driver).accept()
    except Exception:
        pass


def safe_get(driver, url):
    """Navigate to a URL and dismiss any unexpected alerts."""
    driver.get(url)
    dismiss_any_alert(driver)


@pytest.fixture
def driver():
    """Set up a headless Edge browser for each test."""
    options = webdriver.EdgeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")  # important for interactability

    driver = webdriver.Edge(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def login(driver):
    """Helper function to log in the test user."""
    driver.get(f"{BASE_URL}/login.html")

    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "login-username"))
    )

    driver.find_element(By.ID, "login-username").send_keys(TEST_USERNAME)
    driver.find_element(By.ID, "login-password").send_keys(TEST_PASSWORD)
    driver.find_element(By.CSS_SELECTOR, "#login-form button[type='submit']").click()

    # Handle the "Logged in successfully" alert
    try:
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        Alert(driver).accept()
    except Exception:
        pass

    # Wait until we are no longer on the login page
    WebDriverWait(driver, 10).until(
        lambda d: "login" not in d.current_url
    )


def fill_checkin_form(driver, include_location=True):
    """Helper function to fill in the check-in form."""
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "title"))
    )

    # Fill in place name
    driver.find_element(By.ID, "place-name").send_keys("Test Place Name")

    # Fill in the title
    driver.find_element(By.ID, "title").send_keys("Test Checkin Place")

    # Select a category
    Select(driver.find_element(By.ID, "category")).select_by_value("nature")

    # Fill in the description
    driver.find_element(By.ID, "description").send_keys("This is a test description.")

    # Click 4th star using JavaScript to avoid interception
    stars = driver.find_elements(By.CSS_SELECTOR, "#star-picker i")
    star = stars[3]
    driver.execute_script("arguments[0].scrollIntoView(true);", star)
    driver.execute_script("arguments[0].click();", star)

    # Upload a photo
    photo_input = driver.find_element(By.ID, "photo-input")
    driver.execute_script("arguments[0].style.display = 'block';", photo_input)
    photo_input.send_keys(SAMPLE_IMAGE_PATH)

    if include_location:
        driver.find_element(By.ID, "pick-on-map").click()

        WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.ID, "map-picker"))
        )

        map_element = driver.find_element(By.ID, "map-picker")
        action = webdriver.ActionChains(driver)
        action.move_to_element(map_element).click().perform()

        WebDriverWait(driver, 5).until(
            lambda d: d.find_element(By.ID, "lat_input").get_attribute("value") != ""
        )


def js_click(driver, element):
    """Click an element using JavaScript to bypass interception."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    driver.execute_script("arguments[0].click();", element)

# ------------------------------------------------------------------ #
# Selenium Test 1: Submit new checkin form successfully                #
# ------------------------------------------------------------------ #
class TestCheckinFormSubmit:

    def test_submit_checkin_form_successfully(self, driver):
        login(driver)
        safe_get(driver, f"{BASE_URL}/new-checkin.html")
        fill_checkin_form(driver, include_location=True)

        # Set lat/lng directly via JavaScript to bypass JS validation
        driver.execute_script("""
            document.getElementById('lat_input').value = '-31.9505';
            document.getElementById('lng_input').value = '115.8605';
            document.getElementById('rating-value').value = '4';
        """)

        # Submit the form directly via JavaScript, bypassing JS validation
        driver.execute_script("document.getElementById('checkin-form').submit();")

        import time
        time.sleep(2)  # wait for redirect
        print(f"\nURL after submit: {driver.current_url}")

        WebDriverWait(driver, 10).until(
            lambda d: "new-checkin" not in d.current_url
        )

        assert driver.current_url == f"{BASE_URL}/" or "/index" in driver.current_url