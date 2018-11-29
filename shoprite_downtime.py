#! python3
# shoprite_downtime.py - logs onto to downtime page and automatically clicks through each offer

import argparse
import json
import logging
import os
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, \
    ElementNotVisibleException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# TODO replace sleep with micro-sleep so explicit waits work properly after the page redirects


def init_logging():
    """
    Starts up log file in a new log directory where python file is located
    :return: None
    """
    # gets dir path of python script, not cwd, for execution on cron
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    os.makedirs('logs', exist_ok=True)
    log_path = os.path.join('logs', 'shoprite_downtime.log')
    logging.basicConfig(filename=log_path, level=logging.INFO,
                        format='%(asctime)s :: %(levelname)s :: %(name)s :: %(message)s')


def parse_args():
    """
    Parses argument for headless setting
    :return: argparse obj
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--headless', action='store_true', dest='headless_setting', default=False,
                        help='Activates headless mode, default is off.')
    return parser.parse_args()


def get_log_in():
    """
    Gets log in information from a json
    :return: dict with login information
    """
    with open('shoprite_login_dict.json') as f:
        return json.load(f)


def start_browser():
    """
    Starts up browser with headless setting if activated
    :return: webdriver firefox obj
    """
    options = Options()
    options.headless = args.headless_setting
    return webdriver.Firefox(options=options)


def wait_until_clickable(by_selector, selector, wait_time=15):
    """
    Waits for wait time (default 15 seconds) for element to be clickable, by selector
    :param by_selector: String By selector
    :param selector: String Node object selector
    :param wait_time: Int Default 15 second wait time
    :return: None
    """
    WebDriverWait(browser, wait_time).until(ec.element_to_be_clickable((by_selector, selector)))


def find_by_class(selector):
    """
    Returns list of node objects matching class name selector
    :param selector: String Class name selector of node obj
    :return: List of node objects matching class name selector
    """
    return browser.find_elements_by_class_name(selector)


def login(email_, password_):
    """
    Logs into sign in page with provided email and password
    :param email_: String email address
    :param password_: String password
    :return: None
    """
    logging.info(msg='Logging in...')
    try:
        browser.get('https://secure.shoprite.com/User/SignIn/3601')
        # email
        wait_until_clickable(By.ID, 'Email', wait_time=30)
        browser.find_element_by_id('Email').send_keys(email_)
        # pass_word
        wait_until_clickable(By.ID, 'Password')
        browser.find_element_by_id('Password').send_keys(password_)
        # click sign in button
        wait_until_clickable(By.ID, 'SignIn')
        browser.find_element_by_id('SignIn').click()
    except TimeoutException:
        logging.exception(msg='Log in failed. TimeoutException.')
    except (ElementNotVisibleException, ElementClickInterceptedException):
        logging.exception(msg='Element not clickable or visible.')
    except WebDriverException:
        logging.exception(msg='Error.')


def click_thru_tutorial():
    """
    Click through the three tutorial buttons
    :return: None
    """
    browser.get('http://downtimedollars.shoprite.com/app/campaigns')
    time.sleep(3)
    # 3 tries because 3 buttons
    for i in range(3):
        try:
            wait_until_clickable(By.CLASS_NAME, 'TutorialPage_button', wait_time=60)
            find_by_class('TutorialPage_button')[0].click()
            time.sleep(3)
        except TimeoutException:
            logging.exception(msg='Cannot find tutorial buttons')
        except (ElementNotVisibleException, ElementClickInterceptedException):
            logging.exception(msg='Clicking through tutorial failed')
        except WebDriverException:
            logging.exception(msg='Error.')


def detect_promotion():
    """
    Detects promotions on promotions page and calls complete_promotion()
    :return: None
    """
    try:
        wait_until_clickable(By.CLASS_NAME, 'ResponsiveImage_childContainer', wait_time=120)
        promo_iter_cap = find_by_class('ResponsiveImage_childContainer')
        logging.info(msg=f'# of Promotions Detected: {len(promo_iter_cap)}')
        # this puts a cap on iterations, because completing a promo returns to promo home page
        for _ in range(len(promo_iter_cap)):
            logging.info(msg='new iter')
            # checks to see if promo_list is empty or matches the completed, new check because page reloads after each
            promo_list = find_by_class('ResponsiveImage_childContainer')
            promo_count = 0
            for promo in promo_list:
                logging.debug(msg='Promotion Detected')
                # checks if the promotion is already completed
                if promo.find_elements_by_xpath("./ancestor::div[contains(@class, 'CampaignPreviewCardComplete')]"):
                    logging.info(msg='Promotion already completed.')
                    promo_count += 1
                    continue
                else:
                    promo.click()
                    complete_promotion()
                    logging.info(msg='Promotion completed.')
                    time.sleep(5)
                    break
            if promo_count == len(promo_list):
                break
    except TimeoutException:
        logging.info(msg='No promotions found.', exc_info=False)
    except (ElementNotVisibleException, ElementClickInterceptedException):
        logging.exception(msg='Failed to click on promotion.')
    except WebDriverException:
        logging.exception(msg='Error.')


def complete_promotion():
    """
    For each promotion, iterates 25 times through the promotion to click through it
    :return: None
    """
    for i in range(25):
        # clear obscuring objects, wait for page to load
        time.sleep(3)
        try:
            # left or right quiz
            if find_by_class('ResponsiveImage_childContainer'):
                find_by_class('ResponsiveImage_childContainer')[0].click()
                time.sleep(3)
            # card button quiz or video part two
            if find_by_class('CardButton'):
                find_by_class('CardButton')[0].click()
                time.sleep(3)
            # smiley quiz
            if find_by_class('SmileyFaces_img'):
                find_by_class('SmileyFaces_img')[4].click()
                time.sleep(3)
            # video quiz
            if find_by_class('Video_playPauseIconVisible'):
                # play video
                find_by_class('Video_playPauseIconVisible')[0].click()
                # wait until video is over (180 seconds max)
                wait_until_clickable(By.CLASS_NAME, 'Video_playPauseIconVisible', 600)
                time.sleep(3)
                find_by_class('CardButton')[1].click()
            # close and returns to the home screen with promotions.
            if browser.find_elements_by_class_name('ConclusionCard_doneButton'):
                browser.find_elements_by_class_name('ConclusionCard_doneButton')[0].click()
                time.sleep(3)
                if find_by_class('SmileyFaces_img'):
                    find_by_class('SmileyFaces_img')[4].click()
                    time.sleep(3)
                break
            if find_by_class('btn-link'):
                find_by_class('btn-link').click()
                time.sleep(3)
        except TimeoutException:
            logging.exception(msg='Promotion\'s buttons not found.')
        except (ElementNotVisibleException, ElementClickInterceptedException):
            logging.exception(msg='Failed to through promotion\'s buttons.')
        except WebDriverException:
            logging.exception('Failure on clicking through a promotion.')


if __name__ == "__main__":
    init_logging()
    logging.info(msg='*************NEW*************')
    logging.info(msg='*****************************')

    # parse args, start browser, determine if headless mode
    args = parse_args()
    browser = start_browser()

    # get login dict and log in
    login_dict = get_log_in()
    for email, password in login_dict.items():
        login(email, password)
        click_thru_tutorial()
        detect_promotion()
        logging.info(msg='Downtime Dollars Complete.')
        # TODO reactivate this when deploying
        browser.quit()
