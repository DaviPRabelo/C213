import numpy as np
from scipy.signal import TransferFunction, lsim


# ── Sintonia ──────────────────────────────────────────────────────────────────
def tune_imc(k, tau, theta, lam=None):
    if lam is None:
        lam = tau
    Kp = (2 * tau + theta) / (k * (2 * lam + theta))
    Ti = tau + theta / 2.0
    Td = (tau * theta) / (2 * tau + theta)
    return {"Kp": Kp, "Ti": Ti, "Td": Td, "lambda": lam}


def tune_itae(k, tau, theta):
    A, B, C, D, E, F = 0.965, -0.85, 0.796, -0.147, 0.308, 0.929
    r = theta / tau
    Kp = (A / k) * (r ** B)
    Ti = tau / (C + D * r)
    Td = tau * E * (r ** F)
    return {"Kp": Kp, "Ti": Ti, "Td": Td}


# ── Aproximação de Padé ───────────────────────────────────────────────────────
def pade_approx(theta, order=2):
    if theta <= 0:
        return [1.0], [1.0]
    if order == 1:
        return [-theta / 2.0, 1.0], [theta / 2.0, 1.0]
    return (
        [theta**2 / 12.0, -theta / 2.0, 1.0],
        [theta**2 / 12.0,  theta / 2.0, 1.0],
    )


# ── Malha fechada e estabilidade ──────────────────────────────────────────────
def closed_loop_tf(k, tau, theta, Kp, Ti, Td, pade_order=2):
    num_pade, den_pade = pade_approx(theta, pade_order)
    num_plant = np.array(num_pade) * k
    den_plant = np.polymul([tau, 1.0], den_pade)

    if Ti <= 0:
        num_pid = [Kp * Td, Kp]
        den_pid = [1.0]
    else:
        num_pid = [Kp * Ti * Td, Kp * Ti, Kp]
        den_pid = [Ti, 0.0]

    num_ol = np.polymul(num_pid, num_plant)
    den_ol = np.polymul(den_pid, den_plant)
    den_cl = np.polyadd(den_ol, num_ol)
    num_cl = num_ol

    sys_cl = TransferFunction(num_cl, den_cl)
    poles = np.roots(den_cl)
    return sys_cl, poles


def open_loop_tf(k, tau, theta, pade_order=2):
    num_pade, den_pade = pade_approx(theta, pade_order)
    num_plant = np.array(num_pade) * k
    den_plant = np.polymul([tau, 1.0], den_pade)
    return TransferFunction(num_plant, den_plant)


def is_stable(poles, tol=1e-9):
    if len(poles) == 0:
        return False
    return bool(np.all(np.real(poles) < -tol))


def simulate_closed_loop(k, tau, theta, Kp, Ti, Td, SP, t_sim, pade_order=2):
    sys_cl, poles = closed_loop_tf(k, tau, theta, Kp, Ti, Td, pade_order)
    estavel = is_stable(poles)
    u_sp = np.ones_like(t_sim) * SP
    t_out, y_out, _ = lsim(sys_cl, U=u_sp, T=t_sim)
    return t_out, y_out, estavel, poles


def simulate_open_loop(k, tau, theta, U_step, t_sim, pade_order=2):
    sys_ol = open_loop_tf(k, tau, theta, pade_order)
    u = np.ones_like(t_sim) * U_step
    t_out, y_out, _ = lsim(sys_ol, U=u, T=t_sim)
    return t_out, y_out


# ── Métricas ──────────────────────────────────────────────────────────────────
def response_metrics(t, y, SP):
    t = np.asarray(t)
    y = np.asarray(y)
    n_tail = max(5, len(y) // 20)
    y_final = float(np.mean(y[-n_tail:]))

    if y_final == 0:
        tr = float("nan")
    else:
        y10 = 0.10 * y_final
        y90 = 0.90 * y_final
        try:
            i10 = int(np.where(y >= y10)[0][0])
            i90 = int(np.where(y >= y90)[0][0])
            tr = float(t[i90] - t[i10])
        except IndexError:
            tr = float("nan")

    y_peak = float(np.max(y))
    Mp = max(0.0, (y_peak - y_final) / abs(y_final) * 100.0) if y_final != 0 else 0.0

    threshold = 0.02 * abs(y_final) if y_final != 0 else 0.02
    out_band = np.where(np.abs(y - y_final) > threshold)[0]
    ts = float(t[out_band[-1]]) if len(out_band) > 0 else float(t[0])

    ess = float(SP - y_final)
    t_peak = float(t[int(np.argmax(y))])

    return {
        "tr": tr, "ts": ts, "Mp": Mp, "ess": ess,
        "y_final": y_final, "y_peak": y_peak, "t_peak": t_peak,
    }