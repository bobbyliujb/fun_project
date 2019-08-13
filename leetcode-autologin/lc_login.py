#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

def get_driver(DRIVER_PATH):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(DRIVER_PATH, chrome_options=options)

def login(url, username, password, driver):
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.invisibility_of_element_located((By.ID, "initial-loading"))
    )
    driver.find_element_by_css_selector("input[data-cy='username']").send_keys(username)
    driver.find_element_by_css_selector("input[data-cy='password']").send_keys(password)
    driver.find_element_by_css_selector("button[data-cy='sign-in-btn']").click()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nav-user-app"))
    )

def get_progress(url, driver):
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#user-progress-app div.progress-status"))
    )
    
    progress = driver.find_element_by_css_selector("#user-progress-app div.progress-status div.text-success div.status")
    print(progress.get_attribute('innerHTML'))

def main():
    if len(sys.argv) < 3:
        print('Usage: python3 lc_login.py <username> <password> <driver-path>')
        return
    url = 'https://leetcode.com/accounts/login/'
    url_problems = 'https://leetcode.com/problemset/all/'
    username = sys.argv[1]
    password = sys.argv[2]
    DRIVER_PATH = sys.argv[3]
    
    try:
        driver = get_driver(DRIVER_PATH)
        login(url, username, password, driver)
        get_progress(url_problems, driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()