from dataclasses import dataclass
from pathlib import Path

URL = 'https://particuliers.sg.fr/icd/pch/faq/'

driver_path: str = "../ressources/chromedriver.exe"
patterns = [
    r'</a><br/>',
    r'</a>',
    r'<a href="',
    r'<br/> -',
    r'<br/><br/>',
    r'!<br/><br/>',
    r'!<br/>',
    r'<strong>',
    r'<br/>',
    r'</strong>',
    r': <br/>-',
    r'">'
]


@dataclass
class Paths:
    filename: str = "../data/raw_data/thematique.json"
    save_questions_datas: str = "data/raw_data/save_questions_datas.pdf"
    driver_path: str = "../ressources/chromedriver.exe"
    base_url = "https://particuliers.sg.fr/icd/pch/data/faq/sous-thematique-knowledges-public.json?cl2000_sousThematique="

    def __post_init__(self):
        self.base_path = "../data"
        self.data_source = Path(self.base_path) / "raw_data"
        self.source_data = list(self.data_source.glob(self.filename))
