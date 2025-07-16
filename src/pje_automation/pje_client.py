"""
PJe Client - Main automation class for PJe TJMG system.
"""

import glob
import os
import time
from typing import Dict, List, Optional

import requests
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .config import PJeConfig
from .exceptions import (DownloadError, LoginError, NavigationError,
                         ProcessNotFoundError)
from .utils import (ensure_directory_exists, format_file_size,
                    parse_process_number, setup_logging)


class PJeClient:
    """Main client for automating PJe TJMG operations."""

    def __init__(self, headless: bool = False, log_level: str = "INFO"):
        """Initialize PJe client."""
        self.config = PJeConfig()
        self.driver = None
        self.wait = None
        self.headless = headless

        # Setup logging
        log_file = os.path.join(self.config.LOGS_DIR, "pje_automation.log")
        self.logger = setup_logging(log_level, log_file)

        # Create necessary directories
        for directory in self.config.get_directories().values():
            ensure_directory_exists(directory)

    def __enter__(self):
        """Context manager entry."""
        self.setup_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def setup_driver(self) -> None:
        """Set up Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument("--headless")

            # Apply browser options from config
            for option, value in self.config.BROWSER_OPTIONS.items():
                if option == "window_size" and not self.headless:
                    chrome_options.add_argument(f"--window-size={value[0]},{value[1]}")
                elif option == "disable_extensions" and value:
                    chrome_options.add_argument("--disable-extensions")
                elif option == "no_sandbox" and value:
                    chrome_options.add_argument("--no-sandbox")
                elif option == "disable_dev_shm_usage" and value:
                    chrome_options.add_argument("--disable-dev-shm-usage")

            # Additional options
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option(
                "excludeSwitches", ["enable-automation"]
            )
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Set download directory
            download_dir = os.path.abspath(self.config.DATA_DIR)
            prefs = {
                "download.default_directory": download_dir,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
            chrome_options.add_experimental_option("prefs", prefs)

            # Set user agent
            chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )

            self.wait = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT)
            self.logger.info("WebDriver initialized successfully")

        except WebDriverException as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def close(self) -> None:
        """Close the WebDriver."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing WebDriver: {e}")

    def take_screenshot(self, filename: str) -> None:
        """Take a screenshot and save to screenshots directory."""
        screenshot_path = os.path.join(self.config.SCREENSHOTS_DIR, filename)
        self.driver.save_screenshot(screenshot_path)
        self.logger.debug(f"Screenshot saved: {screenshot_path}")

    def login(self) -> bool:
        """Perform login to PJe system."""
        try:
            self.logger.info(f"Navigating to {self.config.LOGIN_URL}")
            self.driver.get(self.config.LOGIN_URL)

            # Wait for main page to load
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.logger.info("✅ Main page loaded successfully")
            self.take_screenshot("01_main_page.png")

            # Switch to SSO iframe
            if not self._handle_sso_iframe():
                raise LoginError("Failed to access SSO iframe")

            # Perform login in iframe
            if not self._perform_iframe_login():
                raise LoginError("Failed to login in SSO iframe")

            # Switch back to main content and verify login
            self.driver.switch_to.default_content()
            time.sleep(5)

            # Check for login success
            if not self._verify_login_success():
                raise LoginError("Login verification failed")

            # Handle site bug with refresh
            self._handle_post_login_refresh()

            self.logger.info("🎉 Login completed successfully!")
            return True

        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.take_screenshot("login_error.png")
            raise LoginError(f"Login failed: {e}")

    def _handle_sso_iframe(self) -> bool:
        """Handle SSO iframe access."""
        try:
            self.logger.info("🔍 Looking for SSO iframe...")
            iframe = self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, self.config.SELECTORS["sso_iframe"])
                )
            )
            self.logger.info("✅ Found ssoFrame iframe")

            self.logger.info("⏳ Waiting for iframe content to load...")
            time.sleep(5)

            self.driver.switch_to.frame(iframe)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            self.logger.info("✅ Switched to ssoFrame iframe")
            self.take_screenshot("02_iframe_content.png")
            return True

        except TimeoutException:
            self.logger.error("❌ SSO iframe not found or not accessible")
            return False

    def _perform_iframe_login(self) -> bool:
        """Perform login inside the SSO iframe."""
        try:
            self.logger.info("🚀 Starting login process in SSO iframe...")

            # Get credentials
            credentials = self.config.get_credentials()

            # Find and fill username
            username_field = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self.config.SELECTORS["username_field"])
                )
            )
            username_field.clear()
            username_field.send_keys(credentials["username"])
            self.logger.info("✅ Username entered successfully")

            # Find and fill password
            password_field = self.driver.find_element(
                By.CSS_SELECTOR, self.config.SELECTORS["password_field"]
            )
            password_field.clear()
            password_field.send_keys(credentials["password"])
            self.logger.info("✅ Password entered successfully")

            # Submit form
            submit_button = self.driver.find_element(
                By.CSS_SELECTOR, self.config.SELECTORS["submit_button"]
            )
            self.take_screenshot("03_before_submit.png")

            submit_button.click()
            self.logger.info("🚀 Login form submitted in SSO iframe!")

            time.sleep(5)
            return True

        except Exception as e:
            self.logger.error(f"❌ Error during iframe login: {e}")
            return False

    def _verify_login_success(self) -> bool:
        """Verify that login was successful."""
        try:
            # Check current URL and page content for success indicators
            current_url = self.driver.current_url
            self.logger.info(f"Current URL after login: {current_url}")

            # Look for success indicators
            page_text = self.driver.page_source.lower()
            success_indicators = ["processo", "consulta", "quadroaviso"]

            for indicator in success_indicators:
                if indicator in page_text:
                    self.logger.info(f"✅ Found success indicator: '{indicator}'")
                    return True

            self.logger.error("❌ No success indicators found")
            return False

        except Exception as e:
            self.logger.error(f"❌ Error verifying login: {e}")
            return False

    def _handle_post_login_refresh(self) -> None:
        """Handle the post-login page refresh bug."""
        try:
            self.logger.info("🔄 Refreshing page after login to handle site bug...")
            self.driver.refresh()
            time.sleep(3)

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(5)

            self.logger.info("✅ Page refreshed successfully")
            self.take_screenshot("04_after_refresh.png")

        except Exception as e:
            self.logger.warning(f"⚠️ Error during post-login refresh: {e}")

    def navigate_to_consultation(self) -> bool:
        """Navigate to the process consultation page."""
        try:
            self.logger.info(
                f"🔍 Navigating to process consultation page: {self.config.CONSULTATION_URL}"
            )
            self.driver.get(self.config.CONSULTATION_URL)

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)

            self.logger.info("✅ Process consultation page loaded successfully")
            self.take_screenshot("05_consultation_page.png")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error navigating to consultation page: {e}")
            raise NavigationError(f"Failed to navigate to consultation page: {e}")

    def search_process(self, process_number: str) -> bool:
        """Search for a process by number."""
        try:
            self.logger.info(f"📝 Searching for process: {process_number}")

            # Parse process number
            process_parts = parse_process_number(process_number)

            # Fill process number fields
            selectors = self.config.SELECTORS["process_fields"]

            # Sequential number
            field = self.driver.find_element(By.ID, selectors["sequential"])
            field.clear()
            field.send_keys(process_parts["sequential"])

            # Verification digit
            field = self.driver.find_element(By.ID, selectors["digit"])
            field.clear()
            field.send_keys(process_parts["digit"])

            # Year
            field = self.driver.find_element(By.ID, selectors["year"])
            field.clear()
            field.send_keys(process_parts["year"])

            # Court
            field = self.driver.find_element(By.ID, selectors["court"])
            field.clear()
            field.send_keys(process_parts["court"])

            self.logger.info("✅ Successfully filled all process number fields")
            self.take_screenshot("06_fields_filled.png")

            # Click search button
            search_button = self.driver.find_element(
                By.CSS_SELECTOR, self.config.SELECTORS["search_button"]
            )
            search_button.click()
            self.logger.info("✅ Search button clicked successfully!")

            time.sleep(5)
            self.take_screenshot("07_search_results.png")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error during process search: {e}")
            raise ProcessNotFoundError(f"Failed to search for process: {e}")

    def download_process_document(self, process_number: str) -> Optional[str]:
        """Download process document and return the file path."""
        try:
            # Click on process link
            if not self._click_process_link(process_number):
                raise ProcessNotFoundError(
                    f"Process link not found for {process_number}"
                )

            # Open download dropdown
            if not self._open_download_dropdown():
                raise DownloadError("Failed to open download dropdown")

            # Click download button
            if not self._click_download_button():
                raise DownloadError("Failed to click download button")

            # Wait for PDF tab and download
            file_path = self._handle_pdf_download()
            if not file_path:
                raise DownloadError("Failed to download PDF file")

            self.logger.info(f"✅ Document downloaded successfully: {file_path}")
            return file_path

        except Exception as e:
            self.logger.error(f"❌ Error downloading document: {e}")
            raise DownloadError(f"Failed to download document: {e}")

    def _click_process_link(self, process_number: str) -> bool:
        """Click on the process link in search results."""
        try:
            self.logger.info("🔍 Looking for process link in search results...")

            # Store current window handle
            current_window = self.driver.current_window_handle

            # Find and click process link
            process_link = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, f"a[title*='{process_number}']")
                )
            )

            process_link.click()
            self.logger.info("✅ Process link clicked successfully!")

            # Wait for new tab and switch to it
            time.sleep(3)
            all_windows = self.driver.window_handles
            new_window = [w for w in all_windows if w != current_window][0]

            self.driver.switch_to.window(new_window)
            self.wait = WebDriverWait(self.driver, self.config.DEFAULT_TIMEOUT)

            time.sleep(5)
            self.take_screenshot("08_process_details.png")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error clicking process link: {e}")
            return False

    def _open_download_dropdown(self) -> bool:
        """Open the download dropdown menu."""
        try:
            self.logger.info("🔍 Looking for download dropdown menu...")

            dropdown_button = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, self.config.SELECTORS["download_dropdown"])
                )
            )

            dropdown_button.click()
            self.logger.info("✅ Download dropdown menu opened successfully!")

            time.sleep(2)
            self.take_screenshot("09_dropdown_opened.png")
            return True

        except Exception as e:
            self.logger.error(f"❌ Error opening download dropdown: {e}")
            return False

    def _click_download_button(self) -> bool:
        """Click the download button using JavaScript."""
        try:
            self.logger.info("🔍 Looking for Download button using JavaScript...")

            js_script = """
            var downloadButton = document.getElementById('navbar:j_id220');
            if (downloadButton) {
                downloadButton.click();
                return true;
            }

            var buttons = document.querySelectorAll('input[value="Download"]');
            if (buttons.length > 0) {
                buttons[0].click();
                return true;
            }

            return false;
            """

            result = self.driver.execute_script(js_script)

            if result:
                self.logger.info(
                    "✅ Download button clicked successfully using JavaScript!"
                )
                time.sleep(3)
                self.take_screenshot("10_download_initiated.png")
                return True
            else:
                self.logger.error("❌ Download button not found")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error clicking download button: {e}")
            return False

    def _handle_pdf_download(self) -> Optional[str]:
        """Handle PDF tab detection and download."""
        try:
            self.logger.info("⏳ Waiting for PDF tab to open...")

            current_window = self.driver.current_window_handle
            start_time = time.time()

            while time.time() - start_time < self.config.DOWNLOAD_TIMEOUT:
                all_windows = self.driver.window_handles
                new_tabs = [tab for tab in all_windows if tab != current_window]

                if len(new_tabs) > 1:  # PDF tab opened
                    pdf_tab = new_tabs[-1]
                    self.driver.switch_to.window(pdf_tab)
                    time.sleep(3)

                    current_url = self.driver.current_url
                    self.logger.info(f"📄 PDF URL: {current_url}")

                    if self.config.FILE_PATTERNS["pdf_url"] in current_url:
                        self.take_screenshot("11_pdf_tab.png")

                        # Download the PDF
                        file_path = self._download_pdf_from_url(current_url)

                        # Close PDF tab and return to process tab
                        self.driver.close()
                        process_tab = new_tabs[0]
                        self.driver.switch_to.window(process_tab)

                        return file_path

                time.sleep(1)

            self.logger.error("❌ Timeout waiting for PDF tab")
            return None

        except Exception as e:
            self.logger.error(f"❌ Error handling PDF download: {e}")
            return None

    def _download_pdf_from_url(self, pdf_url: str) -> Optional[str]:
        """Download PDF file from URL."""
        try:
            self.logger.info(f"⬇️ Downloading PDF from URL...")

            # Generate filename
            filename = f"processo_{int(time.time())}.pdf"
            file_path = os.path.join(self.config.DATA_DIR, filename)

            # Download file
            response = requests.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                self.logger.info(f"✅ PDF downloaded: {file_path}")
                self.logger.info(f"📄 File size: {format_file_size(file_size)}")
                return file_path

            return None

        except Exception as e:
            self.logger.error(f"❌ Error downloading PDF: {e}")
            return None
