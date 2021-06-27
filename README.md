# New Ball Notification

This is a program called **New Ball Notification**(NBN).

## Aim of NBN

* I programmed NBN to deliver the newest bowling ball information to everyone who love bowling via twitter.

* New balls must be registered to USBC and they are uploaded before the formal announcement of release by maker.

## Problem

* In the [USBC site](https://www.bowl.com/approvedballlist/), it takes some times to find new balls from ball list because there are many brands and balls.

* We don't know when the page is updated. If you want to know new ball information earlier than anyone, you have to check this complicated site everyday. It's a bother!.

## Details

* I used **[Selenium](https://www.selenium.dev/documentation/en/)**(python library, support the automation of web browsers) to scrape web page, and **[Twitter API](https://developer.twitter.com/en/docs/twitter-api)** to tweet. I also used python module **"python-twitter"**.This module supports twitter api certification.
* NBN is executed automaticaly and regurarly on the **[Google Cloud Platform](https://console.cloud.google.com/)**, especially using **Google Cloud Function** and **Google Cloud Scheduler**.
* NBN scrapes [USBC](https://www.bowl.com/approvedballlist/)(approved bowling ball list page) regularly. 

## Reference

* [Google Cloud Function + Cloud Scheduler + Python で定期的に Twitter 投稿する](https://qiita.com/niwasawa/items/90476112dfced169c113)

* [Google Cloud FunctionsでPython+seleniumでスクレイピングしてみる](https://blowup-bbs.com/gcp-cloud-functions-python3/)

* [python-twitter](https://python-twitter.readthedocs.io/en/latest/)