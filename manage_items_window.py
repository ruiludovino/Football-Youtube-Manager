# manage_items_window.py
import sqlite3
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
from database import get_all_items

class ManageItemsWindow(QMainWindow):
    def __init__(self, table_name, title):
        super().__init__()
        self.table_name = table_name  # "clubes" ou "jogadores"
        self.setWindowTitle(f"Gerir {title}")
        self.setGeometry(300, 150, 550, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        layout.addWidget(QLabel(f"Lista de {title}"))

        # Campo de filtro
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrar:")
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Escreva para filtrar...")
        self.filter_input.textChanged.connect(self.filter_table)
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        layout.addLayout(filter_layout)

        # Tabela
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Nome"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setColumnHidden(0, True)
        self.table.setSelectionMode(QTableWidget.MultiSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

        # Campo para adicionar novo
        input_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Novo nome")
        input_layout.addWidget(self.name_input)

        btn_add = QPushButton("Adicionar")
        btn_add.clicked.connect(self.add_item)
        input_layout.addWidget(btn_add)

        layout.addLayout(input_layout)

        # Botão apagar (único botão de ação)
        btn_delete = QPushButton("Apagar Selecionado(s)")
        btn_delete.setStyleSheet("background-color: #e74c3c; color: white; padding: 12px; font-size: 16px;")
        btn_delete.clicked.connect(self.delete_item)
        layout.addWidget(btn_delete)

        self.all_items = []
        self.load_items()

    def load_items(self):
        self.all_items = get_all_items(self.table_name)
        self.filter_table()

    def filter_table(self):
        filter_text = self.filter_input.text().strip().lower()
        if filter_text:
            filtered = [item for item in self.all_items if filter_text in item[1].lower()]
        else:
            filtered = self.all_items

        self.table.setRowCount(len(filtered))
        for row, (item_id, name) in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(str(item_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))

    def add_item(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Erro", "Insira um nome!")
            return

        # Abre conexão corretamente aqui
        conn = sqlite3.connect("clips.db")
        cursor = conn.cursor()  # <--- Define cursor aqui
        cursor.execute(f"INSERT OR IGNORE INTO {self.table_name} (nome) VALUES (?)", (name,))
        conn.commit()
        conn.close()

        self.name_input.clear()
        self.load_items()

    def delete_item(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()), reverse=True)
        if not selected_rows:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos um item para apagar!")
            return

        count = len(selected_rows)
        reply = QMessageBox.question(
            self, "Confirma", f"Apagar {count} item(s) selecionado(s)?"
        )
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect("clips.db")
            cursor = conn.cursor()
            for row in selected_rows:
                item_id = int(self.table.item(row, 0).text())
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = ?", (item_id,))
            conn.commit()
            conn.close()
            self.load_items()