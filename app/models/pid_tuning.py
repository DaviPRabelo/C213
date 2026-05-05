import numpy as np
from scipy.signal import TransferFunction, lsim


# ── Sintonia ──────────────────────────────────────────────────────────────────
def tune_imc(k, tau, theta, lam=None):
    if lam is None:
        lam = tau
        
    # IMC para FOPDT
    Kp = (2 * tau + theta) / (k * (2 * lam + theta)) # Kp = (2*tau + theta) / (k*(2*lambda + theta))
    Ti = tau + theta / 2.0 # Ti = tau + theta/2
    Td = (tau * theta) / (2 * tau + theta) # Td = tau*theta / (2*tau + theta)
    return {"Kp": Kp, "Ti": Ti, "Td": Td, "lambda": lam}


def tune_itae(k, tau, theta):
    A, B, C, D, E, F = 0.965, -0.85, 0.796, -0.147, 0.308, 0.929
    
    # Razão adimensional do atraso
    r = theta / tau # r = theta / tau
    
    # ITAE para FOPDT
    Kp = (A / k) * (r ** B) # Kp = (A/k) * r^B
    Ti = tau / (C + D * r) # Ti = tau / (C + D*r)
    Td = tau * E * (r ** F) # Td = tau * E * r^F
    return {"Kp": Kp, "Ti": Ti, "Td": Td}


# ── Aproximação de Padé ───────────────────────────────────────────────────────
def pade_approx(theta, order=2):
    if theta <= 0:
        return [1.0], [1.0]
    
    if order == 1:
        return [-theta / 2.0, 1.0], [theta / 2.0, 1.0] # e^(-theta*s) ≈ (1 - theta*s/2) / (1 + theta*s/2)
    
    # e^(-theta*s) ≈ [(theta²/12)s² - (theta/2)s + 1] / [(theta²/12)s² + (theta/2)s + 1]
    return (
        [theta**2 / 12.0, -theta / 2.0, 1.0],
        [theta**2 / 12.0,  theta / 2.0, 1.0],
    )


# ── Malha fechada e estabilidade ──────────────────────────────────────────────
def closed_loop_tf(k, tau, theta, Kp, Ti, Td, pade_order=2):
    # Planta com atraso aproximado
    # G(s) = k*Padé(theta) / (tau*s + 1)
    num_pade, den_pade = pade_approx(theta, pade_order)
    num_plant = np.array(num_pade) * k
    den_plant = np.polymul([tau, 1.0], den_pade)

    if Ti <= 0:
        # C(s) = Kp*(Td*s + 1)
        num_pid = [Kp * Td, Kp]
        den_pid = [1.0]
    else:
        # C(s) = (Kp*Ti*Td*s² + Kp*Ti*s + Kp) / (Ti*s)
        num_pid = [Kp * Ti * Td, Kp * Ti, Kp]
        den_pid = [Ti, 0.0]

    # Malha aberta
    # L(s) = C(s)*G(s)
    num_ol = np.polymul(num_pid, num_plant)
    den_ol = np.polymul(den_pid, den_plant)
    
    # Malha fechada com realimentação unitária
    # T(s) = L(s)/(1 + L(s))
    den_cl = np.polyadd(den_ol, num_ol)
    num_cl = num_ol

    sys_cl = TransferFunction(num_cl, den_cl)
    poles = np.roots(den_cl)
    return sys_cl, poles


def open_loop_tf(k, tau, theta, pade_order=2):
    # G(s) = k*Padé(theta)/(tau*s + 1)
    num_pade, den_pade = pade_approx(theta, pade_order)
    num_plant = np.array(num_pade) * k
    den_plant = np.polymul([tau, 1.0], den_pade)
    return TransferFunction(num_plant, den_plant)


def is_stable(poles, tol=1e-9):
    if len(poles) == 0:
        return False
    
    # Critério de estabilidade contínua
    return bool(np.all(np.real(poles) < -tol)) # Re(p_i) < -tol para todos os polos


def simulate_closed_loop(k, tau, theta, Kp, Ti, Td, SP, t_sim, pade_order=2):
    sys_cl, poles = closed_loop_tf(k, tau, theta, Kp, Ti, Td, pade_order)
    estavel = is_stable(poles)
    
    # Entrada de referência constante
    u_sp = np.ones_like(t_sim) * SP # r(t) = SP
    t_out, y_out, _ = lsim(sys_cl, U=u_sp, T=t_sim)
    return t_out, y_out, estavel, poles


def simulate_open_loop(k, tau, theta, U_step, t_sim, pade_order=2):
    sys_ol = open_loop_tf(k, tau, theta, pade_order)
    
    # Degrau de entrada em malha aberta:
    u = np.ones_like(t_sim) * U_step # u(t) = U_step
    t_out, y_out, _ = lsim(sys_ol, U=u, T=t_sim)
    return t_out, y_out


# ── Métricas ──────────────────────────────────────────────────────────────────
def response_metrics(t, y, SP):
    t = np.asarray(t)
    y = np.asarray(y)
    
    # Valor final pela média dos últimos 5% das amostras
    n_tail = max(5, len(y) // 20)
    y_final = float(np.mean(y[-n_tail:]))

    if y_final == 0:
        tr = float("nan")
    else:
        # Tempo de subida
        y10 = 0.10 * y_final
        y90 = 0.90 * y_final
        try:
            i10 = int(np.where(y >= y10)[0][0])
            i90 = int(np.where(y >= y90)[0][0])
            tr = float(t[i90] - t[i10]) # tr = t90 - t10
        except IndexError:
            tr = float("nan")

    # Sobressinal
    y_peak = float(np.max(y))
    Mp = max(0.0, (y_peak - y_final) / abs(y_final) * 100.0) if y_final != 0 else 0.0 # Mp = max(0, (y_peak - y_final)/|y_final| * 100)

    # Tempo de acomodação em banda de ±2%
    threshold = 0.02 * abs(y_final) if y_final != 0 else 0.02
    out_band = np.where(np.abs(y - y_final) > threshold)[0]
    ts = float(t[out_band[-1]]) if len(out_band) > 0 else float(t[0])

    # Erro em regime permanente
    ess = float(SP - y_final) # ess = SP - y_final
    t_peak = float(t[int(np.argmax(y))])

    return {
        "tr": tr, "ts": ts, "Mp": Mp, "ess": ess,
        "y_final": y_final, "y_peak": y_peak, "t_peak": t_peak,
    }