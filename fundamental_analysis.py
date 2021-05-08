## Author: Isaac Kargar

import numpy as np
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests

from pytrends.request import TrendReq
from pprint import pprint

from pycoingecko import CoinGeckoAPI



def GetTargetScore(name):
    # read target
    try:
        url = 'https://coincheckup.com/coins/{}/about'.format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
           EC.presence_of_element_located((By.CLASS_NAME, "stars-wrapper"))
        )
        target_score = int(element.get_attribute('uib-tooltip')[:-1].split('.')[0])
        browser.quit()
    except:
        target_score = None
        browser.quit()
        # print('no data for target')

    return target_score
    
def GetCoinCheckupInfo(name):
    # read data from coincheckup
    info = {
        'Team strength': None,
        'Product strength': None,
        'Coin strength': None,
        'GitHub': None
    }
    try:
        url = 'https://coincheckup.com/coins/{}/analysis'.format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
           EC.presence_of_element_located((By.CLASS_NAME, "dl-horizontal"))
        )
        res = element.get_attribute('innerHTML')
        browser.quit()

        parsed_html = BeautifulSoup(res, 'lxml')

        divs = parsed_html.find_all('div')
        for div in divs:
            if "Team strength" in div.text:
        #         print('Team strength:', div.text.split(' ')[-1])
                info['Team strength'] = int(div.text.split(' ')[-1][:-1])
            if "Product strength" in div.text:
        #         print('Product strength:', div.text.split(' ')[-1])
                info['Product strength'] = int(div.text.split(' ')[-1][:-1])
            if "Coin strength" in div.text:
        #         print('Coin strength:', div.text.split(' ')[-1])
                info['Coin strength'] = int(div.text.split(' ')[-1][:-1])
            if "GitHub" in div.text and '%' in div.text:
        #         print('GitHub:', div.text.split(' ')[-1])
                info['GitHub'] = int(div.text.split(' ')[-1][:-1])
    except:
        browser.quit()
        # print('no data in coincheckup analysis')

    return info
        
def GetTwitterScore(name):
    # twitter score
    if name == 'polkadot-new':
        name = 'polkadot'
    try:
        url = 'https://www.coingecko.com/en/coins/{}#social'.format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tab-pane.active"))
        )
        res = element.get_attribute('innerHTML')
        browser.quit()

        parsed_html = BeautifulSoup(res, 'lxml')
        divs = parsed_html.findAll("div", {"class": "social-circle tw-flex flex-column tw-justify-start tw-items-center"})

        for div in divs:
            if 'twitter' in str(div):
                tdiv = div
                
        for d in tdiv:
            try:
                if 'mt-4' in d.get('class'):
                    # print(d.text)
                    n_followers = d.text
            except:
                pass
            
        split_tw = n_followers.split(',')
        if len(split_tw) == 3:
            n_followers = int(split_tw[0]+split_tw[1])
        elif len(split_tw) == 2:
            n_followers = int(split_tw[0])
        else:
            n_followers = 0

        twitter_score = 0
        if n_followers <= 200:
            twitter_score = 20
        elif n_followers <= 300:
            twitter_score = 40
        elif n_followers <= 400:
            twitter_score = 60
        elif n_followers <= 500:
            twitter_score = 80
        elif n_followers >= 500:
            twitter_score = 100
    except:
        twitter_score = None
        browser.quit()
        # print('error in finding twitter follower ')

    return twitter_score

def GetNvtScore(name):
    ## calculate nvt
    try:
        cg = CoinGeckoAPI()
        cg_data = cg.get_price(
            ids=name, 
            vs_currencies='usd', 
            include_market_cap='true', 
            include_24hr_vol='true'
        )

        nvt = cg_data[name]['usd_market_cap'] / cg_data[name]['usd_24h_vol']
        nvt_score = 0
        if nvt <= 15:
            nvt_score = 100
        elif nvt <= 20:
            nvt_score = 80
        elif nvt <= 25:
            nvt_score = 60
        elif nvt <= 30:
            nvt_score = 40
        else:
            nvt_score = 20
    except:
        nvt_score = None
        # print('error in nvt calculation')

    return nvt_score

def GetGoogleTrendScore(name):
    # google trend
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        kw_list = [name]
        pytrends.build_payload(kw_list, cat=0, timeframe='today 5-y', geo='', gprop='')
        df = pytrends.interest_over_time()
        trend = df.iloc[-1][0]
        trend_score = 0
        if trend <= 25:
            trend_score = 25
        elif trend <= 50:
            trend_score = 50
        elif trend <= 75:
            trend_score = 75
        else:
            trend_score = 100
    except:
        trend_score = None
        # print('error in google trend')

    return trend_score
        

def GetRankingFromWeisscrypto(name):
    try:
        url = "https://weisscrypto.com/en/crypto/{}/summary".format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, "r-rating-container"))
        )

        if len(element.text) == 1:
            rank = element.text
        else:
            rank = element.text[0] + element.text[-1]
        browser.quit()
        ranking_dict = {
            'A+': 100,
            'A': 90,
            'A-': 80,
            'B+': 70,
            'B': 60,
            'B-': 50,
            'C+': 40,
            'C': 30,
            'C-': 20,
            'D+': 10,
        }
        score =  ranking_dict[rank]
    except:
        score = None
        browser.quit()
        # print('no data for rank')

    return score
    

def GetRankingFromSimetri(name):
    
    if name == 'polkadot-new':
        name = 'polkadot'
    try:
        url = 'https://www.coingecko.com/en/coins/{}#ratings'.format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
        EC.presence_of_element_located((By.CLASS_NAME, "wrap-grade"))
        )
        child_element_list = element.find_elements_by_tag_name("span")
        rank = child_element_list[0].get_attribute('innerHTML')
        browser.quit()

        ranking_dict = {
            'A+': 100,
            'A': 90,
            'A-': 80,
            'B+': 70,
            'B': 60,
            'B-': 50,
            'C+': 40,
            'C': 30,
            'C-': 20,
            'D+': 10,
        }
        score = ranking_dict[rank]
        
    except:
        score = None
        browser.quit()
        # print('no data for rank')

    return score

def GetRankingFromCoingecko(name):
    if name == 'polkadot-new':
        name = 'polkadot'
    try:
        url = 'https://www.coingecko.com/en/coins/{}#ratings'.format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        element = WebDriverWait(browser, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "badge.badge-warning.text-lg"))
        )
        rank = element.get_attribute('innerHTML')
        browser.quit()
        
        ranking_dict = {
            'AAA': 100,
            'AA': 90,
            'A': 80,
            'BBB': 70,
            'BB': 60,
            'B': 50,
            'CCC': 40,
            'CC': 30,
            'C': 20,
            'DDD': 10,
        }
        score = ranking_dict[rank]

    except:
        score = None
        browser.quit()
        # print('no data for rank')

    return score
        
def GetRankingFromCoincheckup(name):
    try:
        url = "https://coincheckup.com/coins/{}/analysis".format(name)
        browser = webdriver.Chrome('chromedriver_linux64/chromedriver')
        browser.set_window_size(1120, 550)
        browser.get(url)
        table = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "key-financials"))
            )
        time.sleep(2)
        text = table.text
        score = float(text.split(' ')[-2].split('/')[0]) * 20
        browser.quit()

    except:
        score = None
        browser.quit()
        # print('no data for rank')

    return score


if __name__ == '__main__':

    names = ['cardano', 'polkadot-new', 'xrp', 'dogecoin', 'holo', 'tron']
    symbols = ['ada', 'C0006553', 'xrp', 'doge', 'hot', 'trx']
    # names = ['holo']
    # symbols = ['hot']

    for name, symbol in zip(names, symbols):
        print('collecting data for {}'.format(name))
        info = {
            'target': None,
            'Team strength': None,
            'Product strength': None,
            'Coin strength': None,
            'twitter-followers': None,
            'nvt': None,
            'GitHub': None,
            'google-trend': None
        }

        info['target'] = GetTargetScore(name)
        res = GetCoinCheckupInfo(name)
        for item in res: info[item] = res[item] 
        info['twitter-followers'] = GetTwitterScore(name)
        info['nvt'] = GetNvtScore(name)
        info['google-trend'] = GetGoogleTrendScore(name)
        
        print('info for {}: '.format(name))
        pprint(info)

        # calculate total score
        total_score = 0
        cnt = 0
        for item in info:
            if info[item] is not None:
                total_score += info[item]
                cnt += 1

        my_fa_score = total_score/cnt
        print('My FA score for {}: {:.2f}'.format(name, my_fa_score))
        
        #-------------- get ranking from other websites -----------
        ranks = {
            'my_fa_score': my_fa_score,
            'weisscrypto': None,
            'simetri': None,
            'coingecko': None,
            'coincheckup': None
            }
        ranks['weisscrypto'] = GetRankingFromWeisscrypto(symbol)
        ranks['simetri'] = GetRankingFromSimetri(name)
        ranks['coingecko'] = GetRankingFromCoingecko(name)
        ranks['coincheckup'] = GetRankingFromCoincheckup(name)
        ranks_no_none = [ranks[item] for item in ranks if ranks[item] is not None]
        print('\nscore:')
        pprint(ranks)
        avg_score = np.array(ranks_no_none).mean()

        print('Final FA score for {} is: {:.2f}'.format(name, avg_score))

        print('\n\n ------------------------------------ \n\n')

