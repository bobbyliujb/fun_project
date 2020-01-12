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
    options.add_argument("--disable-extensions")
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    return webdriver.Chrome(DRIVER_PATH, chrome_options=options)

"""
Login using given credentials. Print the page if sign in takes a long time
"""
def login(url, username, password, driver, max_retry = 3):
    retry_count = 0
    while retry_count < max_retry:
        driver.get(url)
        element = WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.ID, "initial-loading"))
        )
        driver.find_element_by_css_selector("input[data-cy='username']").send_keys(username)
        driver.find_element_by_css_selector("input[data-cy='password']").send_keys(password)
        driver.find_element_by_css_selector("button[data-cy='sign-in-btn']").click()
        try:
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "nav-user-app"))
            )
            return
        except TimeoutException:
            retry_count += 1
    print(driver.find_element_by_css_selector("body div").text)

"""
Print status from progress page
"""
def get_progress(url, driver):
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ac_total"))
    )
    current_accepted = 0
    while True:     # The number will increment to final stage so we need to compare until it does not change
        accepted = int(driver.find_element_by_id("ac_total").get_attribute("innerHTML"))
        if accepted == current_accepted:
            break
        else:
            current_accepted = accepted
            time.sleep(0.5)
    total = driver.find_element_by_css_selector("#ac_total + span")
    print("%d %s" % (current_accepted, total.get_attribute("innerHTML")))

"""
Sign off
"""
def sign_out(url, driver):
    driver.get(url)
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "nav-user-app"))
    )
    driver.find_element_by_id("nav-user-app").click()
    driver.find_element_by_css_selector("#nav-user-app span ul .dropdown-view .option-list .list-item:nth-child(3)").click()

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 lc_login.py <username> <password> <driver-path>")
        return
    url = "https://leetcode.com/accounts/login/"
    url_progress = "https://leetcode.com/progress/"
    username = sys.argv[1]
    password = sys.argv[2]
    DRIVER_PATH = sys.argv[3]
    
    try:
        driver = get_driver(DRIVER_PATH)
        login(url, username, password, driver)
        get_progress(url_progress, driver)
        sign_out(url_progress, driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()