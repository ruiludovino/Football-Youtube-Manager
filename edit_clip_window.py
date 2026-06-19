# edit_clip_window.py

import os
import VariaveisGlobais as VG
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt

from database import (
    update_clip, get_clip_by_id,
    add_clube, add_jogador,
    get_all_clubes, get_all_jogadores
)
from manage_items_window import ManageItemsWindow

# Pasta fixa onde todos os vídeos estão guardados
DESTINATION_FOLDER = r"C:\Users\ruijl\Dropbox\Codigo\Tube Mastery Monetização\IA\Football Architects\Clips\VideosNaBD"


class EditClipWindow(QMainWindow):
    def __init__(self, clip_id, parent=None):
        super().__init__(parent=parent)
        self.clip_id = clip_id
        self.parent = parent
        self.setWindowTitle("Editar Clip")
        self.setGeometry(400, 200, 650, 850)

        # Carrega os dados do clip
        clip_data = get_clip_by_id(self.clip_id)
        if not clip_data:
            QMessageBox.critical(self, "Erro", "Clip não encontrado!")
            self.close()
            return

        (
            _id, titulo, data_jornada, tipo_jogada,
            jogador_principal, assistencia_de, clube,
            adversario, competicao, caminho_video, tags, notas,
            clube_do_jogador_principal
        ) = clip_data

        # Guarda o caminho original
        self.caminho_video_original = caminho_video or ""
        self.nome_arquivo_atual = os.path.basename(self.caminho_video_original) if self.caminho_video_original else "Sem ficheiro"

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)

        self.clubes = sorted(get_all_clubes())
        self.jogadores = sorted(get_all_jogadores())

        self.inputs = {}

        # ==================== EDIÇÃO DO NOME DO ARQUIVO ====================
        layout.addWidget(QLabel("<b>Nome Atual do Arquivo:</b>"))
        current_file_label = QLabel(self.nome_arquivo_atual)
        current_file_label.setWordWrap(True)
        current_file_label.setStyleSheet("QLabel { color: #34495e; font-size: 14px; padding: 5px; }")
        layout.addWidget(current_file_label)

        layout.addWidget(QLabel("Novo nome do arquivo (inclua a extensão se quiser mudar):"))
        self.new_filename_input = QLineEdit(self.nome_arquivo_atual)
        self.new_filename_input.setPlaceholderText("Deixe igual ou vazio para manter o nome atual")
        layout.addWidget(self.new_filename_input)

        # ==================== TÍTULO ====================
        layout.addWidget(QLabel("Título do Clip (obrigatório):"))
        self.inputs["titulo"] = QLineEdit(titulo or "")
        layout.addWidget(self.inputs["titulo"])

        # ==================== DATA / JORNADA ====================
        layout.addWidget(QLabel("Data / Jornada:"))
        self.inputs["data_jornada"] = QLineEdit(data_jornada or "")
        layout.addWidget(self.inputs["data_jornada"])

        # ==================== TIPO DE JOGADA ====================
        layout.addWidget(QLabel("Tipo de Jogada:"))
        self.inputs["tipo_jogada"] = QComboBox()
        self.inputs["tipo_jogada"].setEditable(True)
        self.inputs["tipo_jogada"].addItems(VG.TIPO_DE_JOGADA)
        self.inputs["tipo_jogada"].setCurrentText(tipo_jogada or "")
        layout.addWidget(self.inputs["tipo_jogada"])

        # ==================== JOGADOR PRINCIPAL ====================
        jogador_layout = QHBoxLayout()
        layout.addWidget(QLabel("Jogador Principal:"))
        self.inputs["jogador_principal"] = QComboBox()
        self.inputs["jogador_principal"].setEditable(True)
        self.inputs["jogador_principal"].addItems(self.jogadores)
        self.inputs["jogador_principal"].setCurrentText(jogador_principal or "")
        jogador_layout.addWidget(self.inputs["jogador_principal"])
        btn_manage_jog = QPushButton("⚙️")
        btn_manage_jog.setFixedWidth(30)
        btn_manage_jog.clicked.connect(lambda: self.open_manage("jogadores", "Jogadores"))
        jogador_layout.addWidget(btn_manage_jog)
        layout.addLayout(jogador_layout)

        # ==================== ASSISTÊNCIA DE ====================
        assist_layout = QHBoxLayout()
        layout.addWidget(QLabel("Assistência de (se aplicável):"))
        self.inputs["assistencia_de"] = QComboBox()
        self.inputs["assistencia_de"].setEditable(True)
        self.inputs["assistencia_de"].addItems(self.jogadores)
        self.inputs["assistencia_de"].setCurrentText(assistencia_de or "")
        assist_layout.addWidget(self.inputs["assistencia_de"])
        btn_manage_assist = QPushButton("⚙️")
        btn_manage_assist.setFixedWidth(30)
        btn_manage_assist.clicked.connect(lambda: self.open_manage("jogadores", "Jogadores"))
        assist_layout.addWidget(btn_manage_assist)
        layout.addLayout(assist_layout)

        # ==================== CLUBE ====================
        clube_layout = QHBoxLayout()
        layout.addWidget(QLabel("Clube:"))
        self.inputs["clube"] = QComboBox()
        self.inputs["clube"].setEditable(True)
        self.inputs["clube"].addItems(self.clubes)
        self.inputs["clube"].setCurrentText(clube or "")
        clube_layout.addWidget(self.inputs["clube"])
        btn_manage_clube = QPushButton("⚙️")
        btn_manage_clube.setFixedWidth(30)
        btn_manage_clube.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        clube_layout.addWidget(btn_manage_clube)
        layout.addLayout(clube_layout)

        # ==================== CLUBE DO JOGADOR PRINCIPAL ====================
        clube_jog_layout = QHBoxLayout()
        layout.addWidget(QLabel("Clube Do Jogador Principal:"))
        self.inputs["clube_do_jogador_principal"] = QComboBox()
        self.inputs["clube_do_jogador_principal"].setEditable(True)
        self.inputs["clube_do_jogador_principal"].addItems(self.clubes)
        self.inputs["clube_do_jogador_principal"].setCurrentText(clube_do_jogador_principal or "")
        clube_jog_layout.addWidget(self.inputs["clube_do_jogador_principal"])
        btn_manage_clube_jog = QPushButton("⚙️")
        btn_manage_clube_jog.setFixedWidth(30)
        btn_manage_clube_jog.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        clube_jog_layout.addWidget(btn_manage_clube_jog)
        layout.addLayout(clube_jog_layout)

        # ==================== ADVERSÁRIO ====================
        adversario_layout = QHBoxLayout()
        layout.addWidget(QLabel("Adversário:"))
        self.inputs["adversario"] = QComboBox()
        self.inputs["adversario"].setEditable(True)
        self.inputs["adversario"].addItems(self.clubes)
        self.inputs["adversario"].setCurrentText(adversario or "")
        adversario_layout.addWidget(self.inputs["adversario"])
        btn_manage_adv = QPushButton("⚙️")
        btn_manage_adv.setFixedWidth(30)
        btn_manage_adv.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        adversario_layout.addWidget(btn_manage_adv)
        layout.addLayout(adversario_layout)

        # ==================== COMPETIÇÃO ====================
        layout.addWidget(QLabel("Competição:"))
        self.inputs["competicao"] = QLineEdit(competicao or "")
        layout.addWidget(self.inputs["competicao"])

        # ==================== TAGS ====================
        layout.addWidget(QLabel("Tags (separadas por vírgula):"))
        self.inputs["tags"] = QLineEdit(tags or "")
        layout.addWidget(self.inputs["tags"])

        # ==================== NOTAS ====================
        layout.addWidget(QLabel("Notas:"))
        self.inputs["notas"] = QLineEdit(notas or "")
        layout.addWidget(self.inputs["notas"])

        # ==================== CAMINHO DO VÍDEO (só leitura) ====================
        layout.addWidget(QLabel("<b>Caminho Completo do Vídeo:</b>"))
        path_label = QLabel(self.caminho_video_original or "Sem caminho")
        path_label.setWordWrap(True)
        path_label.setStyleSheet("QLabel { color: #555; font-size: 12px; padding: 5px; }")
        layout.addWidget(path_label)

        # ==================== BOTÃO GUARDAR ====================
        btn_save = QPushButton("Guardar Alterações")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 15px; font-size: 16px;")
        btn_save.clicked.connect(self.save_changes)
        layout.addWidget(btn_save)

    def open_manage(self, table_name, title):
        self.manage_win = ManageItemsWindow(table_name, title)
        self.manage_win.show()
        self.manage_win.raise_()
        self.manage_win.activateWindow()

    def get_unique_filename(self, desired_filename):
        """Devolve um nome único na pasta DESTINATION_FOLDER"""
        desired_path = os.path.join(DESTINATION_FOLDER, desired_filename)
        if not os.path.exists(desired_path) or desired_path == self.caminho_video_original:
            return desired_filename

        base, ext = os.path.splitext(desired_filename)
        counter = 1
        while True:
            new_filename = f"{base} ({counter}){ext}"
            new_path = os.path.join(DESTINATION_FOLDER, new_filename)
            if not os.path.exists(new_path):
                return new_filename
            counter += 1

    def save_changes(self):
        titulo = self.inputs["titulo"].text().strip()
        if not titulo:
            QMessageBox.warning(self, "Erro", "Título do Clip é obrigatório!")
            return

        # Atualiza variáveis globais
        global last_data_jornada, last_tipo_jogada, last_clube, last_adversario, last_competicao, last_clube_do_jogador_principal
        last_data_jornada = self.inputs["data_jornada"].text().strip()
        last_tipo_jogada = self.inputs["tipo_jogada"].currentText().strip()
        last_clube = self.inputs["clube"].currentText().strip()
        last_adversario = self.inputs["adversario"].currentText().strip()
        last_competicao = self.inputs["competicao"].text().strip()
        last_clube_do_jogador_principal = self.inputs["clube_do_jogador_principal"].currentText().strip()

        clube_text = last_clube or None
        adversario_text = last_adversario or None
        jogador_text = self.inputs["jogador_principal"].currentText().strip() or None
        assistencia_text = self.inputs["assistencia_de"].currentText().strip() or None
        if assistencia_text == "---":
            assistencia_text = None
        clube_jog_text = last_clube_do_jogador_principal or None

        # Adiciona novos itens à BD
        for text, func, lista in [
            (clube_text, add_clube, self.clubes),
            (adversario_text, add_clube, self.clubes),
            (clube_jog_text, add_clube, self.clubes),
            (jogador_text, add_jogador, self.jogadores),
            (assistencia_text, add_jogador, self.jogadores)
        ]:
            if text and text not in lista:
                func(text)
                lista.append(text)

        # === TRATAMENTO DA RENOMEÇÃO DO ARQUIVO ===
        novo_nome_raw = self.new_filename_input.text().strip()
        caminho_final = self.caminho_video_original
        mensagem_extra = ""

        if novo_nome_raw and novo_nome_raw != self.nome_arquivo_atual:
            if not self.caminho_video_original or not os.path.exists(self.caminho_video_original):
                QMessageBox.warning(self, "Aviso", "O ficheiro original não existe no disco. Não foi possível renomear.")
            else:
                # Preserva extensão se o utilizador não a escreveu
                _, ext_original = os.path.splitext(self.nome_arquivo_atual)
                if not novo_nome_raw.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    novo_nome = novo_nome_raw + ext_original
                else:
                    novo_nome = novo_nome_raw

                novo_nome_unico = self.get_unique_filename(novo_nome)
                novo_caminho = os.path.join(DESTINATION_FOLDER, novo_nome_unico)

                try:
                    os.rename(self.caminho_video_original, novo_caminho)
                    caminho_final = novo_caminho
                    mensagem_extra = f"\nFicheiro renomeado para: {novo_nome_unico}"
                except Exception as e:
                    QMessageBox.warning(self, "Aviso", f"Não foi possível renomear o ficheiro:\n{str(e)}\nO nome no disco permanece o mesmo.")
                    # Continua com o caminho original

        # === UPDATE NA BASE DE DADOS ===
        data = (
            titulo,
            self.inputs["data_jornada"].text().strip(),
            self.inputs["tipo_jogada"].currentText().strip() or "Outro",
            jogador_text,
            assistencia_text,
            clube_text,
            adversario_text,
            self.inputs["competicao"].text().strip(),
            caminho_final,  # caminho atualizado se renomeação sucesso
            self.inputs["tags"].text().strip(),
            self.inputs["notas"].text().strip(),
            clube_jog_text
        )

        update_clip(self.clip_id, data)

        # QMessageBox.information(self, "Sucesso", "Clip atualizado com sucesso!" + mensagem_extra)

        if self.parent:
            self.parent.load_clips()

        self.close()