#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re, gspread, time
from bs4 import BeautifulSoup as BS
from selenium import webdriver
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
        # print(tbody_array[i].tr.th.span.u.find_all('b')[2].get_text().lower())
        if (tbody_array[i].tr.th.span != None
            and tbody_array[i].tr.th.span
            and tbody_array[i].tr.th.find('a', class_ = 's xst') != None
            and 'oa' in tbody_array[i].tr.th.find('a', class_ = 's xst').get_text().lower()):
            span = tbody_array[i].tr.th.span
            if (span.u == None):
                i = i + 1
                continue
            
            job_type = span.u.find_all('b')[2].get_text()
            if (job_type != '全职'):
                i = i + 1
                continue

            company_name = span.u.find_all('b')[3].get_text().lower()
            if (company_name not in link_count):
                link_count[company_name] = 0

            if (link_count[company_name] < MAX_LINK_PER_COMPANY):
                link_count[company_name] = link_count[company_name] + 1
                metadata = [company_name, job_type]
                a = tbody_array[i].tr.th.find('a', class_ = 's xst')
                metadata.append(re.sub(r'^\s\|', '', span.find_all('b')[5].next_sibling))       # experience level
                metadata.append('http://www.1point3acres.com/bbs/' + a['href'])               # clickable url
                metadata.append(tbody_array[i].tr.find('td', class_ = 'by').em.span.get_text()) # date
                metadata.append(a.get_text())                   # thread title

                result.append(metadata)
                # temp = '{}\t{}\t{}\t{}\t{}'.format(company_name, metadata[1], metadata[2], metadata[3], metadata[4], metadata[5])
                # print(temp)

        i = i + 1

    return True

def main():
    url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&sortid=311&%1=&sortid=311&page='
    scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

    if len(sys.argv) < 6:
        print('Usage: python3 oa.py <max-page-count> <max-link-per-company> <path-to-credentials> <sheet-id> <path-to-chromedriver>')
        return
    MAX_PAGE = int(sys.argv[1])
    MAX_LINK_PER_COMPANY = int(sys.argv[2])
    credentials = ServiceAccountCredentials.from_json_keyfile_name(sys.argv[3], scope)
    gc = gspread.authorize(credentials)
    SPREADSHEET_ID = sys.argv[4]
    DRIVER_PATH = sys.argv[5]
    wks = gc.open_by_key(SPREADSHEET_ID).get_worksheet(2)

    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

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
            time.sleep(10)
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
