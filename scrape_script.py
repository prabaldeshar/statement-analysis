import os
import re
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

ACCOUNTS_BUTTON_XPATH = "/html/body/app-root/app-container/div/aside/ul/li[2]/a"
ACCOUNT_DETAILS_XPATH = "/html/body/app-root/app-container/div/div/app-main-account/page-loader/section/div[3]/a[1]/span"
STATMENT_BUTTON_XPATH = "/html/body/app-root/app-container/div/div/sbl-account/page-loader/div/sbl-saving-account/app-tabs/ul/li[3]/button"

SCRAPE_URL = os.getenv("SCRAPE_URL")
LOGIN_USERNAME = os.getenv("LOGIN_USERNAME")
LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD")

SLEEP_TIME = 1


def get_transaction_type_from_classes(class_list: list) -> str:
    if "table__title--success" in class_list:
        return "CREDIT"
    elif "table__title--error" in class_list:
        return "DEBIT"
    else:
        return None


def login(page, user_name, password):
    page.get_by_placeholder("Enter Mobile Number").fill(user_name)
    page.get_by_placeholder("Enter Password").fill(password)
    page.click("button[type=submit]")

    return page


def get_date_from_table_row(table_row):
    first_td_tag = table_row.find_all("td", class_="table__td")[0]
    date_parts = first_td_tag.get_text().split()[-3:]
    transaction_date = " ".join(date_parts)

    return transaction_date


def get_transaction_details_from_statement_table(table_elemets):
    for tr in table_elemets[1:]:
        transaction_title = tr.find(class_="table__title").text.strip()
        amount_target_element = tr.find(
            "span", class_=re.compile("table__title(--success|--error)")
        )
        transaction_amount = amount_target_element.text.strip()

        transaction_date = get_date_from_table_row(tr)

        element_classes = amount_target_element.get("class")

        transaction_type = get_transaction_type_from_classes(element_classes)

        print(transaction_title, transaction_amount, transaction_type, transaction_date)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        my_page = browser.new_page()

        my_page.goto(SCRAPE_URL)

        my_page = login(my_page, LOGIN_USERNAME, LOGIN_PASSWORD)
        time.sleep(SLEEP_TIME)

        my_page.locator(f"xpath={ACCOUNTS_BUTTON_XPATH}").click()
        time.sleep(SLEEP_TIME)

        my_page.locator(f"xpath={ACCOUNT_DETAILS_XPATH}").click()
        time.sleep(SLEEP_TIME)

        my_page.locator(f"xpath={STATMENT_BUTTON_XPATH}").click()
        time.sleep(SLEEP_TIME)

        html = my_page.content()
        soup = BeautifulSoup(html, "html.parser")

        tr_tags = soup.find_all("tr")

        get_transaction_details_from_statement_table(tr_tags)


if __name__ == "__main__":
    main()
