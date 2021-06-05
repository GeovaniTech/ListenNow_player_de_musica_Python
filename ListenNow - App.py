from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.Qt import Qt
from View.PY.ui_ListenNow import Ui_ListenNow
import sys


class FrmPrincipal(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        self.ui = Ui_ListenNow()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        self.ui.btn_home.clicked.connect(self.btn_home_clicked)
        self.ui.btn_download.clicked.connect(self.btn_donwloader_clicked)
        self.ui.btn_remover.clicked.connect(self.btn_remover_musicas_clicked)

    def btn_home_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)

    def btn_playlist_clicked(self):
        print('Playlist')

    def btn_adicionar_musicas_clicked(self):
        print('Adicionar Músicas')

    def btn_remover_musicas_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.remover_musicas)

    def btn_donwloader_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.downloader)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FrmPrincipal()
    window.show()
    sys.exit(app.exec())