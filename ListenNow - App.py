import mysql.connector
import pygame
import sys
import os
import eyed3.utils
import youtube_dl
import shutil

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from View.PY.ui_ListenNow import Ui_ListenNow
from tkinter.filedialog import askopenfilenames, askdirectory
from tkinter import Tk

# Configurando Banco
banco = mysql.connector.connect(
    host='192.168.15.2',
    port='3307',
    user='',
    passwd='geovani5280',
    database='banco_musicas'
)

# Verificando conexão com o banco
if banco.is_connected():
    banco_info = banco.get_server_info()
    print('Conexão com o banco realizada com sucesso!')
    print(banco_info)
    cursor = banco.cursor()
    cursor.execute('SELECT database();')
    linha = cursor.fetchone()

    for nome_banco in linha:
        print(f'Conectado ao {nome_banco}')

    # Pegando as músicas do banco
    cursor.execute('SELECT * FROM musicas_app ORDER BY id ASC')
    banco_musicas = cursor.fetchall()


class FrmPrincipal(QMainWindow):

    def __init__(self):
        global id_musica
        QMainWindow.__init__(self)

        # Iniciando o mixer do Pygame
        pygame.init()
        pygame.mixer.init()

        # Pegando os atributos do Design
        self.ui = Ui_ListenNow()
        self.ui.setupUi(self)

        # Verificando se o há músicas ou não para mudar a interface
        self.btn_home_clicked()

        # Deixando o volume no mínimo ao iniciar
        sld = self.ui.volume_slider
        sld.setRange(0, 9)
        sld.setValue(1)

        # Se o valor da barra do volume mudar, ele chama função volume para ajustar a mesma
        sld.valueChanged.connect(self.volume)

        # Setando o botão de play
        self.ui.btn_pausar_play.setStyleSheet(
            'QPushButton {border: 0px solid;background-image: url(:/aaa/play.jpg.png);}'
            'QPushButton:hover {background-image: url(:/aaa/play_hover.jpg.png);}')

        # Inserindo as Colunas na tabela
        self.ui.tableWidget.insertColumn(0)
        self.ui.tableWidget.insertColumn(0)

        colunas = ['Nome', 'ID']
        self.ui.tableWidget.setHorizontalHeaderLabels(colunas)

        # Inserindo a largura de cada coluna
        self.ui.tableWidget.setColumnWidth(0, 550)
        self.ui.tableWidget.setColumnWidth(1, 99)

        # Desativando a opção de editar os textos da tabela
        self.ui.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Setando as linhas da tabela
        row = 0

        # Setado a quantidade de linhas de acordo com o banco
        self.ui.tableWidget.setRowCount(len(banco_musicas))

        # Deixando invisivel os ids das linhas
        self.ui.tableWidget.verticalHeader().setVisible(False)

        for musica in banco_musicas:
            # Tratando erro dos metadados
            eyed3.log.setLevel("ERROR")

            # Pegando os metadados das músicas
            audiofile = eyed3.load(musica[1])

            # Verificando se existe metadados nessa música
            if audiofile.tag.title is None:

                # Definando o nome da música de acordo com o nome do arquivo, pois não há o nome nos metadados
                self.ui.comboBox.addItem(os.path.basename(musica[1]))

                # Adicionando a música a tabela
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(os.path.basename(musica[1])))

                row += 1
            else:

                # Definindo o nome da música de acordo com os metadados
                self.ui.comboBox.addItem(audiofile.tag.title)

                # Adicionando a música a tabela
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(audiofile.tag.title))

                row += 1

        # Clique dos Botões #

        # Home
        self.ui.btn_home.clicked.connect(self.btn_home_clicked)
        self.ui.tableWidget.doubleClicked.connect(self.musicas_da_lista)

        # Downlaod
        self.ui.btn_download.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.downloader))
        self.ui.btn_baixar.clicked.connect(self.download)
        self.ui.btn_baixar_2.clicked.connect(self.diretorio_download)

        # Deletar Músicas
        self.ui.btn_remover.clicked.connect(lambda: self.ui.stackedWidget.setCurrentWidget(self.ui.remover_musicas))
        self.ui.btn_deletar.clicked.connect(lambda: self.deletar_musica())

        # Adicionar Músicas
        self.ui.btn_adicionar.clicked.connect(self.btn_adicionar_musicas_clicked)

        # Tocar Músicas
        self.ui.btn_pausar_play.clicked.connect(self.tocar_musica)

        # Passar e Voltar Músicas
        self.ui.btn_avancar.clicked.connect(self.passar_musica)
        self.ui.btn_voltar.clicked.connect(self.voltar_musica)

    def tocar_musica(self):

        # Chamando as variáveis globais
        global clique_pause_despause
        global banco_musicas
        global id_musica

        # Adicionando um valor ao botão play/pause
        if clique_pause_despause > 0:
            clique_pause_despause += 1

        # Verificando se há música no banco, para tocar a primeira música
        if len(banco_musicas) >= 1 and clique_pause_despause == 0:

            # Adicionando mais um valor ao botão play/pause
            clique_pause_despause += 1

            # Pegando as músicas que estão no banco
            cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
            banco_musicas = cursor.fetchall()

            # Tocando a primeira música do banco
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

            self.nome_musica_artista()

        # Verificando se a primeira música já foi iniciada
        if clique_pause_despause >= 1:

            # Pausando a Música
            if clique_pause_despause % 2 == 0:
                pygame.mixer.music.pause()
                self.ui.btn_pausar_play.setStyleSheet(
                    'QPushButton {border: 0px solid;background-image: url(:/aaa/play.jpg.png);}'
                    'QPushButton:hover {background-image: url(:/aaa/play_hover.jpg.png);}')

            # Despausando a Música
            else:
                self.ui.btn_pausar_play.setStyleSheet(
                    'QPushButton {border: 0px solid;background-image: url(:/aaa/pause.png);}'
                    'QPushButton:hover {background-image: url(:/aaa/pause_hover.png);}')
                pygame.mixer.music.unpause()

        FIM_MUSICA = pygame.USEREVENT+1
        pygame.mixer.music.set_endevent(FIM_MUSICA)

        while True:

            for event in pygame.event.get():

                if event.type == FIM_MUSICA:
                    if len(banco_musicas) > 0:
                        self.passar_musica()

    def musicas_da_lista(self):

        # Chamando as variáveis globais
        global id_musica
        global clique_pause_despause

        # Pegando as músicas do banco
        cursor.execute('SELECT nome FROM musicas_app ORDER BY id ASC')
        banco_musicas = cursor.fetchall()

        # Pegando o id da row, da música selecionada
        musica = self.ui.tableWidget.currentIndex().row()

        if clique_pause_despause == 0:
            clique_pause_despause += 1

        if clique_pause_despause > 0:
            # Defindo o id_musica
            id_musica = int(musica)

            # Tocando a música
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

            self.ui.btn_pausar_play.setStyleSheet(
                'QPushButton {border: 0px solid;background-image: url(:/aaa/pause.png);}'
                'QPushButton:hover {background-image: url(:/aaa/pause_hover.png);}')

            # Chamando a função que define o nome da música e do artista
            self.nome_musica_artista()

        # Verificando se está pausado
        if clique_pause_despause % 2 == 0:
            pygame.mixer.music.pause()

    def volume(self, value):

        # Formatando o valor da barra de volume para o formato aceito pelo Pygame
        volume = f"{0}.{value}"

        # Definindo o volume da música
        pygame.mixer.music.set_volume(float(volume))

    def btn_home_clicked(self):

        # Chamando a variável global
        global banco_musicas

        # Verficando se há música no banco
        if len(banco_musicas) > 0:

            # Mostra tabela com as músicas
            self.ui.stackedWidget.setCurrentWidget(self.ui.musicas)
        else:

            # Mostrando a tela com a logo, e informando que não há músicas adicionadas
            self.ui.stackedWidget.setCurrentWidget(self.ui.home)

    def btn_adicionar_musicas_clicked(self):

        # Chamando variáveis globais
        global banco_musicas
        global novo_id

        # Abrindo tela para selecionar as músicas
        Tk().withdraw()
        filename = askopenfilenames()

        # Pegando o id, diretório da música e fazendo validações
        for musica in filename:
            if musica[-4:] == '.mp3':
                try:

                    # Verificando se a música já está no banco de dados
                    cursor.execute(f'SELECT nome FROM musicas_app WHERE nome = "{musica}"')
                    ok = cursor.fetchall()
                    print(ok[0][0])
                    print(f'Música já está no Banco de Dados!')

                except:
                    # Mostrando a tela com a tabela das músicas
                    self.ui.stackedWidget.setCurrentWidget(self.ui.musicas)

                    # Pegando o id da ultima música adicionada
                    cursor.execute("SELECT MAX(ID) FROM musicas_app")
                    ultimo_id = cursor.fetchone()

                    # Pegando o id da ultima música adicionada
                    for n in ultimo_id:
                        # Caso não tenha id recebe 0
                        if n == None:
                            novo_id = 0
                        else:
                            novo_id = int(n) + 1

                    # Adicionando música ao banco
                    comando_SQL = 'INSERT INTO musicas_app (id, nome) VALUES (%s,%s)'
                    dados = (f"{novo_id}", f"{musica}")
                    cursor.execute(comando_SQL, dados)
                    banco.commit()

                    print('Adicionando música ao banco!')

                    # Limpando a combobox do deletar_musica
                    self.ui.comboBox.clear()

                    # Atulizando o banco_musicas
                    cursor.execute('SELECT * FROM musicas_app ORDER BY id ASC')
                    banco_musicas = cursor.fetchall()

        # Atulizando o banco_musicas
        cursor.execute('SELECT * FROM musicas_app ORDER BY id ASC')
        banco_musicas = cursor.fetchall()

        row = 0

        self.ui.tableWidget.setRowCount(len(banco_musicas))

        # Adicionando as músicas a tabela das músicas
        for musica in banco_musicas:

            # Tratando o erro dos metadados
            eyed3.log.setLevel("ERROR")
            audiofile = eyed3.load(musica[1])

            # Verificando se há metadados na música
            if audiofile.tag.title is None:

                # Adicionando música com o nome do arquivo, pois não há metadados
                self.ui.comboBox.addItem(os.path.basename(musica[1]))

                # Adicionando na tabela
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(os.path.basename(musica[1])))

                row += 1
            else:
                # Adicionando música com o nome de acordo com os metadados
                self.ui.comboBox.addItem(audiofile.tag.title)

                # Adicionando na tabela
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(audiofile.tag.title))

                row += 1

        # Atualizando o banco_musicas
        cursor.execute('SELECT nome FROM musicas_app ORDER BY id ASC')
        banco_musicas = cursor.fetchall()

    def btn_donwloader_clicked(self):

        # Clique dos botões e da tela
        self.ui.stackedWidget.setCurrentWidget(self.ui.downloader)
        self.ui.btn_baixar.clicked.connect(self.download)
        self.ui.btn_baixar_2.clicked.connect(self.diretorio_download)

    def passar_musica(self):

        # Chamando as variáveis globais
        global id_musica
        global banco_musicas
        global clique_pause_despause

        # Pegando as músicas do banco
        cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()

        # Verificando se há mais de uma música no banco
        if clique_pause_despause > 0 and len(banco_musicas) > 1:

            # Verificando se chegou na última música da lista
            if id_musica == len(banco_musicas) - 1:

                # Resetando id para 0
                id_musica -= len(banco_musicas) - 1

                # Tocando a primeira música do banco
                pygame.mixer.music.load(banco_musicas[id_musica][0])
                pygame.mixer.music.play()

                # Chamando função para definir o nome da música e do artista
                self.nome_musica_artista()
            else:
                # Adicionando mais um valor ao id
                id_musica += 1

                # Tocando a proxima música do banco
                pygame.mixer.music.load(banco_musicas[id_musica][0])
                pygame.mixer.music.play()

                # Chamando função para definir o nome da música e do artista
                self.nome_musica_artista()

        # Verificando se está pausado
        if clique_pause_despause % 2 == 0:
            pygame.mixer.music.pause()

        # Tocando a primeira música do banco
        if len(banco_musicas) == 1:
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

    def voltar_musica(self):

        # Pagando a variável global com o id da musica e o banco de dados
        global id_musica
        global banco_musicas

        cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()

        # Tirando um valor do id_musica
        id_musica -= 1

        # Verificando se id da música é maior que 1
        if id_musica >= 1:

            # Tocando a música anterior
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

        # Tocando a primeira música do banco
        if len(banco_musicas) == 1:
            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

        if id_musica == 0:

            pygame.mixer.music.load(banco_musicas[0][0])
            pygame.mixer.music.play()

        if id_musica < 0:
            id_musica = len(banco_musicas) - 1

            pygame.mixer.music.load(banco_musicas[id_musica][0])
            pygame.mixer.music.play()

        # Verificando se está pausado
        if clique_pause_despause % 2 == 0:
            pygame.mixer.music.pause()

        # Chamando função para definir o nome da música e do artista
        self.nome_musica_artista()

    def nome_musica_artista(self):
        # Chamando as variáveis globals
        global id_musica

        cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()

        # Tratando erro dos metadados
        eyed3.log.setLevel("ERROR")
        audiofile = eyed3.load(banco_musicas[id_musica][0])

        # Verificando se há metadados na música
        if audiofile.tag.title is None:

            # Definindo o nome da música de acordo com o nome do arquivo, pois não há metadados
            self.ui.lbl_nome_musica.setText(os.path.basename(banco_musicas[id_musica][0][:-4]))
        else:

            # Definindo o nome da música de acordo com os metadados
            self.ui.lbl_nome_musica.setText(audiofile.tag.title)

        # Verificando se há o nome do artista nos metadados
        if audiofile.tag.artist is None:

            # Informando que não foi encontrado o nome do artista nos metadados
            self.ui.lbl_nome_artista.setText('Artista não encontrado')
        else:

            # Definindo o nome do artista de acordo com os metadados
            self.ui.lbl_nome_artista.setText(audiofile.tag.artist)

    def download(self):
        # Chamando as variáveis globals
        global diretorio

        # Verificando se os campos não estão vazis
        if diretorio != '' and self.ui.line_link != '':
            # Pegando o link informado
            link = self.ui.line_link.text()

            # Tentando efetuar o download

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


        # Pegando o diretório da pasta atual
        pasta_atual = os.path.dirname(os.path.realpath(__file__))
        files = []
        files.clear()

        # Pegando todos os arquivos da pasta e adicionando na lista dos arquivos
        for (dirpath, dirnames, filenames) in os.walk(pasta_atual):
            files.extend(filenames)
            break

        # Verficando se há algum arquivo .mp3
        for arquivo in files:
            if arquivo[-4:] == '.mp3':

                # Movendo arquivo para o diretório informado
                shutil.move(arquivo, diretorio)

    def diretorio_download(self):

        # Chamando as variáveis globals
        global diretorio

        # Abrindo tela para selecionar o diretório
        for n in range(1):
            Tk().withdraw()
            diretorio = askdirectory()

    def deletar_musica(self):

        # Chamando as variáveis globals
        global banco_musicas
        global clique_pause_despause
        global id_musica

        # Pegando o id que será deletado
        id_deletado = 0

        # Pegando as músicas no banco músicas
        cursor.execute('SELECT * FROM musicas_app ORDER BY id ASC')
        banco_musicas = cursor.fetchall()

        # Pegando o item selecionado na combobox do deletar_musicas
        item_combobox = self.ui.comboBox.currentText()

        # Verificando cada música no banco
        for musica in banco_musicas:

            # tratando o erro dos metadados
            eyed3.log.setLevel("ERROR")
            audiofile = eyed3.load(musica[1])

            # Verficações dos nomes
            v1 = item_combobox == os.path.basename(musica[1])
            v2 = item_combobox == audiofile.tag.title
            v3 = item_combobox == os.path.basename(musica[1][:-4])

            # Verificando se alguma foi verdadeira
            if v1 == True or v2 == True or v3 == True:

                # informando que o id_deleta recebe o id da música passada
                id_deletado = musica[0]

                # Deletando a música passada pelas verificações
                cursor.execute(f'DELETE FROM musicas_app WHERE nome = "{musica[1]}"')
                banco.commit()

        # Pegando todas as músicas do banco
        cursor.execute("SELECT * FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()

        # Deletando música da combobox
        self.ui.comboBox.removeItem(self.ui.comboBox.currentIndex())

        # Verificando cada música do banco
        for musica in banco_musicas:

            # Caso tenha músicas maiores que o id da música deletada, o id diminuirá
            if musica[0] > id_deletado:

                # Diminuindo o id das músicas
                cursor.execute(f'UPDATE musicas_app set id = {musica[0] - 1} WHERE nome = "{musica[1]}"')
                banco.commit()

        if id_deletado == 0 and len(banco_musicas) == 1:

            # Diminuindo o id_musica
            id_musica -= 1

            # Pegando todas as músicas do banco
            cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
            banco_musicas = cursor.fetchall()

            # Carregando a única música do banco
            pygame.mixer.music.unload()
            pygame.mixer.music.load(banco_musicas[0][0])

            # Resetando o o botão play/pause
            clique_pause_despause = 0

            # Chamando função para definir o nome da música e do artista
            self.nome_musica_artista()

            # Setando o botão play.
            self.ui.btn_pausar_play.setStyleSheet(
                'QPushButton {border: 0px solid;background-image: url(:/aaa/play.jpg.png);}'
                'QPushButton:hover {background-image: url(:/aaa/play_hover.jpg.png);}')

        # Verificando se era a ultima música do banco
        if id_deletado == len(banco_musicas) and id_musica == id_deletado and id_musica > 0:

            # Pegando as músicas do banco
            cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
            banco_musicas = cursor.fetchall()

            # Diminuindo o id_musica
            id_musica -= 1

            # Carregando a ultima música
            pygame.mixer.music.unload()
            pygame.mixer.music.load(banco_musicas[id_musica][0])

            # Resetando o o botão play/pause
            clique_pause_despause = 0

            # Chamando função para definir o nome da música e do artista
            self.nome_musica_artista()

            # Setando o botão play.
            self.ui.btn_pausar_play.setStyleSheet(
                'QPushButton {border: 0px solid;background-image: url(:/aaa/play.jpg.png);}'
                'QPushButton:hover {background-image: url(:/aaa/play_hover.jpg.png);}')

        # Verificando se a música é diferente dá que está tocando
        if id_deletado != len(banco_musicas) and id_musica > 0:

            # Diminuindo um valor do id_musica
            id_musica -= 1

            # Pegando as músicas do banco
            cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
            banco_musicas = cursor.fetchall()

        # Verificando se está deletando a única música do banco
        if len(banco_musicas) == 0: ###
            # Mudando a tela do home
            self.ui.stackedWidget.setCurrentWidget(self.ui.home)

            # Definindo as lbl nome e artista
            self.ui.lbl_nome_musica.setText('Música')
            self.ui.lbl_nome_artista.setText('Artista')

            # Resetando o botão play/pause
            clique_pause_despause = 0

            # Descarregando a música
            pygame.mixer.music.unload()

            # Resetando o id_musica
            id_musica = 0

            # Setando o botão play.
            self.ui.btn_pausar_play.setStyleSheet(
                'QPushButton {border: 0px solid;background-image: url(:/aaa/play.jpg.png);}'
                'QPushButton:hover {background-image: url(:/aaa/play_hover.jpg.png);}')

        # Pegando as músicas do banco
        cursor.execute("SELECT * FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()

        # linha da tabela
        row = 0

        # Definindo linha da tabela de acordo com o tamanho do banco_musicas
        self.ui.tableWidget.setRowCount(len(banco_musicas))

        # Verificando cada música do banco
        for musica in banco_musicas:

            # Tratando o erro dos metadados
            eyed3.log.setLevel("ERROR")
            audiofile = eyed3.load(musica[1])

            # Verificando se há metadados na música
            if audiofile.tag.title is None:

                # Adicionando música com o nome do arquivo, pois não há metadados
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(os.path.basename(musica[1])))

                row += 1
            else:

                # Adicionando música com o nome de acordo com os metadados
                self.ui.tableWidget.setItem(row, 1, QTableWidgetItem(str(musica[0])))
                self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(audiofile.tag.title))

                row += 1

        cursor.execute("SELECT nome FROM musicas_app ORDER BY id ASC")
        banco_musicas = cursor.fetchall()


if __name__ == '__main__':

    # Variáveis do Sistema
    clique_pause_despause = 0
    id_musica = 0
    diretorio = ''
    novo_id = 0

    # Configuração do Sistema
    app = QApplication(sys.argv)
    window = FrmPrincipal()
    window.show()
    sys.exit(app.exec())
