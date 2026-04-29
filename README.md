# Auto Tinder Bot

Selenium bot that logs into Tinder via phone number and automatically swipes left on profiles.

Open Chrome, navigate to Tinder, log in with your phone number, enter the SMS code when
prompted, then type `resume` — the bot takes over and sends a LEFT ARROW (Nope) keystroke
every 1.2 seconds. Profiles scroll past automatically; if a match overlay appears it is closed
and swiping resumes. The bot runs until you press Ctrl+C or close the terminal.

On subsequent runs the bot reuses a persistent Chrome profile, so if your Tinder session is
still active it skips the login flow entirely and jumps straight to swiping.

There are two builds in this repo. **original/** contains the course script exactly as written
during the Day 50 lesson — one file, all logic inline, credentials stored in constants
(redacted in the committed copy). **advanced/** restructures the same behaviour into an OOP
design: a `TinderBot` class owns every Selenium interaction, `config.py` centralises every
XPath and timing constant, and `main.py` orchestrates the flow. Credentials move to `.env` so
nothing sensitive is ever committed.

This project uses only the browser and Tinder's standard phone-number login flow — no Tinder
API, no third-party services. Selenium drives a real Chrome instance via `undetected-chromedriver`.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick start](#2-quick-start)
3. [Builds comparison](#3-builds-comparison)
4. [Usage](#4-usage)
5. [Data flow](#5-data-flow)
6. [Features](#6-features)
7. [Navigation flow](#7-navigation-flow)
8. [Architecture](#8-architecture)
9. [Module reference](#9-module-reference)
10. [Configuration reference](#10-configuration-reference)
11. [Data schema](#11-data-schema)
12. [Environment variables](#12-environment-variables)
13. [Design decisions](#13-design-decisions)
14. [Course context](#14-course-context)
15. [Dependencies](#15-dependencies)

---

## 1. Prerequisites

### Phone number

You need a phone number connected to your Tinder profile. The bot logs in using Tinder's
phone-number login flow and waits for you to enter the SMS verification code manually.

| `.env` variable | Where to find it                                     |
|-----------------|------------------------------------------------------|
| `TINDER_PHONE`  | Your phone number (local format, e.g. `611122334`)   |

**Gotcha:** The bot pauses after submitting the phone number and waits for you to type
`resume` once you have entered the SMS code in the browser.

**Gotcha:** The XPaths targeting Tinder's buttons are brittle — Tinder's DOM changes
frequently. If the bot fails to click a button, inspect the element in Chrome DevTools and
update the relevant constant in `advanced/config.py`.

### Chrome version

`undetected-chromedriver` requires you to set `CHROME_VERSION` in `advanced/config.py` to
match your installed Chrome major version number.

```bash
# Find your Chrome version:
google-chrome --version      # Linux
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version  # macOS
```

---

## 2. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in TINDER_PHONE
python menu.py              # select 1 or 2, or run builds directly
```

Run the advanced build directly:
```bash
python advanced/main.py
```

---

## 3. Builds comparison

| Feature                       | original/              | advanced/                          |
|-------------------------------|------------------------|------------------------------------|
| Structure                     | Single file            | config + bot + main                |
| Credentials                   | Hardcoded (redacted)   | `.env` via python-dotenv           |
| Login method                  | Phone number           | Phone number                       |
| Persistent Chrome profile     | No                     | Yes — skips login if session alive |
| Popup handling                | Repeated try/except    | `_click_if_present` helper         |
| XPaths / constants            | Inline literals        | All in `config.py`                 |
| Error boundary                | `sys.exit` style       | Raises exceptions to `main`        |
| Browser cleanup               | Not guaranteed         | `finally: bot.quit()`              |
| Importable / testable         | No                     | Yes (`TinderBot` is importable)    |

---

## 4. Usage

### original

```bash
python original/2_step_2_navigate_to_login_page.py
```

Edit `TINDER_PHONE` at the top of the file with your phone number before running. The script
opens Chrome, navigates to Tinder, and starts the phone-number login flow.

### advanced

```bash
# Ensure .env is filled in, then:
python advanced/main.py
```

**First run** — logs in via phone number. The bot pauses after submitting your number;
enter the SMS code in the browser, then type `resume`. Tinder session is saved to
`advanced/.chrome_profile/`.

**Subsequent runs** — the bot navigates straight to `tinder.com/app/recs`. If the session is
still active it prints `Already logged in — skipping login flow.` and starts swiping immediately.

Example terminal output (first run):
```
SMS code sent to your phone. Enter it in the browser, then type 'resume'.
Paused. Type 'resume' to continue: resume
Dismissing popups...
Login complete. Starting auto-swipe loop (LEFT = Nope)...
Nope sent.
Nope sent.
Nope sent.
Swipe error: element not interactable. Retrying after pause...
Nope sent.
```

Example terminal output (returning run):
```
Already logged in — skipping login flow.
Login complete. Starting auto-swipe loop (LEFT = Nope)...
Nope sent.
Nope sent.
```

Press **Ctrl+C** to stop. The browser closes cleanly.

---

## 5. Data flow

```
Input          → Fetch             → Process          → Output
.env phone       Selenium opens      WebDriverWait       ARROW_LEFT
number           Chrome with         locates buttons,    keystroke sent
                 persistent          JS-clicks them,     to browser;
                 profile, navigates  handles popups      Tinder registers
                 to /app/recs        and match overlays  a left swipe
```

1. **Load** — `main.py` reads `TINDER_PHONE` from `.env`.
2. **Open** — `TinderBot.__init__` launches Chrome with the persistent profile and notification prefs.
3. **Navigate** — `open_tinder()` loads `https://tinder.com/app/recs`.
4. **Session check** — `is_logged_in()` checks whether the URL stayed on `/app`; if yes, skip to step 8.
5. **Cookie banner** — `accept_cookies_early()` clicks the initial consent button if present.
6. **Login** — `click_login_button()` → `click_login_with_phone()` → phone number entered → Next clicked.
7. **Manual pause** — bot prints prompt; user enters SMS code in browser, then types `resume`.
8. **Tinder popups** — `dismiss_tinder_popups()` closes cookie consent, location, and notify-me dialogs.
9. **Swipe loop** — `while True`: send `ARROW_LEFT`, sleep 1.2 s; on exception: clear match popup, sleep 2 s.

---

## 6. Features

### Both builds

**Phone number login** — Navigates Tinder's phone-number login flow: clicks "Log in",
selects "Log in with phone number", types the number, and clicks Next.

**Manual SMS pause** — Execution suspends after submitting the phone number and waits for
the user to type `resume` once the SMS code has been entered in the browser.

**Popup dismissal** — Handles Tinder's post-login overlay sequence: cookie/privacy consent,
location permission, and notification prompt.

**Auto-swipe loop** — Sends `Keys.ARROW_LEFT` once per cycle. Tinder registers this as a
left swipe (Nope). Runs indefinitely until Ctrl+C.

**Match popup recovery** — If a match overlay blocks the page and the swipe key stops
working, the bot attempts to click "Back to Tinder" or "Keep Swiping" before resuming.

### Advanced build only

**Persistent Chrome profile** — Chrome launches with `--user-data-dir` pointing to
`advanced/.chrome_profile/`. Cookies and session data survive between runs, so you only need
to log in once.

**Session detection** — On startup the bot navigates to `tinder.com/app/recs` and checks the
resulting URL. If Tinder kept it on `/app`, the session is live and the login flow is skipped.

**OOP encapsulation** — All Selenium calls live inside `TinderBot`. `main.py` reads like a
plain English script; the class is importable and testable independently.

**Centralised config** — Every XPath, URL, timeout, and delay lives in `config.py`. Updating
a broken selector requires changing exactly one line.

**`.env` credentials** — `TINDER_PHONE` is loaded from `.env` at runtime. Nothing sensitive
is committed.

**JS click fallback** — `_js_click()` first attempts a normal Selenium click; if the element
is overlapped or not interactable it falls back to `driver.execute_script("arguments[0].click()")`.

**`finally` cleanup** — `bot.quit()` runs in a `finally` block so the browser closes even
if an unhandled exception is raised.

---

## 7. Navigation flow

### a) Terminal menu tree

```
python menu.py
│
├── 1 → original/2_step_2_navigate_to_login_page.py
│         (subprocess, cwd=original/)
│         Press Enter to return to menu
│
├── 2 → advanced/main.py
│         (subprocess, cwd=advanced/)
│         Press Enter to return to menu
│
└── q → exit
```

### b) Execution flow

```
START
  │
  ▼
Load .env (TINDER_PHONE)
  │
  ▼
Launch Chrome with persistent profile
  │
  ▼
Navigate to tinder.com/app/recs
  │
  ▼
is_logged_in()? ──── YES ──────────────────────────────────┐
  │                                                         │
  NO                                                        │
  │                                                         │
  ▼                                                         │
accept_cookies_early() (optional banner)                    │
  │                                                         │
  ▼                                                         │
Click "Log in" → "Log in with phone number"                 │
  │                                                         │
  ▼                                                         │
Enter phone number → click Next                             │
  │                                                         │
  ▼                                                         │
PAUSE — user enters SMS code in browser, types 'resume'     │
  │                                                         │
  ▼                                                         │
dismiss_tinder_popups() ◄───────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────┐
│  SWIPE LOOP (while True)        │
│                                 │
│  clear_match_popup()            │
│  send ARROW_LEFT (Nope)         │
│    │                            │
│    ├── success → sleep 1.2 s   │
│    │                            │
│    └── exception → sleep 2 s   │
└──────────────── ◄ loop ─────────┘
  │
  ▼ (Ctrl+C)
bot.quit() → browser closes
STOP
```

---

## 8. Architecture

```
day-50-auto-tinder-bot/
│
├── menu.py                    # terminal menu — launches either build
├── art.py                     # ASCII art logo
├── requirements.txt           # pip packages
├── .env.example               # template for credentials
├── .env                       # real credentials — gitignored
├── .gitignore
│
├── original/                  # course files, verbatim (credentials redacted)
│   ├── 0_day_50_goals.py
│   ├── 1_step_1_setup_account.py
│   ├── 2_step_2_navigate_to_login_page.py  # ← main course script
│   ├── 3_step_3_login_with_facebook.py
│   ├── 4_step_4_dismiss_all_requests.py
│   └── 5_step_5_hit_like.py
│
├── advanced/
│   ├── config.py              # all constants: URLs, XPaths, timeouts, delays
│   ├── bot.py                 # TinderBot class — all Selenium logic
│   ├── main.py                # orchestrator — login flow + swipe loop
│   └── .chrome_profile/       # persistent Chrome session (gitignored)
│
└── docs/
    └── COURSE_NOTES.md        # original exercise description + concepts
```

---

## 9. Module reference

### `advanced/bot.py` — class `TinderBot`

| Method | Returns | Description |
|---|---|---|
| `__init__(phone)` | `TinderBot` | Stores phone number; launches Chrome with persistent profile and notification prefs disabled |
| `open_tinder()` | `None` | Navigates to `TINDER_APP_URL` (`/app/recs`) |
| `is_logged_in()` | `bool` | Returns `True` if the URL stayed on `/app` after navigation (session alive) |
| `accept_cookies_early()` | `None` | Clicks Tinder's initial cookie banner if present (3 s timeout) |
| `click_login_button()` | `None` | Clicks the main "Log in" button; raises `RuntimeError` on timeout |
| `click_login_with_phone()` | `None` | Clicks "Log in with phone number" in the modal; raises `RuntimeError` on failure |
| `enter_phone_number()` | `None` | Finds the phone input and types the number from `.env` |
| `click_phone_next()` | `None` | JS-clicks the Next button after the phone number is entered |
| `dismiss_tinder_popups()` | `None` | Clicks cookie consent, location allow, and notify-me buttons in sequence |
| `swipe_left()` | `None` | Sends `Keys.ARROW_LEFT` to the page `<body>` (Nope) |
| `clear_match_popup()` | `None` | Attempts to close a match overlay via known XPaths |
| `quit()` | `None` | Calls `driver.quit()` to close the browser |
| `_js_click(element)` | `None` | Normal click with JS fallback (internal) |
| `_click_if_present(xpath)` | `None` | Click by XPath; silently skip on `TimeoutException` (internal) |
| `_click_first_present(xpath_list)` | `None` | Try each XPath; click the first found (internal) |

---

## 10. Configuration reference

All constants live in `advanced/config.py`.

| Constant | Default | Description |
|---|---|---|
| `TINDER_URL` | `"https://tinder.com"` | Tinder homepage URL |
| `TINDER_APP_URL` | `"https://tinder.com/app/recs"` | Deep link to the swipe screen |
| `CHROME_PROFILE_DIR` | `advanced/.chrome_profile/` | Persistent Chrome user data directory (overrideable via env var) |
| `WAIT_TIMEOUT` | `20` | Seconds `WebDriverWait` waits before timing out |
| `CHROME_VERSION` | `146` | Chrome major version — must match your installed Chrome |
| `NOPE_DELAY` | `1.2` | Seconds to sleep between left swipes |
| `POPUP_CLEAR_PAUSE` | `2.0` | Seconds to sleep after closing a match popup |
| `XPATH_COOKIE_EARLY` | `[...]` | XPath candidates for the initial cookie banner |
| `XPATH_LOGIN_WITH_PHONE` | `[...]` | XPath candidates for the "Log in with phone number" button |
| `CSS_PHONE_INPUT_CANDIDATES` | `[...]` | CSS selectors tried in order to find the phone input field |
| `XPATH_PHONE_NEXT` | `[...]` | XPath candidates for the Next button after phone entry |
| `XPATH_COOKIE_CONSENT` | `[...]` | XPath for post-login cookie consent button |
| `XPATH_LOCATION_ALLOW` | `[...]` | XPath for location permission allow button |
| `XPATH_NOTIFY_ME` | `[...]` | XPath for the notify-me / not-interested button |
| `XPATH_MATCH_CLOSE` | `[...]` | XPath candidates for match popup close buttons |

---

## 11. Data schema

This project has no file input or output. All interaction is with the live Tinder web UI.

**Credential format** (`.env`):
```
TINDER_PHONE=611122334
```

**Swipe signal** — a single `Keys.ARROW_LEFT` keystroke sent to `<body>`. Tinder maps this
to a left swipe (Nope) internally.

**Match popup signal** — any of these button texts indicates a match overlay is blocking the
page: `"BACK TO TINDER"`, `"Back to Tinder"`, `"Keep Swiping"`.

---

## 12. Environment variables

Copy `.env.example` to `.env` and fill in values.

| Variable | Required | Description |
|---|---|---|
| `TINDER_PHONE` | Yes | Phone number connected to your Tinder account (local format, e.g. `611122334`) |
| `CHROME_PROFILE_DIR` | No | Override path for the persistent Chrome profile directory |

---

## 13. Design decisions

**Persistent Chrome profile.** Chrome is launched with `--user-data-dir` pointing to
`advanced/.chrome_profile/`. Cookies and login sessions survive between runs. On the second
run, if Tinder's session cookie is still valid, the login flow is skipped entirely.

**Session detection via URL redirect.** The bot navigates directly to `tinder.com/app/recs`.
If the URL stays on `/app`, the session is live. If Tinder redirects back to the home page,
the session has expired and the login flow runs. This is more reliable than searching for
DOM elements that may change with Tinder's frequent frontend deployments.

**`config.py` — zero magic numbers / inline XPaths.** Tinder's DOM changes frequently.
Centralising every XPath and delay in one file means a broken selector requires changing
exactly one line, not hunting through `bot.py`.

**Separate `TinderBot` class.** All Selenium code is in one place. `main.py` reads like a
plain English script. The class is importable — you can instantiate `TinderBot` in a test or
REPL without running the full flow.

**Credentials via `.env`, never hardcoded.** The original course file contained plaintext
credentials; these are redacted in the committed copy. The advanced build reads from
`os.getenv()` so nothing sensitive can be accidentally committed.

**Short timeouts for optional elements.** Cookie banners, popups, and location prompts use a
3–4 s timeout rather than the global 20 s. When already logged in these elements never
appear; a short timeout means the bot doesn't stall for up to a minute waiting for them.

**`_click_if_present` for optional popups.** Post-login popup sequence is non-deterministic
— Tinder sometimes shows all three, sometimes one, sometimes none. Using a helper that
catches `TimeoutException` silently means the sequence always completes regardless.

**`_js_click` fallback.** Several Tinder buttons are overlapped by other DOM elements and
reject normal Selenium clicks. `driver.execute_script("arguments[0].click()")` bypasses the
interactability check and is a reliable fallback.

**`finally: bot.quit()`.** If any step in the login flow raises an unhandled exception, the
browser closes cleanly instead of leaving a zombie Chrome process.

**Manual `resume` pause.** Tinder's SMS verification cannot be automated. The pause lets
the user enter the code manually without restarting the script.

**`while True` loop, not recursion.** The swipe loop in `main.py` is a plain `while True`
with `time.sleep`. No stack growth, no re-entrant calls.

**No GitHub Actions workflow.** This bot requires an interactive browser session, a manual
SMS step, and runs indefinitely. None of these characteristics are compatible with CI.
Run it locally.

---

## 14. Course context

Built as Day 50 of [100 Days of Code: The Complete Python Pro Bootcamp](https://www.udemy.com/course/100-days-of-code/) by Dr. Angela Yu.

**Concepts covered in the original build:**
- Chrome WebDriver setup with `ChromeOptions`
- Disabling browser notifications via `prefs` experimental option
- `WebDriverWait` + `expected_conditions` for robust element waiting
- Locator strategies: XPath, CSS selector, element ID, tag name
- JavaScript execution for clicks on overlapped elements
- Keyboard simulation with `Keys.ARROW_LEFT`
- `try/except TimeoutException` for optional UI elements
- `while True` bot loop with exception-based recovery

**The advanced build extends into:**
- Object-oriented encapsulation (`TinderBot` class)
- Single-responsibility module layout (`config` / `bot` / `main`)
- Environment-variable credential management with `python-dotenv`
- Persistent Chrome profiles for session reuse across runs
- URL-based session detection to skip login when already authenticated
- Internal helper methods (`_js_click`, `_click_if_present`, `_click_first_present`)
- Clean resource teardown with `finally`

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 15. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `undetected-chromedriver` | `advanced/bot.py` | Launches Chrome in a way that avoids Tinder's bot detection |
| `selenium` | `original/`, `advanced/bot.py` | Browser automation — drives Chrome |
| `python-dotenv` | `advanced/main.py` | Loads `.env` into `os.environ` |
| `os` | `advanced/config.py`, `advanced/main.py`, `menu.py` | Reads env vars; clears terminal |
| `sys` | `advanced/main.py`, `advanced/bot.py`, `menu.py` | `sys.path.insert`, `sys.executable` |
| `time` | `original/`, `advanced/bot.py`, `advanced/main.py` | `time.sleep` for rate limiting |
| `pathlib.Path` | `advanced/main.py`, `advanced/bot.py`, `menu.py` | Portable file paths |
| `subprocess` | `menu.py` | Launches builds as child processes |
