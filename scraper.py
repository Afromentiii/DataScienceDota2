from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from lxml import html
import time
import re
from concurrent.futures import ThreadPoolExecutor

def find_team_name_and_status(Xpath_name, Xpath_status, tree):
    team_name = tree.xpath(Xpath_name)
    team_status = tree.xpath(Xpath_status)
    return team_name[0].text + ", " + team_status[0].text + ", "

def find_players_and_picks(Xpath, tree):
    picks = tree.xpath(Xpath)
    players_and_heroes = []
    for elem in picks:
        hero = re.search(r'\(([^)]+)\)', elem.attrib['data-tooltip-html'])[0].strip("()")
        player = re.search(r'<div><b>(.*?)</b>', elem.attrib['data-tooltip-html']).group(1)
        players_and_heroes.append(f'{player}, {hero}')
    return ", ".join(players_and_heroes)

def scrape_page(page_num):
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)

    base_url = "https://cyberscore.live/en/matches/past/?type=past&page="
    url = base_url + str(page_num)
    print(f"Scraping page {page_num}")

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "content")))
        time.sleep(3.4)

        page_source = driver.page_source
        tree = html.fromstring(page_source)
        matches = tree.xpath('//*[@id="content"]/div[1]/div/div[1]/div[3]/div[2]//a')

        records = []
        for match in matches:
            time.sleep(0.05)
            status = match.xpath('.//div[3]/div/div/span/text()')
            if status and "FF" in status[0]:
                print("Mecz poddany - pomijam")
                continue

            record = ""
            href = match.get("href")
            tier = match.xpath('.//div[contains(@class, "tournament-item-col__tier")]//span')
            full_url = "https://cyberscore.live" + href

            driver.get(full_url)
            tree_picks = html.fromstring(driver.page_source)
            match_time = tree_picks.xpath('//*[@id="content"]/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/div[1]/div[2]/div[1]/div/text()')

            if not match_time:
                print(f"Brak czasu dla meczu {full_url}")
                continue

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

            records.append(record)

    except Exception as e:
        print(f"Błąd na stronie {page_num}: {e}")
        records = []
    finally:
        driver.quit()

    return records

if __name__ == "__main__":
    all_records = []
    pages = range(77, 89)
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_page, page) for page in pages]

        for future in futures:
            result = future.result() 
            all_records.extend(result)

    csv_headers = "Team_A_Name, Team_A_Status, Team_A_Carry_Name, Team_A_Carry_Hero, Team_A_Mid_Name, Team_A_Mid_Hero," \
                  "Team_A_Off_Name, Team_A_Off_Hero, Team_A_Support_Name, Team_A_Support_Hero, Team_A_HardSupport_Name, Team_A_HardSupport_Hero," \
                  "Team_B_Name, Team_B_Status, Team_B_Carry_Name, Team_B_Carry_Hero, Team_B_Mid_Name, Team_B_Mid_Hero, " \
                  "Team_B_Off_Name, Team_B_Off_Hero, Team_B_Support_Name, Team_B_Support_Hero, Team_B_HardSupport_Name, Team_B_HardSupport_Hero," \
                  "Tier, Time"

    with open("data.csv", "a", encoding="utf-8") as f:
        for record in all_records:
            f.write(record + "\n")

    print("Zakończono zapis danych do pliku.")
