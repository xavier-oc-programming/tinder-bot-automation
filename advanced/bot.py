import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import config


class TinderBot:
    """Handles all Selenium interactions with Tinder and the Facebook login popup."""

    def __init__(self, email: str, password: str):
        self._email = email
        self._password = password
        self._tinder_window = None

        options = uc.ChromeOptions()
        options.add_experimental_option(
            "prefs",
            {"profile.default_content_setting_values.notifications": 2},
        )
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, config.WAIT_TIMEOUT)

    # ------------------------------------------------------------------
    # NAVIGATION
    # ------------------------------------------------------------------

    def open_tinder(self):
        """Navigate to Tinder and store the window handle."""
        self.driver.get(config.TINDER_URL)
        self._tinder_window = self.driver.current_window_handle

    def return_to_tinder(self):
        """Switch focus back to the Tinder window after the Facebook popup closes."""
        self.driver.switch_to.window(self._tinder_window)

    # ------------------------------------------------------------------
    # TINDER LOGIN FLOW
    # ------------------------------------------------------------------

    def accept_cookies_early(self):
        """Click Tinder's initial cookie/choices banner if it appears."""
        for xpath in config.XPATH_COOKIE_EARLY:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self._js_click(btn)
                return
            except TimeoutException:
                continue

    def click_login_button(self):
        """Click the main 'Log in' button on the Tinder home page."""
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//header//a[contains(@href, 'tinder.onelink.me')]")
                )
            )
            btn.click()
        except TimeoutException:
            raise RuntimeError("Could not find Tinder login button.")

    def click_login_with_facebook(self):
        """Click 'Login with Facebook' inside the Tinder login modal."""
        time.sleep(2)
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button[aria-label='Login with Facebook']")
                )
            )
            btn.click()
        except TimeoutException:
            try:
                btn = self.driver.find_element(
                    By.XPATH, "//button[@aria-label='Login with Facebook']"
                )
                btn.click()
            except NoSuchElementException:
                raise RuntimeError("Could not find 'Login with Facebook' button.")

    # ------------------------------------------------------------------
    # FACEBOOK POPUP FLOW
    # ------------------------------------------------------------------

    def switch_to_facebook_window(self):
        """Switch driver focus to the Facebook OAuth popup window."""
        main_window = self.driver.current_window_handle
        time.sleep(2)
        for handle in self.driver.window_handles:
            if handle != main_window:
                self.driver.switch_to.window(handle)
                return
        raise RuntimeError("Facebook login window not found.")

    def accept_facebook_cookies(self):
        """Click Facebook's 'Allow all cookies' button if it appears."""
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.XPATH_FB_COOKIE))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.3)
            self._js_click(btn)
            time.sleep(0.5)
        except TimeoutException:
            pass  # cookie popup is optional

    def fill_facebook_credentials(self):
        """Type the Facebook email and password into the login form."""
        email_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.clear()
        email_input.send_keys(self._email)

        pass_input = self.driver.find_element(By.ID, "pass")
        pass_input.clear()
        pass_input.send_keys(self._password)

    def click_facebook_login(self):
        """Click Facebook's 'Log In' submit button."""
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, config.XPATH_FB_LOGIN_BTN))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.3)
            self._js_click(btn)
        except TimeoutException:
            raise RuntimeError("Could not find Facebook 'Log In' button.")

    def click_continue_as(self):
        """Click the 'Continue as [Name]' OAuth confirmation button."""
        for xpath in config.XPATH_FB_CONTINUE_AS:
            try:
                btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                time.sleep(0.3)
                self._js_click(btn)
                time.sleep(0.5)
                return
            except TimeoutException:
                continue
        # No button found — OAuth may have skipped this step

    # ------------------------------------------------------------------
    # POST-LOGIN TINDER POPUPS
    # ------------------------------------------------------------------

    def dismiss_tinder_popups(self):
        """Handle cookie consent, location allow, and notify-me popups after login."""
        self._click_if_present(config.XPATH_COOKIE_CONSENT)
        self._click_if_present(config.XPATH_LOCATION_ALLOW)
        self._click_if_present(config.XPATH_NOTIFY_ME)

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
        """Try a normal click; fall back to JavaScript click."""
        try:
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def _click_if_present(self, xpath: str):
        """Click an element by XPath; silently skip if not found."""
        try:
            btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(0.2)
            self._js_click(btn)
        except TimeoutException:
            pass
