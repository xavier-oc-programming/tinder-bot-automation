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
    """Pause execution until user types 'resume' (manual CAPTCHA/verification step)."""
    while True:
        user_input = input("Paused for manual action. Type 'resume' to continue: ").strip().lower()
        if user_input == "resume":
            break
        print("Not 'resume'. Still paused.")


def main():
    email = os.getenv("FACEBOOK_EMAIL")
    password = os.getenv("FACEBOOK_PASSWORD")
    if not email or not password:
        raise RuntimeError("FACEBOOK_EMAIL and FACEBOOK_PASSWORD must be set in .env")

    bot = TinderBot(email=email, password=password)

    try:
        # --- Open Tinder ---
        bot.open_tinder()
        bot.accept_cookies_early()

        # --- Facebook login flow ---
        bot.click_login_button()
        bot.click_login_with_facebook()
        bot.switch_to_facebook_window()
        bot.accept_facebook_cookies()
        bot.fill_facebook_credentials()
        bot.click_facebook_login()

        # --- Manual pause for 2FA / CAPTCHA ---
        # Facebook may ask for a verification code before showing "Continue as...".
        # Complete any phone/email verification now, then type 'resume'.
        wait_for_resume()

        bot.click_continue_as()

        # --- Return to Tinder and clear popups ---
        bot.return_to_tinder()
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
