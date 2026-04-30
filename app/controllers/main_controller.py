"""
Controller — conecta View ↔ Model (MVC)
C213 - Sistemas de Controle Automático — Grupo 7
"""

import os
import numpy as np
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject

from app.models.system_model import (
    load_mat_file,
    identify_smith,
    tune_imc,
    tune_itae,
    simulate_closed_loop,
)
from app.views.main_window import (
    MainWindow, ACCENT, ACCENT2, ACCENT3, BORDER, TEXT_MUTED, CARD_BG
)


# ── Formatadores que toleram None ───────────────────────────────────────────

def _fmt(value, fmt=".2f", placeholder="—"):
    """Formata valor numérico, retorna placeholder se None."""
    if value is None:
        return placeholder
    try:
        return f"{value:{fmt}}"
    except (TypeError, ValueError):
        return placeholder


# ════════════════════════════════════════════════════════════════════════════

class MainController(QObject):
    def __init__(self, view: MainWindow):
        super().__init__()
        self.view = view

        self._data       = None
        self._ident      = None
        self._pid_params = None
        self._cl_result  = None

        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────────
    # Sinais
    # ──────────────────────────────────────────────────────────────────────
    def _connect_signals(self):
        t_id  = self.view.tab_ident
        t_pid = self.view.tab_pid
        t_gr  = self.view.tab_graf

        t_id.sig_load_file.connect(self._on_load_file)
        t_id.sig_identify.connect(self._on_identify)
        t_id.sig_export.connect(lambda: self._export_canvas(t_id.canvas, "identificacao"))

        t_pid.sig_tune.connect(self._on_tune)
        t_pid.sig_export.connect(lambda: self._export_canvas(t_pid.canvas, "controle_pid"))
        t_pid.combo_method.currentTextChanged.connect(self._on_method_changed)
        t_pid.radio_method.toggled.connect(self._on_method_changed)

        t_gr.sig_compare.connect(self._on_compare)

    # ──────────────────────────────────────────────────────────────────────
    # 1. Carregamento de arquivo
    # ──────────────────────────────────────────────────────────────────────
    def _on_load_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Abrir Dataset", "", "MATLAB Files (*.mat);;All Files (*)"
        )
        if not path:
            return

        try:
            self._data = load_mat_file(path)
        except Exception as e:
            self.view.show_error(f"Erro ao carregar arquivo:\n{e}")
            return

        filename = os.path.basename(path)
        self.view.tab_ident.set_file_label(filename)
        self.view.tab_ident.btn_identify.setEnabled(True)
        self.view.tab_ident.btn_export.setEnabled(False)
        self.view.tab_ident.clear_params()

        # Reseta abas downstream
        self.view.tab_pid.btn_tune.setEnabled(False)
        self.view.tab_pid.btn_export.setEnabled(False)
        self.view.tab_graf.btn_compare.setEnabled(False)
        self._ident = None
        self._cl_result = None

        info = (f"Arquivo: {filename}  |  {len(self._data['time'])} amostras  |  "
                f"vars: {self._data['input_key']} → {self._data['output_key']}")
        self.view.set_status(info)

        self._plot_raw_data()

    def _plot_raw_data(self):
        canvas = self.view.tab_ident.canvas
        canvas.clear_and_style()
        ax = canvas.ax

        t = self._data['time']
        y = self._data['output']
        u = self._data['input']

        ax2 = ax.twinx()
        ax2.set_facecolor("none")
        ax2.tick_params(colors=TEXT_MUTED, labelsize=9)
        for spine in ax2.spines.values():
            spine.set_edgecolor(BORDER)

        line_y = ax.plot(t, y, color=ACCENT, linewidth=1.8, label="Saída y(t)")[0]
        line_u = ax2.plot(t, u, color=ACCENT3, linewidth=1.2, linestyle='--',
                          alpha=0.8, label="Entrada u(t)")[0]

        ax.set_xlabel("Tempo", color=TEXT_MUTED)
        ax.set_ylabel("Saída", color=ACCENT)
        ax2.set_ylabel("Entrada", color=ACCENT3)
        ax.set_title("Dados do Dataset", color=ACCENT, fontsize=12, fontweight='bold')

        ax.legend(handles=[line_y, line_u],
                  facecolor=CARD_BG, edgecolor=BORDER,
                  labelcolor=TEXT_MUTED, fontsize=9)

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    # ──────────────────────────────────────────────────────────────────────
    # 2. Identificação Smith
    # ──────────────────────────────────────────────────────────────────────
    def _on_identify(self):
        if self._data is None:
            return

        try:
            self._ident = identify_smith(
                self._data['time'],
                self._data['output'],
                self._data['input'],
            )
        except Exception as e:
            self.view.show_error(f"Erro na identificação:\n{e}")
            return

        r = self._ident
        self.view.tab_ident.set_params(r['K'], r['tau'], r['theta'], r['eqm'])
        self.view.set_status(
            f"Smith  |  K={r['K']:.4f}  τ={r['tau']:.4f}  "
            f"θ={r['theta']:.4f}  EQM={r['eqm']:.6f}  |  "
            f"degrau detectado em t={r['t_step']:.2f}"
        )

        self._plot_identification()

        # Habilita aba PID + sugere SP igual ao regime permanente
        self.view.tab_pid.btn_tune.setEnabled(True)
        n_tail = max(3, len(self._data['output']) // 20)
        sp_default = float(np.mean(self._data['output'][-n_tail:]))
        self.view.tab_pid.spin_sp.setValue(sp_default)

        # Sugere λ inicial = θ (regra prática IMC)
        if r['theta'] > 0:
            self.view.tab_pid.spin_lam.setValue(max(0.001, r['theta']))

    def _plot_identification(self):
        canvas = self.view.tab_ident.canvas
        canvas.clear_and_style()
        ax = canvas.ax

        t = self._data['time']
        y_real  = self._data['output']
        y_model = self._ident['y_model']

        ax.plot(t, y_real,  color=ACCENT,  linewidth=1.8, label="Dados reais")
        ax.plot(t, y_model, color=ACCENT2, linewidth=1.8, linestyle='--',
                label="Modelo FOPDT (Smith)")

        # Marca o instante do degrau
        if self._ident['t_step'] > t[0]:
            ax.axvline(self._ident['t_step'], color=ACCENT3, linewidth=0.8,
                       linestyle=':', alpha=0.7, label=f"Degrau t={self._ident['t_step']:.1f}")

        r = self._ident
        info = f"K={r['K']:.3f}  τ={r['tau']:.3f}  θ={r['theta']:.3f}  EQM={r['eqm']:.5f}"
        ax.set_title(f"Identificação Smith  —  {info}",
                     color=ACCENT, fontsize=11, fontweight='bold')
        ax.set_xlabel("Tempo", color=TEXT_MUTED)
        ax.set_ylabel("Amplitude", color=TEXT_MUTED)
        ax.legend(facecolor=CARD_BG, edgecolor=BORDER,
                  labelcolor=TEXT_MUTED, fontsize=9)

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

        self.view.tab_ident.btn_export.setEnabled(True)

    # ──────────────────────────────────────────────────────────────────────
    # 3. Sintonia PID
    # ──────────────────────────────────────────────────────────────────────
    def _on_method_changed(self):
        t_pid = self.view.tab_pid
        is_method = t_pid.radio_method.isChecked()
        lam_ok = is_method and t_pid.combo_method.currentText() == "IMC"
        t_pid.spin_lam.setEnabled(lam_ok)

    def _on_tune(self):
        if self._ident is None:
            self.view.show_error("Execute a identificação primeiro.")
            return

        K, tau, theta = self._ident['K'], self._ident['tau'], self._ident['theta']
        t_pid = self.view.tab_pid

        try:
            if t_pid.is_manual():
                Kp, Ti, Td = t_pid.get_pid_params()
                if Ti <= 0:
                    self.view.show_error("Ti deve ser maior que zero.")
                    return
                method_name = "Manual"
            else:
                method = t_pid.get_method()
                if method == "IMC":
                    result = tune_imc(K, tau, theta, t_pid.get_lambda())
                elif method == "ITAE":
                    result = tune_itae(K, tau, theta)
                else:
                    self.view.show_error(f"Método desconhecido: {method}")
                    return

                Kp, Ti, Td  = result['Kp'], result['Ti'], result['Td']
                method_name = result['method']
                t_pid.set_pid_params(Kp, Ti, Td)
        except Exception as e:
            self.view.show_error(f"Erro na sintonia:\n{e}")
            return

        self._pid_params = {'Kp': Kp, 'Ti': Ti, 'Td': Td, 'method': method_name}

        setpoint = t_pid.get_setpoint()
        try:
            self._cl_result = simulate_closed_loop(K, tau, theta, Kp, Ti, Td,
                                                    setpoint=setpoint)
        except Exception as e:
            self.view.show_error(f"Erro na simulação:\n{e}")
            return

        m = self._cl_result['metrics']
        t_pid.set_metrics(m['tr'], m['ts'], m['Mp'], m['ess'])

        self._plot_closed_loop(setpoint, method_name)

        self.view.set_status(
            f"{method_name}  |  Kp={Kp:.4f}  Ti={Ti:.4f}  Td={Td:.4f}  |  "
            f"tr={_fmt(m['tr'])}  ts={_fmt(m['ts'])}  "
            f"Mp={_fmt(m['Mp'])}%  ess={_fmt(m['ess'], '.4f')}"
        )

        self.view.tab_pid.btn_export.setEnabled(True)
        self.view.tab_graf.btn_compare.setEnabled(True)

    def _plot_closed_loop(self, setpoint, method_name):
        canvas = self.view.tab_pid.canvas
        canvas.clear_and_style()
        ax = canvas.ax

        t = self._cl_result['time']
        y = self._cl_result['output']
        m = self._cl_result['metrics']

        ax.plot(t, y, color=ACCENT, linewidth=2, label=f"Saída — {method_name}")
        ax.axhline(setpoint, color=ACCENT2, linewidth=1.2, linestyle='--',
                   label=f"SetPoint = {setpoint:.2f}")

        # Faixa ±2%
        ax.fill_between(t, setpoint * 0.98, setpoint * 1.02,
                        color=ACCENT2, alpha=0.08)

        # Garante limites antes de pegar ax.get_ylim()
        canvas.draw_idle()
        y_lo, y_hi = ax.get_ylim()
        text_y = y_lo + (y_hi - y_lo) * 0.02

        if m['tr'] is not None:
            ax.axvline(m['tr'], color=ACCENT3, linewidth=0.8,
                       linestyle=':', alpha=0.8)
            ax.text(m['tr'], text_y, f" tᵣ={m['tr']:.1f}",
                    color=ACCENT3, fontsize=8)

        if m['ts'] is not None:
            ax.axvline(m['ts'], color='#d2a8ff', linewidth=0.8,
                       linestyle=':', alpha=0.8)
            ax.text(m['ts'], text_y, f" tₛ={m['ts']:.1f}",
                    color='#d2a8ff', fontsize=8)

        ax.set_title(f"Resposta Malha Fechada — {method_name}",
                     color=ACCENT, fontsize=11, fontweight='bold')
        ax.set_xlabel("Tempo", color=TEXT_MUTED)
        ax.set_ylabel("Amplitude", color=TEXT_MUTED)
        ax.legend(facecolor=CARD_BG, edgecolor=BORDER,
                  labelcolor=TEXT_MUTED, fontsize=9)

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    # ──────────────────────────────────────────────────────────────────────
    # 4. Gráficos comparativos
    # ──────────────────────────────────────────────────────────────────────
    def _on_compare(self):
        if self._data is None or self._ident is None or self._cl_result is None:
            self.view.show_info("Execute identificação e sintonia antes de comparar.")
            return

        t_gr = self.view.tab_graf

        # ── OL ──
        canvas_ol = t_gr.canvas_ol
        canvas_ol.clear_and_style()
        ax_ol = canvas_ol.ax

        t  = self._data['time']
        ax_ol.plot(t, self._data['output'], color=ACCENT,  linewidth=1.8,
                   label="Dados reais")
        ax_ol.plot(t, self._ident['y_model'], color=ACCENT2, linewidth=1.6,
                   linestyle='--', label="Modelo FOPDT")
        ax_ol.set_title(f"Malha Aberta — Smith (EQM={self._ident['eqm']:.5f})",
                        color=ACCENT, fontsize=10, fontweight='bold')
        ax_ol.set_xlabel("Tempo", color=TEXT_MUTED)
        ax_ol.set_ylabel("Amplitude", color=TEXT_MUTED)
        ax_ol.legend(facecolor=CARD_BG, edgecolor=BORDER,
                     labelcolor=TEXT_MUTED, fontsize=9)
        canvas_ol.figure.tight_layout(pad=2)
        canvas_ol.draw()

        # ── CL ──
        canvas_cl = t_gr.canvas_cl
        canvas_cl.clear_and_style()
        ax_cl = canvas_cl.ax

        t_cl = self._cl_result['time']
        y_cl = self._cl_result['output']
        sp   = self.view.tab_pid.get_setpoint()
        method = self._pid_params['method'] if self._pid_params else "PID"

        ax_cl.plot(t_cl, y_cl, color=ACCENT, linewidth=2, label=f"{method}")
        ax_cl.axhline(sp, color=ACCENT2, linewidth=1.2, linestyle='--',
                      label=f"SP={sp:.2f}")
        ax_cl.fill_between(t_cl, sp * 0.98, sp * 1.02,
                           color=ACCENT2, alpha=0.08, label="±2%")

        ax_cl.set_title(f"Malha Fechada — {method}",
                        color=ACCENT, fontsize=10, fontweight='bold')
        ax_cl.set_xlabel("Tempo", color=TEXT_MUTED)
        ax_cl.set_ylabel("Amplitude", color=TEXT_MUTED)
        ax_cl.legend(facecolor=CARD_BG, edgecolor=BORDER,
                     labelcolor=TEXT_MUTED, fontsize=9)
        canvas_cl.figure.tight_layout(pad=2)
        canvas_cl.draw()

        self.view.set_status("Comparação atualizada  |  OL × CL")

    # ──────────────────────────────────────────────────────────────────────
    # Exportação
    # ──────────────────────────────────────────────────────────────────────
    def _export_canvas(self, canvas, default_name: str):
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Exportar Gráfico", f"{default_name}.png",
            "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)"
        )
        if not path:
            return
        try:
            canvas.figure.savefig(path, dpi=150, bbox_inches='tight',
                                  facecolor=canvas.figure.get_facecolor())
            self.view.set_status(f"Gráfico exportado: {os.path.basename(path)}")
        except Exception as e:
            self.view.show_error(f"Erro ao exportar:\n{e}")
