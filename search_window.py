# search_window.py

import os
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QMenu, QFileDialog, QApplication  # <<< adiciona QApplication aqui
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
# from PyQt5.QtGui import QHeaderView  # já tens, mas garante
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication  # para detectar teclas modificadoras

from database import get_all_clips, delete_clips
from insert_window import InsertWindow
from edit_clip_window import EditClipWindow

class SortableHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self._modifier = Qt.NoModifier

    def mousePressEvent(self, event):
        self._modifier = event.modifiers()
        super().mousePressEvent(event)

class SearchWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procurar Clips")

        self.resize(1600, 850)
        screen = self.screen().availableGeometry()
        self.move(screen.center() - self.rect().center())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # === BOTÕES DO TOPO (linha separada, à esquerda) ===
        top_buttons_widget = QWidget()
        top_buttons_layout = QHBoxLayout(top_buttons_widget)
        top_buttons_layout.setContentsMargins(0, 0, 0, 10)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setStyleSheet("background-color: #3498db; color: white; padding: 10px; font-weight: bold;")
        btn_refresh.clicked.connect(self.load_clips)

        btn_clear = QPushButton("Limpar Filtros")
        btn_clear.setStyleSheet("background-color: #e67e22; color: white; padding: 10px; font-weight: bold;")
        btn_clear.clicked.connect(self.clear_filters)

        btn_insert = QPushButton("Inserir Novo Clip")
        btn_insert.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; font-weight: bold;")
        btn_insert.clicked.connect(self.open_insert)

        top_buttons_layout.addWidget(btn_refresh)
        top_buttons_layout.addWidget(btn_clear)
        top_buttons_layout.addWidget(btn_insert)
        top_buttons_layout.addStretch()

        layout.addWidget(top_buttons_widget)

        # === ÁREA DE FILTROS ===
        filters_widget = QWidget()
        filters_layout = QGridLayout(filters_widget)

        filter_fields = [
            ("Título", 1),
            ("Data/Jornada", 2),
            ("Tipo Jogada", 3),
            ("Jogador Principal", 4),
            ("Assistência de", 5),
            ("Clube", 6),
            ("Adversário", 7),
            ("Competição", 8),
            ("Tags", 9),
        ]

        self.filter_inputs = {}        # Filtros normais (inclusão)
        self.exclude_inputs = {}        # Novos filtros de exclusão

        for idx, (label_text, db_index) in enumerate(filter_fields):
            # Label da coluna
            label = QLabel(label_text + ":")
            label.setStyleSheet("font-weight: bold;")
            label.setAlignment(Qt.AlignCenter)
            filters_layout.addWidget(label, 0, idx)

            # Filtro normal (inclusão)
            line_edit_include = QLineEdit()
            line_edit_include.setPlaceholderText(f"Filtrar por {label_text.lower()}...")
            line_edit_include.textChanged.connect(self.filter_table)
            filters_layout.addWidget(line_edit_include, 1, idx)

            self.filter_inputs[db_index] = line_edit_include

            # Filtro de exclusão (nova linha)
            line_edit_exclude = QLineEdit()
            line_edit_exclude.setPlaceholderText(f"Excluir se contiver {label_text.lower()}...")
            line_edit_exclude.setStyleSheet("background-color: #ffebee;")  # Cor suave para diferenciar
            line_edit_exclude.textChanged.connect(self.filter_table)
            filters_layout.addWidget(line_edit_exclude, 2, idx)

            self.exclude_inputs[db_index] = line_edit_exclude

        # Larguras relativas das colunas (mesmas proporções para as duas linhas)
        stretch_values = [
            42,   # Título
            18,   # Data/Jornada
            19,   # Tipo Jogada
            22,   # Jogador Principal
            24,   # Assistência de
            15,   # Clube
            16,   # Adversário
            20,   # Competição
            25,   # Tags
        ]

        for i, stretch in enumerate(stretch_values):
            filters_layout.setColumnStretch(i, stretch)

        layout.addWidget(filters_widget)

        # === TABELA ===
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        headers = [
            "ID", "Título", "Data/Jornada", "Tipo Jogada", "Jogador Principal",
            "Assistência de", "Clube", "Adversário", "Competição", "Tags",
            "Caminho Vídeo"
        ]
        self.table.setHorizontalHeaderLabels(headers)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # custom_header = SortableHeader(Qt.Horizontal, self.table)
        # self.table.setHorizontalHeader(custom_header)

        # self.table.setSortingEnabled(True)
##############
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(10, True)

        self.set_column_widths()

        self.table.setSelectionMode(QTableWidget.ExtendedSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.doubleClicked.connect(self.on_double_click)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.context_menu)

        layout.addWidget(self.table, stretch=1)

        # === BOTÕES INFERIORES ===
        bottom_layout = QHBoxLayout()

        btn_play_video = QPushButton("Reproduzir Vídeo Selecionado")
        btn_play_video.setStyleSheet("background-color: #f39c12; color: white; padding: 12px; font-weight: bold;")
        btn_play_video.clicked.connect(self.play_selected_video)
        bottom_layout.addWidget(btn_play_video)

        btn_open_folder = QPushButton("Abrir Pasta do Clip Selecionado")
        btn_open_folder.setStyleSheet("background-color: #9b59b6; color: white; padding: 12px;")
        btn_open_folder.clicked.connect(self.open_selected_folder)
        bottom_layout.addWidget(btn_open_folder)

        btn_delete = QPushButton("Apagar Selecionado(s)")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 12px; font-size: 16px;")
        btn_delete.clicked.connect(self.delete_selected)
        bottom_layout.addWidget(btn_delete)

        btn_copy = QPushButton("Copiar Selecionados P/Pasta")
        btn_copy.setStyleSheet("background-color: #16a085; color: white; padding: 12px; font-weight: bold;")
        btn_copy.clicked.connect(self.copy_selected_to_folder)
        bottom_layout.addWidget(btn_copy)

        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)

        self.sort_columns = []  # lista de (coluna_logical_index, ascending=True/False)

        # Conecta o clique no header
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)

        self.all_clips = []
        self.load_clips()

    def get_sort_key(self, clip, col):
        value = clip[col]
        if value is None:
            return "" if col != 0 else 0
        if col == 0:  # ID numérico
            try:
                return int(value)
            except:
                return 0
        return str(value).lower()  # case-insensitive para texto

    def on_header_clicked(self, logicalIndex):
        if logicalIndex in (0, 10):  # ignora colunas escondidas
            return

        modifier = QApplication.keyboardModifiers()  # deteta se Ctrl está pressionado

        if modifier == Qt.ControlModifier:  # Ctrl + clique = adicionar/toggle secundária
            # Procura se já existe na lista
            for i, (col, asc) in enumerate(self.sort_columns):
                if col == logicalIndex:
                    # Toggle direção
                    self.sort_columns[i] = (logicalIndex, not asc)
                    self.filter_table()
                    return
            # Adiciona nova secundária
            self.sort_columns.append((logicalIndex, True))

        else:  # Clique normal = ordenação primária única
            if self.sort_columns and self.sort_columns[0][0] == logicalIndex:
                # Toggle direção da primária
                self.sort_columns = [(logicalIndex, not self.sort_columns[0][1])]
            else:
                # Nova primária ascendente
                self.sort_columns = [(logicalIndex, True)]

        self.filter_table()

    def set_column_widths(self):
        widths = [
            None, 300, 140, 150, 180, 180, 120, 120, 160, 200, None
        ]
        for col, width in enumerate(widths):
            if width is not None and col >= 1 and col <= 9:
                self.table.setColumnWidth(col, width)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_column_widths()

    def load_clips(self):
        self.all_clips = get_all_clips()
        self.filter_table()

    def clear_filters(self):
        for line_edit in self.filter_inputs.values():
            line_edit.clear()
        for line_edit in self.exclude_inputs.values():
            line_edit.clear()
        self.filter_table()

    def filter_table(self):
        filtered = self.all_clips

        # === FILTROS DE INCLUSÃO ===
        for db_index, line_edit in self.filter_inputs.items():
            text = line_edit.text().strip().lower()
            if text:
                filtered = [clip for clip in filtered if text in str(clip[db_index] or "").lower()]

        # === FILTROS DE EXCLUSÃO ===
        for db_index, line_edit in self.exclude_inputs.items():
            text = line_edit.text().strip().lower()
            if text:
                filtered = [clip for clip in filtered if text not in str(clip[db_index] or "").lower()]

        # === ORDENAÇÃO MÚLTIPLA ===
        if self.sort_columns:
            # Aplica em ordem reversa (secundárias primeiro para stable sort)
            for col, ascending in reversed(self.sort_columns):
                reverse = not ascending
                filtered.sort(
                    key=lambda clip: self.get_sort_key(clip, col),
                    reverse=reverse
                )

        # === PREENCHE TABELA ===
        self.table.setRowCount(len(filtered))
        for row, clip in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(str(clip[0])))
            for col in range(1, 10):
                self.table.setItem(row, col, QTableWidgetItem(str(clip[col] or "")))
            self.table.setItem(row, 10, QTableWidgetItem(str(clip[10] or "")))

        # === MOSTRA SETA NO HEADER (só na coluna primária) ===
        header = self.table.horizontalHeader()
        if self.sort_columns:
            primary_col, primary_asc = self.sort_columns[0]
            order = Qt.AscendingOrder if primary_asc else Qt.DescendingOrder
            header.setSortIndicator(primary_col, order)
        else:
            header.setSortIndicator(-1, Qt.AscendingOrder)  # limpa seta

    # === FUNÇÃO DE CÓPIA COM PERGUNTA FINAL ===
    def copy_selected_to_folder(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos um clip para copiar!")
            return

        destination_folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Destino",
            "",
            QFileDialog.ShowDirsOnly
        )
        if not destination_folder:
            return

        missing_files = []
        copied_count = 0

        for row in selected_rows:
            video_path = self.table.item(row, 10).text().strip()
            title = self.table.item(row, 1).text().strip() or "Sem_Titulo"

            if not video_path or not os.path.exists(video_path):
                missing_files.append(f"{video_path or 'Caminho vazio'}")
                continue

            filename = os.path.basename(video_path)
            dest_path = os.path.join(destination_folder, filename)

            # Evitar sobrescrever ficheiros existentes
            counter = 1
            original_dest = dest_path
            while os.path.exists(dest_path):
                name, ext = os.path.splitext(original_dest)
                dest_path = f"{name}_{counter}{ext}"
                counter += 1

            try:
                shutil.copy2(video_path, dest_path)
                copied_count += 1
            except Exception as e:
                missing_files.append(f"{title} -> Erro ao copiar: {str(e)}")

        # Mensagem final e relatório (se necessário)
        if missing_files:
            report_path = os.path.join(destination_folder, "ficheiros_nao_encontrados.txt")
            with open(report_path, "w", encoding="utf-8") as f:
                f.write("Ficheiros não encontrados ou com erro ao copiar:\n\n")
                for line in missing_files:
                    f.write(line + "\n")

            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Aviso")
            msg.setText(
                f"Cópia concluída com avisos.\n"
                f"{copied_count} ficheiro(s) copiados com sucesso.\n"
                f"{len(missing_files)} problema(s) encontrado(s).\n\n"
                f"Relatório criado em:\n{report_path}"
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Sucesso")
            msg.setText(f"Todos os {len(selected_rows)} clip(s) foram copiados com sucesso!")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        # Pergunta se quer abrir a pasta
        reply = QMessageBox.question(
            self,
            "Abrir pasta?",
            "Abrir a pasta de destino no explorador?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            QDesktopServices.openUrl(QUrl.fromLocalFile(destination_folder))

    # === RESTO DAS FUNÇÕES (inalteradas) ===
    def open_folder(self, video_path):
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "Erro", "Ficheiro de vídeo não encontrado ou caminho inválido!")
            return
        folder_path = os.path.dirname(video_path)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))

    def open_selected_folder(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Erro", "Selecione um clip primeiro!")
            return
        row = selected[0].row()
        video_path = self.table.item(row, 10).text().strip()
        self.open_folder(video_path)

    def play_selected_video(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        video_path = self.table.item(row, 10).text().strip()
        if not video_path or not os.path.exists(video_path):
            QMessageBox.warning(self, "Erro", f"Ficheiro de vídeo não encontrado!\nCaminho: {video_path}")
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(video_path))

    def on_double_click(self):
        row = self.table.currentRow()
        if row < 0:
            return
        clip_id = int(self.table.item(row, 0).text())
        self.edit_win = EditClipWindow(clip_id, parent=self)
        self.edit_win.show()

    def context_menu(self, position):
        if not self.table.selectedItems():
            return
        menu = QMenu()
        menu.addAction("Reproduzir Vídeo", self.play_selected_video)
        menu.addAction("Abrir Pasta do Clip", self.open_selected_folder)
        menu.addSeparator()
        menu.addAction("Editar Clip", self.on_double_click)
        menu.exec_(self.table.mapToGlobal(position))

    def open_insert(self):
        self.insert_win = InsertWindow()
        self.insert_win.show()

    def delete_selected(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        if not selected_rows:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos um clip para apagar!")
            return
        count = len(selected_rows)
        reply = QMessageBox.question(self, "Confirmação", f"Apagar {count} clip(s) selecionado(s)?")
        if reply == QMessageBox.Yes:
            ids_to_delete = [int(self.table.item(row, 0).text()) for row in selected_rows]
            delete_clips(ids_to_delete)
            self.load_clips()
            QMessageBox.information(self, "Sucesso", f"{count} clip(s) apagado(s) com sucesso.")