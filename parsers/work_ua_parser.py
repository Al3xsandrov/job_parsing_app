import re
import os
import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup
from parsers.parser_error import ParserError
from PyQt5.QtCore import QObject, pyqtSignal


class WorkUaParser(QObject):
    progress_updated = pyqtSignal(str, int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.__url = "https://www.work.ua"
        self.__headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
                                        "like Gecko) Mobile/15E148"}
        self.job = ""
        self.__total_pages = 1
        self.count = None

    def get_soup(self, url):
        try:
            req = requests.get(url, headers=self.__headers)
            req.raise_for_status()
            page = req.text
            soup = BeautifulSoup(page, 'lxml')
            return soup
        except requests.exceptions.RequestException as e:
            raise ParserError("An error occurred while executing the request: " + str(e)) from e
        except Exception as e:
            raise ParserError("An unforeseen error occurred: " + str(e))

    def get_job_num(self, job=""):
        if job != "":
            self.job = job
            url = f"{self.__url}/jobs-{self.job.replace(' ', '+')}/"
        else:
            return "Select jobs"

        soup = self.get_soup(url)
        div = soup.select_one("div[class='card']")

        try:
            children = div.find_all()
        except Exception:
            raise ParserError("There are no vacancies for your request yet.")
        else:
            self.__total_pages = self.get_total_pages(soup)

            # Number of vacancies found on request.
            count = re.findall(r"\d+", children[2].text.strip())
            self.count = int(count[0])

            return children[2].text.strip()

    def get_total_pages(self, page):
        pages = page.find("ul", class_="pagination hidden-xs")

        if pages:
            num = pages.find_all("li")[-2].text
            return int(num)
        else:
            return 1

    def run_parse(self):
        job_list = []
        i = 0

        for page_number in range(1, self.__total_pages + 1):
            url = f"{self.__url}/jobs-{self.job.replace(' ', '+')}/?page={page_number}"
            soup = self.get_soup(url)
            jobs = soup.find_all("div", class_="card card-hover card-visited wordwrap job-link")
            for job in jobs:

                url = self.__url + job.find("a").get("href")
                data = self.parse_job(url)

                if data is not None:
                    progress = int((i + 1) * 100 / self.count)
                    i += 1
                    self.progress_updated.emit(f"{data['url']} parsed!", progress)

                    job_list.append(data)

                time.sleep(random.randrange(0, 2))

        timestr = time.strftime("%Y%m%d-%H%M%S")
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_name = f"{self.job}-{timestr}.xlsx"
        file_path = os.path.join(desktop_path, file_name)
        pd.DataFrame(job_list).to_excel(file_path)
        self.progress_updated.emit(f"File '{file_name}' is saved on the desktop.", progress)
        self.finished.emit()

    def parse_job(self, url):
        try:
            soup = self.get_soup(url)
            name = soup.find('h1', class_='add-top-sm', id='h1-name').get_text()
            salary = self.get_value(soup.find('span', title='Зарплата'))
            company = self.get_value(soup.find('span', title='Дані про компанію'))
            address_span = soup.find('span', title='Адреса роботи')
            if address_span is not None:
                address = address_span.next_sibling.text.strip()
            else:
                remote_span = soup.find('span', title='Місце роботи')
                if remote_span is not None:
                    address = remote_span.parent.text.strip()
                else:
                    address = '~~~'
            terms = soup.find('span', title='Умови й вимоги').parent.get_text().strip()
            description = soup.find('div', id='job-description').get_text()

            return {
                'url': url,
                'name': name,
                'salary': salary,
                'company': company,
                'address': address,
                'terms': terms,
                'description': description,
            }
        except Exception as e:
            raise ParserError("An error occurred while parsing the jobs: " + str(e))

    def get_value(self, span):
        if span is not None:
            result = span.find_next_sibling().get_text()
        else:
            result = "~~~"

        return result