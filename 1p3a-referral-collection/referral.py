#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, gspread, time, traceback, datetime
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials

def parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result):
    if (driver.page_source == None):
        return False
    soup = BS(driver.page_source, 'html.parser')
    section_main = soup.find(id='threadlisttableid')
    if (section_main == None):
        print("No threadlisttableid found!")
        return False
    tbody_array = section_main.find_all('tbody', id = re.compile('^normalthread'))
    if (tbody_array == None or len(tbody_array) == 0):
        print("No normalthread tbody found!")
        return False

    i = 0
    while i < len(tbody_array):
        if (tbody_array[i].tr.th.em != None 
            and "招人" in tbody_array[i].tr.th.em.get_text()
            and tbody_array[i].tr.th.span != None
            and tbody_array[i].tr.th.span.span != None):
            span = tbody_array[i].tr.th.span.span
            company_name = span.u.find_all('b')[2].get_text().lower()
            if (company_name not in link_count):
                link_count[company_name] = 0

            if (link_count[company_name] < MAX_LINK_PER_COMPANY):
                link_count[company_name] = link_count[company_name] + 1
                metadata = [company_name]
                a = tbody_array[i].tr.th.find('a', class_ = 's xst')
                metadata.append(span.find('font', color = '#F60').b.get_text())   # major
                metadata.append(span.u.next_sibling)            # experience level
                metadata.append('http://www.1point3acres.com/bbs/' + a['href'])                      # clickable url
                metadata.append(tbody_array[i].tr.find('td', class_ = 'by').em.span.get_text()) # date
                metadata.append(a.get_text())                   # thread title

                result.append(metadata)
                # temp = '{}\t{}\t{}\t{}\t{}\t{}'.format(company_name, metadata[1], metadata[2], metadata[3], metadata[4], metadata[5])
                # print(temp)

        i = i + 1

    return True

def main():
    url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=198&sortid=192&&page='
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

    if len(sys.argv) < 8:
        print('Usage: python3 referral.py <max-page-count> <max-link-per-company> <path-to-credentials> <sheet-id> <path-to-chromedriver> <username> <password>')
        return
    MAX_PAGE = int(sys.argv[1])
    MAX_LINK_PER_COMPANY = int(sys.argv[2])
    CREDENTIAL_PATH = sys.argv[3]
    SPREADSHEET_ID = sys.argv[4]
    DRIVER_PATH = sys.argv[5]
    USERNAME = sys.argv[6]
    PASSWORD = sys.argv[7]

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIAL_PATH, scope)
    gc = gspread.authorize(credentials)
    wks = gc.open_by_key(SPREADSHEET_ID).sheet1
    link_count = dict()
    result = []
    page = 1
    fail_count = 0

    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
    while page <= MAX_PAGE and fail_count < 10:
        print("Get webpage for " + url + str(page))
        try:
            time.sleep(2)
            driver.get(url + str(page))
            element = WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID, "threadlisttableid"))
            )
        except:
            traceback.print_exc()
            try:
                print("Logging in...")
                element = WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.NAME, "loginsubmit"))
                )
                driver.find_element_by_xpath("//*[contains(@id, 'username_')]").send_keys(USERNAME)
                driver.find_element_by_xpath("//*[contains(@id, 'password3_')]").send_keys(PASSWORD)
                driver.find_element_by_name("loginsubmit").click()
            except:
                traceback.print_exc()
            fail_count = fail_count + 1
            continue
        if (parseHtml(driver, link_count, MAX_LINK_PER_COMPANY, result) == False):
            fail_count = fail_count + 1
            continue
        page = page + 1
        fail_count = 0
        print("rows: " + str(len(result)))
    driver.quit()

    row_count = len(result)
    col_count = len(result[0])
    cell_list = wks.range(2, 1, row_count + 1, col_count)
    for i in range(row_count):
        for j in range(col_count):
            cell_list[i * col_count + j].value = result[i][j]
    wks.update_cells(cell_list)
    wks.update_acell("H1", "Update At: " + str(datetime.datetime.now()))

    # Free memory
    del cell_list
    del result
    del link_count
    del wks
    del gc
    del credentials


if __name__ == "__main__":
    main()
