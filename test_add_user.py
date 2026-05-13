# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
import csv
import os
import sys
import time
import unittest

try:
    text_type = unicode
except NameError:
    text_type = str


class addNewUser(unittest.TestCase):
    BASE_URL = "https://school.moodledemo.net/"
    MANAGER_USERNAME = "manager"
    MANAGER_PASSWORD = "moodle26"

    def setUp(self):
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH", "")
        if chromedriver_path:
            self.driver = webdriver.Chrome(executable_path=chromedriver_path)
        else:
            try:
                self.driver = webdriver.Chrome()
            except TypeError:
                self.driver = webdriver.Chrome(executable_path=r'')
        self.driver.implicitly_wait(1)
        self.accept_next_alert = True

    def read_test_data(self):
        """Read all data-driven add-user rows from test_data_users.csv."""
        data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data_users.csv")
        rows = []
        if sys.version_info[0] < 3:
            csv_file = open(data_file, "rb")
        else:
            csv_file = open(data_file, "r", newline="", encoding="utf-8")
        try:
            reader = csv.DictReader(csv_file)
            for row in reader:
                normalized = {}
                for key, value in row.items():
                    normalized[self.to_text(key)] = self.to_text(value).strip()
                rows.append(normalized)
        finally:
            csv_file.close()
        return rows

    def to_text(self, value):
        if value is None:
            return u""
        if isinstance(value, text_type):
            return value
        if isinstance(value, bytes):
            return value.decode("utf-8", "replace")
        try:
            return text_type(value)
        except Exception:
            return repr(value)

    def is_true(self, value):
        return self.to_text(value).strip().lower() in ("1", "true", "yes", "y")

    def find_id(self, element_id):
        if hasattr(self.driver, "find_element_by_id"):
            return self.driver.find_element_by_id(element_id)
        return self.driver.find_element(By.ID, element_id)

    def find_name(self, name):
        if hasattr(self.driver, "find_element_by_name"):
            return self.driver.find_element_by_name(name)
        return self.driver.find_element(By.NAME, name)

    def find_css(self, selector):
        if hasattr(self.driver, "find_element_by_css_selector"):
            return self.driver.find_element_by_css_selector(selector)
        return self.driver.find_element(By.CSS_SELECTOR, selector)

    def find_all_css(self, selector):
        if hasattr(self.driver, "find_elements_by_css_selector"):
            return self.driver.find_elements_by_css_selector(selector)
        return self.driver.find_elements(By.CSS_SELECTOR, selector)

    def find_xpath(self, xpath):
        if hasattr(self.driver, "find_element_by_xpath"):
            return self.driver.find_element_by_xpath(xpath)
        return self.driver.find_element(By.XPATH, xpath)

    def find_all_xpath(self, xpath):
        if hasattr(self.driver, "find_elements_by_xpath"):
            return self.driver.find_elements_by_xpath(xpath)
        return self.driver.find_elements(By.XPATH, xpath)

    def find_link_text(self, text):
        if hasattr(self.driver, "find_element_by_link_text"):
            return self.driver.find_element_by_link_text(text)
        return self.driver.find_element(By.LINK_TEXT, text)

    def page_text(self):
        try:
            return self.to_text(self.find_css("body").text)
        except Exception:
            return u""

    def wait_for_page_ready(self, timeout=6):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

    def is_network_error_page(self):
        text = self.page_text()
        return "ERR_NETWORK_CHANGED" in text or "Your connection was interrupted" in text

    def accept_cookie_notice_if_present(self):
        text = self.page_text()
        if "Error writing to database" in text or "Policy " in text:
            return
        self.click_first_present([
            (
                "xpath",
                "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie') "
                "or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie') "
                "or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie')]"
                "//button[normalize-space(.)='Continue']"
            ),
            (
                "xpath",
                "//*[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie') "
                "or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie') "
                "or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie')]"
                "//a[normalize-space(.)='Continue']"
            ),
            (
                "xpath",
                "//*[@role='dialog' or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modal')]"
                "[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie')]"
                "//button[normalize-space(.)='Continue']"
            ),
            (
                "xpath",
                "//*[@role='dialog' or contains(translate(@class, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'modal')]"
                "[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'cookie')]"
                "//a[normalize-space(.)='Continue']"
            )
        ])

    def safe_get(self, url, retries=2):
        last_exception = None
        for unused_index in range(retries):
            try:
                self.driver.get(url)
                self.wait_for_page_ready()
                time.sleep(0.2)
                self.accept_cookie_notice_if_present()
                if not self.is_network_error_page():
                    return
            except Exception as e:
                last_exception = e
            time.sleep(0.5)
        if last_exception is not None:
            raise last_exception

    def recover_network_error_if_present(self):
        if not self.is_network_error_page():
            return False
        for unused_index in range(2):
            try:
                time.sleep(0.5)
                self.driver.refresh()
                self.wait_for_page_ready()
                time.sleep(0.2)
                self.accept_cookie_notice_if_present()
                if not self.is_network_error_page():
                    return True
            except Exception:
                pass
        return False

    def wait_for_textbox(self, element_id, timeout=5):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.ID, element_id))
            )
        except TimeoutException:
            element = self.find_id(element_id)
            if element.is_displayed() and element.is_enabled():
                return element
            raise

    def scroll_element_to_safe_view(self, element):
        """Scroll the element away from Moodle fixed/sticky headers and footers."""
        try:
            self.driver.execute_script(
                """
                var element = arguments[0];
                var rect = element.getBoundingClientRect();
                var desiredTop = Math.max(80, Math.floor(window.innerHeight * 0.35));
                var targetY = window.pageYOffset + rect.top - desiredTop;
                window.scrollTo(0, Math.max(targetY, 0));
                """,
                element
            )
        except Exception:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            except Exception:
                pass
        time.sleep(0.1)

    def focus_element(self, element):
        self.scroll_element_to_safe_view(element)
        try:
            self.driver.execute_script("arguments[0].focus();", element)
        except Exception:
            pass

    def click_element(self, element):
        self.scroll_element_to_safe_view(element)
        try:
            element.click()
        except StaleElementReferenceException:
            raise
        except (ElementClickInterceptedException, WebDriverException):
            self.scroll_element_to_safe_view(element)
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except StaleElementReferenceException:
                raise
            except Exception:
                self.driver.execute_script(
                    "arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true, view: window}));",
                    element
                )

    def click_id(self, element_id):
        element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        self.click_element(element)

    def set_textbox_value_by_script(self, element, value):
        self.driver.execute_script(
            """
            var element = arguments[0];
            var value = arguments[1];
            element.focus();
            element.value = value;
            element.dispatchEvent(new Event('input', {bubbles: true}));
            element.dispatchEvent(new Event('change', {bubbles: true}));
            element.blur();
            """,
            element,
            value
        )

    def fill_textbox(self, element_id, value):
        element = self.wait_for_textbox(element_id)
        value = self.to_text(value)
        self.focus_element(element)
        try:
            element.clear()
            if value != u"":
                element.send_keys(value)
        except (ElementClickInterceptedException, WebDriverException):
            self.set_textbox_value_by_script(element, value)

    def set_checkbox(self, element_id, checked):
        checkbox = self.find_id(element_id)
        if checkbox.is_selected() != checked:
            self.click_element(checkbox)

    def set_checkbox_if_present(self, element_id, checked):
        try:
            self.set_checkbox(element_id, checked)
        except Exception:
            pass

    def disable_generated_password_if_present(self):
        self.set_checkbox_if_present("id_createpassword", False)

    def find_optional_elements(self, strategy, value):
        if strategy == "id":
            return self.driver.find_elements(By.ID, value)
        if strategy == "name":
            return self.driver.find_elements(By.NAME, value)
        if strategy == "css":
            return self.driver.find_elements(By.CSS_SELECTOR, value)
        if strategy == "xpath":
            return self.driver.find_elements(By.XPATH, value)
        if strategy == "link_text":
            return self.driver.find_elements(By.LINK_TEXT, value)
        return []

    def click_first_present(self, locators, retries=2):
        self.driver.implicitly_wait(0)
        try:
            for unused_retry in range(retries):
                for strategy, value in locators:
                    try:
                        elements = self.find_optional_elements(strategy, value)
                        for element in elements:
                            try:
                                if element.is_displayed() and element.is_enabled():
                                    self.click_element(element)
                                    return True
                            except StaleElementReferenceException:
                                break
                    except StaleElementReferenceException:
                        pass
                    except Exception:
                        pass
                time.sleep(0.1)
            return False
        finally:
            self.driver.implicitly_wait(1)

    def enable_password_field(self):
        try:
            element = self.find_id("id_newpassword")
            if element.is_displayed() and element.is_enabled():
                return
        except Exception:
            pass

        self.click_first_present([
            ("link_text", "Click to enter text"),
            ("css", "#fitem_id_newpassword a"),
            ("xpath", "//a[contains(., 'Click to enter text')]"),
            ("css", "#fitem_id_newpassword [role='button']"),
            ("css", "#fitem_id_newpassword em")
        ])
        time.sleep(0.2)
        self.wait_for_textbox("id_newpassword")

    def logout_current_user(self):
        try:
            self.click_id("user-menu-toggle")
            time.sleep(1)
            self.click_first_present([
                ("link_text", "Log out"),
                ("xpath", "//a[contains(@href, 'logout.php')]")
            ])
            self.wait_for_page_ready()
            time.sleep(1)
        except Exception:
            try:
                self.safe_get(self.BASE_URL + "login/logout.php")
            except Exception:
                pass

    def login_as_manager(self):
        self.safe_get(self.BASE_URL + "login/index.php")
        if "You are currently using guest access" not in self.page_text() and "Log out" in self.page_text():
            return
        try:
            self.fill_textbox("username", self.MANAGER_USERNAME)
            self.fill_textbox("password", self.MANAGER_PASSWORD)
            self.click_first_present([
                ("id", "loginbtn"),
                ("css", "#login input[type='submit']"),
                ("css", "button[type='submit']")
            ])
            self.wait_for_page_ready()
            time.sleep(1)
            self.accept_cookie_notice_if_present()
        except Exception:
            # Already logged in or login form is not currently displayed.
            pass

    def is_add_user_page_ready(self):
        try:
            element = WebDriverWait(self.driver, 2).until(
                EC.presence_of_element_located((By.ID, "id_username"))
            )
            return element.is_displayed() and element.is_enabled()
        except Exception:
            return False

    def open_add_user_page(self):
        add_user_url = self.BASE_URL + "user/editadvanced.php?id=-1"
        for unused_index in range(2):
            self.safe_get(add_user_url)
            if self.is_add_user_page_ready():
                return
            self.login_as_manager()
            self.safe_get(add_user_url)
            if self.is_add_user_page_ready():
                return
            self.logout_current_user()
        self.safe_get(add_user_url)
        self.wait_for_textbox("id_username")

    def fill_add_user_form(self, test_data):
        self.fill_textbox("id_username", test_data.get("username", ""))
        self.disable_generated_password_if_present()
        self.enable_password_field()
        self.fill_textbox("id_newpassword", test_data.get("password", ""))
        self.fill_textbox("id_firstname", test_data.get("firstname", ""))
        self.fill_textbox("id_lastname", test_data.get("lastname", ""))
        self.fill_textbox("id_email", test_data.get("email", ""))

        if test_data.get("suspended", ""):
            self.set_checkbox("id_suspended", self.is_true(test_data.get("suspended", "")))
        if test_data.get("force_password_change", ""):
            self.set_checkbox(
                "id_preference_auth_forcepasswordchange",
                self.is_true(test_data.get("force_password_change", ""))
            )
        if test_data.get("city", ""):
            self.fill_textbox("id_city", test_data.get("city", ""))
        if test_data.get("country", ""):
            Select(self.find_id("id_country")).select_by_visible_text(test_data.get("country", ""))

    def verify_expected_result(self, test_data):
        expected_result = test_data.get("Expected Result", "")
        for unused_index in range(8):
            self.wait_for_page_ready()
            actual_result = self.page_text()
            if expected_result in actual_result:
                return
            if self.recover_network_error_if_present():
                actual_result = self.page_text()
                if expected_result in actual_result:
                    return
            self.accept_cookie_notice_if_present()
            actual_result = self.page_text()
            if expected_result in actual_result:
                return
            time.sleep(1)
        actual_result = self.page_text()
        self.assertTrue(
            expected_result in actual_result,
            "Expected result not found for %s. Expected: %r. Actual page text: %r" % (
                test_data.get("test_id", "unknown"),
                expected_result,
                actual_result[:2000]
            )
        )

    def select_policy_inputs_if_present(self):
        selected_any = False
        self.driver.implicitly_wait(0)
        try:
            inputs = self.find_all_xpath(
                "//input[(starts-with(@name, 'status') or contains(@id, 'status') or "
                "@type='checkbox' or @type='radio') and not(@disabled)]"
            )
            for index in range(len(inputs)):
                try:
                    fresh_inputs = self.find_all_xpath(
                        "//input[(starts-with(@name, 'status') or contains(@id, 'status') or "
                        "@type='checkbox' or @type='radio') and not(@disabled)]"
                    )
                    if index >= len(fresh_inputs):
                        break
                    policy_input = fresh_inputs[index]
                    if not policy_input.is_selected():
                        self.click_element(policy_input)
                        selected_any = True
                        time.sleep(0.1)
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        finally:
            self.driver.implicitly_wait(1)
        return selected_any

    def click_policy_next_if_present(self):
        return self.click_first_present([
            ("link_text", "Next"),
            ("xpath", "//a[normalize-space(.)='Next']"),
            ("xpath", "//button[normalize-space(.)='Next']"),
            ("xpath", "//input[@type='submit' and @value='Next']")
        ], retries=3)

    def click_policy_submit_if_present(self):
        return self.click_first_present([
            ("xpath", "//button[contains(normalize-space(.), 'Save changes')]"),
            ("xpath", "//input[@type='submit' and contains(@value, 'Save changes')]"),
            ("xpath", "//button[contains(normalize-space(.), 'Agree')]"),
            ("xpath", "//input[@type='submit' and contains(@value, 'Agree')]"),
            ("name", "submit"),
            ("css", "input[name='submit']"),
            ("css", "button[type='submit']"),
            ("xpath", "//button[normalize-space(.)='Continue']"),
            ("xpath", "//input[@type='submit' and @value='Continue']"),
            ("xpath", "//a[normalize-space(.)='Continue']")
        ], retries=3)

    def complete_policy_pages_if_present(self, expected_result):
        for unused_index in range(15):
            self.wait_for_page_ready()
            actual_text = self.page_text()
            if expected_result in actual_text:
                return

            if "Policy " in actual_text and "Next" in actual_text:
                if self.click_policy_next_if_present():
                    self.wait_for_page_ready()
                    time.sleep(0.6)
                    continue

            selected = self.select_policy_inputs_if_present()
            if selected:
                time.sleep(0.2)

            if self.click_policy_submit_if_present():
                self.wait_for_page_ready()
                time.sleep(0.8)
                continue

            self.accept_cookie_notice_if_present()
            if expected_result in self.page_text():
                return
            return

    def login_as_created_user_and_verify(self, test_data):
        expected_result = test_data.get("Expected Result", "")
        self.logout_current_user()
        self.safe_get(self.BASE_URL + "login/index.php")
        try:
            self.wait_for_textbox("username", timeout=5)
        except Exception:
            self.logout_current_user()
            self.safe_get(self.BASE_URL + "login/index.php")
        self.fill_textbox("username", test_data.get("username", ""))
        self.fill_textbox("password", test_data.get("password", ""))
        self.click_first_present([
            ("id", "loginbtn"),
            ("css", "#login input[type='submit']"),
            ("css", "button[type='submit']")
        ])
        self.wait_for_page_ready()
        time.sleep(0.5)
        self.accept_cookie_notice_if_present()
        self.complete_policy_pages_if_present(expected_result)
        self.verify_expected_result(test_data)

    def run_add_user_case(self, test_data):
        self.open_add_user_page()
        self.fill_add_user_form(test_data)

        if self.is_true(test_data.get("cancel", "")):
            self.click_id("id_cancel")
            self.wait_for_page_ready()
            time.sleep(0.3)
            self.verify_expected_result(test_data)
            return

        self.click_id("id_submitbutton")
        self.wait_for_page_ready()
        time.sleep(0.5)

        if self.is_true(test_data.get("verify_after_login", "")):
            self.assertTrue(
                "Changes saved" in self.page_text(),
                "User was not created before login verification for %s" % test_data.get("test_id", "unknown")
            )
            self.login_as_created_user_and_verify(test_data)
        else:
            self.verify_expected_result(test_data)

    def test_add_user_data_driven(self):
        verification_errors = []
        for test_data in self.read_test_data():
            try:
                self.run_add_user_case(test_data)
            except Exception as e:
                verification_errors.append("%s: %s" % (test_data.get("test_id", "unknown"), self.to_text(e)))
        if verification_errors:
            self.fail("\n".join(verification_errors))

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        try:
            self.logout_current_user()
        finally:
            self.driver.quit()


if __name__ == "__main__":
    unittest.main()
