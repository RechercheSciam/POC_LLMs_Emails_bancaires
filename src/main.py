import logging
import json
import re
from urllib.parse import quote

import requests
from unidecode import unidecode
import bleach
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from config import patterns, Paths


class DataLLMsEB:
    def __init__(self):
        self.questions_and_answers = []
        self.patterns = patterns
        self.path = Paths()

    def remove_accents(self, text):
        # Utilize the unidecode function to remove accents
        text_without_accents = unidecode(text)
        return text_without_accents

    def clean_description(self, description):
        # Define the patterns to match
        patterns = self.patterns

        # Replace the patterns with empty strings
        for pattern in patterns:
            description = re.sub(pattern, '', description)

        return description

    def get_questions_and_answers(self, sub_theme_url):
        response = requests.get(sub_theme_url)
        data = json.loads(response.text)
        for item in data["donnees"]:
            question = item["labels"][0]["value"]
            description = item["descriptions"][0]["description"]
            description = self.clean_description(description)
            print("Question:", question)
            print("Description:", description)
            print()
            self.questions_and_answers.append(
                {"question": question, "answer": description}
            )

    def read_thematique(self):
        try:
            with open(self.path.filename, "r", encoding="utf-8") as file:
                data = json.load(file)

                for theme, sub_themes in data.items():
                    logging.info(f"Theme: {theme}")
                    logging.info(f"Sub-themes: {sub_themes}")
                    base_url = self.path.base_url
                    if sub_themes:
                        for sub_theme in sub_themes:
                            sub_theme_url = quote(
                                self.remove_accents(sub_theme)
                                .lower()
                                .replace(" ", "-")
                                .replace("'", "")
                            )
                            url = f"{base_url}{sub_theme_url}"
                            logging.info(url)
                            self.get_questions_and_answers(url)
                    else:
                        url = None
                        logging.info(url)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def sanitize_content(self, content):
        # Remove HTML tags and keep only plain text
        sanitized_content = bleach.clean(content, tags=[], strip=True)
        return sanitized_content

    def save_to_pdf(self):
        doc = SimpleDocTemplate(self.path.save_questions_datas, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add a title to the document
        title = Paragraph("<b>SG FAQ Questions</b>", styles["Title"])
        story.append(title)
        story.append(Spacer(1, 12))

        # Add the questions and answers to the document
        for qa in self.questions_and_answers:
            question = Paragraph(qa["question"], styles["Heading2"])
            answer = Paragraph(
                self.sanitize_content(qa["answer"]), styles["BodyText"]
            )
            story.append(question)
            story.append(answer)
            story.append(Spacer(1, 12))

        # Build the document and save it to the PDF file
        doc.build(story)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_llms_eb = DataLLMsEB()
    data_llms_eb.read_thematique()
    data_llms_eb.save_to_pdf()
