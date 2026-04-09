import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
TINDER_URL = "https://tinder.com"
TINDER_PHONE = "*****"   # local phone number, e.g. 611122334


def main():
    # --- Setup WebDriver ---
    options = uc.ChromeOptions()

    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # block
        "profile.default_content_setting_values.geolocation": 1,    # allow
    }
    options.add_experimental_option("prefs", prefs)

    driver = uc.Chrome(options=options, version_main=146)
    wait = WebDriverWait(driver, 20)

    # --- Open Tinder ---
    driver.get(TINDER_URL)

    # Accept cookie banner early
    click_cookie_banner(driver, wait)

    # --- PHONE LOGIN FLOW ---
    click_login_button(driver, wait)
    click_login_with_phone(driver, wait)
    enter_phone_number(driver, wait, TINDER_PHONE)
    click_next(driver, wait)

    # --- MANUAL PAUSE: enter the SMS code in the browser ---
    print("SMS code sent to your phone. Enter it in the browser, then type 'resume'.")
    wait_for_resume()

    # --- HANDLE TINDER POPUPS ---
    click_if_present(driver, wait, "//button[contains(., 'I accept')]")
    click_if_present(driver, wait, "//button[contains(., 'Allow')]")
    click_if_present(driver, wait, "//button[contains(., 'Not interested')]")
    click_if_present(driver, wait, "//button[contains(., 'Maybe later')]")

    print("Login complete. Starting auto-NOPE loop...")
    auto_nope_loop(driver, wait)


# -------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------

def wait_for_resume():
    """Pause execution until user types 'resume'."""
    while True:
        user_input = input("Type 'resume' to continue: ").strip().lower()
        if user_input == "resume":
            break
        print("Not 'resume'. Still paused.")


def click_if_present(driver, wait, xpath, timeout=5):
    """Click element by XPath; silently skip if not found."""
    try:
        btn = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", btn)
    except TimeoutException:
        pass


# -------------------------------------------------
# LOGIN STEPS
# -------------------------------------------------

def click_cookie_banner(driver, wait):
    """Click Tinder's initial cookie/privacy banner if it appears."""
    for xpath in [
        "//button[contains(., 'I accept')]",
        "//button[contains(., 'Accept all')]",
    ]:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)
            return
        except TimeoutException:
            continue


def click_login_button(driver, wait):
    """Click the 'Log in' button in the Tinder header."""
    candidates = [
        "//header//a[contains(@href, 'tinder.onelink.me')]",
        "//header//button[contains(., 'Log in')]",
        "//a[contains(., 'Log in')]",
    ]
    for xpath in candidates:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)
            print("Clicked Tinder 'Log in' button.")
            return
        except TimeoutException:
            continue
    raise Exception("Could not find Tinder 'Log in' button.")


def click_login_with_phone(driver, wait):
    """Click 'Log in with phone number' in the Get Started modal."""
    for xpath in [
        "//button[contains(., 'Log in with phone number')]",
        "//button[contains(., 'phone number')]",
    ]:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)
            print("Clicked 'Log in with phone number'.")
            time.sleep(0.3)  # wait for phone-entry modal to finish animating in
            return
        except TimeoutException:
            continue
    raise Exception("Could not find 'Log in with phone number' button.")


def enter_phone_number(driver, wait, phone):
    """Type the phone number into Tinder's phone input."""
    css_candidates = [
        "input[type='tel']",
        "input[type='text'][placeholder*='Phone']",
        "input[type='text'][placeholder*='phone']",
        "input[inputmode='numeric']",
        "input[inputmode='tel']",
        "input[type='number']",
    ]
    for css in css_candidates:
        try:
            phone_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css))
            )
            driver.execute_script("arguments[0].focus();", phone_input)
            phone_input.clear()
            phone_input.send_keys(phone)
            time.sleep(0.2)
            print(f"Entered phone number: {phone}")
            return
        except TimeoutException:
            continue
    raise Exception("Could not find phone number input field.")


def click_next(driver, wait):
    """Click the Next button on the phone number screen.
    Uses JS click to bypass the disabled state that clears once a number is typed."""
    for xpath in [
        "//button[contains(., 'Next')]",
        "//button[normalize-space(.)='Next']",
    ]:
        try:
            btn = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            driver.execute_script("arguments[0].click();", btn)
            print("Clicked Next.")
            return
        except TimeoutException:
            continue
    raise Exception("Could not find Next button.")


# -------------------------------------------------
# AUTO-NOPE LOOP
# -------------------------------------------------

def auto_nope_loop(driver, wait, delay=1.2):
    """Continuously send LEFT ARROW (Nope). Close match popups as needed."""
    body = driver.find_element(By.TAG_NAME, "body")

    while True:
        clear_match_popup(driver)  # proactive: dismiss any overlay before swiping
        try:
            body.send_keys(Keys.ARROW_LEFT)
            print("Nope sent.")
            time.sleep(delay)
        except Exception as e:
            print(f"Problem sending nope: {e}. Retrying after pause...")
            time.sleep(2)


def clear_match_popup(driver):
    """Try to close match overlays and mid-session install/notification prompts."""
    for xpath in [
        "//button[contains(., 'BACK TO TINDER')]",
        "//button[contains(., 'Back to Tinder')]",
        "//button[contains(., 'Keep Swiping')]",
        "//button[contains(., 'Not interested')]",
        "//button[contains(., 'Not Interested')]",
        "//button[contains(., 'Maybe later')]",
        "//button[contains(., 'No Thanks')]",
        "//button[contains(., 'No thanks')]",
        "//button[normalize-space(.)='Allow']",
    ]:
        try:
            btn = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", btn)
            print("Closed match popup.")
            return
        except Exception:
            continue
    print("No match popup to close.")


# -------------------------------------------------
# MAIN EXECUTION
# -------------------------------------------------
if __name__ == "__main__":
    main()
