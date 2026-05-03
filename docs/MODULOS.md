# Documentação dos módulos

Este documento descreve os arquivos principais do projeto, suas responsabilidades e a relação entre os módulos da arquitetura MVC.

## Visão geral

| Módulo | Responsabilidade |
|---|---|
| `main.py` | inicialização da aplicação Qt |
| `app/views/main_window.py` | construção da IHM, abas, estilos e gráficos |
| `app/controllers/main_controller.py` | conexão entre eventos da IHM e funções do modelo |
| `app/models/system_model.py` | identificação, sintonia PID, simulação e métricas |
| `requirements.txt` | lista de dependências do projeto |

## `main.py`

### Finalidade

Arquivo de entrada da aplicação. Ele cria o objeto `QApplication`, configura suporte a DPI alto, instancia a janela principal e cria o controlador.

### Fluxo

```python
app = QApplication(sys.argv)
view = MainWindow()
controller = MainController(view)
view.show()
sys.exit(app.exec_())
```

### Responsabilidades

- iniciar a aplicação PyQt5;
- configurar nome da aplicação e organização como Grupo 7;
- criar a camada de visualização;
- conectar a visualização ao controlador;
- iniciar o loop de eventos Qt.

## `app/models/system_model.py`

### Finalidade

Contém a lógica matemática e numérica do projeto. Este módulo não depende da interface gráfica.

### Funções principais

#### `load_mat_file(filepath: str) -> dict`

Carrega um arquivo `.mat` e extrai variáveis numéricas.

Processamento aplicado:

1. remove metadados internos do MATLAB;
2. mantém apenas arrays numéricos;
3. detecta vetor de tempo crescente;
4. escolhe entrada e saída por heurística de variância;
5. retorna arrays com mesmo comprimento.

Retorno principal:

```python
{
    'time': time,
    'input': input_signal,
    'output': output,
    'time_key': time_key,
    'input_key': input_key,
    'output_key': output_key,
    'all_keys': keys,
}
```

#### `identify_smith(time, output, input_signal) -> dict`

Identifica um modelo FOPDT pelo método de Smith:

$$
G(s)=\frac{K e^{-\theta s}}{\tau s+1}
$$

Etapas executadas:

1. detecta o instante do degrau na entrada;
2. calcula valores médios antes do degrau e em regime permanente;
3. calcula o ganho `K`;
4. normaliza a resposta;
5. interpola os tempos de 28,3% e 63,2%;
6. estima `τ` e `θ`;
7. simula o modelo FOPDT;
8. calcula o indicador de erro exibido na IHM.

Retorno principal:

```python
{
    'K': K,
    'tau': tau,
    'theta': theta,
    'eqm': eqm,
    'y_model': y_model,
    'y_baseline': y_baseline,
    'u_baseline': u_baseline,
    'delta_u': delta_u,
    't_step': t_step,
    'method': 'Smith',
}
```

#### `_interp_time(time, y_norm, level)`

Função auxiliar para interpolação linear. Retorna o tempo em que a resposta normalizada cruza determinado nível.

$$
t=t_1+\frac{level-y_1}{y_2-y_1}(t_2-t_1)
$$

#### `_simulate_fopdt(K, tau, theta, time, input_signal, y0, u0)`

Simula a planta FOPDT usando integração de Euler com passo variável.

Modelo usado:

$$
\tau\frac{dy_d(t)}{dt}=K u_d(t-\theta)-y_d(t)
$$

#### `tune_imc(K, tau, theta, lam) -> dict`

Calcula os parâmetros PID pelo método IMC.

$$
K_p=\frac{2\tau+\theta}{K(2\lambda+\theta)}
$$

$$
T_i=\tau+\frac{\theta}{2}
$$

$$
T_d=\frac{\tau\theta}{2\tau+\theta}
$$

#### `tune_itae(K, tau, theta) -> dict`

Calcula os parâmetros PID pelo método ITAE.

$$
K_p=\frac{0,965}{K}\left(\frac{\theta}{\tau}\right)^{-0,85}
$$

$$
T_i=\frac{\tau}{0,796-0,147(\theta/\tau)}
$$

$$
T_d=0,308\tau\left(\frac{\theta}{\tau}\right)^{0,929}
$$

#### `simulate_closed_loop(...) -> dict`

Simula o sistema em malha fechada com controlador PID e planta FOPDT.

Recursos implementados:

- atraso por `deque`;
- integração por Euler;
- filtro derivativo de primeira ordem;
- saturação numérica de controle;
- anti-windup por clamping do integrador;
- cálculo automático de métricas.

#### `simulate_open_loop(...) -> np.ndarray`

Executa a simulação em malha aberta usando o modelo FOPDT identificado.

#### `_compute_metrics(t, y, setpoint) -> dict`

Calcula:

- `tr`: tempo de subida;
- `ts`: tempo de acomodação;
- `Mp`: sobressinal percentual;
- `ess`: erro em regime permanente.

## `app/controllers/main_controller.py`

### Finalidade

Responsável por conectar a IHM com o modelo. O Controller recebe sinais emitidos pela View, executa funções do Model e atualiza os campos e gráficos da interface.

### Atributos principais

| Atributo | Conteúdo |
|---|---|
| `_data` | dataset carregado |
| `_ident` | resultado da identificação FOPDT |
| `_pid_params` | parâmetros PID calculados ou inseridos manualmente |
| `_cl_result` | resultado da simulação em malha fechada |

### Métodos principais

#### `_connect_signals()`

Conecta botões e controles da interface aos métodos do Controller:

- carregar arquivo;
- identificar sistema;
- sintonizar PID;
- exportar gráficos;
- atualizar comparação.

#### `_on_load_file()`

Abre uma janela de seleção de arquivo `.mat`, chama `load_mat_file()` e atualiza a aba de identificação.

#### `_plot_raw_data()`

Plota os dados originais do dataset, com saída em um eixo e entrada em eixo secundário.

#### `_on_identify()`

Executa `identify_smith()`, atualiza os cartões de parâmetros FOPDT, habilita a aba de controle e sugere o setpoint como média final da saída.

#### `_plot_identification()`

Plota os dados reais e o modelo FOPDT identificado. Também marca o instante do degrau quando detectado.

#### `_on_tune()`

Executa a sintonia PID. O fluxo depende do modo selecionado:

- modo manual: lê `Kp`, `Ti` e `Td` da IHM;
- modo automático IMC: chama `tune_imc()`;
- modo automático ITAE: chama `tune_itae()`.

Em seguida, chama `simulate_closed_loop()` e atualiza as métricas.

#### `_plot_closed_loop()`

Plota a resposta em malha fechada, o setpoint e a faixa de ±2%.

#### `_on_compare()`

Atualiza a aba de comparação com dois gráficos:

1. malha aberta: dados reais e modelo FOPDT;
2. malha fechada: resposta controlada e setpoint.

#### `_export_canvas()`

Salva o gráfico atual em PNG, PDF ou SVG.

## `app/views/main_window.py`

### Finalidade

Define todos os elementos visuais da IHM em PyQt5.

### Componentes principais

#### Paletas e estilo

O módulo possui duas paletas:

- `DARK_PALETTE`;
- `LIGHT_PALETTE`.

A função `_build_stylesheet()` gera a folha de estilo Qt usada pela aplicação.

#### `MplCanvas`

Classe que encapsula um `FigureCanvas` do Matplotlib para uso dentro do PyQt5.

Métodos principais:

- `_style_ax()`;
- `apply_theme()`;
- `clear_and_style()`.

#### `ParamCard`

Widget visual usado para exibir parâmetros e métricas. É usado para `K`, `τ`, `θ`, `EQM`, `tr`, `ts`, `Mp` e `ess`.

#### `TabIdentificacao`

Aba responsável por:

- seleção de arquivo `.mat`;
- exibição dos parâmetros FOPDT;
- botão de identificação;
- botão de exportação;
- gráfico de dados e modelo.

Sinais emitidos:

```python
sig_load_file
sig_identify
sig_export
```

#### `TabControlePID`

Aba responsável por:

- seleção de modo automático ou manual;
- seleção do método IMC ou ITAE;
- campos de `Kp`, `Ti`, `Td` e `λ`;
- campo de setpoint;
- cartões de métricas;
- gráfico da resposta em malha fechada.

Sinais emitidos:

```python
sig_tune
sig_export
```

#### `TabGraficos`

Aba responsável pela comparação lado a lado entre malha aberta e malha fechada.

Sinal emitido:

```python
sig_compare
```

#### `MainWindow`

Janela principal da aplicação. Cria o cabeçalho, o botão de tema, as três abas e a barra de status.

## `requirements.txt`

Lista as dependências mínimas:

```text
PyQt5>=5.15.0
numpy>=1.21.0
scipy>=1.7.0
matplotlib>=3.4.0
```
