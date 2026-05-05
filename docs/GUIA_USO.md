# Guia de uso da IHM

Este documento descreve o uso prático da interface do projeto **C213 - PID Controller**.

## 1. Abrir o programa

Execute:

```bash
python3 main.py
```

A janela será aberta com quatro abas principais:

1. **Login**;
2. **Identificação**;
3. **Controle PID**;
4. **Gráficos**.

O cabeçalho da IHM identifica o projeto como **C213 - PID Controller** e informa o **Grupo 7** com os métodos **Smith + IMC + ITAE**.

## 2. Aba Login

### Objetivo

Autenticar o usuário antes de liberar as abas de Identificação, Controle PID e Gráficos.

### Passos para login

1. Verifique a URI em **Conexão MongoDB**. O padrão é `mongodb://localhost:27017`.
2. Informe o `username` e a senha.
3. Clique em **Entrar**.
4. Após login válido, as demais abas ficam habilitadas.

### Cadastro

1. Clique em **Não tem conta? Cadastre-se**.
2. Informe nome, username, senha, confirmação de senha e grupo.
3. Clique em **Cadastrar**.
4. Volte para a tela de login e autentique com o usuário criado.

## 3. Aba Identificação

### Objetivo

Carregar o dataset experimental e identificar automaticamente o modelo FOPDT pelo método de Smith.

### Dataset esperado

O arquivo `.mat` deve conter vetores de tempo, entrada e saída. O programa procura os seguintes nomes:

| Grandeza | Nomes aceitos |
|---|---|
| Tempo | `tiempo`, `tempo`, `t`, `time` |
| Entrada | `entrada`, `u`, `input` |
| Saída | `salida`, `saida`, `y`, `output` |

### Passos

1. Clique em **Escolher Arquivo .mat**.
2. Selecione o dataset experimental.
3. A identificação é executada automaticamente.
4. Verifique se o nome do arquivo aparece no painel esquerdo.
5. Analise os parâmetros exibidos:
   - `k`: ganho do processo;
   - `τ`: constante de tempo;
   - `θ`: atraso de transporte;
   - `EQM`: erro quadrático médio do ajuste.
6. Analise os campos do experimento:
   - `u0`: entrada inicial;
   - `uf`: entrada final;
   - `y∞`: saída final estimada;
   - `t_d`: instante do degrau.

### Interpretação do gráfico

O gráfico apresenta:

- curva experimental do processo;
- curva do modelo FOPDT identificado;
- ponto `t1`, associado a 28,3% da variação da saída;
- ponto `t2`, associado a 63,2% da variação da saída.

Quanto mais próxima a curva do modelo estiver da curva real, melhor é a aproximação FOPDT para o dataset.

## 4. Aba Controle PID

### Objetivo

Sintonizar o controlador PID e simular a resposta em malha fechada.

### Modo automático

1. Selecione **Método Automático**.
2. Escolha **IMC** ou **ITAE**.
3. Ajuste o setpoint em `SP`, se necessário.
4. Ajuste o tempo de simulação em `t_sim`, se necessário.
5. Clique em **Sintonizar**.

No modo automático, `Kp`, `Ti` e `Td` são calculados pelo programa e aparecem como campos não editáveis.

### Método IMC

No IMC, o parâmetro `λ` é usado como parâmetro de projeto.

- `λ` menor: resposta mais rápida;
- `λ` maior: resposta mais lenta e geralmente mais robusta.

Quando o dataset é carregado, o programa usa inicialmente `λ=τ`, salvo quando o usuário já definiu outro valor válido.

### Método ITAE

No ITAE, o parâmetro `λ` não é usado. Por isso, a interface exibe `N/A` no campo correspondente.

### Modo manual

1. Selecione **Manual**.
2. Insira os valores de `Kp`, `Ti` e `Td`.
3. Ajuste `SP` e `t_sim`.
4. Clique em **Sintonizar**.

No modo manual, se a malha fechada for instável, a simulação é bloqueada e a IHM mostra os polos instáveis.

## 5. Métricas exibidas

| Campo | Significado |
|---|---|
| `tr` | tempo de subida |
| `ts` | tempo de acomodação |
| `Mp` | sobressinal percentual |
| `ess` | erro em regime permanente |

A faixa ao redor do setpoint representa a banda visual de ±2%.

## 6. Aba Gráficos

### Objetivo

Comparar o comportamento da planta em malha aberta com as respostas em malha fechada dos métodos IMC e ITAE.

### Passos

1. Carregue o dataset na aba **Identificação**.
2. Ajuste `SP` e `t_sim` na aba **Controle PID**, se necessário.
3. Abra a aba **Gráficos**.
4. Clique em **Atualizar Comparação**.

### Interpretação

O gráfico da esquerda mostra:

- resposta natural em malha aberta;
- amplitude do degrau original `Δu=u_f-u_0`;
- valor final teórico `y∞=y0+kΔu`.

O gráfico da direita mostra:

- resposta em malha fechada com IMC;
- resposta em malha fechada com ITAE;
- setpoint;
- faixa de ±2%.

## 7. Exportação de gráficos

Na aba **Identificação**, o botão **Exportar Gráfico** salva o gráfico de identificação.

Na aba **Controle PID**, o botão **Exportar Gráfico** salva a resposta em malha fechada.

Na aba **Gráficos**, o botão **Exportar** salva dois arquivos:

1. o gráfico de comparação em malha fechada;
2. o gráfico de malha aberta, com sufixo `_open_loop`.

Formatos disponíveis:

- `.png`;
- `.pdf`.

## 8. Alternância de tema

O botão no canto superior direito alterna entre tema escuro e tema claro. Os gráficos são redesenhados para acompanhar a paleta ativa.
