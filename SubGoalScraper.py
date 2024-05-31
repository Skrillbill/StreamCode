
import configparser
import shutil
import requests
import wget
import os
import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# log init
logging.basicConfig(filename='error.log',encoding='utf-8',filemode='a',level=logging.INFO,format='%(asctime)s: %(levelname)s -> %(message)s')

# ini loading
try:
    if os.path.isfile('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        update_conf = config['UPDATER_SETTINGS']

    else:
        logging.critical('INI file is not detected.')
except NameError as err:
    logging.critical(f'Variable Error: {err}')
except Exception as err:
    logging.critical(f'Something went wrong: {err}')


def update_redux():
    current_version = "0"
    # latest_url = str(update_conf['chromedriver_latest'])
    if os.path.isfile('LATEST_STABLE'): # current_version defaults to none/0. But if we've updated before, we'll override the variable with whatvever the last downloaded version was.
        with open('LATEST_STABLE') as lrs:
            current_version = lrs.read()

    # google for testing has a json endpoint we can query for the current version of all the release channels. We only care about Stable
    response = requests.get(str(config['UPDATER_SETTINGS']['chromedriver_version']))
    data = response.json()
    new_version = json.dumps(data.get('channels').get('Stable').get('version'))
    new_version = new_version.strip('"') # strip the quotation marks from the json string

    if str(current_version) == str(new_version) : # is already current version
        logging.info(f'No update required: Current: {current_version} and new version {new_version}')
    else: # download new version
        logging.info(f'New version detected: {new_version}. Installed version: {current_version}...Updating')
        url = str(update_conf['chromedriver_mirror']) + new_version + '/win64/chromedriver-win64.zip'
        stable_release = wget.download(url)
        shutil.unpack_archive(stable_release)

        version_file = open('LATEST_STABLE',"w")
        version_file.write(new_version)
        version_file.close()

        logging.info(f'Chromedriver has been updated to {new_version}')


def main():
    file_name = "sub_goal_output.txt"
    update_redux()  # Call our updater
    # Set up the Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode for no GUI
    service = Service(executable_path=r'chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # URL to scrape
    url = "https://www.twitch.tv/colonal/about"

    try:
        driver.get(url)
        time.sleep(5)
        # Find the element using the specified XPath
        element = driver.find_element(By.XPATH,
                                      "/html/body/div[1]/div/div[1]/div/main/div[1]/div[3]/div/div/div[1]/div[1]/div[2]/div/section/div[3]/div/div/div/div[1]/div[2]/div/div[2]/div/div[2]/div[2]/div/div/div/div/div[2]/div[2]/p")

        # Get the text content of the element
        text_content = element.text.split("/")[0]



        with open(file_name, "w") as file:
            file.write(text_content)
        logging.info(f"Text content saved to {file_name} ")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Close the WebDriver
        driver.quit()


if __name__ == '__main__':
    main()