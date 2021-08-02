# coding: UTF-8
import os
import time
import twitter
import tweepy
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.select import By
from fake_useragent import UserAgent
import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage,ImageSendMessage
import requests
import re

def get_last_updated_date(credentials):
    consumer_key=credentials['API_KEY']
    consumer_secret=credentials['API_SECRET']
    access_token_key=credentials['ACCESS_TOKEN']
    access_token_secret=credentials['ACCESS_TOKEN_SECRET']
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)

    api = tweepy.API(auth)
    # auto_follow(api) #自動でフォロー
    Account = "newballnotifier" #取得したいユーザーのユーザーIDを代入
    tweets = api.user_timeline(Account, count=200, page=1)
    for i in range(len(tweets)):
        pattern = r'\d{4}/\d{2}/\d{2}'
        result = re.match(pattern,tweets[i].text)
        if result:
            date = tweets[i].text.split("\n")[0].split('/')
            return date[1] + '/' + date[2] + '/' + date[0]
    print(">>>>>>>>>No date described tweet<<<<<<")
    return

def auto_follow(api):
    follower_list= api.followers(count=25)
    for follower in follower_list:
        api.create_friendship(follower.id)

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
    print("update : " + update )
    print("last update date : " + get_last_updated_date(os.environ))

    if(update != get_last_updated_date(os.environ)):
        select_element = driver.find_element(By.ID,'ddlApprovedBallList')
        select_object = Select(select_element)
        
        #月　日　年
        date = update.split('/') 
        months = ['zero','January','February','March','April','March','June','July','August','September','October','November','December']
        update = months[int(date[0])] + ' ' + str(int(date[1])) + ', ' + date[2]
        print("search update date : " + update)

        search_brands = ['Storm','Roto Grip','900 Global','Sunbridge Co., Ltd.','Brunswick','Ebonite','Hammer','Legend Star','Motiv']
        ballnames,imgs = [],[]
        for i in range(len(search_brands)):
            select_object.select_by_value(search_brands[i])
            time.sleep(4)
            print(search_brands[i])

            approvedlist = driver.find_element_by_id('approvedlist')
            trs = approvedlist.find_elements(By.TAG_NAME,"tr")

            for j in range(len(trs)):
                tds = trs[j].find_elements(By.TAG_NAME,"td")
                name = tds[0].text
                balldate = tds[1].text
                if(balldate == update):
                    image = tds[0].find_element(By.TAG_NAME,'a')
                    img_link = image.get_attribute('data-original-title').split('\'')[1]
                    print(name)
                    print(img_link)
                    ballnames.append(name)
                    imgs.append(img_link)
        send_line_notify(ballnames,imgs,os.environ)
        send_broadcast(ballnames,imgs,os.environ)
        tweet(ballnames,imgs,api,date)
    driver.quit()
    return "ok"

# Line notify ver
def send_line_notify(ballnames,imgs,credentials):

    for i in range(len(ballnames)):
        line_notify_token = credentials['line_notify_token']
        line_notify_api = 'https://notify-api.line.me/api/notify'
        headers = {'Authorization': 'Bearer ' + line_notify_token}
        payload = { 'imageFullsize': imgs[i],
                'imageThumbnail': imgs[i],
                'message': ballnames[i]
            }
        requests.post(line_notify_api, headers = headers, data = payload)

# マロンヌver
def send_broadcast(ballnames,imgs,credentials):
    for i in range(len(ballnames)):
        line_access_token = credentials['line_access_token']
        line_api = LineBotApi(line_access_token)
        message = ballnames[i] + '\n' + imgs[i]
        line_api.broadcast(TextSendMessage (text=message))

def tweet(ballnames,img_links,api,date):
    times = (len(ballnames)-1)//4 + 1
    for i in range(times):
        message = date[2] + '/' + date[0] + '/' + date[1] + '\n' + '>>> New Balls Arrived!!! <<<' + '\n'
        tweet_imgs = []
        for j in range(4):
            if 4*i+j < len(ballnames) : 
                message += '\n' + ballnames[4*i + j]
                tweet_imgs.append(img_links[4*i + j])
        api.PostUpdate(message,media=tweet_imgs)

