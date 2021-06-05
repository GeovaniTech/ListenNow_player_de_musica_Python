from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *
from PyQt5.Qt import Qt
from View.PY.ui_ListenNow import Ui_ListenNow
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import Tk

import mysql.connector
import pygame
import sys

# Configurando Banco
banco = mysql.connector.connect(
    host='localhost',
    port='3307',
    user='root',
    passwd='',
    database='banco_musicas'
)

if banco.is_connected():
    banco_info = banco.get_server_info()
    print('Conexão com o banco realizada com sucesso!')
    print(banco_info)
    cursor = banco.cursor()
    cursor.execute('SELECT database();')
    linha = cursor.fetchone()

    for nome_banco in linha:
        print(f'Conectado ao {nome_banco}')

    cursor.execute('SELECT nome FROM musicas_app')
    banco_musicas = cursor.fetchall()


class FrmPrincipal(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        pygame.init()
        pygame.mixer.init()

        self.ui = Ui_ListenNow()
        self.ui.setupUi(self)

        self.ui.stackedWidget.setCurrentWidget(self.ui.home)
        sld = self.ui.volume_slider
        sld.setRange(0, 9)
        sld.setValue(1)
        sld.valueChanged.connect(self.volume)
        # Clique dos botões
        self.ui.btn_home.clicked.connect(self.btn_home_clicked)
        self.ui.btn_download.clicked.connect(self.btn_donwloader_clicked)
        self.ui.btn_remover.clicked.connect(self.btn_remover_musicas_clicked)
        self.ui.btn_adicionar.clicked.connect(self.btn_adicionar_musicas_clicked)
        self.ui.btn_pausar_play.clicked.connect(self.tocar_musica)
        self.ui.btn_avancar.clicked.connect(self.passar_musica)
        self.ui.btn_voltar.clicked.connect(self.voltar_musica)

    def tocar_musica(self):

        global clique_pause_despause
        global banco_musicas

        # Verificando se o botão pause/despause é maior que 0
        if clique_pause_despause > 0:
            clique_pause_despause += 1

        # Verificando se botão pause/despause é igual a 0 e se o total de músicas na lista é maior ou igual a 1
        if len(banco_musicas) >= 1 and clique_pause_despause == 0:
            global id_musica
            clique_pause_despause += 1

            # Tocando a primeira música do banco
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.load(banco_musicas[0][0])
            pygame.mixer.music.play()

        # Verificando se o botão pause/despause é maior ou igual a 1
        if clique_pause_despause >= 1:

            # Pausando a Música
            if clique_pause_despause % 2 == 0:
                pygame.mixer.music.pause()

            # Despausando a Música
            else:
                pygame.mixer.music.unpause()

    def volume(self, value):
        # Ajustando o volume da música
        volume = f"{0}.{value}"
        pygame.mixer.music.set_volume(float(volume))

    def btn_home_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.home)

    def btn_playlist_clicked(self):
        print('Playlist')

    def btn_adicionar_musicas_clicked(self):

        global banco_musicas

        Tk().withdraw()
        filename = askopenfilenames()

        # Pegando o id, diretório da música e fazendo validações
        for id, musica in enumerate(filename):
            if musica[-4:] == '.mp3':
                try:
                    # Verificando se a música já está no banco de dados
                    cursor.execute(f'SELECT nome FROM musicas_app WHERE nome ="{musica}"')
                    ok = cursor.fetchall()
                    print(ok[0][0])
                    print(f'Música já está no Banco de Dados!')

                except:
                    # Adicionando música ao banco de dados
                    print('Adicionando música ao banco!')
                    comando_SQL = 'INSERT INTO musicas_app (id, nome) VALUES (%s,%s)'
                    dados = (f"{id}", f"{musica}")
                    cursor.execute(comando_SQL, dados)
                    banco.commit()

        # Atualizando o banco_musicas
        cursor.execute('SELECT nome FROM musicas_app')
        banco_musicas = cursor.fetchall()

    def btn_remover_musicas_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.remover_musicas)

    def btn_donwloader_clicked(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.downloader)

    def passar_musica(self):
        global id_musica
        global banco_musicas
        global clique_pause_despause

        if clique_pause_despause > 0 and len(banco_musicas) > 1:

            # Verificando se chegou na última música da lista
            if id_musica == len(banco_musicas) - 1:

                # Resetando id para 0
                id_musica -= len(banco_musicas) - 1
                pygame.mixer.music.load(banco_musicas[id_musica][0])
                pygame.mixer.music.play()

            else:
                # Adicionando mais um valor ao id, para tocar a próxima música da lista
                id_musica += 1
                pygame.mixer.music.load(banco_musicas[id_musica][0])
                pygame.mixer.music.play()

    def voltar_musica(self):

        # Pagando a variável global com o id da musica e o banco de dados
        global id_musica
        global banco_musicas

        # Verificando se id da música é maior ou igual a 1, para assim tirar um valor do id
        if id_musica >= 1:
            id_musica -= 1
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()


if __name__ == '__main__':

    # Variáveis do Sistema
    clique_pause_despause = 0
    id_musica = 0

    # Configuração do Sistema
    app = QApplication(sys.argv)
    window = FrmPrincipal()
    window.show()
    sys.exit(app.exec())