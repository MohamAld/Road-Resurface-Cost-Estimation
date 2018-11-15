import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from area import process
import sys, time, os

from styleSheets import *

import time

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.results = []
        self.bounds = ""
        self.query_area = 0
        self.js_request = ""
        self.price = 1
        self.center = [0, 0]
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.javascriptready = False
        self.form_widget = AreaPage(self)

        self.form_widget.getboundsbutton.clicked.connect(self.get_bounds)

        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.central_widget.addWidget(_widget)
        self.setStyleSheet("QMainWindow {background: '#89AECB';}")

    def get_bounds(self):
        self.form_widget.browser.page().runJavaScript("get_center()", self.update_center)
        self.form_widget.browser.page().runJavaScript("bounds_f()", self._get_bounds)

    def update_center(self, string):
        self.center = string.split(",")
        self.center[0] = float(self.center[0])
        self.center[1] = float(self.center[1])
        self.query_area = float(self.center[2])
        self.price = float(self.center[3])

    def _get_bounds(self, bounds):
        print(bounds)
        # Areas over 1km^2 take longer
        if self.query_area > 1200000:
            msgBox  =  QMessageBox
            res = msgBox.question(self, 'Confirmation', "Are you sure you wish to query this area? Areas over 1km^2 may take longer to process", msgBox.No|msgBox.Yes)
            if res == msgBox.No:
                return

        if self.price <= 0:
            msgBox = QMessageBox
            res = msgBox.warning(self, "Invalid Price", "Error: Price can not be zero or negative!", msgBox.Ok)
            if res == msgBox.Ok:
                return

        time1 = time.time()
        namearea_array = process(bounds)
        self.show_results(namearea_array, bounds)
        time2 = time.time()
        print("Time taken: " + str(time2 - time1))
    def show_results(self, results, bounds):
        '''
        Outputs the results in an elegant way to the frontend
        :param results: results[0] contains the names, results[1] contains the areas
        Both arrays are pre-processed.
        '''
        self.results_widget = ResultsWidget(self)

        self.central_widget.addWidget(self.results_widget)
        self.central_widget.setCurrentWidget(self.results_widget)
        self.results_widget.button.clicked.connect(self.go_back)
        self.results_widget.button2.clicked.connect(self.save_data)



        for i in range(len(results[1])):
            results[1][i] = float("{0:.2f}".format(results[1][i]))

        self.results = results
        self.bounds = bounds
        self.js_request = "display_data("+str(results[0])+","+str(results[1])+",["+str(bounds)+"]," + str(self.center) + "," + str(self.price) + ")"
        self.setStyleSheet("QMainWindow {background: '#000000';}")
        self.results_widget.browser2.page().runJavaScript(self.js_request, self.check)




    def go_back(self):
        self.central_widget.addWidget(self.form_widget)
        self.central_widget.setCurrentWidget(self.form_widget)
        self.setStyleSheet("QMainWindow {background: '#89AECB';}")

    def save_data(self):
        name = QFileDialog.getSaveFileUrl(self, 'Save File')
        if not (name[0].toString()):
            return
        f = open(name[0].toString()[8:], 'w')
        f.write("Bounds queried: " + self.bounds + "\n\n")
        f.write("Road Name\t\t\t\t\tArea")
        for i in range(len(self.results[0])):
            f.write("\n" + self.results[0][i]+ "\t\t\t\t" + str(self.results[1][i]))
        f.close()

    def check(self,result):
        #print("Called: "+str(result))
        if result != "DONE":
            self.results_widget.browser2.page().runJavaScript(self.js_request, self.check)


class AreaPage(QWidget):
    def __init__(self, parent):
        self.callback = parent
        super(AreaPage, self).__init__(parent)
        self.__controls()
        self.__layout()

    def __controls(self):
        self.browser = QWebEngineView()


        self.browser.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]+r'\html\index.html'))

    def __layout(self):
        self.vbox = QVBoxLayout()
        self.hBox = QVBoxLayout()
        self.getboundsbutton = QPushButton()

        self.getboundsbutton.setText("Calculate Quote")
        self.getboundsbutton.setStyleSheet(qPushButton_style)
        self.mapbbox = QTextEdit()
        self.mapbbox.setReadOnly(True)
        self.mapbbox.setStyleSheet(output_sheet)
        self.mapbbox.setFixedHeight(200)
        self.hBox.addWidget(self.browser)
        self.hBox.addWidget(self.getboundsbutton)
       # self.hBox.addWidget(self.mapbbox)
        self.vbox.addLayout(self.hBox)
        self.setLayout(self.vbox)


    def updateBounds(self):
        # self.browser.page().runJavaScript("bounds_f()", self.getBounds)
        self.parent().showResults()
        #browser2.page().runJavaScript("update_results([\"road1\", \"road2\"],[60000, 50000])", print)

    def update_bbox(self, output):
        self.mapbbox.setText(output)

    """
    bounds_f(){
        dsd

    }
    """

       #  self.browser.page().runJavascript("bounds_f()", print)

    def getBounds(self, bounds):
        self.mapbbox.setText(str(bounds))
        self.bounds = bounds

        process(self.bounds, self)


class ResultsWidget(QWidget):
    def __init__(self, parent):
        super(ResultsWidget, self).__init__(parent)
        self.__layout()

    def __layout(self):
        self.vbox2=QVBoxLayout()
        self.hBox2=QHBoxLayout()
        self.browser2=QWebEngineView()
        self.browser2.load(QUrl().fromLocalFile(os.path.split(os.path.abspath(__file__))[0]+r'\html\results.html'))

        self.button = QPushButton()
        self.button.setText("<Back")
        self.button.setStyleSheet(backbutton_style)
        self.button.setFixedHeight(32)
        self.button.setFixedWidth(96)

        self.button2 = QPushButton()
        self.button2.setText("Save")
        self.button2.setFixedHeight(32)
        self.button2.setFixedWidth(96)
        self.button2.setStyleSheet(backbutton_style)
        self.hBox2.setSpacing(0)
        self.hBox2.setContentsMargins(0, 0, 0, 0)


        self.hBox2.addWidget(self.button)
        self.hBox2.addWidget(self.button2)

        self.vbox2.addLayout(self.hBox2)
        self.vbox2.addWidget(self.browser2)

        self.setLayout(self.vbox2)



def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.setWindowTitle("Road Resurface")
    win.show()

    app.exec_()

sys._excepthook = sys.excepthook

def exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)
sys.excepthook = exception_hook

from unit_tests import MyTestCase

if __name__ == '__main__':
    test = MyTestCase().test_something()
    print("All tests passed!")
    sys.exit(main())


