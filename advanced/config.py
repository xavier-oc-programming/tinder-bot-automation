# URLs
TINDER_URL = "https://tinder.com"

# Selenium
WAIT_TIMEOUT = 20    # seconds to wait for elements before timing out
CHROME_VERSION = 146  # must match your installed Chrome major version

# Timing / rate limits
NOPE_DELAY = 1.2   # seconds between left swipes (too fast risks a Tinder block)
POPUP_CLEAR_PAUSE = 2.0  # seconds to wait after closing a match popup

# XPaths — Tinder cookie / privacy banner (appears on home page)
XPATH_COOKIE_EARLY = [
    "//button[contains(., 'I accept')]",
    "//button[contains(., 'Accept all')]",
    "//button[contains(., 'I Accept')]",
]

# XPaths — phone login flow
XPATH_LOGIN_WITH_PHONE = [
    "//button[contains(., 'Log in with phone number')]",
    "//button[contains(., 'phone number')]",
]
CSS_PHONE_INPUT = "input[type='tel']"
XPATH_PHONE_NEXT = "//button[normalize-space(.)='Next']"

# XPaths — post-login Tinder popups
XPATH_COOKIE_CONSENT = [
    "//button[contains(., 'I accept')]",
    "//button[contains(., 'I Accept')]",
]
XPATH_LOCATION_ALLOW = [
    "//button[contains(., 'Allow')]",
    "//button[contains(., 'allow')]",
]
XPATH_NOTIFY_ME = [
    "//button[contains(., 'Not interested')]",
    "//button[contains(., 'Maybe later')]",
    "//button[contains(., 'No Thanks')]",
    "//button[contains(., 'No thanks')]",
]

# XPaths — match popup close buttons
XPATH_MATCH_CLOSE = [
    "//button[contains(., 'BACK TO TINDER')]",
    "//button[contains(., 'Back to Tinder')]",
    "//button[contains(., 'Keep Swiping')]",
]
