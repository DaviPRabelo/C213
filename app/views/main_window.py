"""
View principal — IHM PyQt5 com 3 abas:
  1. Identificação (Smith)
  2. Controle PID (IMC + ITAE)
  3. Gráficos comparativos
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox,
    QDoubleSpinBox, QGroupBox, QRadioButton, QButtonGroup,
    QFrame, QMessageBox, QStatusBar
)
from PyQt5.QtCore import Qt, pyqtSignal

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

# ── Paleta de cores ────────────────────────────────────────────────────────────
DARK_BG     = "#0d1117"
CARD_BG     = "#161b22"
BORDER      = "#30363d"
ACCENT      = "#58a6ff"
ACCENT2     = "#3fb950"
ACCENT3     = "#f78166"
TEXT_MAIN   = "#e6edf3"
TEXT_MUTED  = "#8b949e"
INPUT_BG    = "#21262d"
HOVER       = "#1f6feb"


STYLE_SHEET = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_MAIN};
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 13px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {CARD_BG};
    border-radius: 6px;
}}
QTabBar::tab {{
    background: {DARK_BG};
    color: {TEXT_MUTED};
    padding: 10px 22px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    font-weight: bold;
    letter-spacing: 1px;
}}
QTabBar::tab:selected {{
    background: {CARD_BG};
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
}}
QTabBar::tab:hover:!selected {{
    background: {INPUT_BG};
    color: {TEXT_MAIN};
}}
QPushButton {{
    background: {INPUT_BG};
    color: {TEXT_MAIN};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 7px 18px;
    font-weight: bold;
}}
QPushButton:hover {{
    background: {HOVER};
    border-color: {ACCENT};
    color: white;
}}
QPushButton:pressed {{
    background: #0d419d;
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    background: {DARK_BG};
    border-color: {BORDER};
}}
QPushButton#btnAccent {{
    background: {ACCENT};
    color: {DARK_BG};
    border: none;
}}
QPushButton#btnAccent:hover {{
    background: #79c0ff;
}}
QPushButton#btnGreen {{
    background: {ACCENT2};
    color: {DARK_BG};
    border: none;
}}
QPushButton#btnGreen:hover {{
    background: #56d364;
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 8px;
    font-weight: bold;
    color: {TEXT_MUTED};
    letter-spacing: 1px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    color: {ACCENT};
}}
QLabel {{
    color: {TEXT_MAIN};
}}
QLabel#labelMuted {{
    color: {TEXT_MUTED};
    font-size: 11px;
}}
QLabel#labelValue {{
    color: {ACCENT};
    font-weight: bold;
    font-size: 14px;
    font-family: 'Consolas', monospace;
}}
QLabel#labelTitle {{
    color: {TEXT_MAIN};
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 2px;
}}
QLabel#labelSub {{
    color: {TEXT_MUTED};
    font-size: 11px;
    letter-spacing: 1px;
}}
QDoubleSpinBox, QLineEdit, QComboBox {{
    background: {INPUT_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 5px 8px;
    color: {TEXT_MAIN};
    min-width: 90px;
}}
QDoubleSpinBox:focus, QLineEdit:focus, QComboBox:focus {{
    border-color: {ACCENT};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background: {INPUT_BG};
    border: 1px solid {BORDER};
    color: {TEXT_MAIN};
    selection-background-color: {HOVER};
}}
QRadioButton {{
    color: {TEXT_MAIN};
    spacing: 8px;
}}
QRadioButton::indicator:checked {{
    background: {ACCENT};
    border-radius: 6px;
    border: 2px solid {ACCENT};
}}
QRadioButton::indicator:unchecked {{
    background: {INPUT_BG};
    border-radius: 6px;
    border: 2px solid {BORDER};
}}
QFrame#separator {{
    background: {BORDER};
    max-height: 1px;
}}
QStatusBar {{
    background: {CARD_BG};
    color: {TEXT_MUTED};
    border-top: 1px solid {BORDER};
    font-size: 11px;
}}
"""


# ── Canvas Matplotlib ──────────────────────────────────────────────────────────

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4):
        fig = Figure(figsize=(width, height), facecolor=DARK_BG)
        self.ax = fig.add_subplot(111)
        self._style_ax()
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        fig.tight_layout(pad=2)

    def _style_ax(self):
        self.ax.set_facecolor(CARD_BG)
        self.ax.tick_params(colors=TEXT_MUTED, labelsize=9)
        self.ax.xaxis.label.set_color(TEXT_MUTED)
        self.ax.yaxis.label.set_color(TEXT_MUTED)
        for spine in self.ax.spines.values():
            spine.set_edgecolor(BORDER)

    def clear_and_style(self):
        self.ax.cla()
        self._style_ax()


# ── Widget de parâmetro identificado ──────────────────────────────────────────

class ParamCard(QFrame):
    def __init__(self, label, unit="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"background:{INPUT_BG}; border:1px solid {BORDER}; border-radius:6px; padding:4px;")
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(10, 8, 10, 8)

        lbl = QLabel(label)
        lbl.setObjectName("labelMuted")
        lbl.setAlignment(Qt.AlignCenter)

        self.value_label = QLabel("—")
        self.value_label.setObjectName("labelValue")
        self.value_label.setAlignment(Qt.AlignCenter)

        unit_lbl = QLabel(unit)
        unit_lbl.setObjectName("labelMuted")
        unit_lbl.setAlignment(Qt.AlignCenter)

        layout.addWidget(lbl)
        layout.addWidget(self.value_label)
        layout.addWidget(unit_lbl)

    def set_value(self, v, fmt=".4f"):
        self.value_label.setText(f"{v:{fmt}}")

    def clear(self):
        self.value_label.setText("—")


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 1 — Identificação
# ═══════════════════════════════════════════════════════════════════════════════

class TabIdentificacao(QWidget):
    # Sinais para o controller
    sig_load_file = pyqtSignal()
    sig_identify   = pyqtSignal()
    sig_export     = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ── Painel esquerdo ────────────────────────────────────────────────
        left = QWidget()
        left.setFixedWidth(240)
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(12)

        # Header
        title = QLabel("IDENTIFICAÇÃO")
        title.setObjectName("labelTitle")
        sub = QLabel("Método de Smith — FOPDT")
        sub.setObjectName("labelSub")
        left_layout.addWidget(title)
        left_layout.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator"); sep.setFrameShape(QFrame.HLine)
        left_layout.addWidget(sep)

        # Arquivo
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

        # Parâmetros identificados
        grp_params = QGroupBox("PARÂMETROS FOPDT")
        grp_params_layout = QGridLayout(grp_params)
        grp_params_layout.setSpacing(8)

        self.card_K     = ParamCard("Kₛ", "ganho")
        self.card_tau   = ParamCard("τₛ", "tempo")
        self.card_theta = ParamCard("θₛ", "atraso")
        self.card_eqm   = ParamCard("EQM", "")

        grp_params_layout.addWidget(self.card_K,     0, 0)
        grp_params_layout.addWidget(self.card_tau,   0, 1)
        grp_params_layout.addWidget(self.card_theta, 1, 0)
        grp_params_layout.addWidget(self.card_eqm,   1, 1)
        left_layout.addWidget(grp_params)

        # Botões de ação
        self.btn_identify = QPushButton("🔍  Identificar")
        self.btn_identify.setObjectName("btnGreen")
        self.btn_identify.setEnabled(False)
        self.btn_export = QPushButton("💾  Exportar Gráfico")
        self.btn_export.setEnabled(False)

        left_layout.addWidget(self.btn_identify)
        left_layout.addWidget(self.btn_export)
        left_layout.addStretch()

        # ── Gráfico ───────────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self, width=7, height=5)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet(f"background:{CARD_BG}; color:{TEXT_MUTED};")

        right_layout.addWidget(toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)

        # Conexões internas → emite sinais para controller
        self.btn_load.clicked.connect(self.sig_load_file.emit)
        self.btn_identify.clicked.connect(self.sig_identify.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)

    def set_file_label(self, text):
        self.label_file.setText(text)

    def set_params(self, K, tau, theta, eqm):
        self.card_K.set_value(K)
        self.card_tau.set_value(tau)
        self.card_theta.set_value(theta)
        self.card_eqm.set_value(eqm)

    def clear_params(self):
        for c in [self.card_K, self.card_tau, self.card_theta, self.card_eqm]:
            c.clear()


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 2 — Controle PID
# ═══════════════════════════════════════════════════════════════════════════════

class TabControlePID(QWidget):
    sig_tune   = pyqtSignal()
    sig_export = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # ── Painel esquerdo ────────────────────────────────────────────────
        left = QWidget()
        left.setFixedWidth(260)
        left_layout = QVBoxLayout(left)
        left_layout.setSpacing(12)

        title = QLabel("CONTROLE PID")
        title.setObjectName("labelTitle")
        sub = QLabel("IMC  ·  ITAE")
        sub.setObjectName("labelSub")
        left_layout.addWidget(title)
        left_layout.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator"); sep.setFrameShape(QFrame.HLine)
        left_layout.addWidget(sep)

        # Seleção método
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

        # Parâmetros PID
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

        grp_pid_layout.addWidget(QLabel("Kp :"), 0, 0)
        grp_pid_layout.addWidget(self.spin_Kp,  0, 1)
        grp_pid_layout.addWidget(QLabel("Ti :"), 1, 0)
        grp_pid_layout.addWidget(self.spin_Ti,  1, 1)
        grp_pid_layout.addWidget(QLabel("Td :"), 2, 0)
        grp_pid_layout.addWidget(self.spin_Td,  2, 1)
        grp_pid_layout.addWidget(QLabel("λ  :"), 3, 0)
        grp_pid_layout.addWidget(self.spin_lam, 3, 1)
        left_layout.addWidget(grp_pid)

        # SetPoint e Métricas
        grp_ctrl = QGroupBox("CONTROLE")
        grp_ctrl_layout = QGridLayout(grp_ctrl)

        self.spin_sp = make_spin(lo=-1e4, hi=1e4, dec=2, step=1)
        self.spin_sp.setValue(1.0)

        self.card_tr = ParamCard("tᵣ", "subida")
        self.card_ts = ParamCard("tₛ", "acomod.")
        self.card_mp = ParamCard("Mp", "%")
        self.card_ess = ParamCard("ess", "erro")

        grp_ctrl_layout.addWidget(QLabel("SetPoint:"), 0, 0)
        grp_ctrl_layout.addWidget(self.spin_sp, 0, 1)
        grp_ctrl_layout.addWidget(self.card_tr,  1, 0)
        grp_ctrl_layout.addWidget(self.card_ts,  1, 1)
        grp_ctrl_layout.addWidget(self.card_mp,  2, 0)
        grp_ctrl_layout.addWidget(self.card_ess, 2, 1)
        left_layout.addWidget(grp_ctrl)

        # Botões
        self.btn_tune   = QPushButton("⚙️  Sintonizar")
        self.btn_tune.setObjectName("btnGreen")
        self.btn_tune.setEnabled(False)
        self.btn_export = QPushButton("💾  Exportar Gráfico")
        self.btn_export.setEnabled(False)

        left_layout.addWidget(self.btn_tune)
        left_layout.addWidget(self.btn_export)
        left_layout.addStretch()

        # ── Gráfico ───────────────────────────────────────────────────────
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = MplCanvas(self, width=7, height=5)
        toolbar = NavigationToolbar(self.canvas, self)
        toolbar.setStyleSheet(f"background:{CARD_BG}; color:{TEXT_MUTED};")

        right_layout.addWidget(toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)

        # Conexões
        self.btn_tune.clicked.connect(self.sig_tune.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)
        self.radio_method.toggled.connect(self._on_mode_changed)
        self.radio_manual.toggled.connect(self._on_mode_changed)

        self._on_mode_changed()

    def _on_mode_changed(self):
        is_method = self.radio_method.isChecked()
        self.combo_method.setEnabled(is_method)
        self.spin_Kp.setReadOnly(is_method)
        self.spin_Ti.setReadOnly(is_method)
        self.spin_Td.setReadOnly(is_method)
        lam_visible = is_method and self.combo_method.currentText() == "IMC"
        self.spin_lam.setEnabled(lam_visible)

    def set_pid_params(self, Kp, Ti, Td):
        self.spin_Kp.setValue(Kp)
        self.spin_Ti.setValue(Ti)
        self.spin_Td.setValue(Td)

    def set_metrics(self, tr, ts, Mp, ess):
        def _s(card, v):
            if v is not None:
                card.set_value(v, ".2f")
            else:
                card.clear()
        _s(self.card_tr,  tr)
        _s(self.card_ts,  ts)
        _s(self.card_mp,  Mp)
        _s(self.card_ess, ess)

    def get_pid_params(self):
        return (self.spin_Kp.value(), self.spin_Ti.value(), self.spin_Td.value())

    def is_manual(self):
        return self.radio_manual.isChecked()

    def get_method(self):
        return self.combo_method.currentText()

    def get_lambda(self):
        return self.spin_lam.value()

    def get_setpoint(self):
        return self.spin_sp.value()


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 3 — Gráficos Comparativos
# ═══════════════════════════════════════════════════════════════════════════════

class TabGraficos(QWidget):
    sig_compare = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        header = QHBoxLayout()
        title = QLabel("COMPARAÇÃO — MALHA ABERTA × MALHA FECHADA")
        title.setObjectName("labelTitle")
        self.btn_compare = QPushButton("📊  Atualizar Comparação")
        self.btn_compare.setObjectName("btnAccent")
        self.btn_compare.setEnabled(False)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.btn_compare)
        layout.addLayout(header)

        sep = QFrame(); sep.setObjectName("separator"); sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        # Dois gráficos lado a lado
        plots = QHBoxLayout()
        self.canvas_ol = MplCanvas(self, width=5, height=4)
        self.canvas_cl = MplCanvas(self, width=5, height=4)

        frame_ol = QGroupBox("MALHA ABERTA (Open Loop)")
        fl = QVBoxLayout(frame_ol)
        fl.addWidget(self.canvas_ol)

        frame_cl = QGroupBox("MALHA FECHADA (Closed Loop)")
        fcl = QVBoxLayout(frame_cl)
        fcl.addWidget(self.canvas_cl)

        plots.addWidget(frame_ol)
        plots.addWidget(frame_cl)
        layout.addLayout(plots)

        self.btn_compare.clicked.connect(self.sig_compare.emit)


# ═══════════════════════════════════════════════════════════════════════════════
# Janela Principal
# ═══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C213 — Identificação & Controle PID  |  Grupo 7")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(STYLE_SHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header faixa
        header_bar = QFrame()
        header_bar.setFixedHeight(48)
        header_bar.setStyleSheet(f"background: {CARD_BG}; border-bottom: 1px solid {BORDER};")
        hb_layout = QHBoxLayout(header_bar)
        hb_layout.setContentsMargins(16, 0, 16, 0)

        logo = QLabel("◈  C213  ·  PID CONTROLLER")
        logo.setStyleSheet(f"color: {ACCENT}; font-size: 15px; font-weight: bold; letter-spacing: 3px;")
        grupo = QLabel("GRUPO 7  ·  IMC + ITAE")
        grupo.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; letter-spacing: 2px;")

        hb_layout.addWidget(logo)
        hb_layout.addStretch()
        hb_layout.addWidget(grupo)
        root.addWidget(header_bar)

        # Tabs
        self.tabs = QTabWidget()
        self.tab_ident = TabIdentificacao()
        self.tab_pid   = TabControlePID()
        self.tab_graf  = TabGraficos()

        self.tabs.addTab(self.tab_ident, "  IDENTIFICAÇÃO  ")
        self.tabs.addTab(self.tab_pid,   "  CONTROLE PID   ")
        self.tabs.addTab(self.tab_graf,  "  GRÁFICOS       ")

        root.addWidget(self.tabs, stretch=1)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Pronto  |  Carregue um arquivo .mat para começar")

    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erro", msg)

    def show_info(self, msg: str):
        QMessageBox.information(self, "Info", msg)

    def set_status(self, msg: str):
        self.status.showMessage(msg)
