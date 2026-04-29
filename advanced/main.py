import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import time
import threading
from dotenv import load_dotenv
from selenium.common.exceptions import WebDriverException

load_dotenv(Path(__file__).parent.parent / ".env")

import config
from bot import TinderBot


def mask_phone(phone: str) -> str:
    return "*" * max(0, len(phone) - 3) + phone[-3:]


def wait_for_resume():
    while True:
        user_input = input("Paused. Type 'resume' to continue: ").strip().lower()
        if user_input == "resume":
            break
        print("Not 'resume'. Still paused.")


def is_window_closed(e: Exception) -> bool:
    return "no such window" in str(e).lower() or "web view not found" in str(e).lower()


def swipe_loop(bot):
    """Run the swipe loop with p=pause, r=resume, s=stop controls in a background thread."""
    paused = threading.Event()
    stop   = threading.Event()

    def read_commands():
        print("Controls: [p] pause   [r] resume   [s] stop")
        while not stop.is_set():
            cmd = input().strip().lower()
            if cmd == "p":
                paused.set()
                print("Paused. Type 'r' to resume.")
            elif cmd == "r":
                paused.clear()
                print("Resuming...")
            elif cmd == "s":
                stop.set()
                paused.clear()
                print("Stopping...")

    threading.Thread(target=read_commands, daemon=True).start()

    while not stop.is_set():
        if paused.is_set():
            time.sleep(0.2)
            continue
        bot.clear_match_popup()
        try:
            bot.swipe_left()
            print("Nope sent.")
            time.sleep(config.NOPE_DELAY)
        except WebDriverException as e:
            if is_window_closed(e):
                print("Browser closed — stopping.")
                break
            print(f"Swipe error: {e}. Retrying after pause...")
            time.sleep(config.POPUP_CLEAR_PAUSE)


def main():
    phone = os.getenv("TINDER_PHONE")
    if not phone:
        raise RuntimeError("TINDER_PHONE must be set in .env (local number, e.g. 611122334)")

    bot = TinderBot(phone=phone)

    try:
        bot.open_tinder()
        bot.accept_cookies_early()

        if bot.is_logged_in():
            print("Already logged in — skipping login flow.")
        else:
            bot.click_login_button()
            bot.click_login_with_phone()
            bot.enter_phone_number()
            bot.click_phone_next()
            bot.redact_phone_from_page()

            print(f"SMS code sent to {mask_phone(phone)}. Enter it in the browser, then type 'resume'.")
            wait_for_resume()

            print("Dismissing popups...")
            bot.dismiss_tinder_popups()

        print("Login complete. Starting auto-swipe loop (LEFT = Nope)...")
        swipe_loop(bot)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        bot.quit()


if __name__ == "__main__":
    main()
