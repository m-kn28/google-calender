import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

from lib.custom_logger import logger
from entity.calendar import CalendarEvent


def get_chrome_driver(driver_path: str, is_headress: bool) -> webdriver.Chrome:
    service = Service(executable_path=driver_path)
    if is_headress:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        driver = webdriver.Chrome(service=service)
    return driver


def time_sleep(seconds: int):
    def decorator(func):
        def wrapper(*args, **kwargs):
            time.sleep(seconds)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def access_salon_board(driver: webdriver.Chrome, salon_user_id: str, salon_password: str):
    driver.get("https://salonboard.com/login/")

    driver.find_element(By.NAME, 'userId').send_keys(salon_user_id)
    driver.find_element(By.NAME, 'password').send_keys(salon_password)

    login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[contains(@onclick, 'dologin')]"))
    )
    ActionChains(driver).move_to_element(login_btn).perform()
    login_btn.click()


@time_sleep(3)
def access_schedule(driver: webdriver.Chrome):
    salon_link = driver.find_element(
        By.CSS_SELECTOR, "#kireiStoreInfoArea tbody .storeName a")
    salon_link.click()


@time_sleep(3)
def access_detail_schedule(driver: webdriver.Chrome, start_time: str):
    start_date = datetime.strptime(
        start_time, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y%m%d")
    schedule_link = driver.find_element(
        By.ID, f"sd_{start_date}")
    schedule_link.click()


@time_sleep(3)
def access_register_schedule(driver: webdriver.Chrome, stylist_name: str, start_time: str) -> bool:
    stylist_id = ""
    is_registered = False

    stylist_name_list = driver.find_element(By.ID, "stylistNameList")
    options = stylist_name_list.find_elements(By.TAG_NAME, "option")
    for option in options:
        if stylist_name in option.text:
            stylist_id = option.get_attribute("value").split('_')[1]
            break

    start_datetime = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S%z")
    schedule_date = start_datetime.strftime("%Y%m%d")
    schedule_time = start_datetime.strftime("%H%M")
    empty_time_header = f"//td[contains(@id, 'empty_time_sid_header_{schedule_date}_{schedule_time}_{stylist_id}')]"
    elements = driver.find_elements(By.XPATH, empty_time_header)
    logger.info(f"Found {len(elements)} empty time headers.")
    if len(elements) >= 1:
        elements[0].click()
    else:
        is_registered = True
        logger.info(
            "No matching elements found. already reserved or There are no reservation slots available.")
        logger.info(f"regsiter info: {stylist_name} {start_time}")
    return is_registered


@time_sleep(3)
def register_schedule(driver: webdriver.Chrome, customer_name: str):
    full_name = customer_name.split(' ')
    if len(full_name) > 1:
        sei = full_name[0]
        mei = full_name[1]
    else:
        sei = full_name[0]
        mei = ""

    logger.info(f'Registering Customer Name: {sei} {mei}')

    driver.find_element(By.ID, "nmSeiKana").send_keys(sei)
    driver.find_element(By.ID, "nmSei").send_keys(sei)

    if mei != "":
        driver.find_element(By.ID, "nmMeiKana").send_keys(mei)
        driver.find_element(By.ID, "nmMei").send_keys(mei)

    time.sleep(5)
    register_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "regist"))
    )
    ActionChains(driver).move_to_element(register_btn).perform()
    register_btn.click()

    WebDriverWait(driver, 10).until(EC.alert_is_present())
    time.sleep(5)
    alert = Alert(driver)
    alert.accept()
    logger.info(f"Registerd schedule. customer: {customer_name}")


def register_salon_board(driver_path: str, is_headress: bool, user_id: str, password: str, calendar: CalendarEvent):
    title = calendar.summary.replace('　', ' ').strip()
    start_time = calendar.start

    # Get customer name and stylist name from calendar event title
    title_pattern = r'(.*)様 スタイリスト(.*)'
    match = re.search(title_pattern, title)
    if match:
        customer_name = match.group(1)
        stylist_name = match.group(2)
    else:
        logger.info(
            f"customer name or stylist name is not found. title: {title}")
        return

    # Register schedule
    driver = get_chrome_driver(driver_path, is_headress=is_headress)
    access_salon_board(driver=driver, salon_user_id=user_id,
                       salon_password=password)
    access_schedule(driver=driver)
    access_detail_schedule(driver=driver, start_time=start_time)
    is_registered = access_register_schedule(
        driver=driver, stylist_name=stylist_name, start_time=start_time)
    if is_registered:
        return
    register_schedule(driver=driver, customer_name=customer_name)
    driver.quit()
