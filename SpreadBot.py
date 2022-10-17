import os
import time
from telethon import TelegramClient, sync
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


path = 'A:/PochtaByBitBot/chromedriver.exe'
invest_sum = 1000
invest_sum_rub = 65000

eur_rub = ""
eur_rub_gpb = ""
usdt_eur = ""
rub_usdt = ""
client = ""

def login():
    global client
    try:
        finput = open(f"Data.txt")

        api_id = int(finput.readline())
        api_hash = finput.readline()
        api_hash = api_hash.replace('\n', '')
        print("Data read done")

        client = TelegramClient('Login', api_id, api_hash)
        client.start()

    except Exception as ex:
        time.sleep(120)
        login()

    finally:
        finput.close()

def get_exchange_rates():
    ex_rates_path = 'https://www.pochtabank.ru/support/currencies'
    global eur_rub

    try:
        browser = webdriver.Chrome(executable_path = path)
        

        while (eur_rub == ''):
            browser.get(url=ex_rates_path)
            time.sleep(1)
            background = browser.find_element_by_xpath('//*[@id="wrapper"]/div[2]/div[2]/div/div[5]')
            background.click()
            time.sleep(1)
            eur_rub = browser.find_element_by_xpath('//*[@id="wrapper"]/div[2]/div[2]/div/div[5]/div/div[2]/div[2]/div[12]/div[4]/div').text

        print(str(eur_rub))

        browser.close()
        get_bybit_rates()

    except Exception as ex:
        print(ex)
        print("Browser Error!")
        time.sleep(10)
        browser.close()
        get_exchange_rates()

def get_bybit_rates():
    global usdt_eur
    bybit_path = 'https://www.bybit.com/fiat/purchase/crypto'

    try:
        browser = webdriver.Chrome(executable_path = path)
        browser.get(url=bybit_path)
        try:
            cross_button = browser.find_element_by_xpath('//*[@id="popover-root"]/div/div/div[2]/span')
            cross_button.click()
        except:
            print("No pop-up window.")

        currency_button = browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/span[2]/div/div/div/span[3]')
        currency_button.click()

        eur_button = browser.find_element_by_xpath('//*[@id="popover-root"]/div/div/div/ul/li[1]/div[1]')
        eur_button.click()

        currency_button = browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[3]/div[2]/div/div/div/span[3]')
        currency_button.click()

        usdt_button = browser.find_element_by_xpath('//*[@id="popover-root"]/div/div/div/ul/li[3]/div')
        usdt_button.click()

        input_amount = browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/span[1]/input')
        input_amount.send_keys(str(invest_sum))

        refresh_button = browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[1]/div[1]/div[2]/span/div/i')
        refresh_button.click()
        time.sleep(3)

        for i in range(1,5):
            pay_method = browser.find_element_by_xpath(f'//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div[1]/div/div[{i}]/div/div[3]/div[1]')
            pay_method = str(pay_method.text)
            if (pay_method == 'Mercuryo'):
                method_button = browser.find_element_by_xpath(f'//*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div[1]/div/div[{i}]/div/div[1]')
                method_button.click()
                break
        
        accept_button = browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[3]/div[1]/div[1]/i')
        accept_button.click()
        time.sleep(2)
        usdt_get = str(browser.find_element_by_xpath('//*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[1]/div[4]/span').text)
        time.sleep(2)
        usdt_get = usdt_get[0:-5]
        usdt_get = usdt_get.replace(',', '')

        usdt_eur = round((float(usdt_get)/float(invest_sum)),3)
        print(str(usdt_eur))

        browser.close()
        get_p2p_rates()

    except Exception as ex:
        print(ex)
        client.send_message('@FloydSelenium', str(ex))
        print("Browser Error!")
        time.sleep(10)
        browser.close()
        get_bybit_rates()

def get_p2p_rates():
    global rub_usdt

    rub_usdt = 0.0  
    bybit_p2p_path = 'https://www.bybit.com/fiat/trade/otc/?actionType=0&token=USDT&fiat=RUB&paymentMethod=75'

    try:
        browser = webdriver.Chrome(executable_path = path)
        browser.get(url=bybit_p2p_path)

        try:
            cross_button = browser.find_element_by_xpath('//*[@id="modal-root"]/div/div/div/i')
            cross_button.click()
        except:
            print("No pop-up window.")

        try:
            accept_button = browser.find_element_by_xpath('//*[@id="modal-root"]/div/div/div[3]/button')
            accept_button.click()
        except:
            print("No pop-up window.")

        for i in range(1,5):
            rub_usdt += float(browser.find_element_by_xpath(f'//*[@id="root"]/div[3]/div[1]/div[3]/div[2]/div/div/div/table/tbody/tr[{i}]/td[2]/div/div[1]/span').text)
        rub_usdt = round((rub_usdt/4), 3)  
        print(str(rub_usdt))

        browser.close()

    except Exception as ex:
        print(ex)
        client.send_message('@FloydSelenium', str(ex))
        print("Browser Error!")
        time.sleep(10)
        browser.close()
        get_p2p_rates()

def check_profit():
    global eur_rub
    spend = invest_sum_rub

    try:
        collect = (float(invest_sum_rub)/float(eur_rub)*float(usdt_eur)*float(rub_usdt))
        spread = round(((float(collect)/float(spend))*100-100), 2)

        client.send_message('@FloydSelenium', f'Текущий спред {str(spread)}%\nКурс ПБ {str(eur_rub)} RUB\nКурс биржи {str(usdt_eur)} USDT\nКурс p2p {str(rub_usdt)} RUB')

        if ((spread >= 3)):
            dialogs = client.get_dialogs()
            group = dialogs[0]
            client.send_message(group, f'Текущий спред UP {str(spread)}%\nКурс UP {str(eur_rub)} RUB\nКурс биржи {str(usdt_eur)} USDT\nКурс p2p {str(rub_usdt)} RUB')

    except Exception as ex:
        client.send_message('@FloydSelenium', str(ex))
        time.sleep(60)

#    X-Path:
#    eur button //*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/span[2]/div/div/div/span[3]
#    eur button2 //*[@id="popover-root"]/div/div/div/ul/li[1]/div[1]
#    usdt button //*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[3]/div[2]/div/div/div/span[3]
#    usdt button2 //*[@id="popover-root"]/div/div/div/ul/li[3]/div
#    spend window //*[@id="root"]/div/div[2]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/span[1]/input
#    merc button //*[@id="root"]/div/div[2]/div/div[3]/div[1]/div[2]/div[1]/div/div[4]/div/div[1]
#    collect window //*[@id="root"]/div/div[2]/div/div[3]/div[2]/div[2]/div/div[1]/div[4]/span
#    accept button //*[@id="modal-root"]/div/div/div[3]/button

login()
while True:
    get_exchange_rates()
    check_profit()
    time.sleep(480)