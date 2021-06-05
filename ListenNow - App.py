from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from View.PY.ui_ListenNow import Ui_ListenNow
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import Tk

import mysql.connector
import pygame
import sys
import os
import eyed3
import youtube_dl
import shutil

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
    #cursor.execute('DELETE FROM musicas_app')
    #banco.commit()

class FrmPrincipal(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        pygame.init()
        pygame.mixer.init()

        self.ui = Ui_ListenNow()
        self.ui.setupUi(self)

        self.btn_home_clicked()
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
            self.nome_musica_artista()

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
        global banco_musicas

        if len(banco_musicas) > 0:
            self.ui.stackedWidget.setCurrentWidget(self.ui.musicas)
        else:
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
                    print(musica)

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
        self.ui.btn_baixar.clicked.connect(self.download)
        self.ui.btn_baixar_2.clicked.connect(self.diretorio_download)

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
                self.nome_musica_artista()
            else:
                # Adicionando mais um valor ao id, para tocar a próxima música da lista
                id_musica += 1
                pygame.mixer.music.load(banco_musicas[id_musica][0])
                pygame.mixer.music.play()
                self.nome_musica_artista()

    def voltar_musica(self):

        # Pagando a variável global com o id da musica e o banco de dados
        global id_musica
        global banco_musicas

        # Verificando se id da música é maior ou igual a 1, para assim tirar um valor do id
        if id_musica >= 1:
            id_musica -= 1
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()
            self.nome_musica_artista()

    def nome_musica_artista(self):
        self.ui.lbl_nome_musica.setText(os.path.basename(banco_musicas[id_musica][0][:-4]))
        audiofile = eyed3.load(banco_musicas[id_musica][0])

        if audiofile.tag.artist is None:
            self.ui.lbl_nome_artista.setText('Artista não encontrado')
        else:
            self.ui.lbl_nome_artista.setText(audiofile.tag.artist)

    def download(self):
        global diretorio

        if diretorio != '' and self.ui.line_link != '':
            link = self.ui.line_link.text()
            try:
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([f'{link}'])

            except:
                print('sfs')
        pasta_atual = os.path.dirname(os.path.realpath(__file__))
        files = []
        for (dirpath, dirnames, filenames) in os.walk(pasta_atual):
            files.extend(filenames)
            break

        for arquivo in files:

            musica = str(arquivo)

            if musica[-5:] == '.webm':
                conversao = musica.replace('.webm', '.mp3')
                os.rename(musica, conversao)
            if musica[-4:] == '.m4a':
                conversao = musica.replace('.m4a', '.mp3')
                os.rename(musica, conversao)

        files.clear()
        pasta_atual = os.path.dirname(os.path.realpath(__file__))
        for (dirpath, dirnames, filenames) in os.walk(pasta_atual):
            files.extend(filenames)
            break

        for arquivo in files:
            if arquivo[-4:] == '.mp3':
                shutil.move(arquivo, diretorio)

    def diretorio_download(self):

        global diretorio

        Tk().withdraw()
        diretorio = askdirectory()
        print(diretorio)


if __name__ == '__main__':

    # Variáveis do Sistema
    clique_pause_despause = 0
    id_musica = 0
    diretorio = ''
    # Configuração do Sistema
    app = QApplication(sys.argv)
    window = FrmPrincipal()
    window.show()
    sys.exit(app.exec())