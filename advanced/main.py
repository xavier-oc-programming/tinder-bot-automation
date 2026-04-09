import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import os
import time
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import config
from bot import TinderBot


def wait_for_resume():
    """Pause execution until user types 'resume'."""
    while True:
        user_input = input("Paused. Type 'resume' to continue: ").strip().lower()
        if user_input == "resume":
            break
        print("Not 'resume'. Still paused.")


def main():
    phone = os.getenv("TINDER_PHONE")
    if not phone:
        raise RuntimeError("TINDER_PHONE must be set in .env (local number, e.g. 611122334)")

    bot = TinderBot(phone=phone)

    try:
        # --- Open Tinder ---
        bot.open_tinder()
        bot.accept_cookies_early()

        # --- Phone login flow ---
        bot.click_login_button()
        bot.click_login_with_phone()
        bot.enter_phone_number()
        bot.click_phone_next()

        # --- Manual pause: enter the SMS code in the browser, then type 'resume' ---
        print("SMS code sent to your phone. Enter it in the browser, then type 'resume'.")
        wait_for_resume()

        # --- Handle post-login Tinder popups ---
        bot.dismiss_tinder_popups()

        print("Login complete. Starting auto-swipe loop (LEFT = Nope)...")

        # --- Auto-swipe loop ---
        while True:
            try:
                bot.swipe_left()
                print("Nope sent.")
                time.sleep(config.NOPE_DELAY)
            except Exception as e:
                print(f"Swipe error: {e}. Attempting to clear popup...")
                bot.clear_match_popup()
                time.sleep(config.POPUP_CLEAR_PAUSE)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        bot.quit()


if __name__ == "__main__":
    main()
