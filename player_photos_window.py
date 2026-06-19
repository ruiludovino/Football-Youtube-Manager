# player_photos_window.py

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QMenu
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices

# Caminho fixo da pasta das fotos
PHOTOS_FOLDER = r"C:\Users\ruijl\Dropbox\Codigo\Tube Mastery Monetização\IA\Football Architects\Fotos Atletas"

class PlayerPhotosWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procurar Fotos Jogadores")

        # Tamanho fixo da janela: 1000px de largura, 700px de altura
        window_width = 500
        window_height = 900

        # Centraliza a janela no ecrã
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        x_position = (screen.width() - window_width) // 2
        y_position = (screen.height() - window_height) // 2

        self.setGeometry(x_position, y_position, window_width, window_height)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Topo: Filtro + Refresh
        top_layout = QHBoxLayout()
        filter_label = QLabel("Filtrar:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Pesquise pelo nome do ficheiro...")
        self.filter_input.textChanged.connect(self.filter_table)
        top_layout.addWidget(filter_label)
        top_layout.addWidget(self.filter_input)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        btn_refresh.clicked.connect(self.load_photos)
        top_layout.addWidget(btn_refresh)

        layout.addLayout(top_layout)

        # Tabela com 2 colunas
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nome do Ficheiro", "Extensão"])

        # Configuração das colunas
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Extensão: coluna bem pequena (cerca de 80px – cabe ".jpg", ".png", etc.)
        self.table.setColumnWidth(1, 80)

        # Nome do Ficheiro: expande para ocupar o resto da janela
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        # Alternativa (se quiseres um rácio fixo 3:1 em vez de stretch total):
        # self.table.setColumnWidth(0, 240)  # 3x a largura da extensão
        # self.table.setColumnWidth(1, 80)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)  # opcional

        # Permite selecionar linhas inteiras e múltiplas seleções
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        layout.addWidget(self.table)
        # Ativa o menu de contexto com o botão direito
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)

        # Linha extra (muito importante!) para garantir que funciona em todas as áreas da tabela
        self.table.viewport().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.viewport().customContextMenuRequested.connect(self.context_menu)

        # Botão inferior: Apagar Selecionados
        bottom_layout = QHBoxLayout()
        btn_delete = QPushButton("Apagar Selecionados")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 12px; font-size: 16px;")
        btn_delete.clicked.connect(self.delete_selected)
        bottom_layout.addWidget(btn_delete)
        bottom_layout.addStretch()  # Empurra o botão para a esquerda

        layout.addLayout(bottom_layout)

        self.all_files = []
        self.load_photos()

    def load_photos(self):
        """Carrega todos os ficheiros da pasta (ignora pastas e ficheiros ocultos)"""
        if not os.path.exists(PHOTOS_FOLDER):
            QMessageBox.critical(self, "Erro", f"A pasta não foi encontrada:\n{PHOTOS_FOLDER}")
            self.all_files = []
        else:
            all_entries = os.listdir(PHOTOS_FOLDER)
            files = [f for f in all_entries if os.path.isfile(os.path.join(PHOTOS_FOLDER, f))]
            # Ordena por nome
            files.sort(key=str.lower)
            self.all_files = files

        self.filter_table()

    def filter_table(self):
        """Filtra a tabela com base no texto introduzido"""
        filter_text = self.filter_input.text().strip().lower()
        if filter_text:
            displayed = [f for f in self.all_files if filter_text in f.lower()]
        else:
            displayed = self.all_files

        self.table.setRowCount(len(displayed))
        for row, filename in enumerate(displayed):
            name = os.path.splitext(filename)[0]
            ext = os.path.splitext(filename)[1].lower() or "(sem extensão)"

            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(ext))

    def get_selected_files(self):
        """Devolve lista de nomes de ficheiros selecionados"""
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        return [self.table.item(row, 0).text() + self.table.item(row, 1).text() for row in selected_rows]

    def open_image(self, filepath):
        """Abre a imagem com o programa predefinido do sistema"""
        if os.path.exists(filepath):
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        else:
            QMessageBox.warning(self, "Erro", "Ficheiro não encontrado!")

    def open_selected_image(self):
        """Abre a imagem ao fazer duplo clique ou opção de menu"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        filename = self.table.item(row, 0).text() + self.table.item(row, 1).text()
        filepath = os.path.join(PHOTOS_FOLDER, filename)
        self.open_image(filepath)

    def open_folder(self):
        """Abre a pasta das fotos no explorador"""
        if os.path.exists(PHOTOS_FOLDER):
            QDesktopServices.openUrl(QUrl.fromLocalFile(PHOTOS_FOLDER))
        else:
            QMessageBox.warning(self, "Erro", "Pasta não encontrada!")

    def open_selected_image(self):
        """Abre a imagem ao fazer duplo clique ou opção de menu (apenas uma de cada vez)"""
        selected_rows = set(index.row() for index in self.table.selectedIndexes())
        if not selected_rows:
            return
        if len(selected_rows) > 1:
            QMessageBox.information(self, "Aviso", "Seleciona apenas uma imagem para abrir.")
            return

        row = next(iter(selected_rows))  # Pega a primeira (e única)
        filename = self.table.item(row, 0).text() + self.table.item(row, 1).text()
        filepath = os.path.join(PHOTOS_FOLDER, filename)
        self.open_image(filepath)

    def context_menu(self, position):
        """Menu de contexto ao clicar com o botão direito na tabela"""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            # Se nada estiver selecionado, ainda assim permite abrir a pasta
            menu = QMenu()
            open_folder_action = menu.addAction("Abrir Pasta das Fotos")
            action = menu.exec_(self.table.mapToGlobal(position))
            if action == open_folder_action:
                self.open_folder()
            return

        menu = QMenu()
        open_image_action = menu.addAction("Abrir Imagem")
        open_folder_action = menu.addAction("Abrir Pasta das Fotos")

        action = menu.exec_(self.table.mapToGlobal(position))

        if action == open_image_action:
            # Se houver mais do que uma selecionada, avisa
            selected_rows_set = set(index.row() for index in self.table.selectedIndexes())
            if len(selected_rows_set) > 1:
                QMessageBox.information(self, "Aviso",
                                        "Só é possível abrir uma imagem de cada vez.\nSeleciona apenas uma linha.")
            else:
                self.open_selected_image()  # Abre a única selecionada
        elif action == open_folder_action:
            self.open_folder()

    def delete_selected(self):
        """Apaga os ficheiros selecionados (com confirmação)"""
        selected_files = self.get_selected_files()
        if not selected_files:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos uma foto para apagar!")
            return

        count = len(selected_files)
        reply = QMessageBox.question(
            self, "Confirmação",
            f"Tens a certeza que queres apagar {count} foto(s)?\nEsta ação não pode ser desfeita."
        )
        if reply == QMessageBox.Yes:
            deleted_count = 0
            for filename in selected_files:
                filepath = os.path.join(PHOTOS_FOLDER, filename)
                try:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        deleted_count += 1
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível apagar {filename}:\n{e}")

            QMessageBox.information(self, "Concluído", f"{deleted_count} foto(s) apagada(s) com sucesso.")
            self.load_photos()  # Atualiza a lista