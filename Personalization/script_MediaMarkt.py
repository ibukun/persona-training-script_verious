# imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import FirefoxOptions
import pandas as pd
import numpy as np
import time
import re
from tqdm import tqdm
import argparse
import warnings
from user_agents import parse
warnings.simplefilter("ignore")


# SCRIPT USAGE:
### without user-agent:
# python Personalization/script_MediaMarkt.py
#     --exp_name MM_first_exp1
#     --items_list steelstofzuiger vaatwasser printer loopband tondeuse fohn koptelefoon wasmachine laptop cameras scheerapparaat strijkplank e-reader hoofdtelefoon koelkast oven smartphone magnetron
#     --web_page https://www.mediamarkt.nl/
#     --exec_path Personalization/geckodriver.exe

### with user-agent:
# python Personalization/script_MediaMarkt.py
#     --exp_name MM_second_exp2
#     --items_list steelstofzuiger vaatwasser printer loopband tondeuse fohn koptelefoon wasmachine laptop cameras scheerapparaat strijkplank e-reader hoofdtelefoon koelkast oven smartphone magnetron
#     --web_page https://www.mediamarkt.nl/
#     --exec_path Personalization/geckodriver.exe
#     --ua_string "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30"

# LIST OF UA STRING:
### iPhone's user agent string
# ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
### Samsung Galaxy S3
# ua_string = 'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30'
###  non touch Blackberry device
# ua_string = 'BlackBerry9700/5.0.0.862 Profile/MIDP-2.1 Configuration/CLDC-1.1 VendorID/331 UNTRUSTED/1.0 3gpp-gba'
### iPad's user agent string
# ua_string = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'
### Kindle Fire's user agent string
# ua_string = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_3; en-us; Silk/1.1.0-80) AppleWebKit/533.16 (KHTML, like Gecko) Version/5.0 Safari/533.16 Silk-Accelerated=true'
### Touch capable Windows 8 device
# ua_string = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0; Touch)'


def get_parser():
    # parse parameters
    parser = argparse.ArgumentParser(description='Scrape MediaMarkt website')
    parser.add_argument("--exp_name", type=str, default="", help="Experiment name")
    parser.add_argument("--items_list", nargs='+', default="", help="List of products to search")
    parser.add_argument("--web_page", type=str, default="", help="Website url")
    parser.add_argument("--exec_path", type=str, default="", help="Path to execute the webdriver")
    parser.add_argument("--ua_string", type=str, default="", help="User agent string to specify to identify/detect devices and browsers")
    parser.add_argument("--proxy", type=str, default="", help="Proxy to mimic IP Address Geolocation")

    return parser


def iteration_mobile(driver, item, delays, collected_data):
    # banner button MediaMarkt click to update the search bar
    banner_button = driver.find_element_by_xpath('//*[@title="MediaMarkt"]')
    # randomly choose a delay and freeze the execution to mimic a person usage
    delay = np.random.choice(delays)
    time.sleep(delay)
    banner_button.click()  # press ENTER

    delay = np.random.choice(delays)
    time.sleep(delay)

    # put a query in the search bar
    search = driver.find_element_by_name("query")
    search.send_keys(item)  # put it in the search field
    search.send_keys(Keys.RETURN)  # press ENTER

    time.sleep(5)

    timeout = 30
    try:
        main = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "product-list")))
        time.sleep(5)
        articles = main.find_elements_by_class_name("product-teaser-container")  # get all products from the page
        for article in tqdm(articles):
            price_header = article.find_elements_by_class_name("product-teaser-price")  # get a price object

            if len(price_header) == 0:  # filter garbage from the scraped list of products
                pass
            else:
                _price_header = price_header[0].text  # get a price text
                # process the price string
                price = re.sub(r'[\n\r]+', '', _price_header)
                price = re.sub("\-", "00", price)
                price = re.sub("\.", "", price)
                price = re.sub("\,", ".", price)
                try:
                    price = float(price)
                except:
                    pass

                #                 product_content = article.find_elements_by_class_name('content')            # get an product object
                product_name = article.find_elements_by_class_name('ellipsis-text')  # get a product name

                # temporary dictionary of the product data
                temp = {
                    'website': "MediaMarkt",
                    'item': item,
                    'product': product_name[0].text,
                    'time': pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S"),
                    'price': price
                }

                collected_data.append(temp)  # append the data

    except TimeoutException:
        # driver.quit()
        print("driver has not found products on the webpage")


def iteration(driver, item, delays, collected_data):
    # banner button MediaMarkt click to update the search bar
    banner_button = driver.find_element_by_xpath('//*[@title="MediaMarkt"]')
    # randomly choose a delay and freeze the execution to mimic a person usage
    delay = np.random.choice(delays)
    time.sleep(delay)
    banner_button.click()   # press ENTER

    delay = np.random.choice(delays)
    time.sleep(delay)

    # put a query in the search bar
    search = driver.find_element_by_name("query")
    search.send_keys(item)  # put it in the search field
    search.send_keys(Keys.RETURN)   # press ENTER

    time.sleep(5)

    timeout = 30
    try:
        main = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "products-list")))
        time.sleep(5)
        articles = main.find_elements_by_class_name("product-wrapper")                      # get all products from the page

        for article in tqdm(articles):
            price_header = article.find_elements_by_class_name("small")                     # get a price object

            if len(price_header) == 0:                                                      # filter garbage from the scraped list of products
                pass
            else:
                _price_header = price_header[0].text                                        # get a price text
                # process the price string
                price = re.sub(r'[\n\r]+', '', _price_header)
                price = re.sub("\-", "00", price)
                price = re.sub("\.", "", price)
                price = re.sub("\,", ".", price)
                price = float(price)

                product_content = article.find_elements_by_class_name('content')            # get an product object
                product_name = product_content[0].find_elements_by_tag_name('h2')           # get a product name

                # temporary dictionary of the product data
                temp = {
                        'website': "MediaMarkt",
                        'item': item,
                        'product': product_name[0].text,
                        'time': pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S"),
                        'price': price
                        }

                collected_data.append(temp)                                                 # append the data

    except TimeoutException:
        # driver.quit()
        print("driver has not found products on the webpage")


def main(params):
    # initialize a list of the possible delays to mimic user interaction with websites
    delays = [1, 2, 3, 4, 5]

    # initialize a list where we store all collected data
    collected_data = []

    # list of items to search
    items_list = params.items_list

    # initalize webdriver options
    profile = webdriver.FirefoxProfile()
    if params.ua_string != '':
        # user agent string
        ua_string = params.ua_string
        # initialize user agent
        user_agent = parse(ua_string)
        print(f"Current user-agent: {user_agent}")
        profile.set_preference("general.useragent.override", ua_string)

    PROXY = params.proxy
    if PROXY != '':
        webdriver.DesiredCapabilities.FIREFOX['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL",
        }
        
    opts = FirefoxOptions()
    opts.add_argument("--headless")
    # initialize a webdriver
    driver = webdriver.Firefox(firefox_options=opts, firefox_profile=profile)
    # get the url
    driver.get(params.web_page)

    # time to wait a response from the page
    timeout = 30
    # press the button to accept cookies
    try:
        cookies = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "gdpr-cookie-layer__btn")))

        delay = np.random.choice(delays)
        time.sleep(delay)

        cookies.send_keys(Keys.RETURN)  # press ENTER

    except TimeoutException:
        print("Didn't found the button accept cookies.")

    # initialize a list with failed items
    skipped_items = []

    mobile_users = ['Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3',
                    'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30',
                    'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10']

    # collect the data in a mobile version of the webpage
    if params.ua_string in mobile_users:
        print("Mobile version is being used.")
        for item in tqdm(items_list):
            print("================")
            print(item)
            print("================")
            print("\n")

            try:
                try:
                    try:
                        _ = iteration_mobile(driver, item, delays, collected_data)

                    except:
                        _ = iteration_mobile(driver, item, delays, collected_data)

                except:
                    try:
                        _ = iteration_mobile(driver, item, delays, collected_data)

                    except:
                        _ = iteration_mobile(driver, item, delays, collected_data)

            except:
                print(f"{item} was skipped")
                skipped_items.append(item)
                pass

    else:
        print("PC version is being used.")
        # collect the data
        for item in tqdm(items_list):
            print("================")
            print(item)
            print("================")
            print("\n")

            try:
                try:
                    try:
                        _ = iteration(driver, item, delays, collected_data)

                    except:
                        _ = iteration(driver, item, delays, collected_data)

                except:
                    try:
                        _ = iteration(driver, item, delays, collected_data)

                    except:
                        _ = iteration(driver, item, delays, collected_data)

            except:
                print(f"{item} was skipped")
                skipped_items.append(item)
                pass

    print("Writing csv file...")
    df = pd.DataFrame(collected_data)
    df.to_csv(f'{params.exp_name}' + '_' + pd.to_datetime('now').strftime("%Y-%m-%d %H:%M:%S") + ".csv", index=False)
    print("Writing finished.")

    # close the driver
    driver.quit()


if __name__ == '__main__':
    parser = get_parser()
    params, unknown = parser.parse_known_args()

    # run the script
    main(params)
