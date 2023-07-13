import time
from urllib.parse import quote
import logging
from pdfdocument.document import PDFDocument
from poetry.console.commands import self
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
from src.config import driver_path

from unidecode import unidecode


def initialize_driver():
    # Configure Selenium
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)
    return driver


def remove_accents(text):
    # Utilize the unidecode function to remove accents
    text_without_accents = unidecode(text)
    return text_without_accents


def get_themes(driver):
    # Load the page with Selenium
    url = "https://particuliers.sg.fr/icd/pch/faq/"
    driver.get(url)

    # Wait for the "continue without accepting" button to be present
    continue_button = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="popin_tc_privacy_button_2"]'))
    )

    # Click the "continue without accepting" button
    continue_button.click()

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Select the buttons for each theme
    theme_buttons = soup.find_all('button', class_='stl_btn')

    # Create a list to store the themes
    themes_list = []

    # Extract the titles of the themes and add them to the list
    for button in theme_buttons:
        theme_title = button.find('span').text.strip()
        themes_list.append(theme_title)

    # Return the list of themes
    return themes_list


def get_sub_themes(driver, theme):
    url = generate_url(theme)
    driver.get(url)
    time.sleep(30)
    sub_theme_elements = driver.find_elements(By.XPATH,
                                              '//*[@id="sdcWrapper"]/div/div[2]/div/div[2]/div/div[2]/div/div/ul')
    if not sub_theme_elements:
        return []  # Return an empty list if no sub-themes found

    sub_themes = sub_theme_elements[0].text.split('\n')

    return sub_themes


def generate_url(theme, sub_theme=None):
    base_url = "https://particuliers.sg.fr/icd/pch/faq/"
    theme_url = quote(remove_accents(theme).lower().replace(' ', '-'))

    if sub_theme:
        sub_theme_url = quote(sub_theme.lower().replace(' ', '-'))
        url = f"{base_url}{theme_url}/{sub_theme_url}"
    else:
        url = f"{base_url}{theme_url}"

    return url


def get_questions_and_answers(driver, theme, sub_theme=None):
    url = generate_url(theme, sub_theme)
    driver.get(url)
    time.sleep(30)
    qa_cells = driver.find_elements(By.CSS_SELECTOR, '.faq_questions__cell')

    questions_and_answers = []

    for qa_cell in qa_cells:
        question_element = qa_cell.find_element(By.CSS_SELECTOR,
                                                'a.faq_questions__link')
        question = question_element.text.strip()

        answer_element = qa_cell.find_element(By.CSS_SELECTOR,
                                              'span.faq_questions__short--description')
        answer = answer_element.text.strip()

        questions_and_answers.append({"question": question, "answer": answer})

    return questions_and_answers


def main():
    logging.basicConfig(level=logging.INFO)

    driver = initialize_driver()

    try:
        themes = get_themes(driver)
        logging.info("Themes:")
        logging.info(themes)

        theme_subthemes = {}

        for theme in themes:
            sub_themes = get_sub_themes(driver, theme)
            logging.info(f"Sub-themes for {theme}: {sub_themes}")
            theme = remove_accents(theme)
            sub_themes = [remove_accents(sub_theme) for sub_theme in sub_themes]
            theme_subthemes[theme] = sub_themes

        # Save theme and sub-theme data to a JSON file
        with open("../data/raw_data/theme_subthemes.json", "w") as json_file:
            json.dump(theme_subthemes, json_file, indent=4)

        driver.quit()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        driver.quit()


if __name__ == "__main__":
    main()
