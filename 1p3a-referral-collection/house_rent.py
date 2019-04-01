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

def parseHtml(driver, result):
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
        if (tbody_array[i].tr.th.b != None
            and len(tbody_array[i].tr.th.b.find_all('font')) >= 3):

            a = tbody_array[i].tr.th.find('a', class_ = 's xst')
            url = 'http://www.1point3acres.com/bbs/' + a['href']
            post_date = tbody_array[i].tr.find('td', class_ = 'by').em.span.get_text()
            title = a.get_text()

            info = tbody_array[i].tr.th.get_text()
            start_index = info.find(' - $', 1)
            matched_groups = re.match('.*\-\s\$\s*(.*)(..附近|其他)【(.*):(.*)】(.*)：【(.*)】(.*)找(.*)室友，(.*)', info[start_index:])
            if matched_groups == None:
                print(url)
                print(info[start_index:])
                i = i + 1
                continue
            else:
                matched_groups = matched_groups.groups()

            j = 0
            metadata = []
            while j < len(matched_groups):
                metadata.append(matched_groups[j])
                j = j + 1
            
            metadata.append(url)
            metadata.append(post_date)
            metadata.append(title)
            result.append(metadata)

        i = i + 1

    return True

def main():
    url = 'https://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=224&sortid=319&%1=&sortid=319&page='
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

    if len(sys.argv) < 5:
        print('Usage: python3 house_rent.py <max-page-count> <path-to-credentials> <sheet-id> <path-to-chromedriver>')
        return
    MAX_PAGE = int(sys.argv[1])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(sys.argv[2], scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_ID = sys.argv[3]
    DRIVER_PATH = sys.argv[4]
    wks = gc.open_by_key(SPREADSHEET_ID).get_worksheet(6)

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    result = []
    page = 1
    fail_count = 0

    driver = webdriver.Chrome(DRIVER_PATH, chrome_options=options)
    while page <= MAX_PAGE and fail_count < 10:
        print("Get webpage for " + url + str(page))
        try:
            time.sleep(2)
            driver.get(url + str(page))
            WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID, "threadlisttableid"))
            )
        except:
            traceback.print_exc()
            time.sleep(10)
            fail_count = fail_count + 1
            continue
        if (parseHtml(driver, result) == False):
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
    wks.update_acell("M1", "Update At: " + str(datetime.datetime.now()))

    # Free memory
    del cell_list
    del result
    del wks
    del gc
    del credentials

if __name__ == "__main__":
    main()
