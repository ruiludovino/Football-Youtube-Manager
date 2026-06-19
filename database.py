# database.py
import sqlite3

DB_FILE = "clips.db"

def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()

    # Tabela principal de clips
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data_jornada TEXT,
            tipo_jogada TEXT,
            jogador_principal TEXT,
            assistencia_de TEXT,
            clube TEXT,
            adversario TEXT,
            competicao TEXT,
            caminho_video TEXT NOT NULL,
            tags TEXT,
            notas TEXT,
            clube_do_jogador_principal TEXT   -- <<< NOVO CAMPO
        )
    ''')

    # Tabela Clubes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clubes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabela Jogadores
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabela Adversários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS adversarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

# Funções para adicionar
def add_clube(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO clubes (nome) VALUES (?)", (nome.strip(),))
    conn.commit()
    conn.close()

def add_jogador(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO jogadores (nome) VALUES (?)", (nome.strip(),))
    conn.commit()
    conn.close()

def add_adversario(nome):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO adversarios (nome) VALUES (?)", (nome.strip(),))
    conn.commit()
    conn.close()

# Funções para obter listas
def get_all_clubes():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clubes ORDER BY nome")
    clubes = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clubes

def get_all_jogadores():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM jogadores ORDER BY nome")
    jogadores = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jogadores

def get_all_adversarios():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM adversarios ORDER BY nome")
    adversarios = [row[0] for row in cursor.fetchall()]
    conn.close()
    return adversarios

# Funções para clips
def insert_clip(data):
    try:
        conn = create_connection()
        cursor = conn.cursor()

        # Converte None para string vazia (continua a ser boa prática)
        safe_data = tuple("" if item is None else item for item in data)

        cursor.execute('''
            INSERT INTO clips 
            (titulo, data_jornada, tipo_jogada, jogador_principal, assistencia_de, 
             clube, adversario, competicao, caminho_video, tags, notas, clube_do_jogador_principal)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', safe_data)

        conn.commit()
        conn.close()
        print("Clip inserido com sucesso na BD!")
    except Exception as e:
        print(f"ERRO AO INSERIR CLIP: {e}")
        raise e

def get_all_clips():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips ORDER BY id DESC")
    clips = cursor.fetchall()
    conn.close()
    return clips

def get_clip_by_id(clip_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clips WHERE id = ?", (clip_id,))
    clip = cursor.fetchone()
    conn.close()
    return clip

def update_clip(clip_id, data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clips SET
            titulo = ?, data_jornada = ?, tipo_jogada = ?, jogador_principal = ?,
            assistencia_de = ?, clube = ?, adversario = ?, competicao = ?,
            caminho_video = ?, tags = ?, notas = ?, clube_do_jogador_principal = ?
        WHERE id = ?
    """, (*data, clip_id))
    conn.commit()
    conn.close()

def delete_clips(ids):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM clips WHERE id = ?", [(clip_id,) for clip_id in ids])
    conn.commit()
    conn.close()

# Funções genéricas para gestão (clubes, jogadores, adversarios)
def get_all_items(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, nome FROM {table_name} ORDER BY nome")
    items = cursor.fetchall()
    conn.close()
    return items

def update_item(table_name, item_id, new_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE {table_name} SET nome = ? WHERE id = ?", (new_name.strip(), item_id))
    conn.commit()
    conn.close()

def delete_item(table_name, item_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def get_all_clips():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, titulo, data_jornada, tipo_jogada, jogador_principal, assistencia_de, clube, adversario, competicao, tags, caminho_video FROM clips ORDER BY id DESC")
    return cursor.fetchall()
    conn.close()
    return clips

# Cria as tabelas ao importar o módulo (roda uma vez)
create_tables()



