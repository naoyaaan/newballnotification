# coding: UTF-8
import os
import time
import twitter
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.select import By
from fake_useragent import UserAgent
from datetime import datetime,timedelta
import requests

def get_twitter_api(credentials):
    return twitter.Api(
        consumer_key=credentials['API_KEY'],
        consumer_secret=credentials['API_SECRET'],
        access_token_key=credentials['ACCESS_TOKEN'],
        access_token_secret=credentials['ACCESS_TOKEN_SECRET'])

def handler(data, context):
    api = get_twitter_api(os.environ)

    chrome_options = webdriver.ChromeOptions()

    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--hide-scrollbars')
    chrome_options.add_argument('--enable-logging')
    chrome_options.add_argument('--log-level=0')
    chrome_options.add_argument('--v=99')
    chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.binary_location = os.getcwd() + "/headless-chromium"    
    driver = webdriver.Chrome(os.getcwd() + "/chromedriver",chrome_options=chrome_options)
    url = "https://www.bowl.com/approvedballlist/"
    driver.get(url)

    update = driver.find_element_by_xpath('//*[@id="aspnetForm"]/div[6]/div/div[2]/article/section/p/strong').text
    update = update.split(':')[1].replace(' ','')
    
    now = datetime.now()
    month = str(now.month)
    day = str(now.day)
    if now.month < 10 : month = '0' + month
    if now.day < 10 : day = '0' + day
    today = month + '-' + day + '-' + str(now.year)

    if(today == update):
        months = ['January','February','March','April','March','June','July','August','September','October','November','December']
        update = months[now.month-1] + ' ' + str(now.day) + ', ' + str(now.year)

        select_element = driver.find_element(By.ID,'ddlApprovedBallList')
        select_object = Select(select_element)

        search_brands = ['Storm','Roto Grip','Sunbridge Co., Ltd.','Brunswick','Ebonite','Hammer','Legend Star','Motiv']
        for i in range(len(search_brands)):
            ballnames,imgs = [],[]
            select_object.select_by_value(search_brands[i])
            time.sleep(4)
            print(search_brands[i])

            approvedlist = driver.find_element_by_id('approvedlist')
            trs = approvedlist.find_elements(By.TAG_NAME,"tr")

            message = str(now.year) + '-' + str(now.month) + '-' + str(now.day)+ '\n' + search_brands[i] + ':\n' 

            for j in range(len(trs)):
                tds = trs[j].find_elements(By.TAG_NAME,"td")
                name = tds[0].text
                date = tds[1].text
                if(date == update):
                    image = tds[0].find_element(By.TAG_NAME,'a')
                    img_link = image.get_attribute('data-original-title').split('\'')[1]
                    message += '\n' +  name
                    ballnames.append(name)
                    imgs.append(img_link)
            api.PostUpdate(message,media=imgs)
            send_line_notify(ballnames,imgs)

    driver.quit()
    return "ok"

def send_line_notify(ballnames,imgs):

    for i in range(len(ballnames)):
        line_notify_token = 'b945paFlh4wfkbnx4MQafiuHAAlcfKiYVpZlxisbArw'
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + line_notify_token}
        payload = { 'imageFullsize': imgs[i],
                'imageThumbnail': imgs[i],
                'message': ballnames[i]
            }
        requests.post(line_notify_api, headers = headers, data = payload)