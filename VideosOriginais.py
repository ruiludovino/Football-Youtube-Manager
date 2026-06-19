#ficheiro VideosOriginais.py

import os
import sys
import pyperclip

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QMenu, QAction, QMessageBox,
    QInputDialog, QLabel, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

PASTA_VIDEOS_ORIGINAIS = r"G:\Football Architects\Videos Originais"
FICHEIRO_USADOS = "VideosOriginais.txt"


class VideosOriginais(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vídeos Originais - Disponíveis / Usados")
        self.setGeometry(300, 150, 1100, 700)
        self.setStyleSheet("background-color: #f8f9fa;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        titulo = QLabel("Vídeos Originais")
        titulo.setFont(QFont("Segoe UI", 18, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("color: #2c3e50; margin-bottom: 8px;")
        main_layout.addWidget(titulo)

        listas_layout = QHBoxLayout()
        listas_layout.setSpacing(14)
        main_layout.addLayout(listas_layout)

        # ── Esquerda: Não usados ───────────────────────────────────────
        esquerda_widget = QWidget()
        esquerda_layout = QVBoxLayout(esquerda_widget)

        label_esq = QLabel("Disponíveis (não usados)")
        label_esq.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label_esq.setStyleSheet("color: #28a745;")
        label_esq.setAlignment(Qt.AlignCenter)
        esquerda_layout.addWidget(label_esq)

        self.filtro_nao_usados = QLineEdit()
        self.filtro_nao_usados.setPlaceholderText("Filtrar por nome...")
        self.filtro_nao_usados.textChanged.connect(self.aplicar_filtro_nao_usados)
        self.filtro_nao_usados.setStyleSheet("padding: 6px; font-size: 13px;")
        esquerda_layout.addWidget(self.filtro_nao_usados)

        self.lista_nao_usados = QListWidget()
        self.configurar_lista(self.lista_nao_usados)
        esquerda_layout.addWidget(self.lista_nao_usados)

        listas_layout.addWidget(esquerda_widget, stretch=1)

        # ── Direita: Usados ────────────────────────────────────────────
        direita_widget = QWidget()
        direita_layout = QVBoxLayout(direita_widget)

        label_dir = QLabel("Já usados")
        label_dir.setFont(QFont("Segoe UI", 12, QFont.Bold))
        label_dir.setStyleSheet("color: #6c757d;")
        label_dir.setAlignment(Qt.AlignCenter)
        direita_layout.addWidget(label_dir)

        self.filtro_usados = QLineEdit()
        self.filtro_usados.setPlaceholderText("Filtrar por nome...")
        self.filtro_usados.textChanged.connect(self.aplicar_filtro_usados)
        self.filtro_usados.setStyleSheet("padding: 6px; font-size: 13px;")
        direita_layout.addWidget(self.filtro_usados)

        self.lista_usados = QListWidget()
        self.configurar_lista(self.lista_usados)
        direita_layout.addWidget(self.lista_usados)

        listas_layout.addWidget(direita_widget, stretch=1)

        self.todos_itens_nao_usados = []
        self.todos_itens_usados = []

        self.carregar_videos()

        # ── Conectar duplo clique ──────────────────────────────────────
        self.lista_nao_usados.itemDoubleClicked.connect(self.on_double_click)
        self.lista_usados.itemDoubleClicked.connect(self.on_double_click)

    def configurar_lista(self, lista: QListWidget):
        lista.setFont(QFont("Consolas", 11))
        lista.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ced4da;
                border-radius: 6px;
                padding: 4px;
            }
            QListWidget::item {
                padding: 7px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        lista.setContextMenuPolicy(Qt.CustomContextMenu)
        lista.customContextMenuRequested.connect(
            lambda pos, lst=lista: self.mostrar_menu_contexto(pos, lst)
        )

    def on_double_click(self, item: QListWidgetItem):
        """Duplo clique alterna o estado (usado ↔ não usado)"""
        if not item:
            return
        nome_ficheiro = item.text()
        self.toggle_usado(nome_ficheiro)

    def carregar_videos(self):
        self.lista_nao_usados.clear()
        self.lista_usados.clear()
        self.todos_itens_nao_usados.clear()
        self.todos_itens_usados.clear()

        if not os.path.exists(PASTA_VIDEOS_ORIGINAIS):
            QMessageBox.critical(self, "Erro", f"Pasta não encontrada:\n{PASTA_VIDEOS_ORIGINAIS}")
            return

        usados = self.get_videos_usados()

        for ficheiro in sorted(os.listdir(PASTA_VIDEOS_ORIGINAIS)):
            caminho = os.path.join(PASTA_VIDEOS_ORIGINAIS, ficheiro)
            if not os.path.isfile(caminho):
                continue

            item = QListWidgetItem(ficheiro)
            item.setData(Qt.UserRole, caminho)

            if ficheiro in usados:
                item.setForeground(Qt.gray)
                item.setToolTip("Já utilizado")
                self.todos_itens_usados.append(item)
            else:
                item.setForeground(Qt.black)
                item.setToolTip("Disponível")
                self.todos_itens_nao_usados.append(item)

        self.aplicar_filtro_nao_usados()
        self.aplicar_filtro_usados()

    def aplicar_filtro_nao_usados(self):
        filtro = self.filtro_nao_usados.text().strip().lower()
        self.lista_nao_usados.clear()
        for item in self.todos_itens_nao_usados:
            if not filtro or filtro in item.text().lower():
                self.lista_nao_usados.addItem(item.clone())

    def aplicar_filtro_usados(self):
        filtro = self.filtro_usados.text().strip().lower()
        self.lista_usados.clear()
        for item in self.todos_itens_usados:
            if not filtro or filtro in item.text().lower():
                self.lista_usados.addItem(item.clone())

    def get_videos_usados(self) -> set:
        if not os.path.exists(FICHEIRO_USADOS):
            return set()
        try:
            with open(FICHEIRO_USADOS, "r", encoding="utf-8") as f:
                return {linha.strip() for linha in f if linha.strip()}
        except:
            return set()

    def salvar_videos_usados(self, usados: set):
        try:
            with open(FICHEIRO_USADOS, "w", encoding="utf-8") as f:
                for video in sorted(usados):
                    f.write(video + "\n")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar lista de usados:\n{e}")

    def apagar_ficheiro(self, nome_ficheiro: str, caminho: str):
        reply = QMessageBox.question(
            self, "Confirmar eliminação",
            f"Tem a certeza que deseja APAGAR o ficheiro?\n\n{nome_ficheiro}\n\nEsta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        try:
            os.remove(caminho)
            usados = self.get_videos_usados()
            if nome_ficheiro in usados:
                usados.remove(nome_ficheiro)
                self.salvar_videos_usados(usados)
            QMessageBox.information(self, "Sucesso", f"Ficheiro apagado:\n{nome_ficheiro}")
            self.carregar_videos()
        except PermissionError:
            QMessageBox.critical(self, "Erro", "Sem permissão para apagar.\nVerifique se o ficheiro está em uso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível apagar:\n{str(e)}")

    def toggle_usado(self, nome_ficheiro: str):
        usados = self.get_videos_usados()

        if nome_ficheiro in usados:
            usados.remove(nome_ficheiro)
        else:
            usados.add(nome_ficheiro)

        self.salvar_videos_usados(usados)
        self.carregar_videos()

        # Tenta selecionar o item na nova lista
        nova_lista = self.lista_usados if nome_ficheiro in usados else self.lista_nao_usados
        items = nova_lista.findItems(nome_ficheiro, Qt.MatchExactly)
        if items:
            nova_lista.setCurrentItem(items[0])
            nova_lista.scrollToItem(items[0])

    def criar_shorts(self, nome_original: str):
        qtd, ok = QInputDialog.getInt(
            self,
            "Criar Shorts",
            "Quantos shorts quer criar?",
            value=3,
            minValue=1,
            maxValue=50,
            step=1
        )
        if not ok:
            return

        usados = self.get_videos_usados()

        for i in range(1, qtd + 1):
            novo_nome = f"{i} - {nome_original}"
            if novo_nome not in usados:
                usados.add(novo_nome)

        self.salvar_videos_usados(usados)
        self.carregar_videos()

        QMessageBox.information(
            self,
            "Shorts criados",
            f"Foram criados {qtd} entradas de shorts para:\n{nome_original}\n\nPode ver na lista 'Já usados'."
        )

    def mostrar_menu_contexto(self, posicao, lista: QListWidget):
        item = lista.itemAt(posicao)
        if not item:
            return

        nome_ficheiro = item.text()
        caminho = item.data(Qt.UserRole)

        menu = QMenu(self)

        # ── Botão Mudar Nome ──
        acao_renomear = QAction("Mudar Nome", self)
        acao_renomear.triggered.connect(lambda: self.renomear_ficheiro(nome_ficheiro, caminho))
        menu.addAction(acao_renomear)

        # ── Novo Botão Criar Shorts ──
        acao_criar_shorts = QAction("Criar Shorts", self)
        acao_criar_shorts.triggered.connect(lambda: self.criar_shorts(nome_ficheiro))
        menu.addAction(acao_criar_shorts)

        # ── Toggle usado/não usado ──
        usados = self.get_videos_usados()
        estado = "usado" if nome_ficheiro in usados else "não usado"
        texto_toggle = f"Já Usei / Não Usei  (atualmente: {estado})"
        acao_toggle = QAction(texto_toggle, self)
        acao_toggle.triggered.connect(lambda: self.toggle_usado(nome_ficheiro))
        menu.addAction(acao_toggle)

        # ── Apagar ──
        acao_apagar = QAction("Apagar Ficheiro", self)
        acao_apagar.triggered.connect(lambda: self.apagar_ficheiro(nome_ficheiro, caminho))
        menu.addSeparator()
        menu.addAction(acao_apagar)

        # Grupo Copiar
        acao_copiar_nome = QAction("Copiar Só O Nome", self)
        acao_copiar_nome.triggered.connect(lambda: pyperclip.copy(nome_ficheiro))
        menu.addAction(acao_copiar_nome)

        acao_copiar_caminho = QAction("Copiar Caminho Completo", self)
        acao_copiar_caminho.triggered.connect(lambda: pyperclip.copy(caminho))
        menu.addAction(acao_copiar_caminho)

        # (opcional) mais uma linha de separação antes de apagar
        menu.addSeparator()
        menu.addAction(acao_apagar)

        menu.exec_(lista.viewport().mapToGlobal(posicao))

    def renomear_ficheiro(self, nome_antigo: str, caminho_antigo: str):
        novo_nome, ok = QInputDialog.getText(
            self, "Mudar Nome",
            "Novo nome (com extensão):",
            text=nome_antigo
        )
        if not ok or not novo_nome.strip():
            return

        novo_nome = novo_nome.strip()
        novo_caminho = os.path.join(PASTA_VIDEOS_ORIGINAIS, novo_nome)

        if os.path.exists(novo_caminho):
            QMessageBox.warning(self, "Erro", "Já existe um ficheiro com esse nome.")
            return

        try:
            os.rename(caminho_antigo, novo_caminho)
            usados = self.get_videos_usados()
            if nome_antigo in usados:
                usados.remove(nome_antigo)
                usados.add(novo_nome)
                self.salvar_videos_usados(usados)
            self.carregar_videos()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível renomear:\n{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = VideosOriginais()
    janela.show()
    sys.exit(app.exec_())