import numpy as np
from scipy.signal import lti, lsim


def identify_smith(t, u, y):

    t = np.asarray(t).squeeze()
    u = np.asarray(u).squeeze()
    y = np.asarray(y).squeeze()

    # Detectar instante do degrau
    du = np.diff(u)
    idx_step_candidates = np.where(np.abs(du) > 1e-9)[0]
    if len(idx_step_candidates) == 0:
        raise ValueError("Não foi detectado um degrau na entrada.")
    idx_step = int(idx_step_candidates[0]) + 1
    t_step = float(t[idx_step])

    # Valores de regime
    u0 = float(u[0])
    u1 = float(u[-1])
    delta_u = u1 - u0
    if abs(delta_u) < 1e-9:
        raise ValueError("Variação de entrada Δu é nula.")

    y0 = float(np.mean(y[:idx_step])) if idx_step > 0 else float(y[0])
    n_tail = max(5, len(y) // 10)
    y_inf = float(np.mean(y[-n_tail:]))
    delta_y = y_inf - y0

    k = delta_y / delta_u

    # Tempos t1 (28.3%) e t2 (63.2%)
    y_283 = y0 + 0.283 * delta_y
    y_632 = y0 + 0.632 * delta_y

    t_search = t[idx_step:]
    y_search = y[idx_step:]

    if delta_y < 0:
        t1 = float(np.interp(-y_283, -y_search, t_search))
        t2 = float(np.interp(-y_632, -y_search, t_search))
    else:
        t1 = float(np.interp(y_283, y_search, t_search))
        t2 = float(np.interp(y_632, y_search, t_search))

    t1_rel = t1 - t_step
    t2_rel = t2 - t_step

    tau = 1.5 * (t2_rel - t1_rel)
    theta = t2_rel - tau

    if tau <= 0:
        tau = 1e-3
    if theta < 0:
        theta = 0.0

    eqm = compute_eqm(t, u, y, k, tau, theta, u0=u0, y0=y0)

    return {
        "k": k, "tau": tau, "theta": theta,
        "t_step": t_step, "u0": u0, "u1": u1,
        "y0": y0, "y_inf": y_inf,
        "t1": t1, "t2": t2,
        "t1_rel": t1_rel, "t2_rel": t2_rel,
        "eqm": eqm,
    }


def simulate_fopdt(t, u, k, tau, theta, u0=0.0, y0=0.0):

    t = np.asarray(t).squeeze()
    u = np.asarray(u).squeeze()
    if tau <= 0:
        tau = 1e-6

    sys = lti([k], [tau, 1])
    u_shifted = u - u0
    _, y_no_delay, _ = lsim(sys, U=u_shifted, T=t)

    if len(t) > 1:
        dt = t[1] - t[0]
        n_delay = int(round(theta / dt)) if dt > 0 else 0
    else:
        n_delay = 0

    if n_delay > 0:
        y_sim = np.concatenate(
            [np.zeros(n_delay),
             y_no_delay[:-n_delay] if n_delay <= len(y_no_delay) else y_no_delay]
        )
        if len(y_sim) > len(y_no_delay):
            y_sim = y_sim[: len(y_no_delay)]
    else:
        y_sim = y_no_delay

    return y_sim + y0


def compute_eqm(t, u, y_real, k, tau, theta, u0=0.0, y0=0.0):
    """RMSE entre modelo FOPDT identificado e dados experimentais."""
    y_sim = simulate_fopdt(t, u, k, tau, theta, u0=u0, y0=y0)
    n = len(y_real)
    return float(np.sqrt(np.sum((y_sim - y_real) ** 2) / n))