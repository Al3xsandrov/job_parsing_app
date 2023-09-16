import os
import sys
import importlib
from MainWindow import Ui_MainWindow
from parsers.parser_error import ParserError
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QPushButton, \
     QLineEdit, QTextBrowser, QProgressBar


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.parser_instance = None
        self.job = None

        self.combo_box = self.findChild(QComboBox, "get_parser")
        self.check_btn = self.findChild(QPushButton, "check_btn")
        self.parse_btn = self.findChild(QPushButton, "parse_btn")
        self.text_browser = self.findChild(QTextBrowser, "textBrowser")
        self.progress_bar = self.findChild(QProgressBar, "progressBar")
        self.input = self.findChild(QLineEdit, "input")
        self.init_combo_box()

        self.check_btn.clicked.connect(self.check)
        self.parse_btn.clicked.connect(self.parse)
        self.text_browser.setText("Hello!!\nChoose a parser and let's get started.")

    def init_combo_box(self):
        self.combo_box.addItem("")
        parser_classes = self.get_parser_classes()
        self.combo_box.addItems(parser_classes)
        self.combo_box.currentIndexChanged.connect(self.on_combo_box_changed)

    def on_combo_box_changed(self):
        selected_item = self.sender().currentText()
        if selected_item != "":
            parser_module = importlib.import_module(f"parsers.{selected_item}")
            class_name = "".join(word.capitalize() for word in selected_item.split("_"))
            parser_class = getattr(parser_module, class_name)

            try:
                self.parser_instance = parser_class()
                self.parser_instance.progress_updated.connect(self.update_progress)
                self.parser_instance.finished.connect(self.parsing_finished)
            except Exception:
                self.handle_error("Parser loading issues...")
                return None

            self.thread = QThread()
            self.parser_instance.moveToThread(self.thread)
            self.thread.started.connect(self.parser_instance.run_parse)

            self.input.textChanged.connect(self.handle_text_changed)
            self.input.setEnabled(True)
            self.input.setFocus()
            self.text_browser.append("Enter the query on the line above.")

            return None

        self.input.setEnabled(False)
        self.set_btns_status(False, False)

    def get_parser_classes(self):
        parser_classes = []

        for file_name in os.listdir("parsers"):
            if file_name.endswith("parser.py"):
                name = file_name[:-3]
                parser_classes.append(name)

        return parser_classes

    def handle_text_changed(self):
        if self.input.text() == "":
            self.set_btns_status(False, False)
        else:
            self.set_btns_status(True, False)

    def check(self):
        text = self.input.text()
        for char in "-/":
            text = text.replace(char, "")
        try:
            msg = self.parser_instance.get_job_num(text)
            self.text_browser.append(msg)
            self.set_btns_status(True, True)
        except ParserError as e:
            self.handle_error(e)

    def parse(self):
        try:
            self.set_btns_status(False, False)
            self.progress_bar.setValue(0)
            self.text_browser.append("It will take some time. Please wait...")
            self.thread.start()
        except ParserError as e:
            self.handle_error(e)

    def update_progress(self, url, progress):
        self.text_browser.append(url)
        self.progress_bar.setValue(progress)

    def parsing_finished(self):
        self.thread.quit()
        self.thread.wait()
        self.text_browser.append("Done!")
        self.set_btns_status(True, True)
        self.progress_bar.setValue(0)

    def set_btns_status(self, check: bool, parse: bool):
        self.check_btn.setEnabled(check)
        self.parse_btn.setEnabled(parse)

    def handle_error(self, error):
        self.text_browser.append(str(error))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
