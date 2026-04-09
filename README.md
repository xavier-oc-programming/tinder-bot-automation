# Auto Tinder Bot

Selenium bot that logs into Tinder via Facebook OAuth and automatically swipes left on profiles.

Open Chrome, navigate to Tinder, log in through Facebook, survive a wall of popups, and then
type `resume` — the bot takes over and sends a LEFT ARROW (Nope) keystroke every 1.2 seconds.
Profiles scroll past automatically; if a match overlay appears it is closed and swiping resumes.
The bot runs until you press Ctrl+C or close the terminal.

There are two builds in this repo. **original/** contains the course script exactly as written
during the Day 50 lesson — one file, all logic inline, credentials stored in constants
(redacted in the committed copy). **advanced/** restructures the same behaviour into an OOP
design: a `TinderBot` class owns every Selenium interaction, `config.py` centralises every
XPath and timing constant, and `main.py` orchestrates the flow. Credentials move to `.env` so
nothing sensitive is ever committed.

This project uses only the browser and Facebook's standard OAuth flow — no Tinder API, no
third-party services. Selenium drives a real Chrome instance.

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

### Facebook account

You need a Facebook account connected to your Tinder profile. The bot logs into Tinder
using the "Login with Facebook" OAuth flow.

| `.env` variable    | Where to find it                          |
|--------------------|-------------------------------------------|
| `FACEBOOK_EMAIL`   | Your Facebook login email address         |
| `FACEBOOK_PASSWORD`| Your Facebook account password            |

**Gotcha:** Facebook may present a CAPTCHA or two-factor verification prompt during login.
The bot pauses and waits for you to type `resume` after completing any manual step.

**Gotcha:** The XPaths targeting Tinder and Facebook popup buttons are brittle — Tinder's
DOM changes frequently. If the bot fails to click a button, inspect the element in Chrome
DevTools and update the relevant constant in `advanced/config.py`.

### ChromeDriver

Selenium requires ChromeDriver to match your installed Chrome version.

```
# macOS (Homebrew)
brew install chromedriver

# Or download manually and add to PATH:
# https://chromedriver.chromium.org/downloads
```

Verify ChromeDriver is on your PATH:
```
chromedriver --version
```

---

## 2. Quick start

```bash
pip install -r requirements.txt
cp .env.example .env        # fill in FACEBOOK_EMAIL and FACEBOOK_PASSWORD
python menu.py              # select 1 or 2, or run builds directly
```

Run builds directly:
```bash
python original/2_step_2_navigate_to_login_page.py
python advanced/main.py
```

---

## 3. Builds comparison

| Feature                       | original/              | advanced/                     |
|-------------------------------|------------------------|-------------------------------|
| Structure                     | Single file            | config + bot + main           |
| Credentials                   | Hardcoded (redacted)   | `.env` via python-dotenv      |
| Facebook login logic          | Module-level functions | `TinderBot` class methods     |
| Popup handling                | Repeated try/except    | `_click_if_present` helper    |
| XPaths / constants            | Inline literals        | All in `config.py`            |
| Error boundary                | `sys.exit` style       | Raises exceptions to `main`   |
| Browser cleanup               | Not guaranteed         | `finally: bot.quit()`         |
| Importable / testable         | No                     | Yes (`TinderBot` is importable)|

---

## 4. Usage

### original

```bash
python original/2_step_2_navigate_to_login_page.py
```

Edit `FACEBOOK_EMAIL` and `FACEBOOK_PASSWORD` at the top of the file (lines 13–14) with
your real credentials before running. The script opens Chrome, logs in, and starts swiping.
When prompted, complete any CAPTCHA manually then type `resume`.

### advanced

```bash
# Ensure .env is filled in, then:
python advanced/main.py
```

Example terminal output:
```
Clicked Tinder Login button successfully.
Clicked 'Login with Facebook' successfully.
Switched to Facebook login window.
Filled in Facebook credentials successfully.
Clicked Facebook 'Log In' button (normal click).
Paused for manual action. Type 'resume' to continue: resume
Login complete. Starting auto-swipe loop (LEFT = Nope)...
Nope sent.
Nope sent.
Nope sent.
Swipe error: element not interactable. Attempting to clear popup...
Closed match popup.
Nope sent.
```

Press **Ctrl+C** to stop. The browser closes cleanly.

---

## 5. Data flow

```
Input          → Fetch             → Process          → Output
.env creds       Selenium opens      WebDriverWait       ARROW_LEFT
(email +         Chrome, navigates   locates buttons,    keystroke sent
password)        to tinder.com,      JS-clicks them,     to browser;
                 handles Facebook    handles popups      Tinder registers
                 OAuth popup         and match overlays  a left swipe
```

1. **Load** — `main.py` reads `FACEBOOK_EMAIL` and `FACEBOOK_PASSWORD` from `.env`.
2. **Open** — `TinderBot.__init__` launches Chrome with notifications disabled.
3. **Navigate** — `open_tinder()` loads `https://tinder.com`; window handle is stored.
4. **Cookie banner** — `accept_cookies_early()` clicks the initial consent button.
5. **Login** — `click_login_button()` → `click_login_with_facebook()` → Facebook popup opens.
6. **Facebook window** — driver switches to popup; cookies accepted, credentials filled, Log In clicked, "Continue as..." clicked.
7. **Manual pause** — bot prints prompt; user handles CAPTCHA/2FA if needed, then types `resume`.
8. **Tinder popups** — `dismiss_tinder_popups()` closes cookie consent, location, and notify-me dialogs.
9. **Swipe loop** — `while True`: send `ARROW_LEFT`, sleep 1.2 s; on exception: clear match popup, sleep 2 s.

---

## 6. Features

### Both builds

**Facebook OAuth login** — Navigates the multi-window Facebook login flow: opens the popup,
accepts cookie consent, fills credentials, clicks Log In, and confirms "Continue as...".

**Manual CAPTCHA pause** — Execution suspends after login and waits for the user to type
`resume`. This handles Facebook's occasional CAPTCHA or 2FA prompts.

**Popup dismissal** — Handles Tinder's post-login overlay sequence: cookie/privacy consent,
location permission, and notification prompt.

**Auto-swipe loop** — Sends `Keys.ARROW_LEFT` once per cycle. Tinder registers this as a
left swipe (Nope). Runs indefinitely until Ctrl+C.

**Match popup recovery** — If a match overlay blocks the page and the swipe key stops
working, the bot attempts to click "Back to Tinder" or "Keep Swiping" before resuming.

### Advanced build only

**OOP encapsulation** — All Selenium calls live inside `TinderBot`. `main.py` reads like a
script; the class is importable and testable independently.

**Centralised config** — Every XPath, URL, timeout, and delay lives in `config.py`. Updating
a broken selector requires changing exactly one line.

**`.env` credentials** — `FACEBOOK_EMAIL` and `FACEBOOK_PASSWORD` are loaded from `.env` at
runtime. Nothing sensitive is committed.

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
Load .env credentials
  │
  ▼
Launch Chrome (notifications disabled)
  │
  ▼
Open https://tinder.com ──────────────────── cookie banner? → click Accept
  │
  ▼
Click "Log in" button
  │
  ▼
Click "Login with Facebook"
  │
  ▼
Facebook popup opens → switch driver to popup window
  │
  ├── Facebook cookie banner? → click Allow
  │
  ▼
Fill email + password → click Log In
  │
  ├── "Continue as..." button? → click it
  │
  ▼
PAUSE — user handles CAPTCHA/2FA manually, then types 'resume'
  │
  ▼
Switch back to Tinder window
  │
  ▼
Dismiss Tinder popups (cookie consent → location → notify-me)
  │
  ▼
┌─────────────────────────────────┐
│  SWIPE LOOP (while True)        │
│                                 │
│  send ARROW_LEFT (Nope)         │
│    │                            │
│    ├── success → sleep 1.2 s   │
│    │                            │
│    └── exception                │
│          │                      │
│          ▼                      │
│     clear_match_popup()         │
│       ├── found → JS click      │
│       └── not found → pass      │
│     sleep 2 s                   │
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
├── art.py                     # LOGO ascii art
├── requirements.txt           # pip packages + ChromeDriver note
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
│   └── main.py                # orchestrator — login flow + swipe loop
│
└── docs/
    └── COURSE_NOTES.md        # original exercise description + concepts
```

---

## 9. Module reference

### `advanced/bot.py` — class `TinderBot`

| Method | Returns | Description |
|---|---|---|
| `__init__(email, password)` | `TinderBot` | Stores credentials; launches Chrome with notification prefs disabled |
| `open_tinder()` | `None` | Navigates to `TINDER_URL`; stores the window handle |
| `return_to_tinder()` | `None` | Switches driver focus back to the Tinder window |
| `accept_cookies_early()` | `None` | Clicks Tinder's initial cookie banner if present |
| `click_login_button()` | `None` | Clicks the main "Log in" button; raises `RuntimeError` on timeout |
| `click_login_with_facebook()` | `None` | Clicks "Login with Facebook" in the modal; raises `RuntimeError` on failure |
| `switch_to_facebook_window()` | `None` | Switches focus to the Facebook OAuth popup; raises `RuntimeError` if not found |
| `accept_facebook_cookies()` | `None` | Clicks "Allow all cookies" in the Facebook popup if it appears |
| `fill_facebook_credentials()` | `None` | Clears and types email + password into the Facebook login form |
| `click_facebook_login()` | `None` | Clicks Facebook's "Log In" button; raises `RuntimeError` on timeout |
| `click_continue_as()` | `None` | Clicks "Continue as [Name]"; silently skips if not found |
| `dismiss_tinder_popups()` | `None` | Clicks cookie consent, location allow, and notify-me buttons in sequence |
| `swipe_left()` | `None` | Sends `Keys.ARROW_LEFT` to the page `<body>` (Nope) |
| `clear_match_popup()` | `None` | Attempts to close a match overlay via known XPaths |
| `quit()` | `None` | Calls `driver.quit()` to close the browser |
| `_js_click(element)` | `None` | Normal click with JS fallback (internal) |
| `_click_if_present(xpath)` | `None` | Click by XPath; silently skip on `TimeoutException` (internal) |

---

## 10. Configuration reference

All constants live in `advanced/config.py`.

| Constant | Default | Description |
|---|---|---|
| `TINDER_URL` | `"https://tinder.com"` | Tinder homepage URL |
| `WAIT_TIMEOUT` | `20` | Seconds `WebDriverWait` waits before timing out |
| `NOPE_DELAY` | `1.2` | Seconds to sleep between left swipes |
| `POPUP_CLEAR_PAUSE` | `2.0` | Seconds to sleep after closing a match popup |
| `XPATH_COOKIE_EARLY` | `[...]` | XPath candidates for the initial cookie banner |
| `XPATH_COOKIE_CONSENT` | `"..."` | XPath for post-login cookie consent button |
| `XPATH_LOCATION_ALLOW` | `"..."` | XPath for location permission allow button |
| `XPATH_NOTIFY_ME` | `"..."` | XPath for the notify-me button |
| `XPATH_FB_COOKIE` | `"..."` | XPath for Facebook's "Allow all cookies" button |
| `XPATH_FB_LOGIN_BTN` | `"..."` | XPath for Facebook's "Log In" submit button |
| `XPATH_FB_CONTINUE_AS` | `[...]` | XPath candidates for "Continue as [Name]" |
| `XPATH_MATCH_CLOSE` | `[...]` | XPath candidates for match popup close buttons |

---

## 11. Data schema

This project has no file input or output. All interaction is with the live Tinder web UI.

**Credential format** (`.env`):
```
FACEBOOK_EMAIL=you@example.com
FACEBOOK_PASSWORD=yourpassword
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
| `FACEBOOK_EMAIL` | Yes | Facebook account email used to log into Tinder |
| `FACEBOOK_PASSWORD` | Yes | Facebook account password |

---

## 13. Design decisions

**`config.py` — zero magic numbers / inline XPaths.** Tinder's DOM changes frequently.
Centralising every XPath and delay in one file means a broken selector requires changing
exactly one line, not hunting through `bot.py`.

**Separate `TinderBot` class.** All Selenium code is in one place. `main.py` reads like a
plain English script. The class is importable — you can instantiate `TinderBot` in a test or
REPL without running the full flow.

**Credentials via `.env`, never hardcoded.** The original course file contained plaintext
credentials; these are redacted in the committed copy. The advanced build reads from
`os.getenv()` so nothing sensitive can be accidentally committed.

**`.env.example` committed, `.env` gitignored.** Documents exactly which variables are
needed without leaking values. New contributors copy the example and fill it in.

**`Path(__file__).parent` for all paths.** `.env` is loaded relative to `main.py`'s own
directory, so the build works whether launched from `menu.py` (via `subprocess.run`) or
directly from the terminal.

**`_click_if_present` for optional popups.** Post-login popup sequence is non-deterministic
— Tinder sometimes shows all three, sometimes one, sometimes none. Using a helper that
catches `TimeoutException` silently means the sequence always completes regardless.

**`_js_click` fallback.** Several Tinder and Facebook buttons are overlapped by other DOM
elements and reject normal Selenium clicks. `driver.execute_script("arguments[0].click()")`
bypasses the interactability check and is a reliable fallback.

**`finally: bot.quit()`.** If any step in the login flow raises an unhandled exception, the
browser closes cleanly instead of leaving a zombie Chrome process.

**Manual `resume` pause.** Facebook's CAPTCHA and two-factor prompts cannot be automated
reliably. The pause lets the user handle them manually without restarting the script.

**`while True` loop, not recursion.** The swipe loop in `main.py` is a plain `while True`
with `time.sleep`. No stack growth, no re-entrant calls.

**`try/except` per iteration, not around the whole loop.** A single swipe failure (e.g.,
match popup) does not kill the bot — the exception is caught, the popup is cleared, and the
next iteration starts immediately.

**No GitHub Actions workflow.** This bot requires an interactive browser session, a manual
CAPTCHA step, and runs indefinitely. None of these characteristics are compatible with CI.
Run it locally.

**`sys.path.insert` in `bot.py` and `main.py`.** Ensures sibling imports (`import config`,
`from bot import TinderBot`) resolve correctly whether the scripts are run directly or
launched by `menu.py` via `subprocess.run`.

---

## 14. Course context

Built as Day 50 of [100 Days of Code: The Complete Python Pro Bootcamp](https://www.udemy.com/course/100-days-of-code/) by Dr. Angela Yu.

**Concepts covered in the original build:**
- Chrome WebDriver setup with `ChromeOptions`
- Disabling browser notifications via `prefs` experimental option
- `WebDriverWait` + `expected_conditions` for robust element waiting
- Locator strategies: XPath, CSS selector, element ID, tag name
- Multi-window automation (`window_handles`, `switch_to.window`)
- JavaScript execution for clicks on overlapped elements
- Keyboard simulation with `Keys.ARROW_LEFT`
- `try/except TimeoutException` for optional UI elements
- `while True` bot loop with exception-based recovery

**The advanced build extends into:**
- Object-oriented encapsulation (`TinderBot` class)
- Single-responsibility module layout (`config` / `bot` / `main`)
- Environment-variable credential management with `python-dotenv`
- Internal helper methods (`_js_click`, `_click_if_present`)
- Clean resource teardown with `finally`

See [docs/COURSE_NOTES.md](docs/COURSE_NOTES.md) for the full concept breakdown.

---

## 15. Dependencies

| Module | Used in | Purpose |
|---|---|---|
| `selenium` | `original/`, `advanced/bot.py` | Browser automation — drives Chrome |
| `python-dotenv` | `advanced/main.py` | Loads `.env` into `os.environ` |
| `os` | `advanced/main.py`, `menu.py` | Reads env vars; clears terminal |
| `sys` | `advanced/main.py`, `advanced/bot.py`, `menu.py` | `sys.path.insert`, `sys.executable` |
| `time` | `original/`, `advanced/bot.py`, `advanced/main.py` | `time.sleep` for rate limiting |
| `pathlib.Path` | `advanced/main.py`, `advanced/bot.py`, `menu.py` | Portable file paths |
| `subprocess` | `menu.py` | Launches builds as child processes |
