from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from lxml import html
import time
import re

def find_players_and_picks(Xpath):
    picks = tree_picks.xpath(picks_xpath_team_a)
    for elem in picks:
        hero = re.search(r'\(([^)]+)\)', elem.attrib['data-tooltip-html'])[0].strip("()")
        player = re.search(r'<div><b>.*</b>', elem.attrib['data-tooltip-html'])[0].strip("<div>/<b>")
        print(f'Bohater: {hero} Gracz: {player}')

options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

driver.get("https://cyberscore.live/en/matches/past/")

wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.ID, "content")))

time.sleep(3) 

page_source = driver.page_source
tree = html.fromstring(page_source)

matches = tree.xpath('//*[@id="content"]/div[1]/div/div[1]/div[3]/div[2]//a')

for match in matches:
    href = match.get("href")
    print(href)



    full_url = "https://cyberscore.live" + href
    driver.get(full_url)

    tree_picks = html.fromstring(driver.page_source)
    team_a_name = tree_picks.xpath('//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/div/a/span[2]')
    team_b_name = tree_picks.xpath('//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div/a/span[2]')
    print(team_a_name[0].text)
    print(team_b_name[0].text)

    picks_xpath_team_a = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[1]//div[@class="picks-item"]'
    find_players_and_picks(picks_xpath_team_a)

driver.quit()
