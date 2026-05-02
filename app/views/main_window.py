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

# ── Paletas de cores ───────────────────────────────────────────────────────────
DARK_PALETTE = {
    "BG":       "#0d1117",
    "CARD":     "#161b22",
    "BORDER":   "#30363d",
    "ACCENT":   "#58a6ff",
    "ACCENT2":  "#3fb950",
    "ACCENT3":  "#f78166",
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
    "TEXT":     "#1f2328",
    "MUTED":    "#656d76",
    "INPUT":    "#ffffff",
    "HOVER":    "#0550ae",
    "DISABLED": "#c8ced6",
}

# Tema activo (começa dark)
_current_palette = DARK_PALETTE

def _p(key):
    return _current_palette[key]

def set_palette(palette: dict):
    global _current_palette
    _current_palette = palette

# Atalhos para compatibilidade com o controller (importados de fora)
def _get_colors():
    return (_p("BG"), _p("CARD"), _p("BORDER"),
            _p("ACCENT"), _p("ACCENT2"), _p("ACCENT3"),
            _p("TEXT"), _p("MUTED"), _p("INPUT"), _p("HOVER"))

# Aliases usados no controller
DARK_BG    = property(lambda self: _p("BG"))
CARD_BG    = "#161b22"   # será sobrescrito dinamicamente via função
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#3fb950"
ACCENT3    = "#f78166"
TEXT_MAIN  = "#e6edf3"
TEXT_MUTED = "#8b949e"
INPUT_BG   = "#21262d"
HOVER      = "#1f6feb"


def _build_stylesheet(p):
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
    color: {'white' if p == DARK_PALETTE else 'white'};
}}
QPushButton:pressed {{
    background: {'#0d419d' if p == DARK_PALETTE else '#0550ae'};
}}
QPushButton:disabled {{
    color: {p['MUTED']};
    background: {p['BG']};
    border-color: {p['BORDER']};
}}
QPushButton#btnAccent {{
    background: {p['ACCENT']};
    color: {'#0d1117' if p == DARK_PALETTE else 'white'};
    border: none;
}}
QPushButton#btnAccent:hover {{
    background: {'#79c0ff' if p == DARK_PALETTE else '#0550ae'};
}}
QPushButton#btnGreen {{
    background: {p['ACCENT2']};
    color: {'#0d1117' if p == DARK_PALETTE else 'white'};
    border: none;
}}
QPushButton#btnGreen:hover {{
    background: {'#56d364' if p == DARK_PALETTE else '#1a7f37'};
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
QRadioButton::indicator:checked {{
    background: {p['ACCENT']};
    border-radius: 6px;
    border: 2px solid {p['ACCENT']};
}}
QRadioButton::indicator:unchecked {{
    background: {p['INPUT']};
    border-radius: 6px;
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
"""

STYLE_SHEET = _build_stylesheet(DARK_PALETTE)

# ── Legado: constantes simples para o controller ──────────────────────────────
# (o controller importa estas; serão atualizadas via apply_theme)
DARK_BG    = DARK_PALETTE["BG"]
CARD_BG    = DARK_PALETTE["CARD"]
BORDER     = DARK_PALETTE["BORDER"]
ACCENT     = DARK_PALETTE["ACCENT"]
ACCENT2    = DARK_PALETTE["ACCENT2"]
ACCENT3    = DARK_PALETTE["ACCENT3"]
TEXT_MAIN  = DARK_PALETTE["TEXT"]
TEXT_MUTED = DARK_PALETTE["MUTED"]
INPUT_BG   = DARK_PALETTE["INPUT"]
HOVER      = DARK_PALETTE["HOVER"]


# ── Canvas Matplotlib ──────────────────────────────────────────────────────────

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=6, height=4):
        fig = Figure(figsize=(width, height), facecolor=_current_palette["BG"])
        self.ax = fig.add_subplot(111)
        self._style_ax()
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        fig.tight_layout(pad=2)

    def _style_ax(self):
        p = _current_palette
        self.ax.set_facecolor(p["CARD"])
        self.ax.tick_params(colors=p["MUTED"], labelsize=9)
        self.ax.xaxis.label.set_color(p["MUTED"])
        self.ax.yaxis.label.set_color(p["MUTED"])
        for spine in self.ax.spines.values():
            spine.set_edgecolor(p["BORDER"])

    def apply_theme(self):
        """Re-aplica cores do tema atual ao canvas."""
        p = _current_palette
        self.figure.set_facecolor(p["BG"])
        self._style_ax()
        self.draw_idle()

    def clear_and_style(self):
        self.ax.cla()
        self._style_ax()


# ── Widget de parâmetro identificado ──────────────────────────────────────────

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
        p = _current_palette
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
        self._toolbar = NavigationToolbar(self.canvas, self)
        self._apply_toolbar_theme()

        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)

        # Conexões internas → emite sinais para controller
        self.btn_load.clicked.connect(self.sig_load_file.emit)
        self.btn_identify.clicked.connect(self.sig_identify.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)

    def _apply_toolbar_theme(self):
        p = _current_palette
        self._toolbar.setStyleSheet(
            f"background:{p['CARD']}; color:{p['MUTED']};"
        )

    def apply_theme(self):
        self._apply_toolbar_theme()
        self.canvas.apply_theme()
        for card in [self.card_K, self.card_tau, self.card_theta, self.card_eqm]:
            card.apply_theme()

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
        self._lam_saved = 1.0  # guarda λ ao trocar para ITAE

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
        self._toolbar = NavigationToolbar(self.canvas, self)
        self._apply_toolbar_theme()

        right_layout.addWidget(self._toolbar)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left)
        main_layout.addWidget(right, stretch=1)

        # Conexões
        self.btn_tune.clicked.connect(self.sig_tune.emit)
        self.btn_export.clicked.connect(self.sig_export.emit)
        self.radio_method.toggled.connect(self._on_mode_changed)
        self.radio_manual.toggled.connect(self._on_mode_changed)
        self.combo_method.currentTextChanged.connect(self._on_mode_changed)

        self._on_mode_changed()

    def _on_mode_changed(self, *_):
        is_method = self.radio_method.isChecked()
        is_manual = not is_method
        # combo sempre habilitado — usuário pode escolher IMC/ITAE em qualquer modo
        is_itae   = self.combo_method.currentText() == "ITAE"

        # Salva λ APENAS quando o valor atual é real (não é o "N/A" do ITAE)
        current_lam = self.spin_lam.value()
        if current_lam > self.spin_lam.minimum():
            self._lam_saved = current_lam

        # Salva Kp/Ti/Td antes de qualquer alteração
        kp_val = self.spin_Kp.value()
        ti_val = self.spin_Ti.value()
        td_val = self.spin_Td.value()

        # combo sempre habilitado para trocar IMC/ITAE em qualquer modo
        self.combo_method.setEnabled(True)

        # Kp / Ti / Td: somente editável no modo manual
        for spin, val in ((self.spin_Kp, kp_val),
                          (self.spin_Ti, ti_val),
                          (self.spin_Td, td_val)):
            spin.setReadOnly(is_method)
            spin.setValue(val)

        muted  = _current_palette["MUTED"]
        normal = _current_palette["TEXT"]

        if is_itae:
            # ITAE: λ desabilitado completamente, mostra N/A
            self.spin_lam.setReadOnly(False)   # precisa estar writable para setValue
            self.spin_lam.setEnabled(False)
            self.spin_lam.setSpecialValueText("N/A")
            self.spin_lam.setValue(self.spin_lam.minimum())
            self.lbl_lam.setStyleSheet(f"color: {muted};")
        elif is_manual:
            # Manual: λ editável (usuário pode ajustar)
            self.spin_lam.setEnabled(True)
            self.spin_lam.setReadOnly(False)
            self.spin_lam.setSpecialValueText("")
            self.spin_lam.setValue(self._lam_saved)
            self.lbl_lam.setStyleSheet(f"color: {normal};")
        else:
            # IMC automático: λ visível e editável (é parâmetro de projeto do IMC)
            # mas salvamos o valor atual para não perder ao trocar modo
            self.spin_lam.setEnabled(True)
            self.spin_lam.setReadOnly(True)
            self.spin_lam.setSpecialValueText("")
            self.spin_lam.setValue(self._lam_saved)
            self.lbl_lam.setStyleSheet(f"color: {normal};")

            
    def _apply_toolbar_theme(self):
        p = _current_palette
        self._toolbar.setStyleSheet(
            f"background:{p['CARD']}; color:{p['MUTED']};"
        )

    def apply_theme(self):
        self._apply_toolbar_theme()
        self.canvas.apply_theme()
        for card in [self.card_tr, self.card_ts, self.card_mp, self.card_ess]:
            card.apply_theme()
        self._on_mode_changed()

    def set_pid_params(self, Kp, Ti, Td):
        self.spin_Kp.setValue(Kp)
        self.spin_Ti.setValue(Ti)
        self.spin_Td.setValue(Td)

    def set_lambda(self, lam: float):
        """Atualiza λ e o valor salvo — usar sempre que o controller quiser mudar λ."""
        self._lam_saved = lam
        if self.spin_lam.isEnabled():
            self.spin_lam.setValue(lam)

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
        self._is_dark = True
        self.setWindowTitle("C213 — Identificação & Controle PID  |  Grupo 7")
        self.setMinimumSize(1100, 680)
        self.setStyleSheet(STYLE_SHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header faixa
        self._header_bar = QFrame()
        self._header_bar.setFixedHeight(48)
        self._header_bar.setStyleSheet(
            f"background: {DARK_PALETTE['CARD']}; border-bottom: 1px solid {DARK_PALETTE['BORDER']};")
        hb_layout = QHBoxLayout(self._header_bar)
        hb_layout.setContentsMargins(16, 0, 16, 0)

        self._logo = QLabel("◈  C213  ·  PID CONTROLLER")
        self._logo.setStyleSheet(
            f"color: {DARK_PALETTE['ACCENT']}; font-size: 15px; font-weight: bold; letter-spacing: 3px;")
        self._grupo = QLabel("GRUPO 7  ·  IMC + ITAE")
        self._grupo.setStyleSheet(
            f"color: {DARK_PALETTE['MUTED']}; font-size: 11px; letter-spacing: 2px;")

        # Botão de toggle de tema
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

    # ── Tema ──────────────────────────────────────────────────────────────────
    def _toggle_theme(self):
        self._is_dark = not self._is_dark
        palette = DARK_PALETTE if self._is_dark else LIGHT_PALETTE
        self.apply_theme(palette)

    def apply_theme(self, palette: dict):
        global _current_palette
        _current_palette = palette
        set_palette(palette)

        # Stylesheet global
        self.setStyleSheet(_build_stylesheet(palette))

        # Header bar
        self._header_bar.setStyleSheet(
            f"background: {palette['CARD']}; border-bottom: 1px solid {palette['BORDER']};")
        self._logo.setStyleSheet(
            f"color: {palette['ACCENT']}; font-size: 15px; font-weight: bold; letter-spacing: 3px;")
        self._grupo.setStyleSheet(
            f"color: {palette['MUTED']}; font-size: 11px; letter-spacing: 2px;")

        # Propaga tema para cada aba (toolbars, canvas, ParamCards)
        self.tab_ident.apply_theme()
        self.tab_pid.apply_theme()
        for canvas in (self.tab_graf.canvas_ol, self.tab_graf.canvas_cl):
            canvas.apply_theme()

        # Texto do botão
        self._btn_theme.setText("🌙  Dark" if not self._is_dark else "☀  Light")

    # ── Mensagens ─────────────────────────────────────────────────────────────
    def show_error(self, msg: str):
        QMessageBox.critical(self, "Erro", msg)

    def show_info(self, msg: str):
        QMessageBox.information(self, "Info", msg)

    def set_status(self, msg: str):
        self.status.showMessage(msg)