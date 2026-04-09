# URLs
TINDER_URL = "https://tinder.com"

# Selenium
WAIT_TIMEOUT = 20    # seconds to wait for elements before timing out
CHROME_VERSION = 146  # must match your installed Chrome major version

# Timing / rate limits
NOPE_DELAY = 1.2   # seconds between left swipes (too fast risks a Tinder block)
POPUP_CLEAR_PAUSE = 2.0  # seconds to wait after closing a match popup

# XPaths — Tinder popup buttons
XPATH_COOKIE_EARLY = [
    '//*[@id="c-429777287"]/div/div[2]/div/div/div[1]/div[1]/button',
    "//button[contains(., 'I accept')]",
    "//button[contains(., 'Accept all')]",
]
XPATH_COOKIE_CONSENT = '//*[@id="c-429777287"]/div/div[2]/div/div/div[1]/div[1]/button'
XPATH_LOCATION_ALLOW = '//*[@id="c1298603789"]/div/div[2]/div/div/div[1]/div[1]/button'
XPATH_NOTIFY_ME     = '//*[@id="c-429777287"]/div/div/div/div/div[3]/button[1]'

# XPaths — Facebook login popup
XPATH_FB_COOKIE = (
    '//*[@id="facebook"]/body/div[2]/div[2]/div/div/div/div/div[3]/div[2]/div/div[2]/div[1]'
)
XPATH_FB_LOGIN_BTN = '//*[@id="loginbutton"]'
XPATH_FB_CONTINUE_AS = [
    "//div[@role='button' and starts-with(@aria-label, 'Continue as ')]",
    "//span[starts-with(normalize-space(.), 'Continue as ')]/ancestor::div[@role='button']",
]

# XPaths — match popup close buttons
XPATH_MATCH_CLOSE = [
    "//button[contains(., 'BACK TO TINDER')]",
    "//button[contains(., 'Back to Tinder')]",
    "//button[contains(., 'Keep Swiping')]",
]
