import sys
import subprocess
import io
import os
import uuid
import json

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QPlainTextEdit, QHBoxLayout, QGridLayout, QListWidgetItem, QListWidget, QToolButton, QLineEdit, QFormLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
import fitz  # PyMuPDF

import music_parser as prs
# import project_organiser as porg
from kassia_main import Kassia


absolute_path = os.path.dirname(__file__)


class ProjectView(QMainWindow):

    def __init__(
            self,
            score_ids = [],
            project_name = 'test'
        ):
        super().__init__()

        self.score_ids = score_ids
        self.score_writers = {}
        self.scores_metadata = {}
        self.score_buttons = {}
        self.score_button_widgets = {}

        self.setWindowTitle(f"Project: {project_name}")
        self.setGeometry(0, 0, 600, 700)


        self.new_score_button = QPushButton("Add Score")
        self.new_score_button.clicked.connect(self.start_new_score)

        self.scores_window = QListWidget()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scores_window)
        self.layout.addWidget(self.new_score_button)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(self.layout)


    def add_score_button(self, id): 

        with open(absolute_path + f'\\TEMP\\{id}\\config.json', 'r', encoding = 'utf-8') as f:
            score_metadata = json.load(f)

        score_title = score_metadata['Title']
        title_label = QListWidgetItem(score_title)
        self.scores_window.addItem(title_label)
        self.score_buttons[id] = title_label

        widget = QWidget(self.scores_window)

        move_up_button = QPushButton('<')
        move_up_button.clicked.connect(lambda: self.move_score(id, -1))
        move_down_button = QPushButton('>')
        move_down_button.clicked.connect(lambda: self.move_score(id, 1))

        open_button = QPushButton('Edit')
        open_button.clicked.connect(lambda: self.start_score_writer(score_id=id))

        delete_button = QPushButton('X')
        delete_button.clicked.connect(lambda: self.delete_score(score_id=id))

    
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        layout.addWidget(open_button)
        layout.addWidget(delete_button)
        layout.addWidget(move_up_button)
        layout.addWidget(move_down_button)
        self.scores_window.setItemWidget(title_label, widget)
        self.score_button_widgets[id] = widget

    def start_score_writer(self, score_id):
        self.score_writers[score_id] = ScoreWriter(score_id)
        self.score_writers[score_id].show()
        # self.score_writers[score_id].close_button.clicked.connect(self.save)

    def start_new_score(self):
        new_score_id = uuid.uuid4().hex
        self.score_ids.append(new_score_id)
        self.score_starter = ScoreSetup(new_score_id)
        self.score_starter.show()

        self.score_starter.create_button.clicked.connect(lambda: self.start_score_writer(new_score_id))
        self.score_starter.create_button.clicked.connect(lambda: self.add_score_button(new_score_id))

    def delete_score(self, score_id):
        item = self.score_buttons[score_id]
        # Get the row of the selected item
        row = self.scores_window.row(item)
        # Remove the item from the list
        self.scores_window.takeItem(row)

    def move_score(self, score_id, move_by: int):
        item = self.score_buttons[score_id]
        row = self.scores_window.row(item)
        # Take the current item
        currentItem = self.scores_window.takeItem(row)
        # currentWidget = self.scores_window.itemWidget(item)
        # self.scores_window.removeItemWidget(currentItem)

        currentWidget = self.score_button_widgets[score_id]

        print(type(currentWidget))
        
        # Insert the item at the new position
        self.scores_window.insertItem(row + move_by, currentItem)

        currentItem = self.scores_window.item(row+move_by)
        self.scores_window.setItemWidget(currentItem, currentWidget)
        
    

    def save_project(self, filename):

        output = {}


        scores = []
        for id in self.score_ids:
            
            score_path = absolute_path+f'\\TEMP\\{id}'

            with open(score_path+'\\config.json', 'r', encoding = 'utf-8') as f:
                score = json.load(f)

            if os.path.exists(score_path + '\\raw_music.txt'):
                with open(score_path + '\\raw_music.txt', 'r', encoding="utf-8") as f:
                    raw_music = f.read()
            else:
                raw_music = ''

            score['raw_music'] = raw_music

            scores.append(score)

        output['scores'] = scores 

        with open(filename, 'w') as f:
            json.dump(output, f, indent = 6)

            

class ScoreSetup(QWidget):

    def __init__(self, score_id):
        super().__init__()

        self.setWindowTitle(f"Create New Score")
        self.setGeometry(0, 0, 200, 300)

        self.score_id = score_id

        labels = [
            'Title',
            'Author'
        ]

        self.layout = QVBoxLayout()

        self.label_inputs = {}

        self.form = QFormLayout()
        for l in labels:
            label_input = QLineEdit()
            self.form.addRow(l+':', label_input)
            self.label_inputs[l] = label_input
        self.layout.addLayout(self.form)

        self.create_button = QPushButton("Create")
        self.create_button.clicked.connect(self.submitForm)
        self.layout.addWidget(self.create_button)

        self.setLayout(self.layout)

    def submitForm(self):

        results = {l: l_in.text() for l, l_in in self.label_inputs.items()}
        results['id'] = self.score_id
        score_dir = absolute_path + f'\\TEMP\\{self.score_id}'
        os.makedirs(score_dir)

        with open(score_dir + '\\config.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, indent = 6)

        self.close()


class ScoreWriter(QWidget):

    def __init__(
            self,
            score_id = None
            ):
        super().__init__()

        if score_id is None:
            score_id = uuid.uuid4()

        self.score_id = score_id
        
        score_path = absolute_path+f'\\TEMP\\{score_id}'
        self.score_path = score_path

        with open(self.score_path+'\\config.json', 'r', encoding = 'utf-8') as f:
            self.metadata = json.load(f)

        if os.path.exists(self.score_path + '\\raw_music.txt'):
            with open(self.score_path + '\\raw_music.txt', 'r', encoding="utf-8") as f:
                raw_music = f.read()
            self.raw_music = raw_music

        else:
            # os.makedirs(score_path)
            self.raw_music = None
        
        self.music = None

        headerfile = absolute_path + '\\headers\\psaltoglas1.xml'
        with open(headerfile, 'r', encoding = 'utf-8') as f:
            self.header = f.read()

        self.setWindowTitle(f"Score Writer - {self.metadata['Title']}")
        self.setGeometry(0, 0, 600, 700)

        self.pdf = None

        self.input = QPlainTextEdit()
        if self.raw_music:
            self.input.setPlainText(self.raw_music)

        self.preview_button = QPushButton('Preview')
        self.preview_button.clicked.connect(self.update)

        self.close_button = QPushButton('Save & Close')
        self.close_button.clicked.connect(self.save_close)


        self.layout = QVBoxLayout()
        self.layout.addWidget(self.input)

        self.buttons = QGridLayout()
        self.buttons.addWidget(self.preview_button)
        self.buttons.addWidget(self.close_button)

        self.layout.addWidget(self.preview_button)
        self.layout.addLayout(self.buttons)
        
        self.setLayout(self.layout)

    def update_cache(self):
        self.raw_music = self.input.toPlainText()
    
    def popup_pdf(self, filename):
        self.pdf = PDFViewer(filename)
        self.pdf.show()

    def render_score(self, cache_pdf_file = 'ttt.pdf', cache_xml_file = 'tt.xml'):

        cache_pdf_path = f"{self.score_path}\\{cache_pdf_file}"
        cache_xml_path = f"{self.score_path}\\{cache_xml_file}"

        self.music = prs.music_from_txt(self.raw_music, self.header)
        self.music.write_to_file(cache_xml_path)
        kassia = Kassia(cache_xml_path, cache_pdf_path)

        self.popup_pdf(cache_pdf_path)

    def update(self):
        self.update_cache()
        if self.raw_music:
            self.render_score()

    # def clear_layout(self, layout):
    #     for i in reversed(range(layout.count())):
    #         widget = layout.itemAt(i).widget()
    #         if widget is not None:
    #             widget.deleteLater()

    def save_close(self):
        if not self.raw_music:
            self.raw_music=''
        with open(self.score_path + '\\raw_music.txt', 'w', encoding="utf-8") as f:
            f.write(self.raw_music)
        self.close()


class PDFViewer(QMainWindow):
    def __init__(self, filename):
        super().__init__()

        self.setWindowTitle("PDF Viewer")
        self.setGeometry(500, 30, 600, 700)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        # Load PDF file
        self.doc = fitz.open(filename)

        # Display first page
        self.display_page(self.doc.page_count-1)

    def display_page(self, page_num):
        page = self.doc.load_page(page_num)
        pix = page.get_pixmap()
        image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)

        # Create label to display the page
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignCenter)

        # Clear layout and add the label
        self.clear_layout()
        self.layout.addWidget(label)

    def clear_layout(self):
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ProjectView()
    win.show()
    # viewer = PDFViewer()
    # viewer.show()
    sys.exit(app.exec_())
