# procura_nome_ficheiro_window.py

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QMenu, QFileDialog, QDesktopWidget
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QClipboard
from PyQt5.QtWidgets import QApplication  # Necessário para acessar o clipboard

# Pasta inicial fixa
INITIAL_FOLDER = r"C:\Users\ruijl\Dropbox\Codigo\Tube Mastery Monetização\IA\Football Architects\Clips\1 - Clips Crus Editar Para YouTube"

class ProcuraNomeFicheiroWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procura Nome de Ficheiro - Clips de Futebol")

        # Tamanho da janela
        window_width = 600
        window_height = 800

        # Centraliza a janela no ecrã
        screen = QDesktopWidget().screenGeometry()
        x_position = (screen.width() - window_width) // 2
        y_position = (screen.height() - window_height) // 2
        self.setGeometry(x_position, y_position, window_width, window_height)

        # Pasta atual – começa com a pasta fixa
        self.current_folder = INITIAL_FOLDER if os.path.exists(INITIAL_FOLDER) else ""

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # =============================================
        # Linha 1: Escolher Pasta + caminho atual
        # =============================================
        pasta_layout = QHBoxLayout()

        self.btn_escolher_pasta = QPushButton("Escolher Pasta")
        self.btn_escolher_pasta.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        self.btn_escolher_pasta.clicked.connect(self.escolher_pasta)
        pasta_layout.addWidget(self.btn_escolher_pasta)

        self.label_pasta = QLabel(self.current_folder or "Nenhuma pasta selecionada")
        self.label_pasta.setStyleSheet("color: #7f8c8d; margin-left: 10px;")
        self.label_pasta.setWordWrap(True)
        pasta_layout.addWidget(self.label_pasta)

        pasta_layout.addStretch()
        layout.addLayout(pasta_layout)

        # =============================================
        # Linha 2: Filtro + Refresh
        # =============================================
        filter_layout = QHBoxLayout()

        filter_label = QLabel("Filtrar:")
        filter_layout.addWidget(filter_label)

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Pesquise pelo nome do ficheiro...")
        self.filter_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(self.filter_input)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 10px;")
        btn_refresh.clicked.connect(self.load_files)
        filter_layout.addWidget(btn_refresh)

        layout.addLayout(filter_layout)

        # =============================================
        # Tabela
        # =============================================
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Nome do Ficheiro", "Extensão"])

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setColumnWidth(1, 80)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.ExtendedSelection)

        # Duplo clique abre o vídeo
        self.table.doubleClicked.connect(self.open_selected_video)

        layout.addWidget(self.table)

        # Menu de contexto (botão direito)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)
        self.table.viewport().setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.viewport().customContextMenuRequested.connect(self.context_menu)

        self.all_files = []

        # Carrega automaticamente a pasta inicial
        if self.current_folder:
            self.load_files()
        else:
            self.label_pasta.setText("Pasta inicial não encontrada")

    # ===================================================================
    # Métodos auxiliares
    # ===================================================================
    def escolher_pasta(self):
        pasta = QFileDialog.getExistingDirectory(
            self,
            "Escolher Pasta com Clips de Vídeo",
            self.current_folder or ""
        )
        if pasta:
            self.current_folder = pasta
            self.label_pasta.setText(pasta)
            self.load_files()

    def load_files(self):
        if not self.current_folder or not os.path.exists(self.current_folder):
            self.all_files = []
            self.label_pasta.setText("Pasta não encontrada ou não selecionada")
        else:
            all_entries = os.listdir(self.current_folder)
            files = [f for f in all_entries if os.path.isfile(os.path.join(self.current_folder, f))]
            files.sort(key=str.lower)
            self.all_files = files

        self.filter_table()

    def filter_table(self):
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
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        return [
            self.table.item(row, 0).text() + self.table.item(row, 1).text()
            for row in selected_rows
        ]

    def open_video(self, filepath):
        if os.path.exists(filepath):
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        else:
            QMessageBox.warning(self, "Erro", "Ficheiro não encontrado!")

    def open_selected_video(self):
        selected_files = self.get_selected_files()
        if not selected_files:
            return
        if len(selected_files) > 1:
            QMessageBox.information(self, "Aviso", "Só é possível abrir um vídeo de cada vez.\nSeleciona apenas uma linha.")
            return

        filename = selected_files[0]
        filepath = os.path.join(self.current_folder, filename)
        self.open_video(filepath)

    def open_folder(self):
        """Abre apenas a pasta no Explorador de Ficheiros"""
        if not self.current_folder or not os.path.exists(self.current_folder):
            QMessageBox.warning(self, "Erro", "Pasta não selecionada ou não existe.")
            return
        try:
            os.startfile(self.current_folder)
        except OSError as e:
            QMessageBox.warning(self, "Erro", f"Não foi possível abrir a pasta:\n{e}")

    def copy_filename(self):
        """Copia o(s) nome(s) do(s) ficheiro(s) selecionado(s) para a área de transferência"""
        selected_files = self.get_selected_files()
        if not selected_files:
            return

        # Junta os nomes com quebra de linha
        text_to_copy = "\n".join(selected_files)

        clipboard = QApplication.clipboard()
        clipboard.setText(text_to_copy)

        count = len(selected_files)
        QMessageBox.information(
            self, "Copiado!",
            f"{count} nome(s) de ficheiro copiado(s) para a área de transferência."
        )

    def context_menu(self, position):
        """Menu de contexto ao clicar com o botão direito"""
        selected_files = self.get_selected_files()
        has_selection = bool(selected_files)

        menu = QMenu()

        open_video_action = menu.addAction("Abrir Vídeo")
        menu.addSeparator()
        open_folder_action = menu.addAction("Abrir Pasta")

        if has_selection:
            copy_action = menu.addAction("Copiar Nome")
        else:
            copy_disabled = menu.addAction("Copiar Nome")
            copy_disabled.setEnabled(False)

        action = menu.exec_(self.table.mapToGlobal(position))

        if action == open_video_action:
            self.open_selected_video()
        elif action == open_folder_action:
            self.open_folder()
        elif has_selection and action == copy_action:
            self.copy_filename()