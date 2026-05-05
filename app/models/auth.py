import hashlib
import os
from datetime import datetime


class AuthManager:


    def __init__(self, uri="mongodb://localhost:27017", db_name="C213"):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.collection = "usuarios"
        self._connected = False
        self._current_user = None

    # ── Conexão ──────────────────────────────────────────────────────
    def connect(self):
       
        try:
            from pymongo import MongoClient
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            # Força uma operação para verificar se o servidor está ativo
            self.client.server_info()
            self.db = self.client[self.db_name]
            self.collection = self.db["usuarios"]
            # Criar índice único no username (idempotente)
            self.collection.create_index("username", unique=True)
            self._connected = True
            return True, "Conectado ao MongoDB."
        except ImportError:
            return False, (
                "Biblioteca 'pymongo' não instalada.\n"
                "Execute: pip install pymongo"
            )
        except Exception as exc:
            self._connected = False
            return False, f"Falha ao conectar ao MongoDB:\n{exc}"

    def close(self):
        if self.client:
            self.client.close()
        self._connected = False
        self._current_user = None

    @property
    def is_connected(self):
        return self._connected

    @property
    def current_user(self):
        return self._current_user

    # ── Hash de senha ────────────────────────────────────────────────
    @staticmethod
    def _hash_password(password: str, salt: str = None):
       
        if salt is None:
            salt = os.urandom(16).hex()
        h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
        return h, salt

    # ── Cadastro ─────────────────────────────────────────────────────
    def register(self, username: str, password: str,
                 nome: str = "", grupo: int = 7):

        if not self._connected:
            return False, "Sem conexão com o banco de dados."

        username = username.strip().lower()
        if len(username) < 3:
            return False, "Username deve ter pelo menos 3 caracteres."
        if len(password) < 4:
            return False, "Senha deve ter pelo menos 4 caracteres."

        # Verificar se já existe
        if self.collection.find_one({"username": username}):
            return False, f"Usuário '{username}' já existe."

        pw_hash, salt = self._hash_password(password)

        doc = {
            "username": username,
            "password": pw_hash,
            "salt": salt,
            "nome": nome.strip() if nome else username,
            "grupo": grupo,
            "criado_em": datetime.utcnow(),
            "ultimo_acesso": None,
        }

        try:
            self.collection.insert_one(doc)
            return True, f"Usuário '{username}' cadastrado com sucesso."
        except Exception as exc:
            return False, f"Erro ao cadastrar: {exc}"

    # ── Login ────────────────────────────────────────────────────────
    def login(self, username: str, password: str):

        if not self._connected:
            return False, "Sem conexão com o banco de dados."

        username = username.strip().lower()
        user = self.collection.find_one({"username": username})

        if user is None:
            return False, "Usuário não encontrado."

        pw_hash, _ = self._hash_password(password, salt=user["salt"])
        if pw_hash != user["password"]:
            return False, "Senha incorreta."

        # Atualizar último acesso
        self.collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"ultimo_acesso": datetime.utcnow()}}
        )
        self._current_user = {
            "username": user["username"],
            "nome": user.get("nome", user["username"]),
            "grupo": user.get("grupo", 7),
        }
        return True, f"Bem-vindo, {self._current_user['nome']}!"

    def logout(self):
        self._current_user = None

    # ── Info ──────────────────────────────────────────────────────────
    def get_user_info(self, username: str):
        """Retorna documento do usuário (sem senha/salt) ou None."""
        if not self._connected:
            return None
        user = self.collection.find_one(
            {"username": username.strip().lower()},
            {"password": 0, "salt": 0}
        )
        return user
