# Documentação matemática e de controle

Este documento resume os modelos matemáticos usados na identificação, sintonia e simulação do projeto **C213 PID Controller**, desenvolvido pelo **Grupo 7**.

As fórmulas apresentadas foram organizadas a partir de três fontes principais:

1. o guia da disciplina, que define o uso de identificação FOPDT, método de Smith, sintonia PID e análise de métricas de resposta;
2. a implementação realizada no arquivo `app/models/system_model.py`;
3. referências clássicas de controle de processos associadas aos métodos de Smith, IMC e ITAE.

Para manter a documentação coerente com o software entregue, as equações apresentadas neste arquivo correspondem às fórmulas realmente utilizadas na implementação.

## 1. Modelo FOPDT

O processo é aproximado por um modelo de primeira ordem com atraso, conhecido como FOPDT, do inglês *First Order Plus Dead Time*:

$$
G(s)=\frac{K e^{-\theta s}}{\tau s+1}
$$

em que:

| Símbolo | Significado |
|---|---|
| `K` | ganho estático do processo |
| `τ` | constante de tempo do processo |
| `θ` | atraso de transporte |
| `s` | variável complexa de Laplace |

Esse modelo é usado para representar a dinâmica aproximada da planta térmica a partir de uma resposta ao degrau. O termo exponencial representa o atraso de transporte, enquanto o denominador de primeira ordem representa a dinâmica dominante do processo.

A forma no domínio do tempo, em variáveis de desvio, é:

$$
\tau \dot{y}_d(t)=K u_d(t-\theta)-y_d(t)
$$

com:

$$
y(t)=y_0+y_d(t)
$$

$$
u_d(t)=u(t)-u_0
$$

em que `y_0` é o valor inicial da saída e `u_0` é o valor inicial da entrada.

## 2. Identificação por Smith

A identificação por Smith é usada para estimar os parâmetros do modelo FOPDT:

$$
K,\ \tau,\ \theta
$$

A implementação está concentrada na função `identify_smith()` do arquivo `system_model.py`.

## 2.1 Detecção do degrau

O instante do degrau é determinado pela maior variação absoluta na entrada:

$$
i_{\text{degrau}}=\arg\max_i |u_i-u_{i-1}|
$$

$$
t_{\text{degrau}}=t[i_{\text{degrau}}]
$$

Quando a entrada não possui uma variação detectável, a implementação considera o início do vetor como referência para o degrau.

## 2.2 Ganho estático

O ganho estático do processo é obtido pela razão entre a variação final da saída e a variação final da entrada:

$$
K=\frac{\Delta y}{\Delta u}
$$

com:

$$
\Delta y=y_{ss}-y_0
$$

$$
\Delta u=u_{ss}-u_0
$$

em que `y_ss` e `u_ss` são valores médios em regime permanente, calculados a partir das últimas amostras dos sinais.

Caso a variação da entrada seja aproximadamente nula, a implementação utiliza uma proteção numérica para evitar divisão por zero.

## 2.3 Normalização da resposta

A resposta é normalizada para permitir a extração dos pontos característicos do método:

$$
y_N(t)=\frac{y(t)-y_0}{\Delta y}
$$

Dessa forma, a resposta passa a variar aproximadamente entre 0 e 1, considerando o valor inicial e o valor final do processo.

## 2.4 Pontos característicos de Smith

O método usa os tempos em que a resposta normalizada cruza os níveis de 28,3% e 63,2%:

$$
y_N(t_1)=0,283
$$

$$
y_N(t_2)=0,632
$$

A interpolação linear entre duas amostras consecutivas é feita por:

$$
t=t_a+\frac{y_{\text{ref}}-y_a}{y_b-y_a}(t_b-t_a)
$$

em que:

| Símbolo | Significado |
|---|---|
| `t_a` | instante da amostra anterior ao cruzamento |
| `t_b` | instante da amostra posterior ao cruzamento |
| `y_a` | valor normalizado anterior ao cruzamento |
| `y_b` | valor normalizado posterior ao cruzamento |
| `y_ref` | nível de referência, 0,283 ou 0,632 |

## 2.5 Estimativa dos parâmetros

A constante de tempo é estimada por:

$$
\tau=1,5(t_2-t_1)
$$

O atraso de transporte é estimado por:

$$
\theta=(t_2-\tau)-t_{\text{degrau}}
$$

Para evitar valores inválidos na simulação, a implementação limita os parâmetros a:

$$
\tau>0
$$

$$
\theta\geq 0
$$

Assim, mesmo que a estimativa inicial produza atraso negativo por ruído ou por irregularidade nos dados, o modelo utilizado na simulação permanece fisicamente viável.

## 2.6 Simulação do modelo identificado

Após a obtenção de `K`, `τ` e `θ`, o modelo FOPDT é simulado para comparação com os dados reais.

A equação usada em variáveis de desvio é:

$$
\tau \frac{dy_d(t)}{dt}=K u_d(t-\theta)-y_d(t)
$$

A saída total é reconstruída por:

$$
y(t)=y_0+y_d(t)
$$

No código, a simulação é feita numericamente por integração de Euler com passo variável.

## 2.7 Erro do modelo

O indicador exibido na IHM é nomeado como `EQM`, porém a fórmula implementada calcula a raiz do erro quadrático médio, isto é, o RMSE:

$$
EQM_{\text{app}}=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(y_i-\hat{y}_i)^2}
$$

em que:

| Símbolo | Significado |
|---|---|
| `N` | número de amostras |
| `y_i` | saída medida |
| `\hat{y}_i` | saída estimada pelo modelo FOPDT |

Quanto menor esse valor, maior a proximidade entre o modelo identificado e os dados reais do processo.

## 3. Controlador PID

A lei de controle contínua usada como referência é:

$$
u(t)=K_p\left[e(t)+\frac{1}{T_i}\int_0^t e(\xi)d\xi+T_d\frac{de(t)}{dt}\right]
$$

com erro:

$$
e(t)=SP-y(t)
$$

em que:

| Símbolo | Significado |
|---|---|
| `u(t)` | sinal de controle |
| `K_p` | ganho proporcional |
| `T_i` | tempo integral |
| `T_d` | tempo derivativo |
| `e(t)` | erro entre setpoint e saída |
| `SP` | setpoint |
| `y(t)` | saída do sistema |

A simulação usa integração discreta e filtro derivativo de primeira ordem para reduzir amplificação numérica da parcela derivativa.

## 4. Sintonia IMC

O método IMC, do inglês *Internal Model Control*, usa o parâmetro `λ` como filtro de projeto. A escolha de `λ` altera o compromisso entre rapidez e robustez da resposta.

| Escolha de `λ` | Tendência esperada |
|---|---|
| `λ` menor | resposta mais rápida e mais sensível a ruídos e incertezas |
| `λ` próximo de `θ` | compromisso intermediário entre rapidez e robustez |
| `λ` maior | resposta mais lenta e mais robusta |

As equações documentadas nesta seção são as mesmas utilizadas pela função `tune_imc()`.

A implementação calcula:

$$
K_p=\frac{2\tau+\theta}{K(2\lambda+\theta)}
$$

$$
T_i=\tau+\frac{\theta}{2}
$$

$$
T_d=\frac{\tau\theta}{2\tau+\theta}
$$

em que:

| Símbolo | Significado |
|---|---|
| `λ` | parâmetro de projeto do IMC |
| `K` | ganho estático identificado |
| `τ` | constante de tempo identificada |
| `θ` | atraso identificado |

A escolha de `λ` deve ser justificada de acordo com o desempenho desejado. Valores menores aceleram a resposta, mas podem aumentar o overshoot e a sensibilidade a incertezas. Valores maiores tornam a resposta mais conservadora.

## 5. Sintonia ITAE

O método ITAE, do inglês *Integral of Time-weighted Absolute Error*, procura minimizar o erro absoluto ponderado pelo tempo:

$$
ITAE=\int_0^{\infty}t|e(t)|dt
$$

Esse critério penaliza erros que permanecem por mais tempo durante a resposta transitória. Assim, ele favorece respostas com menor erro persistente.

Para o modelo FOPDT, a implementação usa as seguintes correlações:

$$
K_p=\frac{0,965}{K}\left(\frac{\theta}{\tau}\right)^{-0,85}
$$

$$
T_i=\frac{\tau}{0,796-0,147\left(\frac{\theta}{\tau}\right)}
$$

$$
T_d=0,308\tau\left(\frac{\theta}{\tau}\right)^{0,929}
$$

A razão adimensional usada é:

$$
r=\frac{\theta}{\tau}
$$

Portanto, as equações também podem ser escritas como:

$$
K_p=\frac{0,965}{K}r^{-0,85}
$$

$$
T_i=\frac{\tau}{0,796-0,147r}
$$

$$
T_d=0,308\tau r^{0,929}
$$

A aplicação dessas correlações pressupõe que o atraso identificado seja positivo e que a razão `θ/τ` esteja em uma faixa fisicamente coerente para modelos FOPDT.

## 6. Simulação de malha fechada

O sistema simulado segue a estrutura:

```text
SP -> comparação -> PID -> atraso θ -> planta FOPDT -> saída y(t)
        ^                                             |
        |_____________________________________________|
````

A resposta em malha fechada é calculada pela função `simulate_closed_loop()`.

A atualização de estado da planta é feita por Euler:

$$
y_d[k]=y_d[k-1]+\frac{\Delta t}{\tau}\left(Ku_d[k-d]-y_d[k-1]\right)
$$

em que `d` é o número de amostras correspondente ao atraso:

$$
d=\left\lceil\frac{\theta}{\Delta t}\right\rceil
$$

Os termos usados são:

| Símbolo    | Significado                                |
| ---------- | ------------------------------------------ |
| `y_d[k]`   | saída em variável de desvio na amostra `k` |
| `u_d[k-d]` | entrada atrasada em `d` amostras           |
| `Δt`       | passo de integração                        |
| `d`        | atraso discreto                            |
| `K`        | ganho da planta                            |
| `τ`        | constante de tempo                         |

O atraso é implementado por um buffer discreto, de modo que o sinal de controle aplicado à planta seja retardado pelo número de amostras equivalente a `θ`.

## 7. Filtro derivativo e anti-windup

A parcela derivativa pode amplificar oscilações numéricas e ruídos. Por isso, a implementação utiliza um filtro derivativo de primeira ordem.

A ideia geral é suavizar a derivada do erro antes de aplicá-la na lei de controle. Isso evita que pequenas variações entre amostras causem grandes variações no sinal de controle.

A implementação também utiliza saturação numérica do sinal de controle e uma forma simples de anti-windup por travamento do integrador. Quando o sinal calculado ultrapassa os limites definidos, o integrador não é atualizado, evitando crescimento excessivo da ação integral.

## 8. Métricas de resposta

A IHM exibe métricas clássicas de desempenho da resposta ao degrau.

## 8.1 Tempo de subida

O tempo de subida é calculado como o intervalo entre o instante em que a saída atinge 10% e o instante em que atinge 90% do setpoint:

$$
t_r=t_{0{,}90}-t_{0{,}10}
$$

## 8.2 Sobressinal percentual

O sobressinal percentual é calculado por:

$$
M_p=\frac{y_{\text{max}}-SP}{SP}\cdot 100%
$$

Quando a resposta não ultrapassa o setpoint, o código registra:

$$
M_p=0
$$

## 8.3 Tempo de acomodação

A faixa usada é de aproximadamente ±2% em torno do setpoint:

$$
SP-0,02|SP|\leq y(t)\leq SP+0,02|SP|
$$

O tempo de acomodação é determinado como o primeiro instante após o qual a resposta permanece dentro dessa faixa.

## 8.4 Erro em regime permanente

O erro em regime permanente é calculado por:

$$
e_{ss}=|SP-\bar{y}_{\text{final}}|
$$

A média final é calculada com as últimas amostras da resposta simulada:

$$
\bar{y}*{\text{final}}=\frac{1}{M}\sum*{i=N-M+1}^{N}y_i
$$

em que `M` é o número de amostras finais usadas na média.

## 9. Relação com a IHM

Os parâmetros e métricas calculados são exibidos nas abas da interface.

| Aba           | Dados exibidos                                                |
| ------------- | ------------------------------------------------------------- |
| Identificação | `K`, `τ`, `θ`, `EQM` e curva FOPDT ajustada                   |
| Controle PID  | `Kp`, `Ti`, `Td`, `λ`, setpoint, `t_r`, `t_s`, `M_p` e `e_ss` |
| Gráficos      | comparação entre malha aberta e malha fechada                 |

A aba de identificação permite avaliar se o modelo FOPDT representa adequadamente os dados experimentais. A aba de controle permite aplicar as sintonias IMC e ITAE. A aba de gráficos permite comparar o comportamento em malha aberta e em malha fechada.

---

As referências associadas são:

* Smith, C. L. *Digital Computer Process Control*. Intext Educational Publishers, 1972.
* Rivera, D. E.; Morari, M.; Skogestad, S. *Internal Model Control: PID Controller Design*. Industrial & Engineering Chemistry Process Design and Development, 1986.
* Seborg, D. E.; Edgar, T. F.; Mellichamp, D. A.; Doyle, F. J. *Process Dynamics and Control*. Wiley.
* Guia do Projeto de Identificação de Sistemas e Controle PID da disciplina C213.
