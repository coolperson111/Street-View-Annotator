# Main file to run the entire ap

from PyQt5 import QtWidgets

from ui.gui import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow(28.584968416777624, 77.19327373966009) # delhi road - bhavi suggestion

    offset = 20
    window.setGeometry(0 + offset, 20 + offset, 1300 + offset, 900 + offset)
    window.show()
    app.exec_()
