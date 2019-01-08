#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

def login(url, username, password, DRIVER_PATH):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
    driver.get(url)
    time.sleep(10)

    try:
        driver.find_element_by_id("username-input").send_keys(username)
        driver.find_element_by_id("password-input").send_keys(password)
        driver.find_element_by_id("sign-in-button").click()

        element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, "user-progress-app"))
        )
        progress = driver.find_element_by_css_selector("#user-progress-app div.progress-status div:nth-of-type(2)")
        print(progress.find_element_by_tag_name('div').get_attribute('innerHTML'))
    finally:
        driver.quit()


def main():
    if len(sys.argv) < 3:
        print('Usage: python3 lc_login.py <username> <password> <driver-path>')
        return
    url = 'https://leetcode.com/accounts/login/'
    username = sys.argv[1]
    password = sys.argv[2]
    DRIVER_PATH = sys.argv[3]
    
    login(url, username, password, DRIVER_PATH)


if __name__ == "__main__":
    main()