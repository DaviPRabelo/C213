from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGroupBox, QRadioButton, QButtonGroup,
    QFrame, QMessageBox, QStatusBar, QLineEdit, QStackedWidget,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


# ═══════════════════════════════════════════════════════════════════════════════
# Paletas de cores
# ═══════════════════════════════════════════════════════════════════════════════
DARK_PALETTE = {
    "BG":       "#0d1117",
    "CARD":     "#161b22",
    "BORDER":   "#30363d",
    "ACCENT":   "#58a6ff",   
    "ACCENT2":  "#3fb950",   
    "ACCENT3":  "#f78166",   
    "ACCENT4":  "#bc8cff",   
    "TEXT":     "#e6edf3",
    "MUTED":    "#8b949e",
    "INPUT":    "#21262d",
    "HOVER":    "#1f6feb",
    "DISABLED": "#3a3f47",
}

LIGHT_PALETTE = {
    "BG":       "#f0f2f5",
    "CARD":     "#ffffff",
    "BORDER":   "#d0d7de",
    "ACCENT":   "#0969da",
    "ACCENT2":  "#1a7f37",
    "ACCENT3":  "#cf222e",
    "ACCENT4":  "#8250df",
    "TEXT":     "#1f2328",
    "MUTED":    "#656d76",
    "INPUT":    "#ffffff",
    "HOVER":    "#0550ae",
    "DISABLED": "#c8ced6",
}


_current_palette = DARK_PALETTE


def palette():
    return _current_palette


def set_palette(p):
    global _current_palette
    _current_palette = p


# ═══════════════════════════════════════════════════════════════════════════════
# Stylesheet dinâmico
# ═══════════════════════════════════════════════════════════════════════════════
def build_stylesheet(p):
    is_dark = (p is DARK_PALETTE) or (p["BG"] == DARK_PALETTE["BG"])
    btn_text = "#0d1117" if is_dark else "white"

    return f"""
QMainWindow, QWidget {{
    background-color: {p['BG']};
    color: {p['TEXT']};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {p['BORDER']};
    background: {p['CARD']};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {p['BG']};
    color: {p['MUTED']};
    padding: 10px 22px;
    border: 1px solid {p['BORDER']};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-weight: bold;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {p['CARD']};
    color: {p['ACCENT']};
    border-bottom: 2px solid {p['ACCENT']};
}}
QTabBar::tab:hover:!selected {{
    background: {p['INPUT']};
    color: {p['TEXT']};
}}
QPushButton {{
    background: {p['INPUT']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: bold;
}}
QPushButton:hover {{
    background: {p['HOVER']};
    border-color: {p['ACCENT']};
    color: white;
}}
QPushButton:pressed {{
    background: {'#0d419d' if is_dark else '#0550ae'};
}}
QPushButton:disabled {{
    color: {p['MUTED']};
    background: {p['BG']};
    border-color: {p['BORDER']};
}}
QPushButton#btnAccent {{
    background: {p['ACCENT']};
    color: {btn_text};
    border: none;
}}
QPushButton#btnAccent:hover {{
    background: {'#79c0ff' if is_dark else '#0550ae'};
    color: {btn_text};
}}
QPushButton#btnGreen {{
    background: {p['ACCENT2']};
    color: {btn_text};
    border: none;
}}
QPushButton#btnGreen:hover {{
    background: {'#56d364' if is_dark else '#1a7f37'};
    color: {btn_text};
}}
QPushButton#btnTheme {{
    background: {p['INPUT']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    border-radius: 14px;
    padding: 4px 14px;
    font-size: 12px;
}}
QPushButton#btnTheme:hover {{
    background: {p['HOVER']};
    color: white;
    border-color: {p['ACCENT']};
}}
QGroupBox {{
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 8px;
    font-weight: bold;
    color: {p['MUTED']};
    letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: {p['ACCENT']};
}}
QLabel {{
    color: {p['TEXT']};
}}
QLabel#labelMuted {{
    color: {p['MUTED']};
    font-size: 11px;
}}
QLabel#labelValue {{
    color: {p['ACCENT']};
    font-weight: bold;
    font-size: 14px;
    font-family: 'Consolas', monospace;
}}
QLabel#labelTitle {{
    color: {p['TEXT']};
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#labelSub {{
    color: {p['MUTED']};
    font-size: 11px;
    letter-spacing: 1px;
}}
QDoubleSpinBox, QLineEdit, QComboBox {{
    background: {p['INPUT']};
    border: 1px solid {p['BORDER']};
    border-radius: 4px;
    padding: 5px 8px;
    color: {p['TEXT']};
    min-width: 90px;
}}
QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
    border-color: {p['ACCENT']};
}}
QDoubleSpinBox:read-only {{
    background: {p['DISABLED']};
    color: {p['MUTED']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {p['INPUT']};
    border: 1px solid {p['BORDER']};
    color: {p['TEXT']};
    selection-background-color: {p['HOVER']};
}}
QRadioButton {{
    color: {p['TEXT']};
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 14px;
    height: 14px;
}}
QRadioButton::indicator:checked {{
    background: {p['ACCENT']};
    border-radius: 7px;
    border: 2px solid {p['ACCENT']};
}}
QRadioButton::indicator:unchecked {{
    background: {p['INPUT']};
    border-radius: 7px;
    border: 2px solid {p['BORDER']};
}}
QFrame#separator {{
    background: {p['BORDER']};
    max-height: 1px;
}}
QStatusBar {{
    background: {p['CARD']};
    color: {p['MUTED']};
    border-top: 1px solid {p['BORDER']};
    font-size: 11px;
}}
QToolTip {{
    background: {p['CARD']};
    color: {p['TEXT']};
    border: 1px solid {p['BORDER']};
    padding: 4px;
}}
QLineEdit#loginInput {{
    background: {p['INPUT']};
    border: 1px solid {p['BORDER']};
    border-radius: 6px;
    padding: 10px 14px;
    color: {p['TEXT']};
    font-size: 14px;
    min-width: 240px;
    min-height: 20px;
}}
QLineEdit#loginInput:focus {{
    border-color: {p['ACCENT']};
    border-width: 2px;
}}
QPushButton#btnLogin {{
    background: {p['ACCENT']};
    color: {btn_text};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    min-height: 20px;
}}
QPushButton#btnLogin:hover {{
    background: {'#79c0ff' if is_dark else '#0550ae'};
}}
QPushButton#btnRegister {{
    background: {p['ACCENT2']};
    color: {btn_text};
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
    min-height: 20px;
}}
QPushButton#btnRegister:hover {{
    background: {'#56d364' if is_dark else '#1a7f37'};
}}
QPushButton#btnLink {{
    background: none;
    border: none;
    color: {p['ACCENT']};
    font-size: 12px;
    text-decoration: underline;
    padding: 4px;
}}
QPushButton#btnLink:hover {{
    color: {'#79c0ff' if is_dark else '#0550ae'};
}}
QLabel#labelError {{
    color: {p['ACCENT3']};
    font-size: 11px;
    font-weight: bold;
}}
QLabel#labelSuccess {{
    color: {p['ACCENT2']};
    font-size: 11px;
    font-weight: bold;
}}
QLabel#labelUserBadge {{
    background: {p['INPUT']};
    border: 1px solid {p['BORDER']};
    border-radius: 12px;
    padding: 3px 12px;
    color: {p['ACCENT2']};
    font-size: 11px;
    font-weight: bold;
}}
"""

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4):
        fig = Figure(figsize=(width, height), facecolor=palette()["BG"])
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        self._style_ax()
        fig.tight_layout(pad=2)

    def _style_ax(self):
        p = palette()
        self.ax.set_facecolor(p["CARD"])
        self.ax.tick_params(colors=p["MUTED"], labelsize=9)
        self.ax.xaxis.label.set_color(p["MUTED"])
        self.ax.yaxis.label.set_color(p["MUTED"])
        self.ax.title.set_color(p["TEXT"])
        for spine in self.ax.spines.values():
            spine.set_edgecolor(p["BORDER"])
        # restilizar legend, se houver
        leg = self.ax.get_legend()
        if leg is not None:
            leg.get_frame().set_facecolor(p["CARD"])
            leg.get_frame().set_edgecolor(p["BORDER"])
            for text in leg.get_texts():
                text.set_color(p["TEXT"])

    def apply_theme(self):
        p = palette()
        self.figure.set_facecolor(p["BG"])
        self._style_ax()
        self.draw_idle()

    def clear_and_style(self):
        self.ax.cla()
        self._style_ax()


class ParamCard(QFrame):
    

    def __init__(self, label, unit="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 8, 10, 8)

        self._lbl = QLabel(label)
        self._lbl.setObjectName("labelMuted")
        self._lbl.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel("—")
        self.value_label.setObjectName("labelValue")
        self.value_label.setAlignment(Qt.AlignCenter)

        self._unit_lbl = QLabel(unit)
        self._unit_lbl.setObjectName("labelMuted")
        self._unit_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(self._lbl)
        layout.addWidget(self.value_label)
        layout.addWidget(self._unit_lbl)

        self.apply_theme()

    def apply_theme(self):
        p = palette()
        self.setStyleSheet(
            f"background:{p['INPUT']}; border:1px solid {p['BORDER']};"
            f" border-radius:6px; padding:4px;"
        )
        self._lbl.setStyleSheet(f"color:{p['MUTED']}; font-size:11px;")
        self._unit_lbl.setStyleSheet(f"color:{p['MUTED']}; font-size:11px;")
        self.value_label.setStyleSheet(
            f"color:{p['ACCENT']}; font-weight:bold; font-size:14px;"
        )

    def set_value(self, v, fmt=".4f"):
        try:
            self.value_label.setText(f"{v:{fmt}}")
        except (ValueError, TypeError):
            self.value_label.setText("—")

    def clear(self):
        self.value_label.setText("—")



class TabLogin(QWidget):

    sig_login = pyqtSignal(str, str)
    sig_register = pyqtSignal(str, str, str, int)
    sig_logout = pyqtSignal()
    sig_connect_db = pyqtSignal(str)  

    def __init__(self, parent=None):
        super().__init__(parent)
        self._logged_in = False
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.stack = QStackedWidget()
        outer.addWidget(self.stack)

        self.stack.addWidget(self._build_login_page())     
        self.stack.addWidget(self._build_register_page())  
        self.stack.addWidget(self._build_logged_page())   

    def _build_login_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 32, 32, 32)

        icon = QLabel("◈")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 36px;")

        title = QLabel("C213  ·  PID CONTROLLER")
        title.setObjectName("labelTitle")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Faça login para acessar o sistema")
        sub.setObjectName("labelSub")
        sub.setAlignment(Qt.AlignCenter)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)

        self.input_login_uri = QLineEdit()
        self.input_login_uri.setObjectName("loginInput")
        self.input_login_uri.setPlaceholderText("URI MongoDB  (mongodb://localhost:27017)")
        self.input_login_uri.setText("mongodb://localhost:27017")

        self.input_login_user = QLineEdit()
        self.input_login_user.setObjectName("loginInput")
        self.input_login_user.setPlaceholderText("Username")

        self.input_login_pass = QLineEdit()
        self.input_login_pass.setObjectName("loginInput")
        self.input_login_pass.setPlaceholderText("Senha")
        self.input_login_pass.setEchoMode(QLineEdit.Password)

        self.lbl_login_msg = QLabel("")
        self.lbl_login_msg.setObjectName("labelError")
        self.lbl_login_msg.setAlignment(Qt.AlignCenter)
        self.lbl_login_msg.setWordWrap(True)

        btn_login = QPushButton("Entrar")
        btn_login.setObjectName("btnLogin")
        btn_login.clicked.connect(self._on_login_click)

        self.input_login_pass.returnPressed.connect(self._on_login_click)

        btn_go_register = QPushButton("Não tem conta? Cadastre-se")
        btn_go_register.setObjectName("btnLink")
        btn_go_register.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        card_layout.addWidget(icon)
        card_layout.addWidget(title)
        card_layout.addWidget(sub)
        card_layout.addWidget(sep)
        card_layout.addSpacing(8)
        card_layout.addWidget(QLabel("Conexão MongoDB:"))
        card_layout.addWidget(self.input_login_uri)
        card_layout.addSpacing(4)
        card_layout.addWidget(QLabel("Username:"))
        card_layout.addWidget(self.input_login_user)
        card_layout.addWidget(QLabel("Senha:"))
        card_layout.addWidget(self.input_login_pass)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.lbl_login_msg)
        card_layout.addWidget(btn_login)
        card_layout.addWidget(btn_go_register)

        layout.addWidget(card, alignment=Qt.AlignCenter)
        return page


    def _build_register_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(32, 32, 32, 32)

        title = QLabel("CADASTRO")
        title.setObjectName("labelTitle")
        title.setAlignment(Qt.AlignCenter)

        sub = QLabel("Crie sua conta para acessar o sistema")
        sub.setObjectName("labelSub")
        sub.setAlignment(Qt.AlignCenter)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)

        self.input_reg_nome = QLineEdit()
        self.input_reg_nome.setObjectName("loginInput")
        self.input_reg_nome.setPlaceholderText("Nome completo")

        self.input_reg_user = QLineEdit()
        self.input_reg_user.setObjectName("loginInput")
        self.input_reg_user.setPlaceholderText("Username (mín. 3 caracteres)")

        self.input_reg_pass = QLineEdit()
        self.input_reg_pass.setObjectName("loginInput")
        self.input_reg_pass.setPlaceholderText("Senha (mín. 4 caracteres)")
        self.input_reg_pass.setEchoMode(QLineEdit.Password)

        self.input_reg_pass2 = QLineEdit()
        self.input_reg_pass2.setObjectName("loginInput")
        self.input_reg_pass2.setPlaceholderText("Confirmar senha")
        self.input_reg_pass2.setEchoMode(QLineEdit.Password)

        self.spin_reg_grupo = QDoubleSpinBox()
        self.spin_reg_grupo.setRange(1, 20)
        self.spin_reg_grupo.setDecimals(0)
        self.spin_reg_grupo.setValue(7)
        self.spin_reg_grupo.setPrefix("Grupo  ")

        self.lbl_reg_msg = QLabel("")
        self.lbl_reg_msg.setObjectName("labelError")
        self.lbl_reg_msg.setAlignment(Qt.AlignCenter)
        self.lbl_reg_msg.setWordWrap(True)

        btn_register = QPushButton("Cadastrar")
        btn_register.setObjectName("btnRegister")
        btn_register.clicked.connect(self._on_register_click)

        self.input_reg_pass2.returnPressed.connect(self._on_register_click)

        btn_go_login = QPushButton("Já tem conta? Faça login")
        btn_go_login.setObjectName("btnLink")
        btn_go_login.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        card_layout.addWidget(title)
        card_layout.addWidget(sub)
        card_layout.addWidget(sep)
        card_layout.addSpacing(4)
        card_layout.addWidget(QLabel("Nome:"))
        card_layout.addWidget(self.input_reg_nome)
        card_layout.addWidget(QLabel("Username:"))
        card_layout.addWidget(self.input_reg_user)
        card_layout.addWidget(QLabel("Senha:"))
        card_layout.addWidget(self.input_reg_pass)
        card_layout.addWidget(QLabel("Confirmar:"))
        card_layout.addWidget(self.input_reg_pass2)
        card_layout.addWidget(QLabel("Grupo:"))
        card_layout.addWidget(self.spin_reg_grupo)
        card_layout.addSpacing(4)
        card_layout.addWidget(self.lbl_reg_msg)
        card_layout.addWidget(btn_register)
        card_layout.addWidget(btn_go_login)

        layout.addWidget(card, alignment=Qt.AlignCenter)
        return page


    def _build_logged_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(16)
        card_layout.setContentsMargins(32, 40, 32, 40)

        icon = QLabel("✓")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 48px; color: #3fb950;")

        self.lbl_welcome = QLabel("Bem-vindo!")
        self.lbl_welcome.setObjectName("labelTitle")
        self.lbl_welcome.setAlignment(Qt.AlignCenter)

        self.lbl_user_info = QLabel("")
        self.lbl_user_info.setObjectName("labelSub")
        self.lbl_user_info.setAlignment(Qt.AlignCenter)
        self.lbl_user_info.setWordWrap(True)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)

        info = QLabel(
            "Você está autenticado. Use as abas acima para\n"
            "acessar Identificação, Controle PID e Gráficos."
        )
        info.setAlignment(Qt.AlignCenter)
        info.setObjectName("labelMuted")
        info.setWordWrap(True)

        btn_logout = QPushButton("Sair")
        btn_logout.setObjectName("btnLogin")
        btn_logout.setStyleSheet("")  # herdará do tema
        btn_logout.clicked.connect(self._on_logout_click)

        card_layout.addWidget(icon)
        card_layout.addWidget(self.lbl_welcome)
        card_layout.addWidget(self.lbl_user_info)
        card_layout.addWidget(sep)
        card_layout.addWidget(info)
        card_layout.addSpacing(8)
        card_layout.addWidget(btn_logout)

        layout.addWidget(card, alignment=Qt.AlignCenter)
        return page


    def _on_login_click(self):
        uri = self.input_login_uri.text().strip()
        user = self.input_login_user.text().strip()
        pw = self.input_login_pass.text()

        if not user:
            self.show_login_error("Informe o username.")
            return
        if not pw:
            self.show_login_error("Informe a senha.")
            return

        self.sig_connect_db.emit(uri)
        self.sig_login.emit(user, pw)

    def _on_register_click(self):
        nome = self.input_reg_nome.text().strip()
        user = self.input_reg_user.text().strip()
        pw = self.input_reg_pass.text()
        pw2 = self.input_reg_pass2.text()
        grupo = int(self.spin_reg_grupo.value())

        if not user:
            self.show_register_error("Informe o username.")
            return
        if not pw:
            self.show_register_error("Informe a senha.")
            return
        if pw != pw2:
            self.show_register_error("As senhas não coincidem.")
            return

        uri = self.input_login_uri.text().strip()
        self.sig_connect_db.emit(uri)
        self.sig_register.emit(user, pw, nome, grupo)

    def _on_logout_click(self):
        self.sig_logout.emit()
        self.stack.setCurrentIndex(0)
        self.input_login_pass.clear()
        self.lbl_login_msg.clear()
        self._logged_in = False


    def show_login_error(self, msg):
        self.lbl_login_msg.setObjectName("labelError")
        self.lbl_login_msg.setStyleSheet(f"color: {palette()['ACCENT3']};")
        self.lbl_login_msg.setText(msg)

    def show_login_success(self, msg):
        self.lbl_login_msg.setObjectName("labelSuccess")
        self.lbl_login_msg.setStyleSheet(f"color: {palette()['ACCENT2']};")
        self.lbl_login_msg.setText(msg)

    def show_register_error(self, msg):
        self.lbl_reg_msg.setObjectName("labelError")
        self.lbl_reg_msg.setStyleSheet(f"color: {palette()['ACCENT3']};")
        self.lbl_reg_msg.setText(msg)

    def show_register_success(self, msg):
        self.lbl_reg_msg.setObjectName("labelSuccess")
        self.lbl_reg_msg.setStyleSheet(f"color: {palette()['ACCENT2']};")
        self.lbl_reg_msg.setText(msg)

    def set_logged_in(self, nome, grupo):
        """Muda para a tela de boas-vindas pós-login."""
        self._logged_in = True
        self.lbl_welcome.setText(f"Bem-vindo, {nome}!")
        self.lbl_user_info.setText(f"Grupo {grupo}  ·  Autenticado via MongoDB")
        self.stack.setCurrentIndex(2)

    def is_logged_in(self):
        return self._logged_in

    def get_uri(self):
        return self.input_login_uri.text().strip()

    def apply_theme(self):
        pass



class TabIdentificacao(QWidget):
    sig_load_file = pyqtSignal()
    sig_export = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        left = QWidget()
        left.setFixedWidth(260)
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(12)

        title = QLabel("IDENTIFICAÇÃO")
        title.setObjectName("labelTitle")
        sub = QLabel("Método de Smith — FOPDT")
        sub.setObjectName("labelSub")
        left_layout.addWidget(title)
        left_layout.addWidget(sub)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        left_layout.addWidget(sep)


        grp_file = QGroupBox("DATASET")
        grp_file_layout = QVBoxLayout(grp_file)
        self.btn_load = QPushButton("📂  Escolher Arquivo .mat")
        self.btn_load.setObjectName("btnAccent")
        self.label_file = QLabel("Nenhum arquivo selecionado")
        self.label_file.setObjectName("labelMuted")
        self.label_file.setWordWrap(True)
        grp_file_layout.addWidget(self.btn_load)
        grp_file_layout.addWidget(self.label_file)
        left_layout.addWidget(grp_file)


        grp_params = QGroupBox("PARÂMETROS FOPDT")
        grp_params_layout = QGridLayout(grp_params)
        grp_params_layout.setSpacing(8)

        self.card_K = ParamCard("Kₛ", "ganho")
        self.card_tau = ParamCard("τₛ", "tempo")
        self.card_theta = ParamCard("θₛ", "atraso")
        self.card_eqm = ParamCard("EQM", "RMSE")

        grp_params_layout.addWidget(self.card_K,     0, 0)
        grp_params_layout.addWidget(self.card_tau,   0, 1)
        grp_params_layout.addWidget(self.card_theta, 1, 0)
        grp_params_layout.addWidget(self.card_eqm,   1, 1)
        left_layout.addWidget(grp_params)


        grp_info = QGroupBox("EXPERIMENTO")
        grp_info_layout = QGridLayout(grp_info)
        grp_info_layout.setSpacing(8)

        self.card_u0 = ParamCard("u₀", "")
        self.card_u1 = ParamCard("u_f", "")
        self.card_yinf = ParamCard("y∞", "")
        self.card_tstep = ParamCard("t_d", "degrau")

        grp_info_layout.addWidget(self.card_u0,    0, 0)
        grp_info_layout.addWidget(self.card_u1,    0, 1)
        grp_info_layout.addWidget(self.card_yinf,  1, 0)
        grp_info_layout.addWidget(self.card_tstep, 1, 1)
        left_layout.addWidget(grp_info)

        self.btn_export = QPushButton("💾  Exportar Gráfico")
        self.btn_export.setEnabled(False)
        left_layout.addWidget(self.btn_export)
        left_layout.addStretch()


        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self, width=7, height=5)
        self._toolbar = NavigationToolbar(self.canvas, self)
        self._apply_toolbar_theme()

        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)


        self.btn_load.clicked.connect(self.sig_load_file.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)

    def _apply_toolbar_theme(self):
        p = palette()
        self._toolbar.setStyleSheet(
            f"background:{p['CARD']}; color:{p['MUTED']}; border:none;"
        )

    def apply_theme(self):
        self._apply_toolbar_theme()
        self.canvas.apply_theme()
        for c in (self.card_K, self.card_tau, self.card_theta, self.card_eqm,
                  self.card_u0, self.card_u1, self.card_yinf, self.card_tstep):
            c.apply_theme()

    def set_file_label(self, text):
        self.label_file.setText(text)

    def set_params(self, K, tau, theta, eqm):
        self.card_K.set_value(K, ".4f")
        self.card_tau.set_value(tau, ".4f")
        self.card_theta.set_value(theta, ".4f")
        self.card_eqm.set_value(eqm, ".4f")

    def set_experiment_info(self, u0, u1, y_inf, t_step):
        self.card_u0.set_value(u0, ".2f")
        self.card_u1.set_value(u1, ".2f")
        self.card_yinf.set_value(y_inf, ".3f")
        self.card_tstep.set_value(t_step, ".2f")

    def clear_params(self):
        for c in (self.card_K, self.card_tau, self.card_theta, self.card_eqm,
                  self.card_u0, self.card_u1, self.card_yinf, self.card_tstep):
            c.clear()



class TabControlePID(QWidget):
    sig_tune = pyqtSignal()
    sig_export = pyqtSignal()
    sig_method_changed = pyqtSignal()  
    sig_lambda_changed = pyqtSignal()  

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)


        left = QWidget()
        left.setFixedWidth(280)
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(12)

        title = QLabel("CONTROLE PID")
        title.setObjectName("labelTitle")
        sub = QLabel("IMC  ·  ITAE")
        sub.setObjectName("labelSub")
        left_layout.addWidget(title)
        left_layout.addWidget(sub)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        left_layout.addWidget(sep)


        grp_sel = QGroupBox("MODO DE SINTONIA")
        grp_sel_layout = QVBoxLayout(grp_sel)

        self.radio_method = QRadioButton("Método Automático")
        self.radio_manual = QRadioButton("Manual")
        self.radio_method.setChecked(True)
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.radio_method, 0)
        self.btn_group.addButton(self.radio_manual, 1)

        self.combo_method = QComboBox()
        self.combo_method.addItems(["IMC", "ITAE"])

        grp_sel_layout.addWidget(self.radio_method)
        grp_sel_layout.addWidget(self.combo_method)
        grp_sel_layout.addWidget(self.radio_manual)
        left_layout.addWidget(grp_sel)


        grp_pid = QGroupBox("PARÂMETROS PID")
        grp_pid_layout = QGridLayout(grp_pid)
        grp_pid_layout.setSpacing(8)

        def make_spin(lo=-1e6, hi=1e6, dec=4, step=0.1):
            s = QDoubleSpinBox()
            s.setRange(lo, hi)
            s.setDecimals(dec)
            s.setSingleStep(step)
            return s

        self.spin_Kp = make_spin()
        self.spin_Ti = make_spin()
        self.spin_Td = make_spin()
        self.spin_lam = make_spin(lo=0.001, hi=1e4, dec=3, step=1)
        self.spin_lam.setValue(1.0)
        self._lam_saved = 1.0

        self.lbl_kp  = QLabel("Kp :")
        self.lbl_ti  = QLabel("Ti :")
        self.lbl_td  = QLabel("Td :")
        self.lbl_lam = QLabel("λ  :")
        grp_pid_layout.addWidget(self.lbl_kp,   0, 0)
        grp_pid_layout.addWidget(self.spin_Kp,  0, 1)
        grp_pid_layout.addWidget(self.lbl_ti,   1, 0)
        grp_pid_layout.addWidget(self.spin_Ti,  1, 1)
        grp_pid_layout.addWidget(self.lbl_td,   2, 0)
        grp_pid_layout.addWidget(self.spin_Td,  2, 1)
        grp_pid_layout.addWidget(self.lbl_lam,  3, 0)
        grp_pid_layout.addWidget(self.spin_lam, 3, 1)
        left_layout.addWidget(grp_pid)

        # Setpoint e métricas
        grp_ctrl = QGroupBox("RESPOSTA")
        grp_ctrl_layout = QGridLayout(grp_ctrl)
        grp_ctrl_layout.setSpacing(8)

        self.spin_sp = make_spin(lo=-1e4, hi=1e4, dec=2, step=1)
        self.spin_sp.setValue(45.0)
        self.spin_tsim = make_spin(lo=1.0, hi=1e5, dec=1, step=10)
        self.spin_tsim.setValue(200.0)

        self.card_tr = ParamCard("tᵣ", "subida [s]")
        self.card_ts = ParamCard("tₛ", "acomod. [s]")
        self.card_mp = ParamCard("Mp", "overshoot %")
        self.card_ess = ParamCard("ess", "erro RP")

        grp_ctrl_layout.addWidget(QLabel("SP:"),     0, 0)
        grp_ctrl_layout.addWidget(self.spin_sp,     0, 1)
        grp_ctrl_layout.addWidget(QLabel("t_sim:"), 1, 0)
        grp_ctrl_layout.addWidget(self.spin_tsim,   1, 1)
        grp_ctrl_layout.addWidget(self.card_tr,    2, 0)
        grp_ctrl_layout.addWidget(self.card_ts,    2, 1)
        grp_ctrl_layout.addWidget(self.card_mp,    3, 0)
        grp_ctrl_layout.addWidget(self.card_ess,   3, 1)
        left_layout.addWidget(grp_ctrl)


        self.btn_tune = QPushButton("⚙️  Sintonizar")
        self.btn_tune.setObjectName("btnGreen")
        self.btn_tune.setEnabled(False)
        self.btn_export = QPushButton("💾  Exportar Gráfico")
        self.btn_export.setEnabled(False)

        left_layout.addWidget(self.btn_tune)
        left_layout.addWidget(self.btn_export)
        left_layout.addStretch()


        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self, width=7, height=5)
        self._toolbar = NavigationToolbar(self.canvas, self)
        self._apply_toolbar_theme()

        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)


        self.btn_tune.clicked.connect(self.sig_tune.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)
        self.radio_method.toggled.connect(self._on_mode_changed)
        self.combo_method.currentTextChanged.connect(self._on_combo_changed)
        self.spin_lam.valueChanged.connect(self._on_lambda_changed)

        self._on_mode_changed()

    def _on_mode_changed(self, *_):
        is_method = self.radio_method.isChecked()
        is_itae = self.combo_method.currentText() == "ITAE"


        self.combo_method.setEnabled(True)
        for s in (self.spin_Kp, self.spin_Ti, self.spin_Td):
            s.setReadOnly(is_method)

        if is_itae:
            self.spin_lam.setEnabled(False)
            self.spin_lam.setSpecialValueText("N/A")

            self.spin_lam.blockSignals(True)
            self.spin_lam.setValue(self.spin_lam.minimum())
            self.spin_lam.blockSignals(False)
        else:

            self.spin_lam.setEnabled(True)
            self.spin_lam.setSpecialValueText("")
            self.spin_lam.blockSignals(True)
            if self.spin_lam.value() <= self.spin_lam.minimum():
                self.spin_lam.setValue(self._lam_saved)
            self.spin_lam.blockSignals(False)


        if is_method:
            self.sig_method_changed.emit()

    def _on_combo_changed(self, *_):
        self._on_mode_changed()

    def _on_lambda_changed(self, *_):
        if not self.spin_lam.isEnabled():
            return
        v = self.spin_lam.value()
        if v > self.spin_lam.minimum():
            self._lam_saved = v
            if self.radio_method.isChecked() and self.combo_method.currentText() == "IMC":
                self.sig_lambda_changed.emit()


    def _apply_toolbar_theme(self):
        p = palette()
        self._toolbar.setStyleSheet(
            f"background:{p['CARD']}; color:{p['MUTED']}; border:none;"
        )

    def apply_theme(self):
        self._apply_toolbar_theme()
        self.canvas.apply_theme()
        for c in (self.card_tr, self.card_ts, self.card_mp, self.card_ess):
            c.apply_theme()

    def set_pid_params(self, Kp, Ti, Td):
        self.spin_Kp.blockSignals(True)
        self.spin_Ti.blockSignals(True)
        self.spin_Td.blockSignals(True)
        self.spin_Kp.setValue(Kp)
        self.spin_Ti.setValue(Ti)
        self.spin_Td.setValue(Td)
        self.spin_Kp.blockSignals(False)
        self.spin_Ti.blockSignals(False)
        self.spin_Td.blockSignals(False)

    def set_lambda(self, lam):
        self._lam_saved = lam
        if self.spin_lam.isEnabled():
            self.spin_lam.blockSignals(True)
            self.spin_lam.setValue(lam)
            self.spin_lam.blockSignals(False)

    def set_metrics(self, tr, ts, Mp, ess):
        def _s(card, v, fmt):
            if v is not None:
                card.set_value(v, fmt)
            else:
                card.clear()
        _s(self.card_tr, tr, ".2f")
        _s(self.card_ts, ts, ".2f")
        _s(self.card_mp, Mp, ".2f")
        _s(self.card_ess, ess, ".4f")

    def get_pid_params(self):
        return self.spin_Kp.value(), self.spin_Ti.value(), self.spin_Td.value()

    def is_manual(self):
        return self.radio_manual.isChecked()

    def get_method(self):
        return self.combo_method.currentText()

    def get_lambda(self):
        v = self.spin_lam.value()
        if v <= self.spin_lam.minimum():
            return None
        return v

    def get_setpoint(self):
        return self.spin_sp.value()

    def get_tsim(self):
        return self.spin_tsim.value()


class TabGraficos(QWidget):
    sig_compare = pyqtSignal()
    sig_export = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Cabeçalho
        header = QHBoxLayout()
        title = QLabel("COMPARAÇÃO  ·  MALHA ABERTA × MALHA FECHADA")
        title.setObjectName("labelTitle")
        self.btn_compare = QPushButton("📊  Atualizar Comparação")
        self.btn_compare.setObjectName("btnAccent")
        self.btn_compare.setEnabled(False)
        self.btn_export = QPushButton("💾  Exportar")
        self.btn_export.setEnabled(False)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_compare)
        header.addWidget(self.btn_export)
        layout.addLayout(header)

        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        plots = QHBoxLayout()
        plots.setSpacing(12)

        frame_ol = QGroupBox("MALHA ABERTA  (resposta natural da planta)")
        fl = QVBoxLayout(frame_ol)
        self.canvas_ol = MplCanvas(self, width=5, height=4)
        self._toolbar_ol = NavigationToolbar(self.canvas_ol, self)
        fl.addWidget(self._toolbar_ol)
        fl.addWidget(self.canvas_ol)

        frame_cl = QGroupBox("MALHA FECHADA  (IMC × ITAE)")
        fcl = QVBoxLayout(frame_cl)
        self.canvas_cl = MplCanvas(self, width=5, height=4)
        self._toolbar_cl = NavigationToolbar(self.canvas_cl, self)
        fcl.addWidget(self._toolbar_cl)
        fcl.addWidget(self.canvas_cl)

        plots.addWidget(frame_ol)
        plots.addWidget(frame_cl)
        layout.addLayout(plots)

        self._apply_toolbar_theme()

        # Sinais
        self.btn_compare.clicked.connect(self.sig_compare.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)

    def _apply_toolbar_theme(self):
        p = palette()
        for tb in (self._toolbar_ol, self._toolbar_cl):
            tb.setStyleSheet(
                f"background:{p['CARD']}; color:{p['MUTED']}; border:none;"
            )

    def apply_theme(self):
        self._apply_toolbar_theme()
        self.canvas_ol.apply_theme()
        self.canvas_cl.apply_theme()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._is_dark = True
        self._theme_callback = None  
        self.setWindowTitle("C213  ·  Identificação & Controle PID  ·  Grupo 7")
        self.setMinimumSize(1180, 720)
        self.setStyleSheet(build_stylesheet(DARK_PALETTE))

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header_bar = QFrame()
        self._header_bar.setFixedHeight(48)
        hb_layout = QHBoxLayout(self._header_bar)
        hb_layout.setContentsMargins(16, 0, 16, 0)

        self._logo = QLabel("◈  C213  ·  PID CONTROLLER")
        self._grupo = QLabel("GRUPO 7  ·  SMITH + IMC + ITAE")

        self._btn_theme = QPushButton("☀  Light")
        self._btn_theme.setObjectName("btnTheme")
        self._btn_theme.setFixedWidth(90)
        self._btn_theme.clicked.connect(self._toggle_theme)

        hb_layout.addWidget(self._logo)
        hb_layout.addStretch()
        hb_layout.addWidget(self._grupo)
        hb_layout.addSpacing(12)
        hb_layout.addWidget(self._btn_theme)
        root.addWidget(self._header_bar)

        self._style_header(DARK_PALETTE)

        self.tabs = QTabWidget()
        self.tab_login = TabLogin()
        self.tab_ident = TabIdentificacao()
        self.tab_pid = TabControlePID()
        self.tab_graf = TabGraficos()

        self.tabs.addTab(self.tab_login, "  LOGIN  ")
        self.tabs.addTab(self.tab_ident, "  IDENTIFICAÇÃO  ")
        self.tabs.addTab(self.tab_pid,   "  CONTROLE PID   ")
        self.tabs.addTab(self.tab_graf,  "  GRÁFICOS       ")

        for i in (1, 2, 3):
            self.tabs.setTabEnabled(i, False)

        root.addWidget(self.tabs, stretch=1)

        self._user_badge = QLabel("")
        self._user_badge.setObjectName("labelUserBadge")
        self._user_badge.setVisible(False)
        hb_layout.insertWidget(3, self._user_badge)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Pronto  |  Faça login para começar")

    def _style_header(self, p):
        self._header_bar.setStyleSheet(
            f"background:{p['CARD']}; border-bottom:1px solid {p['BORDER']};"
        )
        self._logo.setStyleSheet(
            f"color:{p['ACCENT']}; font-size:15px; font-weight:bold; letter-spacing:3px;"
        )
        self._grupo.setStyleSheet(
            f"color:{p['MUTED']}; font-size:11px; letter-spacing:2px;"
        )

    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        new_palette = DARK_PALETTE if self._is_dark else LIGHT_PALETTE
        self.apply_theme(new_palette)

    def apply_theme(self, p):
        set_palette(p)
        self.setStyleSheet(build_stylesheet(p))
        self._style_header(p)
        self.tab_login.apply_theme()
        self.tab_ident.apply_theme()
        self.tab_pid.apply_theme()
        self.tab_graf.apply_theme()
        self._btn_theme.setText("🌙  Dark" if not self._is_dark else "☀  Light")
        if self._theme_callback is not None:
            self._theme_callback()

    def set_theme_callback(self, cb):

        self._theme_callback = cb

    def show_error(self, msg):
        QMessageBox.critical(self, "Erro", msg)

    def show_warning(self, msg):
        QMessageBox.warning(self, "Aviso", msg)

    def show_info(self, msg):
        QMessageBox.information(self, "Info", msg)

    def set_status(self, msg):
        self.status.showMessage(msg)

    def unlock_tabs(self, nome, grupo):

        for i in (1, 2, 3):
            self.tabs.setTabEnabled(i, True)
        self._user_badge.setText(f"👤  {nome}  ·  Grupo {grupo}")
        self._user_badge.setVisible(True)
        self.tabs.setCurrentIndex(1)

    def lock_tabs(self):
        for i in (1, 2, 3):
            self.tabs.setTabEnabled(i, False)
        self._user_badge.setVisible(False)
        self.tabs.setCurrentIndex(0)
        self.set_status("Sessão encerrada  |  Faça login para continuar")
