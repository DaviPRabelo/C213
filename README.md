# C213 - PID

Aplicação desktop para identificação de sistemas e projeto de controladores PID, desenvolvida para a disciplina **C213** pelo **Grupo 7**.

---

## Visão Geral

A aplicação implementa o fluxo completo de trabalho em controle automático: desde o carregamento de dados experimentais até a sintonia e simulação de um controlador PID, com visualização interativa dos resultados.

O modelo utilizado é o **FOPDT (First Order Plus Dead Time)**:

```
G(s) = K · exp(-θ·s) / (τ·s + 1)
```

---

## Funcionalidades

### Aba 1 — Identificação
- Carregamento de datasets no formato MATLAB (`.mat`)
- Detecção automática de sinais de entrada e saída via variância
- Identificação pelo **Método de Smith** com estimativa dos parâmetros K, τ e θ
- Cálculo do erro quadrático médio (EQM)
- Visualização: dados reais vs. modelo identificado
- Exportação de gráficos (PNG, PDF, SVG)

### Aba 2 — Controle PID
- **Sintonia automática:**
  - **IMC** (Internal Model Control) — parâmetro λ ajustável
  - **ITAE** (Integral of Time-weighted Absolute Error)
- **Sintonia manual:** entrada direta de Kp, Ti e Td
- Simulação em malha fechada com:
  - Anti-windup (clamping do integrador)
  - Filtro derivativo de 1ª ordem (N = 10)
  - Buffer circular para simulação do tempo morto
- Métricas de desempenho: tempo de subida (tr), tempo de acomodação (ts), sobressinal (Mp%) e erro em regime permanente (ess)
- Exportação de gráficos

### Aba 3 — Comparação
- Gráfico de malha aberta: dados reais vs. modelo FOPDT
- Gráfico de malha fechada: resposta PID vs. referência (setpoint)
- Exibição do EQM

### Interface
- Tema claro / escuro com alternância em tempo real

---

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Linguagem | Python 3 |
| Interface gráfica | PyQt5 >= 5.15.0 |
| Computação científica | NumPy >= 1.21.0, SciPy >= 1.7.0 |
| Visualização | Matplotlib >= 3.4.0 |
| Arquitetura | MVC (Model-View-Controller) |

---

## Estrutura do Projeto

```
C213/
├── main.py                      # Ponto de entrada da aplicação
├── requirements.txt             # Dependências Python
└── app/
    ├── controllers/
    │   └── main_controller.py   # Bridge View ↔ Model
    ├── models/
    │   └── system_model.py      # Algoritmos de identificação e simulação
    └── views/
        └── main_window.py       # Interface PyQt5 (3 abas)
```

---

## Instalação e Execução

**Pré-requisito:** Python 3.8+

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar a aplicação
python main.py
```

---

## Como Usar

1. **Identificação**
   - Clique em **Carregar Arquivo** e selecione um arquivo `.mat` com dados do sistema
   - Clique em **Identificar** para estimar os parâmetros FOPDT pelo Método de Smith
   - Verifique o EQM e o gráfico comparativo

2. **Controle PID**
   - Escolha o método de sintonia: IMC, ITAE ou Manual
   - Configure o setpoint desejado
   - Clique em **Sintonizar / Simular** para rodar a simulação em malha fechada
   - Analise as métricas de desempenho (tr, ts, Mp, ess)

3. **Comparação**
   - Vá à aba **Comparação** para visualizar ambos os resultados lado a lado

---

## Algoritmos Implementados

### Identificação — Método de Smith
Estima K, τ e θ a partir de uma resposta ao degrau, usando os instantes em que a saída atinge 28,3% e 63,2% do valor final.

### Sintonia IMC
Calcula Kp, Ti e Td a partir dos parâmetros FOPDT e do parâmetro de projeto λ (trade-off entre velocidade e robustez).

### Sintonia ITAE
Aplica fórmulas analíticas baseadas no critério ITAE para rastreamento de referência.

### Simulação em Malha Fechada
Integração numérica discreta (passo adaptativo) com:
- PID paralelo (Kp, Ki = 1/Ti, Kd = Td)
- Filtro derivativo: `N = 10`
- Anti-windup por clamping: `U ∈ [-1×10⁵, 1×10⁵]`
- Buffer circular de `ceil(θ/dt)` posições para o atraso puro

---

## Grupo 7 — C213 
- Daví Padula Rabelo
- Kauã Victor Garcia Siécola
- Matheus Renó Torres
