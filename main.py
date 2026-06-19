import sys
import os
import database  # Importa o módulo – cria a tabela automaticamente

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QFont, QDesktopServices

# Import das janelas / funcionalidades
from insert_window import InsertWindow
from search_window import SearchWindow
from player_photos_window import PlayerPhotosWindow
from procura_nome_ficheiro_window import ProcuraNomeFicheiroWindow
from JanelaFontes import JanelaFontes
from TabelaDeProjetos import DashboardProjetos

# Novo import para Vídeos Originais
from VideosOriginais import VideosOriginais  # ← ajuste o nome da classe/função se for diferente


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Clips de Futebol")
        self.setGeometry(300, 100, 700, 700)  # um pouco mais alto para caber mais botões
        self.setStyleSheet("background-color: #f0f0f0;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignCenter)
        main_layout.setSpacing(20)

        # Título
        title = QLabel("Gestor de Clips")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin: 20px;")
        main_layout.addWidget(title)

        subtitle = QLabel("Organiza os teus clips de golos, assistências e jogadas")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d;")
        main_layout.addWidget(subtitle)

        # Botão Dashboard com Cards (recomendado)
        btn_dashboard = QPushButton("Dashboard Projetos")
        dashboard_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 18px;
                font-size: 18px;
                font-weight: bold;
                border-radius: 10px;
                min-width: 340px;
            }
            QPushButton:hover { background-color: #219653; }
        """
        btn_dashboard.setStyleSheet(dashboard_style)
        btn_dashboard.clicked.connect(self.open_dashboard_window)

        dashboard_layout = QHBoxLayout()
        dashboard_layout.addStretch()
        dashboard_layout.addWidget(btn_dashboard)
        dashboard_layout.addStretch()
        main_layout.addLayout(dashboard_layout)

        # Linha separadora
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # Estilos de cor por linha
        blue_style = """
            QPushButton { background-color: #3498db; color: white; border: none; padding: 15px; font-size: 16px; border-radius: 8px; min-width: 200px; }
            QPushButton:hover { background-color: #2980b9; }
        """

        orange_style = """
            QPushButton { background-color: #e67e22; color: white; border: none; padding: 15px; font-size: 16px; border-radius: 8px; min-width: 200px; }
            QPushButton:hover { background-color: #d35400; }
        """

        green_style = """
            QPushButton { background-color: #27ae60; color: white; border: none; padding: 15px; font-size: 16px; border-radius: 8px; min-width: 200px; }
            QPushButton:hover { background-color: #219a52; }
        """

        # PRIMEIRA LINHA (Azul)
        row1 = QHBoxLayout()
        row1.setSpacing(30)
        btn_insert = QPushButton("Inserir Novo Clip")
        btn_insert.setStyleSheet(blue_style)
        btn_insert.clicked.connect(self.open_insert_window)
        row1.addWidget(btn_insert)

        btn_search = QPushButton("Procurar Clips")
        btn_search.setStyleSheet(blue_style)
        btn_search.clicked.connect(self.open_search_window)
        row1.addWidget(btn_search)
        main_layout.addLayout(row1)

        # SEGUNDA LINHA (Laranja)
        row2 = QHBoxLayout()
        row2.setSpacing(30)
        btn_procura_nome = QPushButton("Procura Nome Ficheiro")
        btn_procura_nome.setStyleSheet(orange_style)
        btn_procura_nome.clicked.connect(self.ProcuraNomeFicheiro)
        row2.addWidget(btn_procura_nome)

        btn_player_photos = QPushButton("Procurar Fotos Jogadores")
        btn_player_photos.setStyleSheet(orange_style)
        btn_player_photos.clicked.connect(self.open_player_photos_window)
        row2.addWidget(btn_player_photos)
        main_layout.addLayout(row2)

        # TERCEIRA LINHA (Verde)
        row3 = QHBoxLayout()
        row3.setSpacing(30)
        btn_yt_fontes = QPushButton("Fontes YouTube")
        btn_yt_fontes.setStyleSheet(green_style)
        btn_yt_fontes.clicked.connect(self.open_yt_fontes_window)
        row3.addWidget(btn_yt_fontes)

        btn_open_project = QPushButton("Abrir Pasta Deste Programa")
        btn_open_project.setStyleSheet(green_style)
        btn_open_project.clicked.connect(self.open_project_folder)
        row3.addWidget(btn_open_project)
        main_layout.addLayout(row3)

        # QUARTA LINHA (Verde) ← NOVO BOTÃO
        row4 = QHBoxLayout()
        row4.setSpacing(30)
        btn_videos_originais = QPushButton("Vídeos Originais")
        btn_videos_originais.setStyleSheet(green_style)
        btn_videos_originais.clicked.connect(self.open_videos_originais)
        row4.addWidget(btn_videos_originais)

        # (podes adicionar outro botão aqui se quiseres manter o padrão de 2 botões por linha)
        # btn_extra = QPushButton("Outro")
        # btn_extra.setStyleSheet(green_style)
        # row4.addWidget(btn_extra)

        main_layout.addLayout(row4)

        # Botão Sair
        btn_exit = QPushButton("Sair")
        btn_exit.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                border-radius: 8px;
                min-width: 150px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        btn_exit.clicked.connect(self.close)

        exit_layout = QHBoxLayout()
        exit_layout.addStretch()
        exit_layout.addWidget(btn_exit)
        exit_layout.addStretch()
        main_layout.addLayout(exit_layout)

        main_layout.addStretch()

    # Métodos das janelas
    def open_insert_window(self):
        self.insert_win = InsertWindow()
        self.insert_win.show()

    def open_search_window(self):
        self.search_win = SearchWindow()
        self.search_win.show()

    def open_player_photos_window(self):
        self.player_photos_win = PlayerPhotosWindow()
        self.player_photos_win.show()

    def ProcuraNomeFicheiro(self):
        self.procura_nome_win = ProcuraNomeFicheiroWindow()
        self.procura_nome_win.show()

    def open_yt_fontes_window(self):
        self.yt_fontes_win = JanelaFontes()
        self.yt_fontes_win.show()

    def open_project_folder(self):
        project_path = os.path.dirname(os.path.abspath(__file__))
        QDesktopServices.openUrl(QUrl.fromLocalFile(project_path))

    def open_dashboard_window(self):
        self.dashboard_win = DashboardProjetos()
        self.dashboard_win.show()

    # Novo método para Vídeos Originais
    def open_videos_originais(self):
        # Ajuste conforme o que existe realmente em VideosOriginais.py
        # Exemplos possíveis:

        # 1. Se for uma classe que cria uma janela
        self.videos_originais_win = VideosOriginais()
        self.videos_originais_win.show()

        # 2. Se for uma função simples
        # VideosOriginais()

        # 3. Se for uma janela modal (com parent)
        # dialog = VideosOriginais(self)
        # dialog.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())