import os
import numpy as np
import scipy.io as sio

from PyQt5.QtWidgets import QFileDialog

from app.models.identification import identify_smith, simulate_fopdt
from app.models.pid_tuning import (
    tune_imc, tune_itae,
    simulate_closed_loop, simulate_open_loop,
    closed_loop_tf, is_stable, response_metrics,
)
from app.views.main_window import palette


class MainController:
    def __init__(self, view):
        self.view = view

        # Estado
        self.t = None
        self.u = None
        self.y = None
        self.params = None     
        self.last_sim = None   

        self._connect_signals()

    # ──────────────────────────────────────────────────────────────────
    def _connect_signals(self):
        # Aba 1 — Identificação
        self.view.tab_ident.sig_load_file.connect(self.load_dataset)
        self.view.tab_ident.sig_export.connect(self._export_ident)


        self.view.tab_pid.sig_tune.connect(self.simulate_pid)
        self.view.tab_pid.sig_method_changed.connect(self._update_pid_from_method)
        self.view.tab_pid.sig_lambda_changed.connect(self._update_pid_from_method)
        self.view.tab_pid.sig_export.connect(self._export_pid)

        self.view.tab_graf.sig_compare.connect(self.compare_plots)
        self.view.tab_graf.sig_export.connect(self._export_compare)


    def load_dataset(self):
        path, _ = QFileDialog.getOpenFileName(
            self.view, "Selecionar arquivo .mat", "", "MATLAB files (*.mat)"
        )
        if not path:
            return

        try:
            data = sio.loadmat(path)
            t = self._find_key(data, ["tiempo", "tempo", "t", "time"])
            u = self._find_key(data, ["entrada", "u", "input"])
            y = self._find_key(data, ["salida", "saida", "y", "output"])
            if t is None or u is None or y is None:
                raise ValueError(
                    "Não localizei os vetores tempo/entrada/saída no .mat.\n"
                    "Esperado: 'tiempo'/'tempo', 'entrada', 'salida'/'saida'."
                )
            self.t = np.asarray(t).squeeze()
            self.u = np.asarray(u).squeeze()
            self.y = np.asarray(y).squeeze()


            self.params = identify_smith(self.t, self.u, self.y)

            # Atualizar UI
            p = self.params
            self.view.tab_ident.set_file_label(os.path.basename(path))
            self.view.tab_ident.set_params(
                p["k"], p["tau"], p["theta"], p["eqm"]
            )
            self.view.tab_ident.set_experiment_info(
                p["u0"], p["u1"], p["y_inf"], p["t_step"]
            )
            self._plot_identification()
            self.view.tab_ident.btn_export.setEnabled(True)


            self.view.tab_pid.btn_tune.setEnabled(True)
            self.view.tab_graf.btn_compare.setEnabled(True)

            if self.view.tab_pid.spin_lam.value() <= self.view.tab_pid.spin_lam.minimum() + 0.001:
                self.view.tab_pid.set_lambda(self.params["tau"])
            self.view.tab_pid._lam_saved = self.params["tau"]
            if self.view.tab_pid.spin_lam.isEnabled():
                self.view.tab_pid.set_lambda(self.params["tau"])

            # Recalcular PID conforme método atual
            self._update_pid_from_method()

            self.view.set_status(
                f"✓ Identificação concluída  |  k={p['k']:.4f}  τ={p['tau']:.4f}"
                f"  θ={p['theta']:.4f}  EQM={p['eqm']:.4f}"
            )
        except Exception as exc:
            self.view.show_error(f"Erro ao carregar dataset:\n\n{exc}")

    @staticmethod
    def _find_key(d, candidates):
        for c in candidates:
            if c in d:
                return d[c]
        return None

    def _plot_identification(self):
        canvas = self.view.tab_ident.canvas
        canvas.clear_and_style()
        ax = canvas.ax
        p = palette()
        par = self.params

        # Dados experimentais
        ax.plot(self.t, self.y, color=p["ACCENT"], linewidth=1.6, alpha=0.85,
                label="Experimental")

        # Modelo identificado
        y_sim = simulate_fopdt(
            self.t, self.u,
            par["k"], par["tau"], par["theta"],
            u0=par["u0"], y0=par["y0"]
        )
        ax.plot(self.t, y_sim, color=p["ACCENT3"], linewidth=2, linestyle="--",
                label=f"Smith  (k={par['k']:.3f}, τ={par['tau']:.2f}, θ={par['theta']:.2f})")

        # Marcar t1 (28.3%) e t2 (63.2%)
        delta_y = par["y_inf"] - par["y0"]
        y_283 = par["y0"] + 0.283 * delta_y
        y_632 = par["y0"] + 0.632 * delta_y
        ax.axhline(y_283, color=p["MUTED"], linestyle=":", alpha=0.4)
        ax.axhline(y_632, color=p["MUTED"], linestyle=":", alpha=0.4)
        ax.plot(par["t1"], y_283, "o", color=p["ACCENT2"], markersize=8,
                label=f"t₁ (28.3%) = {par['t1']:.2f} s")
        ax.plot(par["t2"], y_632, "s", color=p["ACCENT4"], markersize=8,
                label=f"t₂ (63.2%) = {par['t2']:.2f} s")

        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Saída")
        ax.set_title(f"Identificação por Smith   ·   EQM = {par['eqm']:.4f}",
                     color=p["TEXT"])
        ax.grid(True, color=p["BORDER"], alpha=0.3)

        leg = ax.legend(loc="lower right", fontsize=9, frameon=True)
        leg.get_frame().set_facecolor(p["CARD"])
        leg.get_frame().set_edgecolor(p["BORDER"])
        for text in leg.get_texts():
            text.set_color(p["TEXT"])

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    def _export_ident(self):
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Salvar gráfico", "identificacao_smith.png",
            "PNG (*.png);;PDF (*.pdf)"
        )
        if path:
            self.view.tab_ident.canvas.figure.savefig(
                path, dpi=150, bbox_inches="tight",
                facecolor=self.view.tab_ident.canvas.figure.get_facecolor()
            )
            self.view.set_status(f"✓ Gráfico exportado: {path}")


    def _update_pid_from_method(self):
        """Recalcula Kp/Ti/Td a partir do método selecionado (modo automático)."""
        if self.params is None:
            return
        if self.view.tab_pid.is_manual():
            return  # em modo manual, nada a fazer

        method = self.view.tab_pid.get_method()
        k, tau, theta = self.params["k"], self.params["tau"], self.params["theta"]

        if method == "IMC":
            lam = self.view.tab_pid.get_lambda()
            if lam is None or lam <= 0:
                lam = tau
                self.view.tab_pid.set_lambda(lam)
            tuned = tune_imc(k, tau, theta, lam=lam)
        else:
            tuned = tune_itae(k, tau, theta)

        self.view.tab_pid.set_pid_params(tuned["Kp"], tuned["Ti"], tuned["Td"])

    def simulate_pid(self):
        if self.params is None:
            self.view.show_warning("Carregue primeiro um dataset na aba de Identificação.")
            return

        Kp, Ti, Td = self.view.tab_pid.get_pid_params()
        SP = self.view.tab_pid.get_setpoint()
        t_total = self.view.tab_pid.get_tsim()
        k, tau, theta = self.params["k"], self.params["tau"], self.params["theta"]

        # Verificar estabilidade
        try:
            _, poles = closed_loop_tf(k, tau, theta, Kp, Ti, Td)
        except Exception as exc:
            self.view.show_error(f"Falha ao montar a malha fechada:\n{exc}")
            return

        if not is_stable(poles):
            unstable = poles[np.real(poles) >= 0]
            msg = (f"⚠  Malha fechada INSTÁVEL com Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f}.\n\n"
                   f"Polos com parte real ≥ 0: {len(unstable)}\n")
            for ppole in unstable[:5]:
                msg += f"   {ppole:.3f}\n"
            if self.view.tab_pid.is_manual():
                self.view.show_warning(msg + "\nA simulação NÃO será executada.")
                return
            else:
                self.view.show_warning(msg)

        # Simulação
        n = max(401, int(t_total * 20) + 1)
        t_sim = np.linspace(0, t_total, n)
        t, y, estavel, poles = simulate_closed_loop(k, tau, theta, Kp, Ti, Td, SP, t_sim)
        m = response_metrics(t, y, SP)

        self.view.tab_pid.set_metrics(m["tr"], m["ts"], m["Mp"], m["ess"])
        self._plot_closed_loop(t, y, SP, m, Kp, Ti, Td)

        self.last_sim = {
            "t": t, "y": y, "SP": SP,
            "Kp": Kp, "Ti": Ti, "Td": Td,
            "metrics": m,
            "method": ("Manual" if self.view.tab_pid.is_manual()
                       else self.view.tab_pid.get_method()),
        }

        self.view.tab_pid.btn_export.setEnabled(True)
        self.view.set_status(
            f"✓ Simulação PID  |  Kp={Kp:.3f}  Ti={Ti:.3f}  Td={Td:.3f}"
            f"  |  tr={m['tr']:.2f}s  ts={m['ts']:.2f}s  Mp={m['Mp']:.2f}%"
        )

    def _plot_closed_loop(self, t, y, SP, m, Kp, Ti, Td):
        canvas = self.view.tab_pid.canvas
        canvas.clear_and_style()
        ax = canvas.ax
        p = palette()

        method = ("Manual" if self.view.tab_pid.is_manual()
                  else self.view.tab_pid.get_method())

        # Setpoint
        ax.axhline(SP, color=p["ACCENT"], linestyle="--", linewidth=1.5,
                   label=f"SP = {SP}")
        # Banda ±2%
        ax.fill_between(t, SP * 0.98, SP * 1.02,
                        color=p["ACCENT"], alpha=0.08, label="±2 % SP")
        # Resposta
        ax.plot(t, y, color=p["ACCENT3"], linewidth=2,
                label=f"PV ({method})")

        # Marcadores
        if not np.isnan(m["tr"]) and m["y_final"] != 0:
            y90 = 0.9 * m["y_final"]
            try:
                i90 = int(np.where(y >= y90)[0][0])
                ax.plot(t[i90], y[i90], "o", color=p["ACCENT2"], markersize=8,
                        label=f"tr = {m['tr']:.2f} s")
            except Exception:
                pass

        if m["Mp"] > 0.5:
            ax.plot(m["t_peak"], m["y_peak"], "^", color=p["ACCENT3"],
                    markersize=10, label=f"Mp = {m['Mp']:.2f} %")

        ax.axvline(m["ts"], color=p["ACCENT4"], linestyle=":", alpha=0.7,
                   label=f"ts = {m['ts']:.2f} s")

        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("PV")
        ax.set_title(
            f"Malha Fechada  ·  {method}   "
            f"(Kp={Kp:.3f}, Ti={Ti:.3f}, Td={Td:.3f})",
            color=p["TEXT"]
        )
        ax.grid(True, color=p["BORDER"], alpha=0.3)

        leg = ax.legend(loc="lower right", fontsize=9, frameon=True)
        leg.get_frame().set_facecolor(p["CARD"])
        leg.get_frame().set_edgecolor(p["BORDER"])
        for text in leg.get_texts():
            text.set_color(p["TEXT"])

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    def _export_pid(self):
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Salvar gráfico", "resposta_pid.png",
            "PNG (*.png);;PDF (*.pdf)"
        )
        if path:
            self.view.tab_pid.canvas.figure.savefig(
                path, dpi=150, bbox_inches="tight",
                facecolor=self.view.tab_pid.canvas.figure.get_facecolor()
            )
            self.view.set_status(f"✓ Gráfico exportado: {path}")


    def compare_plots(self):
        if self.params is None:
            self.view.show_warning("Carregue primeiro um dataset na aba de Identificação.")
            return

        k, tau, theta = self.params["k"], self.params["tau"], self.params["theta"]
        SP = self.view.tab_pid.get_setpoint()
        t_total = self.view.tab_pid.get_tsim()
        t_sim = np.linspace(0, t_total, max(401, int(t_total * 20) + 1))

        # ── Malha aberta — usar amplitude do degrau original do experimento
        U_step = self.params["u1"] - self.params["u0"]
        t_ol, y_ol = simulate_open_loop(k, tau, theta, U_step, t_sim)
        # somar offset y0 para mostrar no mesmo nível do experimento
        y_ol_plot = y_ol + self.params["y0"]

        # ── Malha fechada — IMC e ITAE
        imc = tune_imc(k, tau, theta, lam=self._lambda_for_compare(tau))
        itae = tune_itae(k, tau, theta)

        t_imc, y_imc, est_imc, _ = simulate_closed_loop(
            k, tau, theta, imc["Kp"], imc["Ti"], imc["Td"], SP, t_sim
        )
        t_itae, y_itae, est_itae, _ = simulate_closed_loop(
            k, tau, theta, itae["Kp"], itae["Ti"], itae["Td"], SP, t_sim
        )

        m_imc = response_metrics(t_imc, y_imc, SP)
        m_itae = response_metrics(t_itae, y_itae, SP)

        self._plot_open_loop(t_ol, y_ol_plot, U_step)
        self._plot_compare_closed(t_imc, y_imc, t_itae, y_itae, SP,
                                  imc, itae, m_imc, m_itae)
        self.view.tab_graf.btn_export.setEnabled(True)

        self.view.set_status(
            f"✓ Comparação atualizada  |  IMC: tr={m_imc['tr']:.2f}s, ts={m_imc['ts']:.2f}s  "
            f"|  ITAE: tr={m_itae['tr']:.2f}s, ts={m_itae['ts']:.2f}s"
        )

    def _lambda_for_compare(self, tau):
        """λ usado na comparação — pega o atual da UI ou tau como default."""
        lam = self.view.tab_pid.get_lambda()
        return lam if (lam is not None and lam > 0) else tau

    def _plot_open_loop(self, t, y, U_step):
        canvas = self.view.tab_graf.canvas_ol
        canvas.clear_and_style()
        ax = canvas.ax
        p = palette()

        ax.plot(t, y, color=p["ACCENT"], linewidth=2,
                label=f"PV  (degrau Δu = {U_step:.1f})")
        # linha tracejada do valor final teórico
        y_inf_teo = self.params["y0"] + self.params["k"] * U_step
        ax.axhline(y_inf_teo, color=p["MUTED"], linestyle="--", alpha=0.6,
                   label=f"y∞ = {y_inf_teo:.2f}")

        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("PV")
        ax.set_title("Malha Aberta — Resposta natural", color=p["TEXT"])
        ax.grid(True, color=p["BORDER"], alpha=0.3)

        leg = ax.legend(loc="lower right", fontsize=9)
        leg.get_frame().set_facecolor(p["CARD"])
        leg.get_frame().set_edgecolor(p["BORDER"])
        for text in leg.get_texts():
            text.set_color(p["TEXT"])

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    def _plot_compare_closed(self, t_imc, y_imc, t_itae, y_itae, SP,
                             imc, itae, m_imc, m_itae):
        canvas = self.view.tab_graf.canvas_cl
        canvas.clear_and_style()
        ax = canvas.ax
        p = palette()

        ax.axhline(SP, color=p["MUTED"], linestyle="--", linewidth=1.3,
                   label=f"SP = {SP}")
        ax.fill_between(t_imc, SP * 0.98, SP * 1.02,
                        color=p["ACCENT"], alpha=0.06)

        ax.plot(t_imc, y_imc, color=p["ACCENT"], linewidth=2,
                label=f"IMC  (tr={m_imc['tr']:.1f}, ts={m_imc['ts']:.1f}, Mp={m_imc['Mp']:.1f}%)")
        ax.plot(t_itae, y_itae, color=p["ACCENT2"], linewidth=2,
                label=f"ITAE (tr={m_itae['tr']:.1f}, ts={m_itae['ts']:.1f}, Mp={m_itae['Mp']:.1f}%)")

        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("PV")
        ax.set_title("Malha Fechada — IMC × ITAE", color=p["TEXT"])
        ax.grid(True, color=p["BORDER"], alpha=0.3)

        leg = ax.legend(loc="lower right", fontsize=8)
        leg.get_frame().set_facecolor(p["CARD"])
        leg.get_frame().set_edgecolor(p["BORDER"])
        for text in leg.get_texts():
            text.set_color(p["TEXT"])

        canvas.figure.tight_layout(pad=2)
        canvas.draw()

    def _export_compare(self):
        path, _ = QFileDialog.getSaveFileName(
            self.view, "Salvar gráfico", "comparacao_malhas.png",
            "PNG (*.png);;PDF (*.pdf)"
        )
        if not path:
            return
        import matplotlib.pyplot as plt
        from matplotlib.figure import Figure
        base, ext = os.path.splitext(path)
        path_cl = path
        path_ol = f"{base}_open_loop{ext}"
        self.view.tab_graf.canvas_cl.figure.savefig(
            path_cl, dpi=150, bbox_inches="tight",
            facecolor=self.view.tab_graf.canvas_cl.figure.get_facecolor()
        )
        self.view.tab_graf.canvas_ol.figure.savefig(
            path_ol, dpi=150, bbox_inches="tight",
            facecolor=self.view.tab_graf.canvas_ol.figure.get_facecolor()
        )
        self.view.set_status(f"✓ Exportado: {path_cl} e {path_ol}")


    def refresh_plots(self):
        """Re-renderiza os plots com as cores do tema atual."""
        if self.params is not None:
            self._plot_identification()
        if self.last_sim is not None:
            s = self.last_sim
            self._plot_closed_loop(
                s["t"], s["y"], s["SP"], s["metrics"],
                s["Kp"], s["Ti"], s["Td"]
            )