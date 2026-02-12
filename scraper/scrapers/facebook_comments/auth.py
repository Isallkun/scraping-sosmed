"""Facebook authentication module using Playwright"""

from typing import Optional
from playwright.sync_api import Browser, BrowserContext, Page

from scraper.utils.logger import get_logger
from scraper.scrapers.facebook_comments.config import FBCommentConfig
from scraper.scrapers.facebook_comments.utils import random_delay, save_cookies, load_cookies

logger = get_logger('scraper.facebook_comments.auth')


class FacebookAuth:
    """Handle Facebook authentication using Playwright"""

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        self.email = email or FBCommentConfig.FB_EMAIL
        self.password = password or FBCommentConfig.FB_PASSWORD
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def login(self, browser: Browser, use_saved_cookies: bool = True) -> Page:
        """
        Login to Facebook using credentials or saved cookies.

        Args:
            browser: Playwright browser instance
            use_saved_cookies: Whether to try loading saved cookies first

        Returns:
            Authenticated page
        """
        logger.info("Starting Facebook authentication...")

        # Try to load saved cookies first
        if use_saved_cookies:
            cookies = load_cookies()
            if cookies:
                logger.info("Loading saved cookies...")
                self.context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                self.context.add_cookies(cookies)
                self.page = self.context.new_page()

                self.page.goto("https://www.facebook.com", timeout=FBCommentConfig.REQUEST_TIMEOUT)
                random_delay(3, 5)

                if self._is_logged_in():
                    logger.info("Successfully authenticated using saved cookies")
                    return self.page
                else:
                    logger.warning("Saved cookies expired, proceeding with fresh login...")
                    self.context.close()
                    self.context = None
                    self.page = None

        # Create browser context for fresh login
        if not self.context:
            self.context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

        if not self.page:
            self.page = self.context.new_page()

        return self._perform_login()

    def _perform_login(self) -> Page:
        """Perform actual login with credentials"""
        logger.info("Performing login with credentials...")

        try:
            self.page.goto("https://www.facebook.com", timeout=FBCommentConfig.REQUEST_TIMEOUT)
            random_delay(2, 3)

            # Fill email
            email_input = self.page.wait_for_selector(
                'input[name="email"]',
                timeout=10000
            )
            email_input.fill(self.email)
            random_delay(1, 2)

            # Fill password
            password_input = self.page.query_selector('input[name="pass"]')
            if password_input:
                password_input.fill(self.password)
                random_delay(1, 2)

            # Click login button
            login_button = self.page.query_selector('button[name="login"]')
            if not login_button:
                login_button = self.page.query_selector('button[type="submit"]')

            if login_button:
                login_button.click()
                logger.info("Login button clicked, waiting for response...")

                try:
                    self.page.wait_for_load_state("networkidle", timeout=30000)
                    random_delay(3, 5)
                except Exception as e:
                    logger.warning(f"Network idle timeout: {e}")
                    random_delay(3, 5)

                # Check for challenge/CAPTCHA
                if self._check_for_captcha():
                    logger.warning("CHALLENGE/CAPTCHA detected!")
                    logger.warning("Facebook requires additional verification.")
                    logger.warning("Please complete the challenge in the browser.")
                    input("Press ENTER after challenge is complete...")

                    try:
                        self.page.wait_for_url(
                            lambda url: '/checkpoint/' not in url and '/authentication/' not in url,
                            timeout=10000
                        )
                        random_delay(3, 5)
                    except Exception as e:
                        logger.warning(f"Timeout waiting for navigation: {e}")
                        random_delay(2, 3)

                    # Re-check login after challenge
                    max_retries = 3
                    for attempt in range(max_retries):
                        is_logged_in = self._is_logged_in()
                        has_challenge = self._check_for_captcha()

                        if is_logged_in and not has_challenge:
                            cookies = self.context.cookies()
                            save_cookies(cookies)
                            logger.info("Login successful after challenge!")
                            return self.page

                        if attempt < max_retries - 1:
                            random_delay(2, 4)

                    raise Exception("Facebook login failed after challenge")

                # Check if login was successful
                if self._is_logged_in():
                    logger.info("Login successful!")
                    cookies = self.context.cookies()
                    save_cookies(cookies)
                    return self.page
                else:
                    logger.warning("Automated login failed.")
                    logger.warning("Please login manually in the open browser window.")
                    input("Press ENTER after you have logged in manually...")

                    if self._is_logged_in():
                        logger.info("Login successful (manual verification)!")
                        cookies = self.context.cookies()
                        save_cookies(cookies)
                        return self.page
                    else:
                        raise Exception("Facebook login failed")
            else:
                logger.error("Login button not found")
                raise Exception("Login button not found")

        except Exception as e:
            logger.error(f"Login error: {e}")
            raise

    def _is_logged_in(self) -> bool:
        """Check if currently logged in to Facebook"""
        try:
            try:
                self.page.wait_for_load_state("domcontentloaded", timeout=5000)
            except Exception:
                pass

            current_url = self.page.url
            challenge_url_patterns = ['/checkpoint/', '/two_step_verification/', '/authentication/']
            for pattern in challenge_url_patterns:
                if pattern in current_url.lower():
                    return False

            login_form = self.page.query_selector('input[name="email"]')
            if login_form:
                return False

            if "login" in current_url.lower():
                return False

            if "facebook.com" in current_url:
                logger.info("On facebook.com without login form or challenge - LOGGED IN")
                return True

            return False
        except Exception as e:
            logger.error(f"Error checking login status: {e}")
            return False

    def _check_for_captcha(self) -> bool:
        """Check if CAPTCHA or challenge verification is present"""
        try:
            current_url = self.page.url

            challenge_patterns = [
                '/checkpoint/',
                '/two_step_verification/',
                '/authentication/'
            ]

            for pattern in challenge_patterns:
                if pattern in current_url.lower():
                    logger.info(f"Challenge page detected via URL: {pattern}")
                    return True

            captcha_selectors = [
                'iframe[title*="captcha"]',
                'iframe[title*="CAPTCHA"]',
                'div[id*="captcha"]',
                'div[class*="captcha"]'
            ]

            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    logger.info(f"CAPTCHA detected via selector: {selector}")
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking for CAPTCHA: {e}")
            return False

    def close(self) -> None:
        """Close browser context"""
        if self.context:
            self.context.close()
            logger.info("Browser context closed")
