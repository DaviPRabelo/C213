# Documentação matemática e de controle

Este documento resume os modelos matemáticos usados na identificação, sintonia e simulação do projeto **C213 - PID Controller**, desenvolvido pelo **Grupo 7**.

## 1. Modelo FOPDT

O processo é aproximado por um modelo de primeira ordem com atraso:

$$
G(s)=\frac{k e^{-\theta s}}{\tau s+1}
$$

| Símbolo | Significado |
|---|---|
| `k` | ganho estático do processo |
| `τ` | constante de tempo |
| `θ` | atraso de transporte |
| `s` | variável de Laplace |

Sem atraso, a parte de primeira ordem é:

$$
G_0(s)=\frac{k}{\tau s+1}
$$

## 2. Identificação pelo método de Smith

A função `identify_smith(t, u, y)` estima `k`, `τ` e `θ` a partir da resposta ao degrau.

### 2.1 Detecção do degrau

O código calcula:

$$
\Delta u_i=u_i-u_{i-1}
$$

O primeiro índice com variação significativa é usado como instante do degrau:

$$
i_d=\min\{i:|u_i-u_{i-1}|>10^{-9}\}
$$

$$
t_d=t[i_d]
$$

### 2.2 Valores de regime

A entrada inicial e final são:

$$
u_0=u[0]
$$

$$
u_f=u[-1]
$$

A variação da entrada é:

$$
\Delta u=u_f-u_0
$$

A saída inicial é calculada como média antes do degrau:

$$
y_0=\operatorname{mean}(y[0:i_d])
$$

A saída em regime é aproximada pela média das últimas amostras:

$$
y_{\infty}=\operatorname{mean}(y[N-n_{tail}:N])
$$

com:

$$
n_{tail}=\max\left(5,\left\lfloor\frac{N}{10}\right\rfloor\right)
$$

A variação da saída é:

$$
\Delta y=y_{\infty}-y_0
$$

### 2.3 Ganho estático

$$
k=\frac{\Delta y}{\Delta u}
$$

Se `Δu` for aproximadamente nulo, a função interrompe a identificação.

### 2.4 Pontos de 28,3% e 63,2%

$$
y_{28,3}=y_0+0,283\Delta y
$$

$$
y_{63,2}=y_0+0,632\Delta y
$$

A função usa interpolação linear para obter os tempos `t1` e `t2` associados a esses níveis.

### 2.5 Tempos relativos

$$
t_{1,rel}=t_1-t_d
$$

$$
t_{2,rel}=t_2-t_d
$$

### 2.6 Estimativa de `τ` e `θ`

$$
\tau=1,5(t_{2,rel}-t_{1,rel})
$$

$$
\theta=t_{2,rel}-\tau
$$

Proteções numéricas:

$$
\tau\leq0\Rightarrow\tau=10^{-3}
$$

$$
\theta<0\Rightarrow\theta=0
$$

## 3. Simulação FOPDT em malha aberta

A função `simulate_fopdt()` simula a parte sem atraso por:

$$
G_0(s)=\frac{k}{\tau s+1}
$$

A entrada é convertida para variável de desvio:

$$
u_d(t)=u(t)-u_0
$$

O atraso é aplicado por deslocamento de amostras:

$$
n_\theta=\operatorname{round}\left(\frac{\theta}{\Delta t}\right)
$$

A saída total é:

$$
y(t)=y_0+y_d(t)
$$

## 4. Erro do modelo

A função `compute_eqm()` calcula o erro quadrático médio:

$$
EQM=\frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i-y_i)^2
$$

## 5. Controlador PID

A forma contínua de referência é:

$$
u(t)=K_p\left[e(t)+\frac{1}{T_i}\int_0^t e(\xi)d\xi+T_d\frac{de(t)}{dt}\right]
$$

com:

$$
e(t)=SP-y(t)
$$

No domínio de Laplace:

$$
C(s)=K_p\left(1+\frac{1}{T_i s}+T_d s\right)
$$

Em forma racional:

$$
C(s)=\frac{K_pT_iT_ds^2+K_pT_is+K_p}{T_i s}
$$

Se `Ti<=0`, a implementação usa uma forma PD:

$$
C(s)=K_p(T_d s+1)
$$

## 6. Sintonia IMC

A função `tune_imc(k, tau, theta, lam)` usa:

$$
K_p=\frac{2\tau+\theta}{k(2\lambda+\theta)}
$$

$$
T_i=\tau+\frac{\theta}{2}
$$

$$
T_d=\frac{\tau\theta}{2\tau+\theta}
$$

Quando `λ` não é informado:

$$
\lambda=\tau
$$

## 7. Sintonia ITAE

O critério ITAE é:

$$
ITAE=\int_0^{\infty}t|e(t)|dt
$$

A função `tune_itae(k, tau, theta)` usa:

$$
A=0,965,\quad B=-0,85,\quad C=0,796,\quad D=-0,147,\quad E=0,308,\quad F=0,929
$$

A razão adimensional é:

$$
r=\frac{\theta}{\tau}
$$

As correlações são:

$$
K_p=\frac{A}{k}r^B
$$

$$
T_i=\frac{\tau}{C+Dr}
$$

$$
T_d=\tau E r^F
$$

Substituindo as constantes:

$$
K_p=\frac{0,965}{k}\left(\frac{\theta}{\tau}\right)^{-0,85}
$$

$$
T_i=\frac{\tau}{0,796-0,147\left(\frac{\theta}{\tau}\right)}
$$

$$
T_d=0,308\tau\left(\frac{\theta}{\tau}\right)^{0,929}
$$

## 8. Aproximação de Padé

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

Se `θ<=0`, a função retorna numerador e denominador unitários, isto é, sem atraso.

## 9. Malha fechada

A malha aberta é:

$$
L(s)=C(s)G(s)
$$

A malha fechada com realimentação unitária é:

$$
T(s)=\frac{L(s)}{1+L(s)}
$$

## 10. Estabilidade

A estabilidade é verificada pelos polos da malha fechada:

$$
\operatorname{Re}(p_i)<-tol,\quad \forall i
$$

com:

$$
tol=10^{-9}
$$

## 11. Métricas

### Valor final

$$
y_f=\operatorname{mean}(y[N-n_{tail}:N])
$$

com:

$$
n_{tail}=\max\left(5,\left\lfloor\frac{N}{20}\right\rfloor\right)
$$

### Tempo de subida

$$
y_{10}=0,10y_f
$$

$$
y_{90}=0,90y_f
$$

$$
t_r=t_{90}-t_{10}
$$

### Sobressinal

$$
y_{pico}=\max(y)
$$

$$
M_p=\max\left(0,\frac{y_{pico}-y_f}{|y_f|}100\right)
$$

### Tempo de acomodação

A banda usada é:

$$
|y(t)-y_f|\leq0,02|y_f|
$$

O tempo de acomodação é tomado como o último instante fora dessa banda:

$$
t_s=\max\{t:|y(t)-y_f|>0,02|y_f|\}
$$

### Erro em regime permanente

$$
e_{ss}=SP-y_f
$$
