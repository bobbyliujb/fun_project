#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, time, traceback, datetime
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials

def get_driver(DRIVER_PATH):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return webdriver.Chrome(DRIVER_PATH, chrome_options=options)

def login(url, username, password, driver):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ls_username"))
    )
    try:
        driver.find_element_by_id("ls_username").send_keys(username)
        driver.find_element_by_id("ls_password").send_keys(password)
        driver.find_element_by_css_selector("#lsform button").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "um"))
        )
    except:
        traceback.print_exc()

def click_attendance(driver):
    try:
        driver.find_element_by_css_selector("#um p a:nth-of-type(4)").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "kx"))
        )
        driver.find_element_by_id("kx").click()
        input_box = driver.find_element_by_id("todaysay")
        input_box.clear()
        input_box.send_keys("签到威武")
        driver.find_element_by_css_selector("#qiandao p button").click()
    except:
        traceback.print_exc()

def get_points(driver):
    try:
        print(driver.find_element_by_id("extcreditmenu").get_attribute('innerHTML'))
    except:
        traceback.print_exc()

def main():
    if len(sys.argv) < 3:
        print('Usage: python3 1p3a_attendance.py <username> <password> <driver-path>')
        return
    url = 'https://www.1point3acres.com/bbs/'
    username = sys.argv[1]
    password = sys.argv[2]
    DRIVER_PATH = sys.argv[3]
    
    try:
        driver = get_driver(DRIVER_PATH)
        login(url, username, password, driver)
        click_attendance(driver)
        get_points(driver)
    finally:
        driver.quit()

if __name__ == "__main__":
    main()