from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from lxml import html
import time
import re

def find_team_name_and_status(Xpath_name, Xpath_status, tree):
    team_name = tree.xpath(Xpath_name)
    team_status = tree.xpath(Xpath_status)
    print(f'Nazwa Druzyny: {team_name[0].text} Status Druzyny: {team_status[0].text}')
    return team_name[0].text + ", " + team_status[0].text + ", "

def find_players_and_picks(Xpath, tree):
    picks = tree.xpath(Xpath)
    players_and_heroes = []
    for elem in picks:
        hero = re.search(r'\(([^)]+)\)', elem.attrib['data-tooltip-html'])[0].strip("()")
        player = re.search(r'<div><b>(.*?)</b>', elem.attrib['data-tooltip-html']).group(1)
        print(f'Bohater: {hero} Gracz: {player}')
        players_and_heroes.append(f'{player}, {hero}')

    return ", ".join(players_and_heroes)

options = Options()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

base_url = "https://cyberscore.live/en/matches/past/?type=past&page="
max = 50 + 1
records = []
for page_num in range(1, max):  # np. N = 5, 10, ile chcesz stron
    url = base_url + str(page_num)
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.ID, "content")))

    time.sleep(3) 

    page_source = driver.page_source
    tree = html.fromstring(page_source)

    matches = tree.xpath('//*[@id="content"]/div[1]/div/div[1]/div[3]/div[2]//a')

    for match in matches:
        status = match.xpath('.//div[3]/div/div/span/text()')
        if status and "FF" in status[0]:
            print("Mecz poddany")
            continue
      
        record = str()
        href = match.get("href")
        tier = match.xpath('.//div[contains(@class, "tournament-item-col__tier")]//span')
        print("Mecz: " + href + "Tier: " + tier[0][0].tail.strip("-"))

        full_url = "https://cyberscore.live" + href
        driver.get(full_url)

        tree_picks = html.fromstring(driver.page_source)
        match_time = tree_picks.xpath('//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div/text()')
        print(match_time[0])
        picks_xpath_team_a = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[1]/div[1]//div[@class="picks-item"]'
        team_name_a_xpath = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/div/a/span[2]'
        team_status_a_xpath = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/div/div/div[2]'
        record += find_team_name_and_status(team_name_a_xpath, team_status_a_xpath, tree_picks)
        record += find_players_and_picks(picks_xpath_team_a, tree_picks) + ", "

        picks_xpath_team_b = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[2]/div[2]/div[1]//div[@class="picks-item"]'
        team_name_b_xpath = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div/a/span[2]'
        team_status_b_xpath = '//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div/div[2]/div[1]/div[3]/div/div/div[2]'
        record += find_team_name_and_status(team_name_b_xpath, team_status_b_xpath, tree_picks)
        record += find_players_and_picks(picks_xpath_team_b, tree_picks)
        record += ", " + tier[0][0].tail.strip("-") + ", " + match_time[0]

        print("\n")
        print(record)
        records.append(record)

csv_headers = "Team_A_Name, Team_A_Status, Team_A_Carry_Name, Team_A_Carry_Hero, Team_A_Mid_Name, Team_A_Mid_Hero" \
              "Team_A_Off_Name, Team_A_Off_Hero, Team_A_Support_Name, Team_A_Support_Hero, Team_A_HardSupport_Name, Team_A_HardSupport_Hero" \
              "Team_B_Name, Team_B_Status, Team_B_Carry_Name, Team_B_Carry_Hero, Team_B_Mid_Name, Team_B_Mid_Hero, " \
              "Team_B_Off_Name, Team_B_Off_Hero, Team_B_Support_Name, Team_B_Support_Hero, Team_B_HardSupport_Name, Team_B_HardSupport_Hero" \
              "Tier, Time "
driver.quit()

with open("matches.csv", "w", encoding="utf-8") as f:
    f.write(csv_headers + "\n")
    for record in records:
        f.write(record + "\n")