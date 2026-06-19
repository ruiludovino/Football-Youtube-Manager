# JanelaFontes.py
import os
import subprocess
import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QPushButton,
    QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtGui import QFont, QBrush, QColor, QDesktopServices
from PyQt5.QtCore import Qt, QUrl

class JanelaFontes(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("YT Fontes - Lista de Canais")
        self.setGeometry(100, 50, 1100, 800)
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Título principal
        title = QLabel("Fontes YouTube (Canais.txt)")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Área de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        self.content_layout.setSpacing(10)

        scroll.setWidget(self.content_widget)
        main_layout.addWidget(scroll)

        # Botões no fundo
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(25)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedWidth(200)
        btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold;")
        btn_refresh.clicked.connect(self.refresh_conteudo)
        buttons_layout.addWidget(btn_refresh)

        btn_open_file = QPushButton("Abrir Ficheiro")
        btn_open_file.setFixedWidth(200)
        btn_open_file.setStyleSheet("background-color: #f39c12; color: white; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold;")
        btn_open_file.clicked.connect(self.abrir_ficheiro_no_editor)
        buttons_layout.addWidget(btn_open_file)

        btn_close = QPushButton("Fechar")
        btn_close.setFixedWidth(200)
        btn_close.setStyleSheet("background-color: #e74c3c; color: white; padding: 12px; border-radius: 8px; font-size: 16px; font-weight: bold;")
        btn_close.clicked.connect(self.close)
        buttons_layout.addWidget(btn_close)

        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        main_layout.addWidget(buttons_widget, alignment=Qt.AlignCenter)

        self.links_por_grupo = []  # Lista de listas de links por grupo
        self.carregar_canais()

    def abrir_link_individual(self, url):
        if url and url.strip():
            QDesktopServices.openUrl(QUrl(url.strip()))

    def abrir_todos_links_do_grupo(self, indice_grupo):
        if 0 <= indice_grupo < len(self.links_por_grupo):
            for url in self.links_por_grupo[indice_grupo]:
                if url.strip():
                    QDesktopServices.openUrl(QUrl(url.strip()))

    def abrir_ficheiro_no_editor(self):
        file_path = os.path.join(os.path.dirname(__file__), "Canais.txt")
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "Aviso", "Ficheiro 'Canais.txt' não encontrado!")
            return
        try:
            if sys.platform.startswith('win'):
                os.startfile(file_path)
            elif sys.platform.startswith('darwin'):
                subprocess.Popen(['open', file_path])
            else:
                subprocess.Popen(['xdg-open', file_path])
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível abrir o ficheiro:\n{str(e)}")

    def refresh_conteudo(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.links_por_grupo = []
        self.carregar_canais()

    def carregar_canais(self):
        file_path = os.path.join(os.path.dirname(__file__), "Canais.txt")

        if not os.path.exists(file_path):
            lbl = QLabel("Ficheiro 'Canais.txt' não encontrado na pasta do projeto!")
            lbl.setStyleSheet("color: red; font-size: 16px;")
            lbl.setAlignment(Qt.AlignCenter)
            self.content_layout.addWidget(lbl)
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                linhas = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao ler o ficheiro:\n{str(e)}")
            return

        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Descrição", "Link"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setAlternatingRowColors(True)
        table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 10px;
            }
        """)

        row_count = 0
        table.setRowCount(len(linhas))

        grupo_atual_links = []
        indice_grupo_atual = -1

        for linha in linhas:
            linha = linha.rstrip("\n")
            stripped = linha.strip()

            if not linha:
                continue

            if stripped.startswith("###"):
                if grupo_atual_links:
                    self.links_por_grupo.append(grupo_atual_links[:])
                    grupo_atual_links = []

                indice_grupo_atual += 1

                grupo_nome = stripped[3:].strip() or "Sem Nome"

                table.setSpan(row_count, 0, 1, 2)
                item_grupo = QTableWidgetItem(f"  {grupo_nome}  ")
                item_grupo.setBackground(QBrush(QColor("#3498db")))
                item_grupo.setForeground(QBrush(QColor("white")))
                item_grupo.setFont(QFont("Arial", 14, QFont.Bold))
                item_grupo.setTextAlignment(Qt.AlignCenter)
                item_grupo.setData(Qt.UserRole, "grupo")
                item_grupo.setData(Qt.UserRole + 1, indice_grupo_atual)
                item_grupo.setToolTip("Duplo clique para abrir todos os links deste grupo")

                table.setItem(row_count, 0, item_grupo)
                row_count += 1

            else:
                partes = linha.split("\t", 1)
                if len(partes) < 2:
                    continue

                descricao = partes[0].strip()
                url = partes[1].strip()

                if not descricao or not url:
                    continue

                # Descrição
                item_desc = QTableWidgetItem(descricao)
                item_desc.setData(Qt.UserRole + 2, url)  # Guardar URL na descrição também
                table.setItem(row_count, 0, item_desc)

                # Link
                item_link = QTableWidgetItem(url)
                item_link.setForeground(QBrush(QColor("#e74c3c")))
                item_link.setToolTip("Duplo clique na linha para abrir este link")
                item_link.setData(Qt.UserRole + 2, url)
                table.setItem(row_count, 1, item_link)

                grupo_atual_links.append(url)
                row_count += 1

        if grupo_atual_links:
            self.links_por_grupo.append(grupo_atual_links)

        table.setRowCount(row_count)

        # Único handler para duplo clique em qualquer linha
        table.itemDoubleClicked.connect(self.duplo_clique_na_tabela)

        self.content_layout.addWidget(table)

    def duplo_clique_na_tabela(self, item):
        """Trata duplo clique em qualquer célula da tabela"""
        if not item:
            return

        # Se for linha de grupo
        if item.data(Qt.UserRole) == "grupo":
            indice = item.data(Qt.UserRole + 1)
            if isinstance(indice, int):
                self.abrir_todos_links_do_grupo(indice)

        # Se for linha normal (tem URL guardada)
        else:
            url = item.data(Qt.UserRole + 2)
            if url and isinstance(url, str):
                self.abrir_link_individual(url)