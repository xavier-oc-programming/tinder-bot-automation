# Course Notes — Day 50

## Exercise Description

Build an automated Tinder bot using Selenium that:
1. Opens Tinder in Chrome
2. Logs in via Facebook OAuth
3. Dismisses cookie, location, and notification popups
4. Automatically swipes left (Nope) on profiles in a continuous loop

This is a capstone exercise for the Selenium module, combining all skills practised in
Days 48–50: browser automation, multi-window handling, waiting strategies, and
interacting with complex third-party login flows.

## Concepts Covered

- `selenium.webdriver.Chrome` + `ChromeOptions` (detach, notification prefs)
- `WebDriverWait` + `expected_conditions` (`element_to_be_clickable`, `presence_of_element_located`)
- Locator strategies: `By.XPATH`, `By.CSS_SELECTOR`, `By.ID`, `By.TAG_NAME`
- Multi-window handling (`window_handles`, `switch_to.window`)
- JavaScript injection click (`execute_script("arguments[0].click()"`) for stubborn elements
- `Keys.ARROW_LEFT` for keyboard-driven swiping
- `try/except TimeoutException` for optional popups
- `while True` bot loop with error recovery

## Original Files

| File | Content |
|---|---|
| `0_day_50_goals.py` | Comment stub — course day outline |
| `1_step_1_setup_account.py` | Comment stub — Tinder account setup notes |
| `2_step_2_navigate_to_login_page.py` | **Full implementation** — the working bot |
| `3_step_3_login_with_facebook.py` | Comment stub — step placeholder |
| `4_step_4_dismiss_all_requests.py` | Comment stub — step placeholder |
| `5_step_5_hit_like.py` | Comment stub — step placeholder |

The course delivered the full solution in a single file. The numbered stubs represent
the step-by-step build-up taught during the lesson.

## Credential Note

The original course file (`2_step_2_navigate_to_login_page.py`) contained hardcoded
Facebook credentials. These have been redacted with `*****` in all committed copies.
The advanced build reads credentials from `.env` via `python-dotenv`.

## The Advanced Build Extends Into

- Object-oriented design (all browser logic encapsulated in `TinderBot`)
- Separation of config constants from logic (`config.py`)
- Credentials via `.env` — never hardcoded
- `Path(__file__).parent` for portable file paths
- Clean error boundary: `TinderBot` raises exceptions; `main.py` decides how to handle them
- `bot.quit()` in a `finally` block ensures the browser always closes cleanly
