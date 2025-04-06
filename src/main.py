# Main file to run the entire ap

from PyQt5 import QtWidgets

from ui.gui import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow(30.71097990326242, 76.8009197345154) # v3 road sec 28/29

    offset = 20
    window.setGeometry(0 + offset, 20 + offset, 1300 + offset, 900 + offset)
    window.show()
    app.exec_()
