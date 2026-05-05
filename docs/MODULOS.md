# Documentação dos módulos

Este documento descreve os arquivos principais do projeto, suas responsabilidades e a relação entre as camadas da arquitetura MVC.

## Visão geral

| Módulo | Responsabilidade |
|---|---|
| `main.py` | inicialização da aplicação Qt |
| `app/views/main_window.py` | construção da IHM, abas, estilos, temas, cartões e gráficos |
| `app/controllers/main_controller.py` | conexão entre eventos da IHM e rotinas matemáticas |
| `app/models/identification.py` | identificação FOPDT pelo método de Smith, simulação FOPDT e cálculo de EQM |
| `app/models/pid_tuning.py` | sintonia IMC, sintonia ITAE, aproximação de Padé, funções de transferência, simulações e métricas |
| `requirements.txt` | dependências Python do projeto |

## `main.py`

Arquivo de entrada da aplicação. Cria o objeto `QApplication`, configura suporte a DPI alto, instancia a janela principal e cria o controlador.

Fluxo principal:

```python
app = QApplication(sys.argv)
view = MainWindow()
controller = MainController(view)
view.show()
sys.exit(app.exec_())
```

## `app/models/identification.py`

Contém as rotinas de identificação do modelo FOPDT a partir da resposta ao degrau.

### `identify_smith(t, u, y) -> dict`

Identifica o modelo:

$$
G(s)=\frac{k e^{-\theta s}}{\tau s+1}
$$

Etapas executadas:

1. converte `t`, `u` e `y` para arrays NumPy;
2. detecta o instante do degrau pela primeira variação significativa em `u`;
3. calcula `u0`, `u1`, `Δu`, `y0`, `y_inf` e `Δy`;
4. calcula `k=Δy/Δu`;
5. calcula os níveis de 28,3% e 63,2%;
6. obtém `t1` e `t2` por interpolação linear;
7. calcula `t1_rel` e `t2_rel` em relação ao instante do degrau;
8. estima `τ` e `θ`;
9. aplica proteções numéricas para `τ>0` e `θ>=0`;
10. calcula o erro do modelo com `compute_eqm()`.

Campos de retorno:

```python
{
    "k": k,
    "tau": tau,
    "theta": theta,
    "t_step": t_step,
    "u0": u0,
    "u1": u1,
    "y0": y0,
    "y_inf": y_inf,
    "t1": t1,
    "t2": t2,
    "t1_rel": t1_rel,
    "t2_rel": t2_rel,
    "eqm": eqm,
}
```

### `simulate_fopdt(t, u, k, tau, theta, u0=0.0, y0=0.0)`

Simula o modelo FOPDT. Primeiro cria a parte sem atraso:

$$
G_0(s)=\frac{k}{\tau s+1}
$$

Depois desloca a resposta simulada em número inteiro de amostras:

$$
n_\theta=\operatorname{round}\left(\frac{\theta}{\Delta t}\right)
$$

A saída final é reconstruída por:

$$
y(t)=y_0+y_d(t)
$$

### `compute_eqm(t, u, y_real, k, tau, theta, u0=0.0, y0=0.0)`

Calcula o erro quadrático médio:

$$
EQM=\frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i-y_i)^2
$$

## `app/models/pid_tuning.py`

Contém as rotinas de sintonia PID, montagem de funções de transferência, simulação e cálculo de métricas.

### `tune_imc(k, tau, theta, lam=None)`

Calcula os parâmetros PID pelo método IMC:

$$
K_p=\frac{2\tau+\theta}{k(2\lambda+\theta)}
$$

$$
T_i=\tau+\frac{\theta}{2}
$$

$$
T_d=\frac{\tau\theta}{2\tau+\theta}
$$

Quando `lam` não é informado, a função usa `λ=τ`.

### `tune_itae(k, tau, theta)`

Calcula os parâmetros PID pelo método ITAE:

$$
r=\frac{\theta}{\tau}
$$

$$
K_p=\frac{0,965}{k}r^{-0,85}
$$

$$
T_i=\frac{\tau}{0,796-0,147r}
$$

$$
T_d=0,308\tau r^{0,929}
$$

### `pade_approx(theta, order=2)`

Retorna os polinômios da aproximação de Padé para o atraso.

Ordem 1:

$$
e^{-\theta s}\approx\frac{1-\frac{\theta}{2}s}{1+\frac{\theta}{2}s}
$$

Ordem 2:

$$
e^{-\theta s}\approx
\frac{\frac{\theta^2}{12}s^2-\frac{\theta}{2}s+1}
{\frac{\theta^2}{12}s^2+\frac{\theta}{2}s+1}
$$

### `closed_loop_tf(k, tau, theta, Kp, Ti, Td, pade_order=2)`

Monta a função de transferência de malha fechada:

$$
T(s)=\frac{C(s)G(s)}{1+C(s)G(s)}
$$

Para `Ti>0`, o controlador é:

$$
C(s)=K_p\left(1+\frac{1}{T_i s}+T_d s\right)
$$

Em forma racional:

$$
C(s)=\frac{K_pT_iT_ds^2+K_pT_is+K_p}{T_i s}
$$

A função retorna o sistema `TransferFunction` e os polos da malha fechada.

### `open_loop_tf(k, tau, theta, pade_order=2)`

Monta a função de transferência em malha aberta com atraso aproximado por Padé.

### `is_stable(poles, tol=1e-9)`

Verifica estabilidade pelo critério:

$$
\operatorname{Re}(p_i)<-tol,\quad \forall i
$$

### `simulate_closed_loop(k, tau, theta, Kp, Ti, Td, SP, t_sim, pade_order=2)`

Simula a resposta ao setpoint em malha fechada usando `scipy.signal.lsim`.

Retorno:

```python
t_out, y_out, estavel, poles
```

### `simulate_open_loop(...)`

Simula a resposta em malha aberta para uma entrada constante `U_step`.

### `response_metrics(t, y, SP)`

Calcula:

| Campo | Descrição |
|---|---|
| `tr` | tempo de subida, entre 10% e 90% do valor final |
| `ts` | último instante fora da banda de ±2% do valor final |
| `Mp` | sobressinal percentual |
| `ess` | erro em regime permanente |
| `y_final` | valor final estimado pela média das últimas amostras |
| `y_peak` | valor máximo da resposta |
| `t_peak` | instante do valor máximo |

## `app/controllers/main_controller.py`

Controla o fluxo da aplicação.

### Estado interno

| Atributo | Conteúdo |
|---|---|
| `t` | vetor de tempo |
| `u` | vetor de entrada |
| `y` | vetor de saída |
| `params` | parâmetros identificados pelo método de Smith |
| `last_sim` | última simulação em malha fechada |

### Sinais conectados

| Origem | Sinal | Destino |
|---|---|---|
| `tab_ident` | `sig_load_file` | `load_dataset()` |
| `tab_ident` | `sig_export` | `_export_ident()` |
| `tab_pid` | `sig_tune` | `simulate_pid()` |
| `tab_pid` | `sig_method_changed` | `_update_pid_from_method()` |
| `tab_pid` | `sig_lambda_changed` | `_update_pid_from_method()` |
| `tab_pid` | `sig_export` | `_export_pid()` |
| `tab_graf` | `sig_compare` | `compare_plots()` |
| `tab_graf` | `sig_export` | `_export_compare()` |

### `load_dataset()`

Abre o arquivo `.mat`, procura os vetores de tempo, entrada e saída, executa `identify_smith()` automaticamente e atualiza a IHM. A versão atual não usa um botão separado de identificação.

### `_plot_identification()`

Plota os dados experimentais, o modelo FOPDT identificado e os pontos de 28,3% e 63,2%.

### `_update_pid_from_method()`

Recalcula `Kp`, `Ti` e `Td` sempre que o método automático ou o parâmetro `λ` são alterados. No modo manual, não altera os valores inseridos pelo usuário.

### `simulate_pid()`

Monta a malha fechada, verifica estabilidade, simula a resposta ao setpoint e atualiza métricas e gráfico.

### `compare_plots()`

Gera dois gráficos:

1. malha aberta com a amplitude de degrau original do experimento;
2. malha fechada comparando IMC e ITAE para o mesmo setpoint e tempo de simulação.

### `_export_compare()`

Exporta dois arquivos: o gráfico de malha fechada e o gráfico de malha aberta com sufixo `_open_loop`.

### `refresh_plots()`

Redesenha os gráficos com as cores do tema atual quando a IHM muda entre tema escuro e tema claro.

## `app/views/main_window.py`

Define a IHM principal.

### Elementos principais

| Classe | Função |
|---|---|
| `MplCanvas` | encapsula `FigureCanvas` e aplica estilo aos gráficos |
| `ParamCard` | cartão usado para exibir valores numéricos |
| `TabIdentificacao` | aba de carregamento, identificação e parâmetros FOPDT |
| `TabControlePID` | aba de sintonia, setpoint, tempo de simulação e métricas |
| `TabGraficos` | aba de comparação entre malha aberta e malha fechada |
| `MainWindow` | janela principal com header, abas, status bar e alternância de tema |

### Aba Identificação

Exibe:

- carregamento de dataset `.mat`;
- parâmetros `k`, `τ`, `θ` e `EQM`;
- informações do experimento: `u0`, `uf`, `y∞` e `t_d`;
- gráfico da identificação por Smith.

### Aba Controle PID

Exibe:

- modo automático ou manual;
- seleção IMC/ITAE;
- `Kp`, `Ti`, `Td`;
- `λ`, habilitado somente quando aplicável;
- `SP`;
- `t_sim`;
- métricas `tr`, `ts`, `Mp` e `ess`.

### Aba Gráficos

Exibe:

- gráfico de malha aberta, com resposta natural da planta;
- gráfico de malha fechada, comparando IMC e ITAE.
