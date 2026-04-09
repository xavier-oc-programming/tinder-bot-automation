import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
TINDER_URL = "https://tinder.com"
FACEBOOK_EMAIL = "*****"
FACEBOOK_PASSWORD = "*****"


def main():
    # --- Setup WebDriver ---
    options = uc.ChromeOptions()

    # Disable Chrome notifications (prevents popup “tinder.com wants to show notifications”)
    prefs = {“profile.default_content_setting_values.notifications”: 2}
    options.add_experimental_option(“prefs”, prefs)

    driver = uc.Chrome(options=options, version_main=146)
    wait = WebDriverWait(driver, 20)

    # --- Open Tinder and store window handle ---
    driver.get(TINDER_URL)
    tinder_window = driver.current_window_handle

    # Accept cookie choices as soon as possible
    click_tinder_accept_choices_early(driver, wait)

    # --- FACEBOOK LOGIN FLOW ---
    click_login_button(driver, wait)
    click_login_with_facebook(driver, wait)
    switch_to_facebook_window(driver)
    accept_facebook_cookies(driver, wait)
    fill_facebook_credentials(driver, wait, FACEBOOK_EMAIL, FACEBOOK_PASSWORD)
    click_facebook_login(driver, wait)
    click_continue_as_button(driver, wait)

    # --- MANUAL CAPTCHA / VERIFICATION PAUSE ---
    wait_for_resume()

    # --- RETURN TO TINDER WINDOW AFTER RESUME ---
    driver.switch_to.window(tinder_window)

    # --- HANDLE TINDER POPUPS ---
    click_tinder_cookie_consent(driver, wait)
    click_tinder_location_allow(driver, wait)
    click_tinder_notify_me_button(driver, wait)

    print("Finished post-resume popup handling. Starting auto-NOPE loop...")
    auto_nope_loop(driver, wait)


# -------------------------------------------------
# UTILITY FUNCTIONS
# -------------------------------------------------

def wait_for_resume():
    """Pause execution until user types 'resume'."""
    while True:
        user_input = input("Paused for manual action. Type 'resume' to continue: ").strip().lower()
        if user_input == "resume":
            break
        else:
            print("Not 'resume'. Still paused.")


# -------------------------------------------------
# FACEBOOK / TINDER LOGIN STEPS
# -------------------------------------------------

def click_login_button(driver, wait):
    """Clicks the main 'Log in' button on Tinder."""
    try:
        login_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//header//a[contains(@href, 'tinder.onelink.me')]")
            )
        )
        login_btn.click()
        print("Clicked Tinder Login button successfully.")
    except TimeoutException:
        raise Exception("Could not find Tinder login button.")


def click_login_with_facebook(driver, wait):
    """Clicks 'Login with Facebook' button inside the Tinder modal."""
    time.sleep(2)
    try:
        fb_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Login with Facebook']")
            )
        )
        fb_btn.click()
        print("Clicked 'Login with Facebook' successfully.")
    except TimeoutException:
        try:
            fb_btn = driver.find_element(By.XPATH, "//button[@aria-label='Login with Facebook']")
            fb_btn.click()
        except NoSuchElementException:
            raise Exception("Could not find 'Login with Facebook' button.")


def switch_to_facebook_window(driver):
    """Switches to the Facebook login popup window."""
    main_window = driver.current_window_handle
    time.sleep(2)
    for handle in driver.window_handles:
        if handle != main_window:
            driver.switch_to.window(handle)
            print("Switched to Facebook login window.")
            return
    raise Exception("Facebook login window not found.")


def accept_facebook_cookies(driver, wait):
    """Clicks Facebook's 'Allow all cookies' consent button."""
    try:
        cookie_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="facebook"]/body/div[2]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", cookie_btn)
        time.sleep(0.3)
        try:
            cookie_btn.click()
            print("Clicked Facebook 'Allow all cookies' (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", cookie_btn)
            print("Clicked Facebook 'Allow all cookies' (JS click).")
        time.sleep(0.5)
    except TimeoutException:
        print("No Facebook cookie popup detected — continuing.")


def fill_facebook_credentials(driver, wait, email, password):
    """Fills in the Facebook login form."""
    email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))
    email_input.clear()
    email_input.send_keys(email)

    pass_input = driver.find_element(By.ID, "pass")
    pass_input.clear()
    pass_input.send_keys(password)

    print("Filled in Facebook credentials successfully.")


def click_facebook_login(driver, wait):
    """Clicks Facebook's 'Log In' button."""
    try:
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="loginbutton"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
        time.sleep(0.3)
        try:
            login_btn.click()
            print("Clicked Facebook 'Log In' button (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", login_btn)
            print("Clicked Facebook 'Log In' button (JS click).")
    except TimeoutException:
        print("Could not find Facebook 'Log In' button.")


def click_continue_as_button(driver, wait):
    """Clicks the 'Continue as [Name]' Facebook OAuth popup button."""
    candidate_xpaths = [
        "//div[@role='button' and starts-with(@aria-label, 'Continue as ')]",
        "//span[starts-with(normalize-space(.), 'Continue as ')]/ancestor::div[@role='button']",
    ]
    for xpath in candidate_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.3)
            try:
                btn.click()
                print("Clicked 'Continue as ...' button (normal click).")
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
                print("Clicked 'Continue as ...' button (JS click).")
            time.sleep(0.5)
            return
        except TimeoutException:
            continue
    print("No 'Continue as ...' popup detected — continuing.")


# -------------------------------------------------
# TINDER POPUP HANDLERS
# -------------------------------------------------

def click_tinder_accept_choices_early(driver, wait):
    """Clicks Tinder's initial cookie/choices banner."""
    possible_xpaths = [
        '//*[@id="c-429777287"]/div/div[2]/div/div/div[1]/div[1]/button',
        "//button[contains(., 'I accept')]",
        "//button[contains(., 'Accept all')]",
    ]
    for xpath in possible_xpaths:
        try:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.2)
            try:
                btn.click()
                print("Clicked Tinder cookie/choices early (normal click).")
            except Exception:
                driver.execute_script("arguments[0].click();", btn)
                print("Clicked Tinder cookie/choices early (JS click).")
            return
        except TimeoutException:
            continue
    print("No initial Tinder cookie/choices banner found at start.")


def click_tinder_cookie_consent(driver, wait):
    """Clicks Tinder's cookie/privacy consent 'I accept' button."""
    try:
        accept_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="c-429777287"]/div/div[2]/div/div/div[1]/div[1]/button')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", accept_btn)
        time.sleep(0.2)
        try:
            accept_btn.click()
            print("Clicked Tinder cookie consent (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", accept_btn)
            print("Clicked Tinder cookie consent (JS click).")
    except TimeoutException:
        print("Tinder cookie consent not found — maybe already accepted.")


def click_tinder_location_allow(driver, wait):
    """Clicks Tinder's location permission 'Allow' button."""
    try:
        allow_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="c1298603789"]/div/div[2]/div/div/div[1]/div[1]/button')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", allow_btn)
        time.sleep(0.2)
        try:
            allow_btn.click()
            print("Clicked Tinder location 'Allow' (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", allow_btn)
            print("Clicked Tinder location 'Allow' (JS click).")
    except TimeoutException:
        print("Tinder location popup not found — maybe already handled.")


def click_tinder_notify_me_button(driver, wait):
    """Clicks Tinder's 'Notify Me' button."""
    try:
        notify_btn = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="c-429777287"]/div/div/div/div/div[3]/button[1]')
            )
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", notify_btn)
        time.sleep(0.2)
        try:
            notify_btn.click()
            print("Clicked Tinder 'Notify Me' button (normal click).")
        except Exception:
            driver.execute_script("arguments[0].click();", notify_btn)
            print("Clicked Tinder 'Notify Me' button (JS click).")
    except TimeoutException:
        print("Tinder 'Notify Me' popup not found — maybe already handled.")


# -------------------------------------------------
# AUTO-NOPE LOOP
# -------------------------------------------------

def auto_nope_loop(driver, wait, delay=1.2):
    """
    Continuously send LEFT ARROW (Nope).
    If a match popup or some overlay appears, try to close it and continue.
    delay: seconds to wait between nopes (too fast = Tinder may block).
    """
    body = driver.find_element(By.TAG_NAME, "body")

    while True:
        try:
            # send left arrow
            body.send_keys(Keys.ARROW_LEFT)
            print("Nope sent.")
            time.sleep(delay)
        except Exception as e:
            print(f"Problem sending nope: {e}. Trying to clear popups...")
            clear_match_popup(driver)
            time.sleep(2)


def clear_match_popup(driver):
    """
    Tries to close the 'It's a match!' overlay so we can keep swiping.
    """
    possible_xpaths = [
        "//button[contains(., 'BACK TO TINDER')]",
        "//button[contains(., 'Back to Tinder')]",
        "//button[contains(., 'Keep Swiping')]",
    ]
    for xpath in possible_xpaths:
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
