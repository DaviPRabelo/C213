# Guia de uso da IHM

Este documento descreve o uso prático da interface do projeto C213 - PID Controller.

## 1. Abrir o programa

Execute:

```bash
python3 main.py
```

A janela será aberta com três abas principais:

1. **Identificação**;
2. **Controle PID**;
3. **Gráficos**.

## 2. Aba Identificação

### Objetivo

Carregar o dataset experimental e identificar o modelo FOPDT pelo método de Smith.

### Passos

1. Clique em **Escolher Arquivo .mat**.
2. Selecione um dataset com dados experimentais.
3. Verifique se o nome do arquivo aparece no painel esquerdo.
4. Clique em **Identificar**.
5. Analise os parâmetros exibidos:
   - `K`: ganho do processo;
   - `τ`: constante de tempo;
   - `θ`: atraso;
   - `EQM`: indicador de erro do ajuste.

### Interpretação do gráfico

O gráfico apresenta:

- curva azul: dados reais do processo;
- curva verde tracejada: modelo FOPDT identificado;
- linha vertical: instante de aplicação do degrau.

Quanto mais próxima a curva do modelo estiver da curva real, melhor é a aproximação FOPDT para o dataset.

## 3. Aba Controle PID

### Objetivo

Sintonizar o controlador PID e simular a resposta em malha fechada.

### Modo automático

1. Selecione **Método Automático**.
2. Escolha **IMC** ou **ITAE**.
3. Ajuste o setpoint, se necessário.
4. Clique em **Sintonizar**.

No modo automático, `Kp`, `Ti` e `Td` são calculados pelo programa.

### Método IMC

No IMC, o parâmetro `λ` é usado como parâmetro de projeto.

- `λ` menor: resposta mais rápida;
- `λ` maior: resposta mais robusta e mais lenta.

### Método ITAE

No ITAE, o parâmetro `λ` não é usado. Por isso, a interface exibe `N/A` no campo correspondente.

### Modo manual

1. Selecione **Manual**.
2. Insira os valores de `Kp`, `Ti` e `Td`.
3. Ajuste o setpoint.
4. Clique em **Sintonizar**.

O modo manual é útil para ajuste fino e comparação com os métodos automáticos.

## 4. Métricas exibidas

| Campo | Significado |
|---|---|
| `tr` | tempo de subida |
| `ts` | tempo de acomodação |
| `Mp` | sobressinal percentual |
| `ess` | erro em regime permanente |

A faixa verde em torno do setpoint representa a banda de ±2%, usada para avaliar o tempo de acomodação.

## 5. Aba Gráficos

### Objetivo

Comparar o comportamento em malha aberta e malha fechada.

### Passos

1. Execute a identificação na aba **Identificação**.
2. Execute a sintonia na aba **Controle PID**.
3. Abra a aba **Gráficos**.
4. Clique em **Atualizar Comparação**.

### Interpretação

O gráfico da esquerda mostra:

- dados reais em malha aberta;
- modelo FOPDT identificado.

O gráfico da direita mostra:

- saída controlada em malha fechada;
- setpoint;
- faixa de ±2%.

## 6. Exportação de gráficos

Os botões **Exportar Gráfico** salvam o gráfico atual em:

- `.png`;
- `.pdf`;
- `.svg`.
