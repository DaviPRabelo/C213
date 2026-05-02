"""
Modelo: Identificação FOPDT por Smith e Sintonia PID (IMC + ITAE)
C213 - Sistemas de Controle Automático — Grupo 7

Função de transferência:
    G(s) = K * exp(-θ·s) / (τ·s + 1)
"""

from collections import deque
import numpy as np
from scipy.io import loadmat


# ════════════════════════════════════════════════════════════════════════════
# 1. Carregamento de Dataset
# ════════════════════════════════════════════════════════════════════════════

def load_mat_file(filepath: str) -> dict:
    raw = loadmat(filepath)
    
    # --- AJUSTE PRINCIPAL: Filtrar apenas o que é numérico e converter corretamente ---
    data = {}
    for k, v in raw.items():
        if k.startswith('_'):
            continue
        
        # Converte para array numpy
        arr = np.array(v)
        
        # Verifica se o array é numérico. Se for 'object' ou 'struct', ignoramos para cálculos
        if np.issubdtype(arr.dtype, np.number) and arr.size > 0:
            data[k] = arr.flatten().astype(float)
    # --------------------------------------------------------------------------------

    if len(data) < 1:
        raise ValueError("O arquivo .mat não contém variáveis numéricas válidas.")

    keys = list(data.keys())

    # Detecta vetor de tempo
    time_key = None
    for k, v in data.items():
        # Heurística: pelo menos 2 elementos, crescente, positivo
        if len(v) > 1 and np.all(np.diff(v) > 0) and v[0] >= 0:
            time_key = k
            break

    if time_key is None:
        n = max(len(v) for v in data.values())
        time = np.arange(n, dtype=float)
        time_key = '_generated_time'
    else:
        time = data[time_key]

    remaining = [k for k in keys if k != time_key]

    if not remaining: # Caso só exista o tempo no arquivo
        output_key = time_key
        output = time
        input_key = '_generated_input'
        input_signal = np.ones_like(time)
    elif len(remaining) == 1:
        output_key = remaining[0]
        input_key = '_generated_input'
        input_signal = np.ones_like(data[output_key])
        output = data[output_key]
    else:
        # Variância para distinguir entrada de saída
        variances = {k: float(np.var(data[k])) for k in remaining}
        sorted_keys = sorted(variances, key=variances.get)
        input_key = sorted_keys[0]
        output_key = sorted_keys[-1]
        input_signal = data[input_key]
        output = data[output_key]

    n = min(len(time), len(input_signal), len(output))
    
    return {
        'time':       time[:n],
        'input':      input_signal[:n],
        'output':     output[:n],
        'time_key':   time_key,
        'input_key':  input_key,
        'output_key': output_key,
        'all_keys':   keys,
    }
# ════════════════════════════════════════════════════════════════════════════
# 2. Identificação FOPDT — Método de Smith
# ════════════════════════════════════════════════════════════════════════════

def identify_smith(time: np.ndarray, output: np.ndarray,
                   input_signal: np.ndarray) -> dict:
    """
    Método de Smith para identificação FOPDT:
        G(s) = K · e^(-θs) / (τs + 1)

    Passos:
      1. Detecta o instante do degrau (t_step) na entrada.
      2. Calcula baseline (média antes do degrau) e regime (média no final).
      3. K = ΔY / ΔU
      4. Normaliza saída em [0, 1] e interpola t1 (28,3%) e t2 (63,2%).
      5. τ = 1,5·(t2 - t1)   ;   θ = (t2 - τ) - t_step
      6. EQM entre dados reais e modelo identificado.
    """
    time = np.asarray(time, dtype=float)
    output = np.asarray(output, dtype=float)
    input_signal = np.asarray(input_signal, dtype=float)

    # ── Detecta instante do degrau ────────────────────────────────────────
    du = np.diff(input_signal)
    if np.any(np.abs(du) > 1e-9):
        step_idx = int(np.argmax(np.abs(du))) + 1
    else:
        step_idx = 0
    t_step = float(time[step_idx]) if step_idx < len(time) else float(time[0])

    # ── Baseline e regime permanente (média robusta) ──────────────────────
    n_steady = max(3, len(output) // 20)

    if step_idx > 0:
        u_baseline = float(np.mean(input_signal[:step_idx]))
        y_baseline = float(np.mean(output[:step_idx]))
    else:
        u_baseline = float(input_signal[0])
        y_baseline = float(output[0])

    u_steady = float(np.mean(input_signal[-n_steady:]))
    y_steady = float(np.mean(output[-n_steady:]))

    delta_u = u_steady - u_baseline
    delta_y = y_steady - y_baseline

    if abs(delta_u) < 1e-9:
        delta_u = 1.0

    K = delta_y / delta_u

    if abs(delta_y) < 1e-9:
        raise ValueError("A saída não respondeu ao degrau (Δy ≈ 0).")

    # ── Normaliza e interpola ─────────────────────────────────────────────
    y_norm_full = (output - y_baseline) / delta_y

    t_after = time[step_idx:]
    y_after = y_norm_full[step_idx:]

    t1 = _interp_time(t_after, y_after, 0.283)
    t2 = _interp_time(t_after, y_after, 0.632)

    if t1 is None or t2 is None or t2 <= t1:
        tau = (t2 - t_step) if t2 else (time[-1] - t_step) / 3
        theta = 0.0
    else:
        tau = 1.5 * (t2 - t1)
        theta = (t2 - tau) - t_step

    tau = max(1e-6, float(tau))
    theta = max(0.0, float(theta))

    # ── EQM ────────────────────────────────────────────────────────────────
    y_model = _simulate_fopdt(K, tau, theta, time, input_signal,
                              y0=y_baseline, u0=u_baseline)
    eqm = float(np.sqrt(np.mean((output - y_model) ** 2)))

    return {
        'K': float(K),
        'tau': tau,
        'theta': theta,
        'eqm': eqm,
        'y_model': y_model,
        'y_baseline': y_baseline,
        'u_baseline': u_baseline,
        'delta_u': float(delta_u),
        't_step': t_step,
        'method': 'Smith',
    }


def _interp_time(time: np.ndarray, y_norm: np.ndarray, level: float):
    """Interpolação linear: encontra t tal que y_norm(t) = level."""
    idx = np.where(y_norm >= level)[0]
    if len(idx) == 0:
        return None
    i = int(idx[0])
    if i == 0:
        return float(time[0])
    y1, y2 = y_norm[i - 1], y_norm[i]
    t1, t2 = time[i - 1], time[i]
    if y2 == y1:
        return float(t2)
    return float(t1 + (level - y1) * (t2 - t1) / (y2 - y1))


def _simulate_fopdt(K: float, tau: float, theta: float,
                    time: np.ndarray, input_signal: np.ndarray,
                    y0: float = 0.0, u0: float = 0.0) -> np.ndarray:
    """
    Simula resposta FOPDT a sinal arbitrário usando Euler com passo variável.

    Modelo (em variáveis de desvio):
        τ · dy_d/dt = K · u_d(t-θ) - y_d
        y(t) = y0 + y_d(t)        ;       u_d = u(t) - u0
    """
    time = np.asarray(time, dtype=float)
    n = len(time)
    y = np.zeros(n)
    y[0] = y0

    if n < 2:
        return y

    u_dev = input_signal - u0

    for i in range(1, n):
        dt = time[i] - time[i - 1]
        t_delayed = time[i] - theta

        if t_delayed <= time[0]:
            u_d = u_dev[0]
        else:
            u_d = float(np.interp(t_delayed, time, u_dev))

        y_d_prev = y[i - 1] - y0
        y_d = y_d_prev + dt / tau * (K * u_d - y_d_prev)
        y[i] = y0 + y_d

    return y


# ════════════════════════════════════════════════════════════════════════════
# 3. Sintonia PID — IMC (Internal Model Control)
# ════════════════════════════════════════════════════════════════════════════

def tune_imc(K: float, tau: float, theta: float, lam: float) -> dict:
    """
    Sintonia IMC para FOPDT (Rivera, Morari, Skogestad, 1986):

        Kp = τ / (K · (λ + θ))
        Ti = τ
        Td = θ / 2

    O parâmetro λ controla o trade-off entre velocidade e robustez:
      - λ ≈ θ/2  → resposta rápida, menor robustez
      - λ ≈ θ    → equilíbrio
      - λ ≈ 2θ+  → resposta lenta, alta robustez
    """
    if lam <= 0:
        raise ValueError("λ deve ser maior que zero.")
    if K == 0:
        raise ValueError("K não pode ser zero.")

    Kp = ((2*tau)+theta) / (K * ((2*lam) + theta))
    Ti = tau + (theta / 2.0)
    Td = (tau *theta) / (2.0*tau + theta)

    return {'Kp': Kp, 'Ti': Ti, 'Td': Td, 'method': 'IMC', 'lambda': lam}


# ════════════════════════════════════════════════════════════════════════════
# 4. Sintonia PID — ITAE (Integral of Time-weighted Absolute Error)
# ════════════════════════════════════════════════════════════════════════════

def tune_itae(K: float, tau: float, theta: float) -> dict:
    """
    Sintonia ITAE para FOPDT — critério de rastreamento de referência
    (Seborg, Edgar, Mellichamp, 2016):

        Kp = (0,965/K) · (θ/τ)^(-0,855)
        Ti = τ / (0,796 - 0,1465·(θ/τ))
        Td = 0,308 · τ · (θ/τ)^(0,929)

    Faixa de validade recomendada: 0,1 ≤ θ/τ ≤ 1,0
    """
    
    if K == 0:
        raise ValueError("K não pode ser zero.")
    if tau <= 0:
        raise ValueError("τ deve ser positivo.")

    ratio = (theta / tau)

    Kp = (0.965 / K) * (ratio ** -0.85)   # B = -0.85 (documento disciplina)
    Ti = tau / (0.796 - 0.147 * ratio)    # D = -0.147 (documento disciplina)
    Td = 0.308 * tau * (ratio ** 0.929)   # E=0.308, F=0.929

    return {'Kp': Kp, 'Ti': Ti, 'Td': Td, 'method': 'ITAE'}


# ════════════════════════════════════════════════════════════════════════════
# 5. Simulação de Malha Fechada
# ══════════════════════════════════

def simulate_closed_loop(K: float, tau: float, theta: float,
                          Kp: float, Ti: float, Td: float,
                          setpoint: float = 1.0,
                          t_end: float = None,
                          n_points: int = 2000) -> dict:
    """
    Simula resposta ao degrau em malha fechada via integração de Euler.

        SP ──►(+)──► PID ──► u ──► [atraso θ] ──► Planta FOPDT ──► y
              (-)                                                     │
               └─────────────────────────────────────────────────────┘

    - Passo dt ≤ τ/50 garante estabilidade numérica
    - Atraso θ implementado por buffer circular (deque)
    - Filtro derivativo de 1ª ordem (N=10) contra amplificação de ruído
    - Anti-windup por clamping no integrador
    """
    if tau <= 0:
        raise ValueError("τ deve ser positivo.")
    if Ti <= 0:
        raise ValueError("Ti deve ser positivo.")

    if t_end is None:
        t_end = max(15 * tau, 15 * theta, 100.0)

    dt_max = tau / 50.0
    n_steps = max(n_points, int(np.ceil(t_end / dt_max)))
    dt = t_end / n_steps

    delay_steps = max(0, int(np.ceil(theta / dt)))
    u_delay_buf = deque([0.0] * (delay_steps + 1), maxlen=delay_steps + 1)

    N = 10.0
    U_MAX = 1e5
    U_MIN = -1e5

    y_val    = 0.0
    integral = 0.0
    deriv_f  = 0.0
    prev_err = setpoint - y_val

    t_arr = np.zeros(n_steps)
    y_arr = np.zeros(n_steps)
    u_arr = np.zeros(n_steps)

    for i in range(n_steps):
        t_arr[i] = i * dt
        err = setpoint - y_val

        integral_new = integral + err * dt

        if Td > 1e-12:
            deriv_f = (N * (err - prev_err) + deriv_f * (Td * N - dt)) / (Td * N + dt)
        else:
            deriv_f = 0.0

        u_pid = Kp * (err + integral_new / Ti + Td * deriv_f)

        u_sat = float(np.clip(u_pid, U_MIN, U_MAX))
        if u_pid == u_sat:
            integral = integral_new

        u_delay_buf.appendleft(u_sat)
        u_delayed = u_delay_buf[-1]

        y_val = y_val + dt / tau * (K * u_delayed - y_val)

        y_arr[i] = y_val
        u_arr[i] = u_sat
        prev_err = err

    metrics = _compute_metrics(t_arr, y_arr, setpoint)
    return {
        'time': t_arr,
        'output': y_arr,
        'input': u_arr,
        'metrics': metrics,
    }


def simulate_open_loop(K: float, tau: float, theta: float,
                       input_signal: np.ndarray, time: np.ndarray,
                       y0: float = 0.0, u0: float = 0.0) -> np.ndarray:
    """Simula resposta em malha aberta do modelo FOPDT identificado."""
    return _simulate_fopdt(K, tau, theta, time, input_signal, y0=y0, u0=u0)


# ════════════════════════════════════════════════════════════════════════════
# 6. Métricas de Desempenho
# ════════════════════════════════════════════════════════════════════════════

def _compute_metrics(t: np.ndarray, y: np.ndarray, setpoint: float) -> dict:
    """
    Métricas da resposta ao degrau:
      - tr  : tempo de subida (10% → 90% do SP)
      - ts  : tempo de acomodação (entrada definitiva na faixa ±2%)
      - Mp  : overshoot percentual
      - ess : erro em regime permanente (média dos últimos 5%)
    """
    metrics = {'tr': None, 'ts': None, 'Mp': None, 'ess': None}

    if setpoint == 0 or len(y) < 2:
        return metrics

    # Tempo de subida
    y_norm = y / setpoint
    idx_10 = np.where(y_norm >= 0.1)[0]
    idx_90 = np.where(y_norm >= 0.9)[0]
    if len(idx_10) > 0 and len(idx_90) > 0:
        metrics['tr'] = float(t[idx_90[0]] - t[idx_10[0]])

    # Overshoot
    y_max = float(np.max(y))
    if setpoint > 0 and y_max > setpoint:
        metrics['Mp'] = float((y_max - setpoint) / setpoint * 100)
    else:
        metrics['Mp'] = 0.0

    # Tempo de acomodação ±2%
    band = 0.02 * abs(setpoint)
    out_of_band = np.where(np.abs(y - setpoint) > band)[0]
    if len(out_of_band) == 0:
        metrics['ts'] = float(t[0])
    elif out_of_band[-1] >= len(t) - 1:
        metrics['ts'] = None
    else:
        metrics['ts'] = float(t[out_of_band[-1] + 1])

    # Erro em regime permanente
    n_tail = max(3, len(y) // 20)
    y_ss = float(np.mean(y[-n_tail:]))
    metrics['ess'] = float(abs(setpoint - y_ss))

    return metrics