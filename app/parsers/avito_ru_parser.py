import requests
from bs4 import BeautifulSoup
from app.parsers.parser_error import ParserError
from PyQt5.QtCore import pyqtSignal


class AvitoRuParser(object):
    """Parser class for Avito.ru website.

    Attributes:
        progress_updated (pyqtSignal): Signal emitted to update progress.
        finished (pyqtSignal): Signal emitted when parsing is finished.
    """
    progress_updated = pyqtSignal(str, int)
    finished = pyqtSignal()

    def __init__(self) -> None:
        """Initialize the parser."""
        super().__init__()
        self.__url = "https://www.avito.ru"
        self.__headers = {"User-Agent": "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, "
                                        "like Gecko) Mobile/15E148"}
        self.job = ""
        self.__total_pages = 1
        self.count = None

    def get_soup(self, url: str) -> BeautifulSoup:
        """Get BeautifulSoup object from the given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            BeautifulSoup: The BeautifulSoup object.

        Raises:
            ParserError: If an error occurs during request or parsing.
        """
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

    def get_job_num(self, job: str = "") -> str:
        pass

    def get_total_pages(self, page: BeautifulSoup) -> int:
        pass

    def run_parse(self) -> None:
        pass

    def parse_job(self, url: str) -> dict:
        pass

    def get_value(self, span: BeautifulSoup) -> str:
        pass
