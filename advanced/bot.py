import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import config


class TinderBot:
    """Handles all Selenium interactions with Tinder (phone number login flow)."""

    def __init__(self, phone: str):
        self._phone = phone

        options = uc.ChromeOptions()
        options.add_experimental_option(
            "prefs",
            {
                "profile.default_content_setting_values.notifications": 2,  # block
                "profile.default_content_setting_values.geolocation": 1,    # allow
            },
        )
        self.driver = uc.Chrome(options=options, version_main=config.CHROME_VERSION)
        self.wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------

    def open_tinder(self):
        """Navigate to Tinder."""
        self.driver.get(config.TINDER_URL)

    # ------------------------------------------------------------------
    # LOGIN FLOW
    # ------------------------------------------------------------------

    def accept_cookies_early(self):
        """Click Tinder's initial cookie/privacy banner if it appears."""
        for xpath in config.XPATH_COOKIE_EARLY:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self._js_click(btn)
                return
            except TimeoutException:
                continue

    def click_login_button(self):
        """Click the 'Log in' button in the Tinder header."""
        candidates = [
            "//header//a[contains(@href, 'tinder.onelink.me')]",
            "//header//button[contains(., 'Log in')]",
            "//a[contains(., 'Log in')]",
        ]
        for xpath in candidates:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self._js_click(btn)
                return
            except TimeoutException:
                continue
        raise RuntimeError("Could not find Tinder 'Log in' button.")

    def click_login_with_phone(self):
        """Click 'Log in with phone number' in the Get Started modal."""
        for xpath in config.XPATH_LOGIN_WITH_PHONE:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self._js_click(btn)
                time.sleep(0.3)  # wait for phone-entry modal to finish animating in
                return
            except TimeoutException:
                continue
        raise RuntimeError("Could not find 'Log in with phone number' button.")

    def enter_phone_number(self):
        """Type the phone number into Tinder's phone input field."""
        fast = WebDriverWait(self.driver, 3)  # short per-candidate timeout
        for css in config.CSS_PHONE_INPUT_CANDIDATES:
            try:
                phone_input = fast.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css))
                )
                self.driver.execute_script("arguments[0].focus();", phone_input)
                phone_input.clear()
                phone_input.send_keys(self._phone)
                time.sleep(0.2)  # let the Next button become active
                return
            except TimeoutException:
                continue
        raise RuntimeError("Could not find phone number input field.")

    def click_phone_next(self):
        """Click the Next button after entering the phone number.
        Uses JS click to bypass the disabled state that clears once a number is typed."""
        fast = WebDriverWait(self.driver, 3)  # short per-candidate timeout
        for xpath in config.XPATH_PHONE_NEXT:
            try:
                btn = fast.until(EC.presence_of_element_located((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].click();", btn)
                return
            except TimeoutException:
                continue
        raise RuntimeError("Could not find Next button on phone number screen.")

    # ------------------------------------------------------------------
    # POST-LOGIN TINDER POPUPS
    # ------------------------------------------------------------------

    def dismiss_tinder_popups(self):
        """Attempt to dismiss cookie consent, location, and notification popups.
        Uses a short timeout — popups are optional and may not appear."""
        short_wait = WebDriverWait(self.driver, 4)
        for xpath_list in [
            config.XPATH_COOKIE_CONSENT,
            config.XPATH_LOCATION_ALLOW,
            config.XPATH_NOTIFY_ME,
        ]:
            self._click_first_present(xpath_list, wait=short_wait)

    # ------------------------------------------------------------------
    # SWIPING
    # ------------------------------------------------------------------

    def swipe_left(self):
        """Send a LEFT ARROW key press to the page body (Nope)."""
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.ARROW_LEFT)

    def clear_match_popup(self):
        """Close an 'It's a match!' overlay so swiping can continue."""
        for xpath in config.XPATH_MATCH_CLOSE:
            try:
                btn = self.driver.find_element(By.XPATH, xpath)
                self.driver.execute_script("arguments[0].click();", btn)
                return
            except Exception:
                continue

    # ------------------------------------------------------------------
    # TEARDOWN
    # ------------------------------------------------------------------

    def quit(self):
        """Close the browser."""
        self.driver.quit()

    # ------------------------------------------------------------------
    # INTERNAL HELPERS
    # ------------------------------------------------------------------

    def _js_click(self, element):
        """Normal click with JavaScript fallback."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def _click_if_present(self, xpath: str):
        """Click an element by XPath; silently skip if not found within timeout."""
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.2)
            self._js_click(btn)
        except TimeoutException:
            pass

    def _click_first_present(self, xpath_list: list, wait=None):
        """Try each XPath in order; click the first one found, skip if none."""
        w = wait or self.wait
        for xpath in xpath_list:
            try:
                btn = w.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self._js_click(btn)
                return
            except TimeoutException:
                continue
