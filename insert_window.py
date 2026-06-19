# insert_window.py

import VariaveisGlobais as VG

import os
import shutil
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt

from database import (
    insert_clip, add_clube, add_jogador,
    get_all_clubes, get_all_jogadores
)
from manage_items_window import ManageItemsWindow

# Caminho COMPLETO e FIXO onde os vídeos serão movidos
DESTINATION_FOLDER = r"C:\Users\ruijl\Dropbox\Codigo\Tube Mastery Monetização\IA\Football Architects\Clips\VideosNaBD"

# === VARIÁVEIS GLOBAIS PARA GUARDAR OS ÚLTIMOS VALORES USADOS ===
# === VARIÁVEIS GLOBAIS PARA GUARDAR OS ÚLTIMOS VALORES USADOS ===
last_data_jornada = ""
last_tipo_jogada = ""
last_clube = ""
last_adversario = ""
last_competicao = ""
last_clube_do_jogador_principal = ""

import re

import re



class InsertWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inserir Novo Clip")
        self.setGeometry(400, 200, 650, 750)

        # Usa diretamente o caminho completo definido no topo
        self.destination_folder = DESTINATION_FOLDER

        # Cria a pasta de destino se ainda não existir
        if not os.path.exists(self.destination_folder):
            os.makedirs(self.destination_folder)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)

        self.clubes = sorted(get_all_clubes())
        self.jogadores = sorted(get_all_jogadores())

        self.inputs = {}

        # ==================== CAMINHO DO VÍDEO ====================
        path_layout = QHBoxLayout()
        layout.addWidget(QLabel("Caminho do Vídeo (obrigatório):"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Caminho obrigatório")
        path_layout.addWidget(self.path_input)
        btn_browse = QPushButton("Procurar Vídeo")
        btn_browse.clicked.connect(self.browse_file)
        path_layout.addWidget(btn_browse)
        layout.addLayout(path_layout)

        # ==================== TÍTULO ====================
        layout.addWidget(QLabel("Título do Clip (obrigatório):"))
        self.inputs["titulo"] = QLineEdit()
        layout.addWidget(self.inputs["titulo"])

        # ==================== DATA / JORNADA ====================
        layout.addWidget(QLabel("Data / Jornada (ex: Jornada 5, Final UCL 2025):"))
        self.inputs["data_jornada"] = QLineEdit()
        layout.addWidget(self.inputs["data_jornada"])

        # ==================== TIPO DE JOGADA ====================
        layout.addWidget(QLabel("Tipo de Jogada:"))
        self.inputs["tipo_jogada"] = QComboBox()
        self.inputs["tipo_jogada"].setEditable(True)
        self.inputs["tipo_jogada"].addItems(VG.TIPO_DE_JOGADA)
        layout.addWidget(self.inputs["tipo_jogada"])

        # ==================== JOGADOR PRINCIPAL ====================
        jogador_layout = QHBoxLayout()
        layout.addWidget(QLabel("Jogador Principal:"))
        self.inputs["jogador_principal"] = QComboBox()
        self.inputs["jogador_principal"].setEditable(True)
        self.inputs["jogador_principal"].addItems(self.jogadores)
        jogador_layout.addWidget(self.inputs["jogador_principal"])
        btn_manage_jog = QPushButton("⚙️")
        btn_manage_jog.setFixedWidth(30)
        btn_manage_jog.setToolTip("Gerir Jogadores")
        btn_manage_jog.clicked.connect(lambda: self.open_manage("jogadores", "Jogadores"))
        jogador_layout.addWidget(btn_manage_jog)
        layout.addLayout(jogador_layout)

        # ==================== ASSISTÊNCIA DE ====================
        assist_layout = QHBoxLayout()
        layout.addWidget(QLabel("Assistência de (se aplicável):"))
        self.inputs["assistencia_de"] = QComboBox()
        self.inputs["assistencia_de"].setEditable(True)
        self.inputs["assistencia_de"].addItems(self.jogadores)
        assist_layout.addWidget(self.inputs["assistencia_de"])
        btn_manage_assist = QPushButton("⚙️")
        btn_manage_assist.setFixedWidth(30)
        btn_manage_assist.setToolTip("Gerir Jogadores")
        btn_manage_assist.clicked.connect(lambda: self.open_manage("jogadores", "Jogadores"))
        assist_layout.addWidget(btn_manage_assist)
        layout.addLayout(assist_layout)

        # ==================== CLUBE ====================
        clube_layout = QHBoxLayout()
        layout.addWidget(QLabel("Clube:"))
        self.inputs["clube"] = QComboBox()
        self.inputs["clube"].setEditable(True)
        self.inputs["clube"].addItems(self.clubes)
        clube_layout.addWidget(self.inputs["clube"])
        btn_manage_clube = QPushButton("⚙️")
        btn_manage_clube.setFixedWidth(30)
        btn_manage_clube.setToolTip("Gerir Clubes")
        btn_manage_clube.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        clube_layout.addWidget(btn_manage_clube)
        layout.addLayout(clube_layout)

        # ==================== CLUBE DO JOGADOR PRINCIPAL ====================
        clube_jogador_layout = QHBoxLayout()
        layout.addWidget(QLabel("Clube Do Jogador Principal:"))
        self.inputs["clube_do_jogador_principal"] = QComboBox()
        self.inputs["clube_do_jogador_principal"].setEditable(True)
        self.inputs["clube_do_jogador_principal"].addItems(self.clubes)
        self.inputs["clube_do_jogador_principal"].setCurrentText("")  # começa vazio
        clube_jogador_layout.addWidget(self.inputs["clube_do_jogador_principal"])

        btn_manage_clube_jog = QPushButton("⚙️")
        btn_manage_clube_jog.setFixedWidth(30)
        btn_manage_clube_jog.setToolTip("Gerir Clubes")
        btn_manage_clube_jog.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        clube_jogador_layout.addWidget(btn_manage_clube_jog)

        layout.addLayout(clube_jogador_layout)

        # ==================== ADVERSÁRIO ====================
        adversario_layout = QHBoxLayout()
        layout.addWidget(QLabel("Adversário:"))
        self.inputs["adversario"] = QComboBox()
        self.inputs["adversario"].setEditable(True)
        self.inputs["adversario"].addItems(self.clubes)
        adversario_layout.addWidget(self.inputs["adversario"])
        btn_manage_adv = QPushButton("⚙️")
        btn_manage_adv.setFixedWidth(30)
        btn_manage_adv.setToolTip("Gerir Clubes")
        btn_manage_adv.clicked.connect(lambda: self.open_manage("clubes", "Clubes"))
        adversario_layout.addWidget(btn_manage_adv)
        layout.addLayout(adversario_layout)

        # ==================== COMPETIÇÃO ====================
        layout.addWidget(QLabel("Competição:"))
        self.inputs["competicao"] = QLineEdit()
        layout.addWidget(self.inputs["competicao"])

        # ==================== TAGS ====================
        layout.addWidget(QLabel("Tags (separadas por vírgula):"))
        self.inputs["tags"] = QLineEdit()
        layout.addWidget(self.inputs["tags"])

        # ==================== NOTAS ====================
        layout.addWidget(QLabel("Notas:"))
        self.inputs["notas"] = QLineEdit()
        layout.addWidget(self.inputs["notas"])

        # ==================== BOTÃO GUARDAR ====================
        btn_save = QPushButton("Guardar Clip")
        btn_save.setStyleSheet("background-color: #27ae60; color: white; padding: 15px; font-size: 16px;")
        btn_save.clicked.connect(self.save_clip)
        layout.addWidget(btn_save)

        # Preenche com os últimos valores usados
        self.load_last_used_values()

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self.browse_file)

    def load_last_used_values(self):
        global last_data_jornada, last_tipo_jogada, last_clube, last_adversario, last_competicao, last_clube_do_jogador_principal

        if last_data_jornada:
            self.inputs["data_jornada"].setText(last_data_jornada)

        if last_tipo_jogada:
            idx = self.inputs["tipo_jogada"].findText(last_tipo_jogada)
            if idx != -1:
                self.inputs["tipo_jogada"].setCurrentIndex(idx)
            else:
                self.inputs["tipo_jogada"].setCurrentText(last_tipo_jogada)

        if last_clube:
            idx = self.inputs["clube"].findText(last_clube)
            if idx != -1:
                self.inputs["clube"].setCurrentIndex(idx)
            else:
                self.inputs["clube"].setCurrentText(last_clube)

        if last_adversario:
            idx = self.inputs["adversario"].findText(last_adversario)
            if idx != -1:
                self.inputs["adversario"].setCurrentIndex(idx)
            else:
                self.inputs["adversario"].setCurrentText(last_adversario)

        if last_competicao:
            self.inputs["competicao"].setText(last_competicao)

        # Carrega o último valor usado para o clube do jogador principal
        # if last_clube_do_jogador_principal:
        #     idx = self.inputs["clube_do_jogador_principal"].findText(last_clube_do_jogador_principal)
        #     if idx != -1:
        #         self.inputs["clube_do_jogador_principal"].setCurrentIndex(idx)
        #     else:
        #         self.inputs["clube_do_jogador_principal"].setCurrentText(last_clube_do_jogador_principal)

    def CalculaCampos(self, titulo_sugerido):
        """
        Processa o título do vídeo e preenche automaticamente os campos da janela
        com base na ordem das partes extraídas.
        """
        if not titulo_sugerido:
            return

        # Passo 0: Tudo em maiúsculas para padronizar
        titulo_limpo = titulo_sugerido.upper()

        if "SEM ASSISTÊNCIA" in titulo_limpo:
            titulo_limpo = re.sub(r"SEM ASSISTÊNCIA", "NO ASS", titulo_limpo)

        titulo_limpo = re.sub(r"PÊNALTI", "PENALTI", titulo_limpo)
        titulo_limpo = re.sub(r"PENALTY", "PENALTI", titulo_limpo)

        # === NOVO: Adiciona '-' antes de 'ASS' se não tiver um à esquerda ===
        # Procura por ' ASS ' (com possíveis espaços antes/depois) que NÃO tenha '-' imediatamente antes
        # Usa lookahead negativo para garantir que não há '-' antes do 'ASS'
        if " NO ASS" not in titulo_limpo and "-NO ASS" not in titulo_limpo:
            titulo_limpo = re.sub(
                r'(?<!-)\b\s*ASS\s*\b',  # 'ASS' com espaços opcionais, mas sem '-' antes
                r' -ASS ',  # Substitui por ' -ASS ' (com hífen e espaços padronizados)
                titulo_limpo,
                flags=re.IGNORECASE
            )

        # Passo 1: Remove minutos como 90', 45'+ etc - nao trocar a ordem destes testes
        titulo_limpo = re.sub(r"\d+'", "", titulo_limpo)
        if "REMATE AREA" in titulo_limpo:
            titulo_limpo = re.sub(r"REMATE AREA", "GOLO REMATE AREA", titulo_limpo)
        elif "REMATE - AREA" in titulo_limpo:
            titulo_limpo = re.sub(r"REMATE - AREA", "GOLO REMATE AREA", titulo_limpo)
        else:
            titulo_limpo = re.sub(r"REMATE", "GOLO REMATE", titulo_limpo)
        if "CABECEIO" in titulo_limpo:
            titulo_limpo = re.sub(r"CABECEIO", "GOLO CABEÇA", titulo_limpo)
        elif "CABEÇA" in titulo_limpo:
            titulo_limpo = re.sub(r"CABEÇA", "GOLO CABEÇA", titulo_limpo)
        elif "CABECA" in titulo_limpo:
            titulo_limpo = re.sub(r"CABECA", "GOLO CABEÇA", titulo_limpo)
        titulo_limpo = re.sub(r"AUTO-GOLO", "AUTO GOLO", titulo_limpo)
        titulo_limpo = re.sub(r"PARIS SAINT-GERMAIN", "PSG", titulo_limpo)
        titulo_limpo = re.sub(r"--", "-", titulo_limpo)
        titulo_limpo = re.sub(r"24 25", "24/25", titulo_limpo)
        titulo_limpo = re.sub(r"23 24", "23/24", titulo_limpo)
        titulo_limpo = re.sub(r"25 26", "25/26", titulo_limpo)

        # Passo 2: Isola "NO ASS" com '-' antes e depois (para ficar como parte separada)
        titulo_limpo = re.sub(r"\b(no\s*ass)\b", r" - \1 - ", titulo_limpo, flags=re.IGNORECASE)

        # Passo 3: Converte 1 0 ou 1X0 em 1/0 (para ajudar na deteção do jogo)
        titulo_limpo = re.sub(r"(\d+)\s*[Xx]\s*(\d+)", r"\1/\2", titulo_limpo)

        # Passo 4: Divide por '-'
        partes = [parte.strip() for parte in titulo_limpo.split('-') if parte.strip()]

        # Passo 5: Deteta parte do tipo "PSG 1/0 GIRONA" e separa em duas partes: clube + adversário
        novas_partes = []
        for parte in partes:
            # Procura padrão: texto + número/número + texto
            match = re.match(r"^(.+?)\s*\d+/\d+\s+(.+)$", parte)
            if match:
                novas_partes.append(match.group(1).strip())  # Clube
                novas_partes.append(match.group(2).strip())  # Adversário
            else:
                novas_partes.append(parte)
        partes = novas_partes

        # Passo 6: Substitui 'CL' por 'CHAMPIONS LEAGUE'
        partes = ['CHAMPIONS LEAGUE' if parte == 'CL' else parte for parte in partes]

        # === PREENCHIMENTO AUTOMÁTICO DOS CAMPOS DA JANELA ===
        # Índices esperados (se existirem):
        # 0 → Competição
        # 1 → Data / Jornada
        # 2 → Clube
        # 3 → Adversário
        # 4 → Jogador Principal
        # 5 → Assistência de (se houver)
        # 6 → Tipo de Jogada (ex: NO ASS, COM ASS, GOLO REMATE, etc.)
        # 7+ → Tags (junta tudo o resto com vírgula)

        if len(partes) <= 4:
            QMessageBox.information(None, "Erro No Ficheiro",
                                    f"Não processei nada porque o nome do ficheiro é inválido\n{partes}")
            return

        # quer dizer que nao tem o campo "no ass", assim insiro
        if len(partes)>=6:
            if "GOLO" in partes[5]:
                partes.insert(5, "NO ASS")

        if len(partes) <=5:
            if partes[4]=="REMATE":
                QMessageBox.information(None, "Erro No Ficheiro", f"Não processei nada porque o nome do ficheiro é inválido\n{partes}")
                return

        if len(partes) > 0:
            self.inputs["competicao"].setText(partes[0])

        if len(partes) > 1:
            self.inputs["data_jornada"].setText(partes[1])

        if len(partes) > 2:
            clube = partes[2]
            idx = self.inputs["clube"].findText(clube)
            if idx != -1:
                self.inputs["clube"].setCurrentIndex(idx)
            else:
                self.inputs["clube"].setCurrentText(clube)

        if len(partes) > 3:
            adversario = partes[3]
            idx = self.inputs["adversario"].findText(adversario)
            if idx != -1:
                self.inputs["adversario"].setCurrentIndex(idx)
            else:
                self.inputs["adversario"].setCurrentText(adversario)

        if len(partes) > 4:
            jogador = partes[4]
            idx = self.inputs["jogador_principal"].findText(jogador)
            if idx != -1:
                self.inputs["jogador_principal"].setCurrentIndex(idx)
            else:
                self.inputs["jogador_principal"].setCurrentText(jogador)

        if len(partes) > 5:
            if partes[5] not in VG.TIPO_DE_JOGADA_ESPECIAL:
                assistencia = partes[5]
                # Especial: "NO ASS" → Golo sem assistência
                if "NO ASS" in assistencia:
                    assistencia = "---"  # ou outro que prefiras
                elif "ASS " in assistencia:
                    assistencia = assistencia.replace("ASS ", "")
                idx = self.inputs["assistencia_de"].findText(assistencia)
                if idx != -1:
                    self.inputs["assistencia_de"].setCurrentIndex(idx)
                else:
                    self.inputs["assistencia_de"].setCurrentText(assistencia)

        if len(partes) > 6:
            tipo_jogada = partes[6]
            idx = self.inputs["tipo_jogada"].findText(tipo_jogada)
            if idx != -1:
                self.inputs["tipo_jogada"].setCurrentIndex(idx)
            else:
                self.inputs["tipo_jogada"].setCurrentText(tipo_jogada)

        # Tags: tudo a partir do 7º elemento (índice 7 em diante)
        if len(partes) > 7:
            tags = ", ".join(partes[7:])
            self.inputs["tags"].setText(tags)

        #Lida com o caso de nao ser um golo (ser defesa ou frango ou drible, etc)
        if partes[5] in VG.TIPO_DE_JOGADA_ESPECIAL and len(partes) == 6:
            tipo_jogada = partes[5]
            idx = self.inputs["tipo_jogada"].findText(tipo_jogada)
            if idx != -1:
                self.inputs["tipo_jogada"].setCurrentIndex(idx)
            else:
                self.inputs["tipo_jogada"].setCurrentText(tipo_jogada)

        # Preenche automaticamente o Clube do Jogador Principal com o mesmo do campo "Clube" (se ainda estiver vazio)
        # if len(partes) > 2 and "clube_do_jogador_principal" in self.inputs:
        #     current = self.inputs["clube_do_jogador_principal"].currentText().strip()
        #     if not current:  # só preenche se estiver vazio
        #         clube_principal = partes[2]
        #         idx = self.inputs["clube_do_jogador_principal"].findText(clube_principal)
        #         if idx != -1:
        #             self.inputs["clube_do_jogador_principal"].setCurrentIndex(idx)
        #         else:
        #             self.inputs["clube_do_jogador_principal"].setCurrentText(clube_principal)

        # Opcional: só para debug, vê no console o que foi extraído
        print("Partes processadas:", partes)

    def browse_file(self):
        clips_folder = VG.PASTA_DOS_CLIPS

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Vídeo",
            clips_folder,
            "Vídeos (*.mp4 *.avi *.mov *.mkv *.webm)"
        )
        if file_name:
            self.path_input.setText(file_name)

            base_name = os.path.basename(file_name)
            title_suggestion = os.path.splitext(base_name)[0]

            if not self.inputs["titulo"].text().strip():
                self.inputs["titulo"].setText(title_suggestion)

            self.setWindowTitle(f"Inserir Novo Clip - {title_suggestion}")

            self.CalculaCampos( title_suggestion )

    def get_unique_destination_path(self, original_path):
        filename = os.path.basename(original_path)
        destination_path = os.path.join(self.destination_folder, filename)

        if not os.path.exists(destination_path):
            return destination_path

        base, ext = os.path.splitext(filename)
        counter = 1
        while True:
            new_filename = f"{base} ({counter}){ext}"
            destination_path = os.path.join(self.destination_folder, new_filename)
            if not os.path.exists(destination_path):
                return destination_path
            counter += 1

    def save_clip(self):
        titulo = self.inputs["titulo"].text().strip()
        caminho_original = self.path_input.text().strip()

        if not titulo or not caminho_original:
            QMessageBox.warning(self, "Erro", "Título e caminho do vídeo são obrigatórios!")
            return

        if not os.path.exists(caminho_original):
            QMessageBox.warning(self, "Erro", "O ficheiro de vídeo selecionado não existe!")
            return

        # Guarda os valores para usar na próxima inserção
        global last_data_jornada, last_tipo_jogada, last_clube, last_adversario, last_competicao, last_clube_do_jogador_principal
        last_data_jornada = self.inputs["data_jornada"].text().strip()
        last_tipo_jogada = self.inputs["tipo_jogada"].currentText().strip()
        last_clube = self.inputs["clube"].currentText().strip()
        last_adversario = self.inputs["adversario"].currentText().strip()
        last_competicao = self.inputs["competicao"].text().strip()
        last_clube_do_jogador_principal = self.inputs["clube_do_jogador_principal"].currentText().strip()  # <<< NOVO

        # Valores para inserção
        clube_text = last_clube
        adversario_text = last_adversario
        jogador_text = self.inputs["jogador_principal"].currentText().strip()
        assistencia_text = self.inputs["assistencia_de"].currentText().strip()
        clube_jogador_text = last_clube_do_jogador_principal  # <<< NOVO

        # Adiciona novos itens às listas e BD se necessário
        if clube_text and clube_text not in self.clubes:
            add_clube(clube_text)
            self.clubes.append(clube_text)
        if adversario_text and adversario_text not in self.clubes:
            add_clube(adversario_text)
            self.clubes.append(adversario_text)
        if jogador_text and jogador_text not in self.jogadores:
            add_jogador(jogador_text)
            self.jogadores.append(jogador_text)
        if assistencia_text and assistencia_text not in self.jogadores:
            add_jogador(assistencia_text)
            self.jogadores.append(assistencia_text)

        # <<< NOVO: Adiciona clube do jogador principal se for novo
        if clube_jogador_text and clube_jogador_text not in self.clubes:
            add_clube(clube_jogador_text)
            self.clubes.append(clube_jogador_text)

        try:
            novo_caminho = self.get_unique_destination_path(caminho_original)
            shutil.copy2(caminho_original, novo_caminho)

            try:
                os.remove(caminho_original)
                apagou_original = True
            except Exception as delete_error:
                apagou_original = False
                erro_apagar = str(delete_error)

            # <<< TUPLA ATUALIZADA COM O NOVO CAMPO (último antes de tags/notas)
            data = (
                titulo,
                last_data_jornada,
                last_tipo_jogada or "Outro",
                jogador_text or None,
                assistencia_text or None,
                clube_text or None,
                adversario_text or None,
                last_competicao,
                novo_caminho,
                self.inputs["tags"].text().strip(),
                self.inputs["notas"].text().strip(),
                clube_jogador_text or None  # Novo campo: clube do jogador principal
            )

            insert_clip(data)

            if not apagou_original:
                mensagem = (f"Clip guardado com sucesso!\n\n"
                            f"⚠️ Não foi possível apagar o ficheiro original.\n"
                            f"Motivo: {erro_apagar}\n"
                            f"Apaga manualmente:\n{caminho_original}")
                QMessageBox.information(self, "Sucesso com aviso", mensagem)

            self.clear_fields()
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao copiar o vídeo:\n{str(e)}")

    def clear_fields(self):
        self.inputs["titulo"].clear()
        self.path_input.clear()
        self.inputs["data_jornada"].clear()
        self.inputs["tipo_jogada"].setCurrentIndex(0)
        self.inputs["jogador_principal"].setCurrentIndex(-1)
        self.inputs["assistencia_de"].setCurrentIndex(-1)
        self.inputs["clube"].setCurrentIndex(-1)
        self.inputs["adversario"].setCurrentIndex(-1)
        self.inputs["competicao"].clear()
        self.inputs["tags"].clear()
        self.inputs["notas"].clear()
        # <<< NOVO: limpa o novo campo
        if "clube_do_jogador_principal" in self.inputs:
            self.inputs["clube_do_jogador_principal"].setCurrentIndex(-1)
            self.inputs["clube_do_jogador_principal"].setCurrentText("")
        self.setWindowTitle("Inserir Novo Clip")

    def open_manage(self, table_name, title):
        self.manage_win = ManageItemsWindow(table_name, title)
        self.manage_win.show()
        self.manage_win.raise_()
        self.manage_win.activateWindow()