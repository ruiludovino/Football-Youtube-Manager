import os
import subprocess
import re
import configparser
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QProgressBar, QPushButton, QScrollArea,
    QFrame, QSizePolicy, QHBoxLayout, QTextEdit,
    QMenu, QAction, QInputDialog, QMessageBox, QLineEdit,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QRect, QSize, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

# =====================================================================
# CONFIGURAÇÕES GLOBAIS
# =====================================================================
PASTA_VIDEOS_SHORTS = r"G:\Football Architects\Shorts"
PASTA_VIDEOS_LONGOS = r"G:\Football Architects\Videos Longos"
FICHEIRO_CONFIG_BASE = "Configuracao.txt"

FILE_LONGOS = "VideosLongos.txt"
FILE_SHORTS = "VideosShorts.txt"

ETAPAS_LONGOS = [
    "Baixei Original", "No Capcut", "Intro (6s)", "Separar\n    Audio", "Audio\n     Original", "Separar\n    Cenas",
    "Video\n    140-160%", "Relâmpagos\n       e Efeitos", "Bola Mesma\n    Pos.Trans.", "Música\n   de Fundo",
    "Transições", "Comentários", "Legendas", "Logo\n    Do Canal", "Testar no Youtube", "Ajustes Cor",
    "Público", "Público\n   (Golos)", "Setas Nos\n  Jogadores", "Highlight\n   Startrek", "Next Videos\n       Text",
    "Relógio", "Som Do Relógio", "Caixa Registadora", "Som dos Chutes", "Efeito Verde\\Vermelho",
    "Melhorar Com IA", "Melhorar com 4K", "Criei Versão Final" , "Apaguei Teste YT", "Miniatura", "Carregado\n   No YouTube", "Golos Na BD", "Terminado"
]

ETAPAS_SHORTS = [
    "Baixei Original", "No Capcut", "Separar\n    Audio", "Titulo Y»1300", "Audio\n     Original", "Separar\n    Cenas",
    "Video 316-200%", "Relâmpagos\n       e Efeitos", "Bola Mesma\n    Pos.Trans.", "Música\n   de Fundo",
    "Transições", "Comentários", "Legendas", "Logo\n    Do Canal", "Testar no Youtube", "Ajustes Cor",
    "Público", "Público\n   (Golos)", "Setas Nos\n  Jogadores", "Highlight\n   Startrek",
    "Relógio", "Som Do Relógio", "Caixa Registadora", "Som dos Chutes", "Efeito Verde\\Vermelho",
    "Melhorar Com IA", "Melhorar com 4K", "Criei Versão Final" , "Apaguei Teste YT", "Criei Versão Longo", "Carregado\n   No YouTube",  "Carreguei No Tiktok",
    "Carreguei No Insta", "Terminado"
]


def limpar_chave(etapa):
    # Remove \n, reduz múltiplos espaços para um, remove espaços extras, e converte para minúsculas
    limpo = re.sub(r'\s+', ' ', etapa.replace('\n', '')).strip()
    return limpo.lower()

    
ETAPAS_KEYS_LONGOS = [limpar_chave(e) for e in ETAPAS_LONGOS]
ETAPAS_KEYS_SHORTS = [limpar_chave(e) for e in ETAPAS_SHORTS]


class QSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, initial=False):
        super().__init__(parent)
        self._checked = initial
        self.setFixedSize(62, 34)
        self._circle_position = 4
        self.animation = QPropertyAnimation(self, b"circle_position")
        self.animation.setDuration(180)

    @property
    def circle_position(self):
        return self._circle_position

    @circle_position.setter
    def circle_position(self, value):
        self._circle_position = value
        self.update()

    def sizeHint(self):
        return QSize(62, 34)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()

    def toggle(self):
        self._checked = not self._checked
        self.animation.stop()
        self.animation.setStartValue(self.circle_position)
        self.animation.setEndValue(28 if self._checked else 4)
        self.animation.start()
        self.toggled.emit(self._checked)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bg_color = QColor("#28a745") if self._checked else QColor("#6c757d")
        painter.setPen(Qt.NoPen)
        painter.setBrush(bg_color)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 17, 17)
        painter.setBrush(QColor("white"))
        painter.drawEllipse(int(self.circle_position), 4, 26, 26)
        painter.setPen(QColor("white"))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        if self._checked:
            painter.drawText(QRect(8, 2, 20, 30), Qt.AlignCenter, "ON")
        else:
            painter.drawText(QRect(34, 2, 20, 30), Qt.AlignCenter, "OFF")


class ProjetoCard(QFrame):
    def __init__(self, nome, estados, janela):
        super().__init__()
        self.nome_projeto = nome
        self.estados = estados
        self.janela = janela
        self.botoes_etapas = {}  # key → QPushButton

        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumWidth(1600)
        self.setMaximumWidth(2000)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.setStyleSheet("""
            background-color: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #dee2e6;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)          # reduz espaçamento vertical geral

        # Linha única: título | progresso | [espaço] | ícones de ação + botão Etapas
        main_header = QHBoxLayout()
        main_header.setContentsMargins(0, 0, 0, 8)
        main_header.setSpacing(12)

        # Título à esquerda
        titulo = QLabel(self.nome_projeto)
        titulo.setCursor(Qt.PointingHandCursor)  # mostra a mãozinha ao passar o mouse
        titulo.setContextMenuPolicy(Qt.CustomContextMenu)  # ativa menu de contexto (botão direito)
        titulo.customContextMenuRequested.connect(self._copiar_nome_projeto)
        titulo.mousePressEvent = self._titulo_clicked  # mantém o clique esquerdo funcionando
        titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")
        titulo.setWordWrap(True)
        main_header.addWidget(titulo, stretch=1)

        # Progresso (pequeno)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFixedWidth(100)
        self.progress.setFixedHeight(18)
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p%")
        self.atualizar_progresso()
        main_header.addWidget(self.progress)

        # Espaço flexível
        main_header.addStretch()

        # Container horizontal para os ícones + botão Etapas
        actions_container = QHBoxLayout()
        actions_container.setSpacing(6)
        actions_container.setContentsMargins(0, 0, 0, 0)

        icon_style = """
            QPushButton {
                background-color: %s;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 18px;
                min-width: 40px;
                max-width: 40px;
                height: 40px;
            }
            QPushButton:hover {
                background-color: %s;
            }
        """

        btn_ativar = QPushButton("✓")
        btn_ativar.setToolTip("Ativar Todos")
        btn_ativar.setStyleSheet(icon_style % ("#28a745", "#218838"))
        btn_ativar.clicked.connect(self.ativar_todos)
        actions_container.addWidget(btn_ativar)

        btn_desativar = QPushButton("✗")
        btn_desativar.setToolTip("Desativar Todos")
        btn_desativar.setStyleSheet(icon_style % ("#dc3545", "#c82333"))
        btn_desativar.clicked.connect(self.desativar_todos)
        actions_container.addWidget(btn_desativar)

        btn_apagar = QPushButton("🗑")
        btn_apagar.setToolTip("Apagar")
        btn_apagar.setStyleSheet(icon_style % ("#c82333", "#a71d2a"))
        btn_apagar.clicked.connect(lambda: self.janela.apagar_projeto(self.nome_projeto))
        actions_container.addWidget(btn_apagar)

        btn_mudar_nome = QPushButton("✏")
        btn_mudar_nome.setToolTip("Mudar Nome")
        btn_mudar_nome.setStyleSheet(icon_style % ("#0d6efd", "#0b5ed7"))
        btn_mudar_nome.clicked.connect(self.mudar_nome_projeto)
        actions_container.addWidget(btn_mudar_nome)

        # Botões que aparecem em LONGOS e SHORTS
        btn_pasta = QPushButton("📁")
        btn_pasta.setToolTip("Abrir Pasta")
        btn_pasta.setStyleSheet(icon_style % ("#6f42c1", "#5a32a3"))
        btn_pasta.clicked.connect(self.abrir_pasta_projeto)
        actions_container.addWidget(btn_pasta)

        btn_config = QPushButton("⚙")
        btn_config.setToolTip("Abrir Configuração")
        btn_config.setStyleSheet(icon_style % ("#17a2b8", "#138496"))
        btn_config.clicked.connect(self.abrir_configuracao)
        actions_container.addWidget(btn_config)

        # Botões exclusivos de LONGOS
        if self.janela.modo_atual == "longos":
            btn_shots = QPushButton("🎬")
            btn_shots.setToolTip("Criar Shots")
            btn_shots.setStyleSheet(icon_style % ("#fd7e14", "#e06b00"))
            btn_shots.clicked.connect(lambda: self.janela.criar_shorts_para_este_longo(self.nome_projeto))
            actions_container.addWidget(btn_shots)

            btn_historico = QPushButton("📦")
            btn_historico.setToolTip("Colocar no Histórico (apenas projetos 100% concluídos)")
            if self.janela.is_projeto_completo(self.estados):
                btn_historico.setStyleSheet(icon_style % ("#6f42c1", "#5a32a3"))
            else:
                btn_historico.setStyleSheet(icon_style % ("#6c757d", "#5a6268"))
                btn_historico.setEnabled(False)
                btn_historico.setText("📦")
            btn_historico.clicked.connect(self.colocar_no_historico)
            actions_container.addWidget(btn_historico)

        # Botão Etapas no final
        self.expand_btn = QPushButton("▼ Etapas")
        self.expand_btn.setCheckable(True)
        self.expand_btn.setFixedHeight(28)
        self.expand_btn.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:checked {
                background-color: #138496;
            }
        """)

        # ← COLOQUE ESTA LINHA AQUI (é esta que faltava)
        self.expand_btn.toggled.connect(self.toggle_etapas)

        actions_container.addWidget(self.expand_btn)

        main_header.addLayout(actions_container)
        layout.addLayout(main_header)

        # Container expansível para as etapas
        self.etapas_widget = QWidget()
        etapas_layout = QVBoxLayout(self.etapas_widget)
        etapas_layout.setContentsMargins(0, 0, 0, 0)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setContentsMargins(8, 8, 8, 8)

        displays = self.janela.get_displays()
        keys = self.janela.get_keys()

        for i, texto in enumerate(displays):
            key = keys[i]
            btn = QPushButton(texto)
            btn.setFixedHeight(52)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCheckable(True)
            btn.setChecked(estados.get(key, False))

            self.botoes_etapas[key] = btn

            if texto == "Intro (6s)":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_intro(b))
            elif texto == "Bola Mesma\n    Pos.Trans.":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_bola_mesma_pos(b))
            elif texto == "Ajustes Cor":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_ajustes_cor(b))
            elif texto == "Relâmpagos\n       e Efeitos":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_relampagos_efeitos(b))
            elif texto == "Logo\n    Do Canal":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_logo_canal(b))
            elif texto == "Transições":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_transicoes(b))
            elif texto == "Audio\n     Original":
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(lambda pos, b=btn: self.mostrar_menu_audio_original(b))

            self.atualizar_estilo(btn, texto)
            btn.clicked.connect(lambda _, k=key, b=btn: self.toggle_etapa(k, b))

            grid.addWidget(btn, i // 10, i % 10)

        # ─── CAMPO DE NOTAS ─────────────────────────────────
        self.notas_edit = QTextEdit()
        self.notas_edit.setPlaceholderText("Notas, lembretes, observações...")
        self.notas_edit.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: none;
                border-radius: 0;
                padding: 6px 8px;
                font-size: 13px;
                margin: 0;
            }
            QTextEdit:focus {
                border: none;
                outline: none;
            }
        """)
        self.notas_edit.setMinimumHeight(60)
        self.notas_edit.setMaximumHeight(140)
        self.notas_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.notas_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.notas_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Carregar notas existentes
        if self.janela.modo_atual == "longos":
            pasta_base = PASTA_VIDEOS_LONGOS
            caminho_notas = os.path.join(pasta_base, self.nome_projeto, "notas.txt")
        else:
            nome_seguro = re.sub(r'[<>:"/\\|?*]', '_', self.nome_projeto)
            caminho_notas = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_seguro}_notas.txt")

        if os.path.isfile(caminho_notas):
            try:
                with open(caminho_notas, "r", encoding="utf-8") as f:
                    conteudo = f.read().strip()
                    self.notas_edit.setPlainText(conteudo)
            except Exception as e:
                print(f"Erro ao ler notas de {caminho_notas}: {e}")

        self.notas_edit.textChanged.connect(self.salvar_notas)

        etapas_layout.addSpacing(10)
        etapas_layout.addWidget(self.notas_edit)
        etapas_layout.addSpacing(6)
        etapas_layout.addLayout(grid)
        layout.addWidget(self.etapas_widget)

        self.atualizar_cor_titulo_por_ia()

        self.etapas_widget.hide()
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

    def atualizar_cor_titulo_por_ia(self):
        """Muda a cor do nome do projeto para vermelho apenas se:
           - 'Melhorar Com IA' NÃO estiver concluído
           - E o projeto ESTIVER em 'Testar no Youtube' (etapa marcada)
        """
        if self.janela.modo_atual != "longos":
            return

        # Chaves das etapas (devem bater exatamente com ETAPAS_KEYS_LONGOS)
        key_ia = "melhorar com ia"
        key_testar = "testar no youtube"

        btn_ia = self.botoes_etapas.get(key_ia)
        btn_testar = self.botoes_etapas.get(key_testar)

        # Se alguma das duas etapas não existir no dicionário → não altera nada
        if not btn_ia or not btn_testar:
            titulo = self.findChild(QLabel)
            if titulo:
                titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")
            return

        em_teste = btn_testar.isChecked()  # True = verde / em teste
        ia_pendente = not btn_ia.isChecked()  # True = vermelho / pendente

        deve_ficar_vermelho = em_teste and ia_pendente

        titulo = self.findChild(QLabel)  # o QLabel do nome do projeto

        if titulo:
            if deve_ficar_vermelho:
                titulo.setStyleSheet("""
                    font-size: 15px;
                    font-weight: bold;
                    color: #dc3545;
                    background: rgba(220, 53, 69, 0.08);
                    border-radius: 4px;
                    padding: 2px 6px;
                """)
            else:
                titulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #2c3e50;")

    def _titulo_clicked(self, event):
        if event.button() == Qt.LeftButton:
            # Inverte o estado (expande se estava fechado, fecha se estava aberto)
            novo_estado = not self.expand_btn.isChecked()
            self.expand_btn.setChecked(novo_estado)
            # O resto (mostrar/esconder, mudar texto do botão, ajustar altura) acontece sozinho

    def _copiar_nome_projeto(self, pos):
        """Copia o nome e mostra uma mensagem flutuante que some sozinha em 2 segundos"""
        # Copia para o clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(self.nome_projeto)

        # Cria uma label flutuante (não bloqueia o programa)
        msg = QLabel(f"Copiado: {self.nome_projeto}", self)
        msg.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 13px;
            border: 1px solid #34495e;
        """)
        msg.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        msg.adjustSize()

        # Posiciona no centro do card ou no mouse
        global_pos = self.mapToGlobal(self.rect().center())
        msg.move(global_pos.x() - msg.width() // 2, global_pos.y() - msg.height() // 2 - 50)

        # Mostra e fecha sozinho após 1000 ms (1 segundo)
        msg.show()
        QTimer.singleShot(1000, msg.deleteLater)

    def toggle_etapas(self, checked):
        self.etapas_widget.setVisible(checked)
        self.expand_btn.setText("▲ Etapas" if checked else "▼ Etapas")

        if checked:
            num_linhas_grid = (len(self.janela.get_displays()) + 9) // 10
            altura_grid = num_linhas_grid * 60 + 40
            altura_notas = 140
            altura_total = 120 + altura_grid + altura_notas
            self.setMinimumHeight(min(altura_total, 700))
            self.setMaximumHeight(16777215)
        else:
            self.setMinimumHeight(80)
            self.setMaximumHeight(100)

    def colocar_no_historico(self):
        if self.janela.modo_atual != "longos":
            return

        if not self.janela.is_projeto_completo(self.estados):
            QMessageBox.information(
                self, "Não concluído",
                "Este projeto ainda não está 100% concluído.\nTodos os passos devem estar verdes."
            )
            return

        reply = QMessageBox.question(
            self, "Colocar no Histórico",
            f"Deseja realmente arquivar o projeto **{self.nome_projeto}**?\n\n"
            "Esta ação irá:\n"
            "• Mover a pasta do projeto para uma pasta de arquivo\n"
            "• Remover o projeto da lista atual\n\n"
            "Não é possível desfazer.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        pastas_historico = self.janela.listar_pastas_historico()

        if not pastas_historico:
            QMessageBox.warning(
                self, "Sem pastas de arquivo",
                f"Não foram encontradas pastas que não comecem por número em:\n{PASTA_VIDEOS_LONGOS}\n\n"
                "Crie pelo menos uma pasta (ex: 'Histórico 2025', 'Arquivados', 'Concluídos', etc.)"
            )
            return

        pasta_escolhida, ok = QInputDialog.getItem(
            self, "Escolher pasta de destino",
            "Para qual pasta deseja mover este projeto?",
            pastas_historico, 0, False
        )

        if not ok or not pasta_escolhida:
            return

        if self.janela.mover_para_historico(self.nome_projeto, pasta_escolhida):
            QMessageBox.information(
                self, "Projeto arquivado",
                f"O projeto foi movido com sucesso para:\n{pasta_escolhida}/{self.nome_projeto}\n\n"
                "Já foi removido da lista ativa."
            )
            self.janela.carregar_projetos()

    def mudar_nome_projeto(self):
        match = re.match(r'^\d+\s*-\s*(.+)$', self.nome_projeto.strip())
        texto_inicial = match.group(1) if match else self.nome_projeto

        nome_novo_base, ok = QInputDialog.getText(
            self, "Mudar Nome do Projeto",
            "Novo título (sem o número):", text=texto_inicial
        )
        if ok and nome_novo_base.strip():
            self.janela.renomear_projeto(self.nome_projeto, nome_novo_base.strip())

    def ativar_todos(self):
        for key in self.janela.get_keys():
            self.estados[key] = True
        self.atualizar_todos_botoes()
        self.atualizar_progresso()
        self.atualizar_cor_titulo_por_ia()
        self.janela.salvar()

    def desativar_todos(self):
        for key in self.janela.get_keys():
            self.estados[key] = False
        self.atualizar_todos_botoes()
        self.atualizar_progresso()
        self.atualizar_cor_titulo_por_ia()
        self.janela.salvar()

    def atualizar_todos_botoes(self):
        for key, btn in self.botoes_etapas.items():
            if key in self.estados:
                btn.setChecked(self.estados[key])
                try:
                    idx = self.janela.get_keys().index(key)
                    display = self.janela.get_displays()[idx]
                    self.atualizar_estilo(btn, display)
                except (ValueError, IndexError):
                    pass

    def atualizar_estilo(self, btn, texto):
        if btn.isChecked():
            btn.setStyleSheet("""
                QPushButton {
                    background: #28a745;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #218838;
                }
            """)
            btn.setText(f"✓ {texto}")
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: #c82333;
                }
            """)
            btn.setText(f"✗ {texto}")

        btn.style().unpolish(btn)
        btn.style().polish(btn)
        btn.update()

    def atualizar_progresso(self):
        total = len(self.estados)
        concluidos = sum(1 for v in self.estados.values() if v)
        perc = (concluidos / total * 100) if total > 0 else 0
        self.progress.setValue(int(perc))

    def toggle_etapa(self, key, btn):
        if key not in self.estados:
            self.estados[key] = False
        self.estados[key] = btn.isChecked()
        displays = self.janela.get_displays()
        try:
            idx = self.janela.get_keys().index(key)
            self.atualizar_estilo(btn, displays[idx])
        except (ValueError, IndexError):
            pass
        self.atualizar_progresso()
        self.janela.salvar()
        self.atualizar_cor_titulo_por_ia()

    def mostrar_menu_intro(self, button):
        msg = QMessageBox(self)
        msg.setWindowTitle("Instruções - Intro (6s)")
        msg.setIcon(QMessageBox.Information)

        texto = (
            "Intro »» VIDEO »» Basico »» Mistura »» Opacidade\n\n"
            "    • pega 2 clips de 3 segundos\n"
            "    • coloca eles mais transparentes para ficarem mais escuros 50%\n"
            "    • Adiciona texto:\n"
            "         com o jogo do tipo \"ARSENAL X MAN UNITED\" itálico\n"
            "         PODE COLOCAR observação como \"LAST MINUTE DRAMA\""
        )

        msg.setText(texto)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        # Opcional: deixar um pouco maior / mais legível
        msg.setStyleSheet("""
            QMessageBox {
                font-family: Consolas;
                font-size: 13px;
            }
            QLabel {
                min-width: 480px;
            }
        """)

        msg.exec_()  # <-- bloqueia até clicar OK

    def mostrar_menu_bola_mesma_pos(self, button):
        msg = QMessageBox(self)
        msg.setWindowTitle("Bola Mesma Posição na Transição")
        msg.setIcon(QMessageBox.Information)

        texto = (
            "Na transição de um clip para outro,\n"
            "tente colocar a bola na mesma posição na tela\n"
            "para facilitar o acompanhamento do espectador.\n\n"
            "Isso cria uma continuidade visual mais fluida\n"
            "e torna a edição mais profissional."
        )

        msg.setText(texto)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        # Estilo para ficar mais legível e com aparência próxima do que você usava
        msg.setStyleSheet("""
            QMessageBox {
                font-family: Consolas, monospace;
                font-size: 13px;
            }
            QLabel {
                min-width: 420px;
                color: #e0e0ff;
                background-color: #1e1e1e;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #0d6efd;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)

        msg.exec_()  # Só fecha quando clicar em OK

    def mostrar_menu_ajustes_cor(self, button):
        msg = QMessageBox(self)
        msg.setWindowTitle("Instruções - Ajustes de Cor")
        msg.setIcon(QMessageBox.Information)

        texto = (
            "Ajustes de cor no CapCut\n\n"
            "Ajuste → Adjustments (Ajustar)\n\n"
            "• Temp:          -5\n"
            "• Tint (Matiz):  -5\n"
            "• Saturation (Saturação):   +6\n"
            "• Contraste:     6\n"
            "• Highlight / Destacar:  24"
        )

        msg.setText(texto)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        # Estilo para ficar mais legível e com aparência próxima ao que você usava
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
                color: #e0ffff;
                font-family: Consolas;
                font-size: 13px;
            }
            QLabel {
                min-width: 420px;
                padding: 10px;
            }
            QPushButton {
                background-color: #005566;
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007080;
            }
        """)

        # Exibe a mensagem e bloqueia até o usuário clicar em OK
        msg.exec_()

    def mostrar_menu_relampagos_efeitos(self, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1e1e1e; color: #ffe0e0; font-family: Consolas; font-size: 13px; padding: 10px 16px; }
            QMenu::item { padding: 6px 36px 6px 12px; }
            QMenu::item:selected { background-color: #800000; color: white; }
        """)
        font_mono = QFont("Consolas", 12)

        linhas = [
            "Colocar relâmpagos",
            "nas comemorações",
            "ou outros efeitos"
        ]

        for texto in linhas:
            action = QAction(texto, self)
            action.setFont(font_mono)
            action.setEnabled(False)
            menu.addAction(action)

        pos = button.mapToGlobal(QPoint(0, button.height() + 4))
        menu.exec_(pos)

    def mostrar_menu_logo_canal(self, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1e1e1e; color: #e0e0ff; font-family: Consolas; font-size: 13px; padding: 10px 16px; }
            QMenu::item { padding: 5px 32px 5px 12px; }
            QMenu::item:selected { background-color: #003366; color: white; }
        """)
        font_mono = QFont("Consolas", 12)

        linhas = [
            "Logo do Canal em todo o video",
            "com 20-30% transparente",
            "Ir a 'Básico »» Mistura »» Opacidade'"
        ]

        for texto in linhas:
            action = QAction(texto, self)
            action.setFont(font_mono)
            action.setEnabled(False)
            menu.addAction(action)

        pos = button.mapToGlobal(QPoint(0, button.height() + 4))
        menu.exec_(pos)

    def mostrar_menu_transicoes(self, button):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1e1e1e; color: #e0e0e0; font-family: Consolas; font-size: 13px; padding: 10px 16px; }
            QMenu::item { padding: 6px 32px 6px 12px; }
            QMenu::item:selected { background-color: #444; color: white; }
        """)
        font_mono = QFont("Consolas", 12)

        action = QAction("colocar transições entre clips", self)
        action.setFont(font_mono)
        action.setEnabled(False)
        menu.addAction(action)

        pos = button.mapToGlobal(QPoint(0, button.height() + 4))
        menu.exec_(pos)

    def mostrar_menu_audio_original(self, button):
        msg = QMessageBox(self)
        msg.setWindowTitle("Instruções - Áudio Original")
        msg.setIcon(QMessageBox.Information)

        texto = (
            "Se usar o áudio original:\n\n"
            "• Ativar a opção **Normalize Loudness**\n\n"
            "Isso ajuda a manter o volume consistente e evita que o áudio fique muito baixo ou distorcido."
        )

        msg.setText(texto)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setDefaultButton(QMessageBox.Ok)

        # Estilo para ficar mais legível e com aparência próxima do que você usava
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #1e1e1e;
                color: #d0ffd0;
                font-family: Consolas;
                font-size: 13px;
            }
            QLabel {
                min-width: 420px;
                padding: 8px;
            }
            QPushButton {
                background-color: #006633;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #007744;
            }
        """)

        msg.exec_()  # Abre a caixa e só fecha quando clicar em OK

    def abrir_pasta_projeto(self):
        if self.janela.modo_atual == "longos":
            caminho = os.path.join(PASTA_VIDEOS_LONGOS, self.nome_projeto)
        else:
            caminho = os.path.join(PASTA_VIDEOS_SHORTS)

        if not os.path.isdir(caminho):
            QMessageBox.warning(
                self, "Pasta não encontrada",
                f"Não encontrei a pasta:\n\n{caminho}\n\n"
                "Verifica se o nome do projeto está correto."
            )
            return

        try:
            subprocess.Popen(f'explorer "{caminho}"')
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não consegui abrir a pasta:\n{str(e)}")

    def abrir_configuracao(self):
        if self.janela.modo_atual == "longos":
            pasta_projeto = os.path.join(PASTA_VIDEOS_LONGOS, self.nome_projeto)
            caminho_arquivo = os.path.join(pasta_projeto, "Configuracao.txt")
        else:
            pasta_projeto = os.path.join(PASTA_VIDEOS_SHORTS, self.nome_projeto)
            caminho_arquivo = os.path.join(PASTA_VIDEOS_SHORTS, self.nome_projeto+".txt")
            modelo = os.path.join(PASTA_VIDEOS_SHORTS, "Configuracao - modelo.txt")



        # Se o ficheiro NÃO existir e for modo SHORTS → copiar o modelo
        if self.janela.modo_atual == "shorts" and not os.path.isfile(caminho_arquivo):


            if not os.path.isfile(modelo):
                QMessageBox.warning(
                    self, "Modelo não encontrado",
                    f"Não encontrei o ficheiro modelo:\n{modelo}\n\n"
                    "Crie o ficheiro 'Configuracao - modelo.txt' na pasta de Shorts."
                )
                return

            try:
                shutil.copy2(modelo, caminho_arquivo)
                print(f"[INFO] Copiado modelo para: {caminho_arquivo}")
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro ao copiar modelo",
                    f"Não consegui copiar o modelo:\n{str(e)}"
                )
                return

        # Agora verifica novamente (caso tenha copiado ou já existia)
        if not os.path.isfile(caminho_arquivo):
            QMessageBox.warning(
                self, "Ficheiro não encontrado",
                f"Não encontrei o ficheiro:\n\n{caminho_arquivo}\n\n"
                "Verifique se o arquivo 'Configuracao.txt' existe na pasta do projeto."
            )
            return

        try:
            subprocess.Popen(['notepad.exe', caminho_arquivo])
        except Exception as e:
            QMessageBox.critical(
                self, "Erro ao abrir ficheiro",
                f"Não consegui abrir o Configuracao.txt:\n{str(e)}"
            )

    def salvar_notas(self):
        texto = self.notas_edit.toPlainText().strip()

        if not texto:
            return

        self.estados['notas'] = texto
        self.janela.salvar()

        if self.janela.modo_atual == "longos":
            pasta_base = PASTA_VIDEOS_LONGOS
            caminho_notas = os.path.join(pasta_base, self.nome_projeto, "notas.txt")
        else:
            nome_seguro = re.sub(r'[<>:"/\\|?*]', '_', self.nome_projeto.strip())
            caminho_notas = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_seguro}_notas.txt")

        try:
            with open(caminho_notas, "w", encoding="utf-8") as f:
                f.write(texto)
        except Exception as e:
            print(f"[DEBUG NOTAS] ERRO no ficheiro separado {caminho_notas}: {type(e).__name__} - {str(e)}")


class DashboardProjetos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Football Architects - Dashboard")
        self.setGeometry(100, 50, 1800, 900)

        self.modo_atual = "longos"
        self.projetos_longos = {}
        self.projetos_shorts = {}
        self.search_term = ""

        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 10)

        header = QHBoxLayout()
        header.setContentsMargins(25, 15, 25, 10)
        header.setSpacing(20)

        self.lbl_titulo = QLabel("Vídeos Longos")
        self.lbl_titulo.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        header.addWidget(self.lbl_titulo)
        header.addStretch()

        filtro_layout = QHBoxLayout()
        filtro_layout.setSpacing(12)

        self.btn_sendo_feitos = QPushButton("Sendo Feitos")
        self.btn_em_teste = QPushButton("Em Teste no Youtube")
        self.btn_terminados = QPushButton("Terminados")

        botoes_filtro = [
            (self.btn_sendo_feitos, "sendo_feitos"),
            (self.btn_em_teste, "em_teste"),
            (self.btn_terminados, "terminados")
        ]

        for btn, nome_filtro in botoes_filtro:
            btn.setCheckable(True)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background: #6c757d; 
                    color: white; 
                    border: none; 
                    border-radius: 6px; 
                    padding: 8px 16px; 
                    font-weight: bold;
                }
                QPushButton:checked {
                    background: #0d6efd;
                }
                QPushButton:hover {
                    background: #5a6268;
                }
            """)
            filtro_layout.addWidget(btn)

        self.btn_sendo_feitos.setChecked(True)
        self.filtro_atual = "sendo_feitos"

        self.btn_sendo_feitos.clicked.connect(lambda: self.mudar_filtro("sendo_feitos"))
        self.btn_em_teste.clicked.connect(lambda: self.mudar_filtro("em_teste"))
        self.btn_terminados.clicked.connect(lambda: self.mudar_filtro("terminados"))

        header.addLayout(filtro_layout)
        header.addStretch()
        self.main_layout.addLayout(header)

        # Barra de pesquisa
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(25, 0, 25, 10)
        search_label = QLabel("Procurar:")
        search_label.setStyleSheet("font-size: 16px; color: #2c3e50;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Digite o nome do projeto...")
        self.search_input.setStyleSheet("padding: 8px; border: 1px solid #dee2e6; border-radius: 6px;")
        self.search_input.textChanged.connect(self.filtrar_projetos)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        self.main_layout.addLayout(search_layout)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_longos = QPushButton("Ver Longos")
        btn_longos.setStyleSheet("padding: 10px 20px; background: #0d6efd; color: white; border-radius: 6px;")
        btn_longos.clicked.connect(lambda: self.mudar_modo("longos"))
        botoes.addWidget(btn_longos)

        btn_shorts = QPushButton("Ver Shorts")
        btn_shorts.setStyleSheet("padding: 10px 20px; background: #6610f2; color: white; border-radius: 6px;")
        btn_shorts.clicked.connect(lambda: self.mudar_modo("shorts"))
        botoes.addWidget(btn_shorts)

        self.btn_novo = QPushButton("+ Novo Longo")
        self.btn_novo.setStyleSheet(
            "padding: 12px 24px; background: #28a745; color: white; border-radius: 8px; font-weight: bold;")
        self.btn_novo.clicked.connect(self.criar_novo_projeto)
        botoes.addWidget(self.btn_novo)

        self.main_layout.addLayout(botoes)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.viewport().setAutoFillBackground(False)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        self.grid_container = QWidget()
        self.grid = QGridLayout(self.grid_container)
        self.grid.setSpacing(2)
        self.grid.setContentsMargins(4, 4, 4, 4)
        self.grid.setAlignment(Qt.AlignTop)

        scroll.setWidget(self.grid_container)
        self.main_layout.addWidget(scroll)

        btn_atualizar = QPushButton("↻ Atualizar")
        btn_atualizar.setStyleSheet(
            "font-size: 14px; padding: 10px; background: #0d6efd; color: white; border-radius: 6px;")
        btn_atualizar.clicked.connect(self.carregar_projetos)
        self.main_layout.addWidget(btn_atualizar)

        self.carregar_projetos()



    def is_projeto_completo(self, estados):
        if not estados:
            return False
        return all(estados.values())

    def listar_pastas_historico(self):
        if not os.path.isdir(PASTA_VIDEOS_LONGOS):
            return []

        pastas = []
        for item in os.listdir(PASTA_VIDEOS_LONGOS):
            caminho = os.path.join(PASTA_VIDEOS_LONGOS, item)
            if os.path.isdir(caminho) and not re.match(r'^\d', item.strip()):
                pastas.append(item)

        pastas.sort()
        return pastas

    def mover_para_historico(self, nome_projeto, pasta_destino):
        origem = os.path.join(PASTA_VIDEOS_LONGOS, nome_projeto)
        destino = os.path.join(PASTA_VIDEOS_LONGOS, pasta_destino, nome_projeto)

        if not os.path.isdir(origem):
            QMessageBox.critical(self, "Erro", f"Pasta origem não encontrada:\n{origem}")
            return False

        if os.path.exists(destino):
            QMessageBox.warning(self, "Erro", f"Já existe uma pasta com esse nome em:\n{destino}")
            return False

        try:
            shutil.move(origem, destino)
            print(f"[HISTÓRICO] Movido: {origem} → {destino}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao mover", f"Não foi possível mover a pasta:\n{str(e)}")
            return False

        if nome_projeto in self.projetos_longos:
            del self.projetos_longos[nome_projeto]
            self.salvar()

        return True

    def filtrar_projetos(self, text):
        self.search_term = text.strip().lower()
        self.carregar_projetos()

    def mudar_filtro(self, novo_filtro):
        if novo_filtro == self.filtro_atual:
            return

        self.filtro_atual = novo_filtro

        self.btn_sendo_feitos.setChecked(novo_filtro == "sendo_feitos")
        self.btn_em_teste.setChecked(novo_filtro == "em_teste")
        self.btn_terminados.setChecked(novo_filtro == "terminados")

        self.carregar_projetos()

    def salvar(self):
        try:
            config = configparser.ConfigParser()
            for nome, estados in self.projetos_longos.items():
                sec = {}
                for k, v in estados.items():
                    chave_normal = limpar_chave(k)
                    if chave_normal in ETAPAS_KEYS_LONGOS:
                        sec[chave_normal] = str(v).lower()
                config[nome] = sec
            with open(FILE_LONGOS, 'w', encoding='utf-8') as f:
                config.write(f)

            config = configparser.ConfigParser()
            for nome, estados in self.projetos_shorts.items():
                sec = {}
                for k, v in estados.items():
                    chave_normal = limpar_chave(k)
                    if chave_normal in ETAPAS_KEYS_SHORTS:
                        sec[chave_normal] = str(v).lower()
                config[nome] = sec
            with open(FILE_SHORTS, 'w', encoding='utf-8') as f:
                config.write(f)

        except Exception as e:
            print(f"[ERRO AO SALVAR] {type(e).__name__}: {str(e)}")
            QMessageBox.warning(self, "Erro ao salvar", f"Não consegui salvar os ficheiros:\n{str(e)}")

    def mudar_modo(self, modo):
        if modo == self.modo_atual:
            return
        self.modo_atual = modo
        self.lbl_titulo.setText("Vídeos Longos" if modo == "longos" else "Vídeos Shorts")
        self.btn_novo.setText(f"+ Novo {'Longo' if modo == 'longos' else 'Short'}")
        self.carregar_projetos()

    def get_file(self):
        return FILE_LONGOS if self.modo_atual == "longos" else FILE_SHORTS

    def get_keys(self):
        return ETAPAS_KEYS_LONGOS if self.modo_atual == "longos" else ETAPAS_KEYS_SHORTS

    def get_displays(self):
        return ETAPAS_LONGOS if self.modo_atual == "longos" else ETAPAS_SHORTS

    def get_projetos(self):
        return self.projetos_longos if self.modo_atual == "longos" else self.projetos_shorts

    def carregar_projetos(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if w := item.widget():
                w.deleteLater()

        config = configparser.ConfigParser()
        ficheiro = self.get_file()

        projetos = self.get_projetos()
        projetos.clear()

        if os.path.exists(ficheiro):
            config.read(ficheiro, encoding='utf-8')
            for sec in config.sections():
                estados = {}
                for k in self.get_keys():
                    if '1300' in k:
                        pass
                    valor = config.getboolean(sec, k, fallback=False)
                    estados[k] = valor
                projetos[sec] = estados

        filtrados = []

        for nome, estados in projetos.items():
            terminado = estados.get("terminado", False)
            testar_youtube = estados.get("testar no youtube", False)

            if self.filtro_atual == "terminados":
                if terminado:
                    filtrados.append(nome)
            elif self.filtro_atual == "em_teste":
                if testar_youtube and not terminado:
                    filtrados.append(nome)
            else:
                if not terminado and not testar_youtube:
                    filtrados.append(nome)

        if self.search_term:
            filtrados = [n for n in filtrados if self.search_term in n.lower()]

        filtrados.sort(key=lambda x: x.strip().lower())

        if not filtrados:
            lbl = QLabel(f"Nenhum projeto em \"{self.filtro_atual.replace('_', ' ').title()}\"")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size: 18px; color: #6c757d; padding: 40px;")
            self.grid.addWidget(lbl, 0, 0)
            return

        for i, nome in enumerate(filtrados):
            card = ProjetoCard(nome, projetos[nome], self)
            self.grid.addWidget(card, i // 1, 0)

    def criar_novo_projeto(self):
        if self.modo_atual != "longos":
            nome, ok = QInputDialog.getText(self, "Novo Short",
                                            "Nome do projeto (ex: 1 - Nome do short):")
            if not ok or not nome.strip():
                return
            nome = nome.strip()

            projetos = self.get_projetos()
            if nome in projetos:
                QMessageBox.warning(self, "Erro", f"Já existe '{nome}'.")
                return

            projetos[nome] = {k: False for k in self.get_keys()}
            self.salvar()
            self.carregar_projetos()
            return

        reply = QMessageBox.question(
            self, "Novo Vídeo Longo",
            "Quer escolher uma pasta já existente ou quer começar um novo?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No
        )

        if reply == QMessageBox.Cancel:
            return

        projetos = self.get_projetos()

        if reply == QMessageBox.Yes:
            pastas_existentes = []
            if os.path.isdir(PASTA_VIDEOS_LONGOS):
                for item in os.listdir(PASTA_VIDEOS_LONGOS):
                    caminho = os.path.join(PASTA_VIDEOS_LONGOS, item)
                    if os.path.isdir(caminho):
                        if re.match(r'^\d+\s*-\s*.+$', item.strip()):
                            pastas_existentes.append(item)

            if not pastas_existentes:
                QMessageBox.information(self, "Nenhuma pasta encontrada",
                                        "Não existem pastas de projetos na localização configurada.")
                return

            pastas_existentes.sort(key=lambda x: int(re.match(r'^(\d+)', x.strip()).group(1))
            if re.match(r'^(\d+)', x.strip()) else 999999)

            escolha, ok = QInputDialog.getItem(
                self, "Escolher pasta existente",
                "Selecione a pasta que deseja usar como projeto:",
                pastas_existentes, 0, False
            )

            if not ok or not escolha:
                return

            if escolha in projetos:
                QMessageBox.information(self, "Já registado",
                                        f"A pasta '{escolha}' já está registada no dashboard.")
                return

            projetos[escolha] = {k: False for k in self.get_keys()}

            caminho_config_base = os.path.join(PASTA_VIDEOS_LONGOS, FICHEIRO_CONFIG_BASE)
            caminho_destino = os.path.join(PASTA_VIDEOS_LONGOS, escolha, FICHEIRO_CONFIG_BASE)

            if os.path.isfile(caminho_config_base) and not os.path.isfile(caminho_destino):
                try:
                    shutil.copy2(caminho_config_base, caminho_destino)
                except Exception as e:
                    print(f"[AVISO] Não consegui copiar Configuracao.txt: {e}")

            self.salvar()
            self.carregar_projetos()
            QMessageBox.information(self, "Projeto adicionado", f"Pasta existente registada:\n{escolha}")

        else:
            titulo_dialogo = "Novo Vídeo Longo"
            label_texto = "Nome do vídeo (sem número):\nEx: CR7 vs Benfica"

            nome_base, ok = QInputDialog.getText(self, titulo_dialogo, label_texto)
            if not ok or not nome_base.strip():
                return

            nome_base = nome_base.strip()

            if not os.path.isdir(PASTA_VIDEOS_LONGOS):
                QMessageBox.critical(self, "Erro", f"Pasta não encontrada:\n{PASTA_VIDEOS_LONGOS}")
                return

            maior_numero = 0
            for item in os.listdir(PASTA_VIDEOS_LONGOS):
                caminho_completo = os.path.join(PASTA_VIDEOS_LONGOS, item)
                if not os.path.isdir(caminho_completo):
                    continue
                match = re.match(r'^(\d+)\s*-\s*.+$', item.strip())
                if match:
                    num = int(match.group(1))
                    if num > maior_numero:
                        maior_numero = num

            proximo_numero = maior_numero + 1
            nome_pasta = f"{proximo_numero} - {nome_base}"
            caminho_nova_pasta = os.path.join(PASTA_VIDEOS_LONGOS, nome_pasta)

            if os.path.exists(caminho_nova_pasta):
                QMessageBox.warning(self, "Aviso", f"A pasta já existe:\n{nome_pasta}")
                return

            try:
                os.makedirs(caminho_nova_pasta)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível criar a pasta:\n{str(e)}")
                return

            caminho_config_origem = os.path.join(PASTA_VIDEOS_LONGOS, FICHEIRO_CONFIG_BASE)
            if os.path.isfile(caminho_config_origem):
                try:
                    destino_config = os.path.join(caminho_nova_pasta, FICHEIRO_CONFIG_BASE)
                    shutil.copy2(caminho_config_origem, destino_config)
                except Exception as e:
                    print(f"[AVISO] Falha ao copiar Configuracao.txt base: {e}")

            nome_projeto_registo = nome_pasta

            if nome_projeto_registo not in projetos:
                projetos[nome_projeto_registo] = {k: False for k in self.get_keys()}
                self.salvar()

            QMessageBox.information(self, "Projeto criado",
                                    f"Pasta criada:\n{nome_pasta}\n\nConfiguração copiada (se existia).")

            self.carregar_projetos()

    def criar_shorts_para_este_longo(self, nome_longo):
        if self.modo_atual != "longos":
            QMessageBox.warning(self, "Aviso", "Esta opção só funciona no modo 'Vídeos Longos'.")
            return

        qtd, ok = QInputDialog.getInt(
            self, "Quantos Shorts?",
            "Quantos shorts deseja criar?",
            3, 1, 50, 1
        )

        if not ok:
            return

        projetos_shorts = self.projetos_shorts
        nome_base = nome_longo.strip()
        criados = 0
        ja_existiam = 0

        for i in range(1, qtd + 1):
            novo_nome = f"{i} - {nome_base}"
            if novo_nome in projetos_shorts:
                ja_existiam += 1
                continue

            projetos_shorts[novo_nome] = {k: False for k in ETAPAS_KEYS_SHORTS}
            criados += 1

        if criados > 0:
            self.salvar()
            msg = f"Foram criados {criados} short(s) com sucesso!"
            if ja_existiam > 0:
                msg += f"\n{ja_existiam} já existiam."
            QMessageBox.information(self, "Sucesso", msg)
        else:
            QMessageBox.information(self, "Aviso", "Nenhum short criado (todos já existiam).")

    def apagar_projeto(self, nome_projeto):
        reply = QMessageBox.question(
            self, "Confirmar exclusão",
            f"Tem certeza que deseja apagar o projeto '{nome_projeto}'?\nEsta ação não pode ser desfeita.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            projetos = self.get_projetos()
            if nome_projeto in projetos:
                del projetos[nome_projeto]
                self.salvar()
                self.carregar_projetos()

    def renomear_projeto(self, nome_antigo, nome_novo_base):
        if not nome_novo_base or nome_novo_base.strip() == "":
            return

        nome_novo_base = nome_novo_base.strip()

        projetos = self.get_projetos()

        if self.modo_atual != "longos":
            if nome_novo_base in projetos:
                QMessageBox.warning(self, "Erro", f"Já existe '{nome_novo_base}'.")
                return

            if nome_antigo in projetos:
                # Renomear ficheiro de configuração (ex: "Nome Antigo.txt" → "Nome Novo.txt")
                caminho_antigo_txt = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_antigo}.txt")
                caminho_novo_txt = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_novo_base}.txt")
                if os.path.isfile(caminho_antigo_txt):
                    try:
                        os.rename(caminho_antigo_txt, caminho_novo_txt)
                    except Exception as e:
                        print(f"Erro ao renomear {caminho_antigo_txt}: {e}")
                        QMessageBox.warning(self, "Aviso", f"Não consegui renomear o ficheiro de configuração:\n{e}")

                # Renomear ficheiro de notas (ex: "Nome Antigo_notas.txt" → "Nome Novo_notas.txt")
                nome_antigo_seguro = re.sub(r'[<>:"/\\|?*]', '_', nome_antigo)
                nome_novo_seguro = re.sub(r'[<>:"/\\|?*]', '_', nome_novo_base)
                caminho_antigo_notas = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_antigo_seguro}_notas.txt")
                caminho_novo_notas = os.path.join(PASTA_VIDEOS_SHORTS, f"{nome_novo_seguro}_notas.txt")
                if os.path.isfile(caminho_antigo_notas):
                    try:
                        os.rename(caminho_antigo_notas, caminho_novo_notas)
                    except Exception as e:
                        print(f"Erro ao renomear {caminho_antigo_notas}: {e}")
                        QMessageBox.warning(self, "Aviso", f"Não consegui renomear o ficheiro de notas:\n{e}")

                # Atualiza o dicionário e salva
                projetos[nome_novo_base] = projetos.pop(nome_antigo)
                self.salvar()
                self.carregar_projetos()
            return

        match = re.match(r'^(\d+)\s*-\s*(.+)$', nome_antigo.strip())
        if not match:
            if nome_novo_base in projetos:
                QMessageBox.warning(self, "Erro", f"Já existe '{nome_novo_base}'.")
                return
            if nome_antigo in projetos:
                projetos[nome_novo_base] = projetos.pop(nome_antigo)
                self.salvar()
                self.carregar_projetos()
            return

        numero = match.group(1)
        nome_novo_completo = f"{numero} - {nome_novo_base}"

        if nome_novo_completo == nome_antigo:
            return

        if nome_novo_completo in projetos:
            QMessageBox.warning(self, "Erro", f"Já existe:\n{nome_novo_completo}")
            return

        caminho_antigo = os.path.join(PASTA_VIDEOS_LONGOS, nome_antigo)
        caminho_novo = os.path.join(PASTA_VIDEOS_LONGOS, nome_novo_completo)

        if not os.path.isdir(caminho_antigo):
            reply = QMessageBox.question(
                self, "Pasta não encontrada",
                f"A pasta física não foi encontrada:\n{nome_antigo}\n\n"
                "Deseja alterar apenas o nome no registo?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                projetos[nome_novo_completo] = projetos.pop(nome_antigo)
                self.salvar()
                self.carregar_projetos()
            return

        try:
            if os.path.exists(caminho_novo):
                QMessageBox.warning(self, "Erro", f"Já existe:\n{nome_novo_completo}")
                return
            os.rename(caminho_antigo, caminho_novo)
        except PermissionError:
            QMessageBox.critical(self, "Erro de permissão",
                                 "Sem permissão para renomear.\nVerifique se algum ficheiro está aberto.")
            return
        except FileExistsError:
            QMessageBox.warning(self, "Erro", "O destino já existe.")
            return
        except Exception as e:
            QMessageBox.critical(self, "Erro ao renomear", f"Não foi possível renomear:\n{str(e)}")
            return

        if nome_antigo in projetos:
            projetos[nome_novo_completo] = projetos.pop(nome_antigo)
            self.salvar()
            self.carregar_projetos()

        QMessageBox.information(self, "Sucesso",
                                f"Renomeado:\n{nome_antigo} → {nome_novo_completo}\n\n"
                                f"Pasta física também renomeada.")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = DashboardProjetos()
    window.show()
    sys.exit(app.exec_())