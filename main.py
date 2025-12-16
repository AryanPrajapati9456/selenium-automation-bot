import json
import time
import random
import logging
import os
import re
from datetime import datetime

from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

# Import our utility modules
from utils.interaction import human_sleep, clean_phone
from utils.masking import mask_identifiers
from utils.logger import setup_logging

# Import configuration
from config import (
    URL, MAX_RETRIES, THREAD_COUNT, RETRY_DELAY_RANGE,
    XPATH_MY_SECTION, XPATH_INPUT_NUMBER, XPATH_INPUT_PASSWORD, XPATH_LOGIN_BUTTON,
    CSS_POP_CANCEL, CSS_POP_CONFIRM, CSS_BALANCE_CONTAINER,
    XPATH_LOGOUT, XPATH_LOGOUT_YES
)

# Shared indexes for two-way traversal
top_index = 0
bottom_index = 0  # will set after loading accounts
index_lock = threading.Lock()  # protects top/bottom index


def get_browser():
    """
    Initialize and configure Chrome WebDriver for automation.
    
    Returns:
        webdriver.Chrome: Configured Chrome WebDriver instance
    """
    opts = Options()
    opts.add_argument("--incognito")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(1366, 720)
    return driver


def fast_popup_handler(driver):
    """
    Efficiently handle popups by clicking cancel/confirm buttons if they exist.
    
    Uses JavaScript clicks for reliability and implements early termination
    when no more clickable elements are found.
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance
    """
    for _ in range(15):  # 0.75 sec max
        clicked = False

        try:
            el = driver.find_element(By.CSS_SELECTOR, CSS_POP_CANCEL)
            driver.execute_script("arguments[0].click();", el)
            clicked = True
        except:
            pass

        try:
            el = driver.find_element(By.CSS_SELECTOR, CSS_POP_CONFIRM)
            driver.execute_script("arguments[0].click();", el)
            clicked = True
        except:
            pass

        if not clicked:
            break  # nothing left to click

        time.sleep(0.05)


def extract_balance(driver):
    """
    Extract account balance from the balance container element.
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance
        
    Returns:
        float or None: Extracted balance value or None if extraction fails
    """
    try:
        wait = WebDriverWait(driver, 20)

        elem = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, CSS_BALANCE_CONTAINER))
        )

        balance_text = elem.text.strip()

        match = re.search(r"(\d+[\.,]?\d*)", balance_text)
        if not match:
            return None

        num = match.group(1).replace(",", "")
        return float(num)

    except Exception as e:
        logging.error(f"Balance extraction error: {e}")
        return None


def check_operating_too_fast(driver, timeout=3):
    """
    Detect if "operating too fast" modal is displayed.
    
    Automatically closes the modal if detected to allow continuation.
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance
        timeout (int): Maximum time to wait for modal
        
    Returns:
        bool: True if "operating too fast" modal detected, False otherwise
    """
    try:
        modal_body = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".uni-modal__bd"))
        )

        text = modal_body.text.strip().lower()

        # Close popup if button exists
        try:
            driver.find_element(
                By.CSS_SELECTOR, ".uni-modal__btn.uni-modal__btn_primary"
            ).click()
        except:
            pass

        if "operating too fast" in text:
            return True

        return False

    except:
        return False


def login(driver, account_data, first_login):
    """
    Handle authenticated session entry with rate-limit detection 
    and first-login popup handling.
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance
        account_data (dict): Account credentials and identifiers
        first_login (bool): Flag indicating if this is the first login attempt
        
    Returns:
        tuple: (success_status, message)
    """
    wait = WebDriverWait(driver, 20)

    # Extract account information
    account_id = account_data.get("account_id", "UNKNOWN")
    login_identifier = account_data.get("login_identifier", "")
    credential = account_data.get("credential", "")

    # Navigate to account section
    try:
        my_section = wait.until(
            EC.element_to_be_clickable((By.XPATH, XPATH_MY_SECTION))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", my_section)
        my_section.click()
    except:
        return False, "MySectionNotFound"

    human_sleep()  # small pause after click

    # Prepare login identifier for input
    clean_identifier = clean_phone(login_identifier)

    # Enter login identifier
    input_num = wait.until(
        EC.visibility_of_element_located((By.XPATH, XPATH_INPUT_NUMBER))
    )

    # Fully clear field before input
    input_num.click()
    input_num.send_keys(Keys.CONTROL + "a")
    input_num.send_keys(Keys.DELETE)
    driver.execute_script("arguments[0].value = '';", input_num)
    input_num.clear()

    # Type full identifier instantly
    input_num.send_keys(clean_identifier)

    # Pause after entering identifier
    human_sleep(0.8)

    # Enter credential
    input_pass = wait.until(
        EC.visibility_of_element_located((By.XPATH, XPATH_INPUT_PASSWORD))
    )
    input_pass.clear()
    input_pass.send_keys(credential)

    # Pause before clicking login
    human_sleep(1.5, 2)

    # Submit login form
    wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_LOGIN_BUTTON))).click()
    human_sleep()

    # Check for rate limiting
    if check_operating_too_fast(driver):
        return False, "FastClick"

    # Handle incorrect login attempts
    try:
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, ".uni-modal__btn.uni-modal__btn_primary")
            )
        )
        driver.find_element(
            By.CSS_SELECTOR, ".uni-modal__btn.uni-modal__btn_primary"
        ).click()
        return False, "IncorrectLogin"
    except:
        pass

    # Handle first-time login popups
    if first_login:
        fast_popup_handler(driver)
    else:
        # Only click if they appear (rare after first login)
        fast_popup_handler(driver)

    return True, "Success"


def logout(driver):
    """
    Perform account logout procedure.
    
    Args:
        driver (webdriver.Chrome): Active WebDriver instance
        
    Returns:
        bool: True if logout successful, False otherwise
    """
    wait = WebDriverWait(driver, 15)

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_LOGOUT))).click()
    except:
        return False

    human_sleep(0.3, 0.6)

    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, XPATH_LOGOUT_YES))).click()
    except:
        return False

    human_sleep()
    return True


def bot_top_to_bottom(accounts):
    """
    Process accounts from top to bottom in the list.
    
    Args:
        accounts (list): List of account dictionaries to process
    """
    global top_index, bottom_index
    driver = get_browser()
    driver.get(URL)
    output = []
    first_login = True

    while True:
        with index_lock:
            if top_index > bottom_index:
                break
            acc_index = top_index
            top_index += 1

        acc = accounts[acc_index]
        account_id = acc.get("account_id", f"ACC_{acc_index}")

        logging.info(f"[TOP BOT] --- Processing {mask_identifiers(account_id)} ---")

        attempt = 0
        max_retry = 1

        while True:
            login_success, msg = login(driver, acc, first_login)

            if msg == "FastClick" and attempt < max_retry:
                logging.warning(f"{mask_identifiers(account_id)} → Operating too fast, retrying slowly...")

                # FULL slow retype strategy
                human_sleep(4)

                attempt += 1
                continue

            break

        if not login_success:
            entry = {
                "account_id": account_id,
                "status": msg
            }
        else:
            first_login = False
            balance = extract_balance(driver)
            status = "Success" if balance is not None else "BalanceMissing"
            entry = {
                "account_id": account_id,
                "balance": balance,
                "status": status,
            }

            if not logout(driver):
                logging.error(f"{mask_identifiers(account_id)} → Logout failed")
                entry["status"] = "LogoutFailed"

        output.append(entry)

        # Save top bot output
        with open("output1.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

        logging.info(f"[TOP BOT] {mask_identifiers(account_id)} → Done")

    driver.quit()
    logging.info("[TOP BOT] Finished.")


def bot_bottom_to_top(accounts):
    """
    Process accounts from bottom to top in the list.
    
    Args:
        accounts (list): List of account dictionaries to process
    """
    global top_index, bottom_index
    driver = get_browser()
    driver.get(URL)
    output = []
    first_login = True

    while True:
        with index_lock:
            if bottom_index < top_index:
                break
            acc_index = bottom_index
            bottom_index -= 1

        acc = accounts[acc_index]
        account_id = acc.get("account_id", f"ACC_{acc_index}")

        logging.info(f"[BOTTOM BOT] --- Processing {mask_identifiers(account_id)} ---")

        attempt = 0
        max_retry = 1

        while True:
            login_success, msg = login(driver, acc, first_login)

            if msg == "FastClick" and attempt < max_retry:
                logging.warning(f"{mask_identifiers(account_id)} → Operating too fast, retrying slowly...")

                # FULL slow retype strategy
                human_sleep(4)

                attempt += 1
                continue

            break

        if not login_success:
            entry = {
                "account_id": account_id,
                "status": msg
            }
        else:
            first_login = False
            balance = extract_balance(driver)
            status = "Success" if balance is not None else "BalanceMissing"
            entry = {
                "account_id": account_id,
                "balance": balance,
                "status": status,
            }

            if not logout(driver):
                logging.error(f"{mask_identifiers(account_id)} → Logout failed")
                entry["status"] = "LogoutFailed"

        output.append(entry)

        # Save bottom bot output
        with open("output2.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4)

        logging.info(f"[BOTTOM BOT] {mask_identifiers(account_id)} → Done")

    driver.quit()
    logging.info("[BOTTOM BOT] Finished.")


if __name__ == "__main__":
    # Setup logging
    setup_logging()
    
    with open("input.json", "r", encoding="utf-8") as f:
        accounts = json.load(f)

    # Initialize shared indexes
    top_index = 0
    bottom_index = len(accounts) - 1

    # Start threads
    threads = []
    for i in range(min(THREAD_COUNT, len(accounts))):
        if i % 2 == 0:
            t = threading.Thread(target=bot_top_to_bottom, args=(accounts,))
        else:
            t = threading.Thread(target=bot_bottom_to_top, args=(accounts,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    logging.info("ALL BOTS FINISHED. Outputs saved in output1.json and output2.json")