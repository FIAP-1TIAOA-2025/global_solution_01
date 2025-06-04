# --- PASSO 0: Preparação Inicial ---

# Instalar pacotes essenciais (se ainda não tiver feito)
# install.packages("dplyr") # Para manipulação de dados [9, 10]
# install.packages("tidyr") # Útil para organizar dados [10, 11]
# install.packages("ggplot2") # Para visualização de dados [1, 12]
# install.packages("DescTools") # Para calcular a Moda [13]

# Carregar os pacotes
library(dplyr)
library(tidyr)
library(ggplot2)
library(DescTools) # Pode ser necessário carregar para usar a função Mode [13]

# Carregar seus dados para um dataframe no R.
# Assumindo que seus dados estão em um arquivo CSV chamado "dados_climaticos.csv"
# Se estiverem em outro formato, ajuste a função de leitura (ex: read.xlsx para Excel)
# Certifique-se de que o arquivo está no diretório de trabalho ou forneça o caminho completo.
df_clima <- read.csv("dados_climaticos.csv")

# Visualizar as primeiras linhas para verificar se carregou corretamente
head(df_clima)

# Verificar a estrutura dos dados
str(df_clima)
1. Limpeza e Pré-processamento dos Dados
Esta etapa é crucial para garantir que os dados estejam prontos para análise e modelagem. O primeiro passo é lidar com valores ausentes, que em R são frequentemente representados como NA.
# --- PASSO 1: Limpeza e Pré-processamento ---

# 1.1 Identificar e Contar Valores Ausentes [14, 15]
# Utiliza is.na() para verificar quais valores são NA e colSums() para contar por coluna [16]
valores_ausentes_por_coluna <- colSums(is.na(df_clima))
print("Número de valores ausentes por coluna:")
print(valores_ausentes_por_coluna)

# 1.2 Estratégias de Tratamento de Valores Ausentes [14]
# As fontes mencionam estratégias como remover, preencher ou imputar [14].
# Exemplos simples baseados nas fontes:

# Opção A: Remover linhas com QUALQUER valor ausente [14, 16]
# A função drop_na() do pacote tidyr (ou dplyr) faz isso [16].
# Use a pipe %>% do dplyr para encadear operações [16].
# df_clima_limpo <- df_clima %>% drop_na()
# print(paste("Número de linhas após remover NA:", nrow(df_clima_limpo)))

# Opção B: Preencher valores ausentes com uma estatística (ex: mediana ou média) [14]
# A mediana é uma medida robusta que não é afetada por outliers [fora das fontes].
# Exemplo: Preencher NA na coluna 'temperature_2m_mean' com a mediana dessa coluna
# mediana_temp <- median(df_clima$temperature_2m_mean, na.rm = TRUE) # na.rm=TRUE ignora NAs no cálculo
# df_clima$temperature_2m_mean[is.na(df_clima$temperature_2m_mean)] <- mediana_temp

# Implemente a estratégia que for mais adequada para seu projeto.
# Mantenha a versão original ou trabalhe com uma cópia limpa.
df_clima_trabalho <- df_clima # Criar uma cópia para trabalhar

# 1.3 Outras Limpezas (Detecção e correção de erros, remoção de duplicatas) [14]
# As fontes mencionam essas tarefas [14], mas não fornecem código R específico aqui.
# Em R, você usaria funções como:
# duplicated() para identificar linhas duplicadas
# unique() para obter linhas únicas
# Código para corrigir erros específicos dependeria da natureza dos erros.

2. Análise Descritiva de Dados
Esta análise fornecerá uma visão geral das suas variáveis climáticas. Você calculará medidas de tendência central, dispersão e posição.
# --- PASSO 2: Análise Descritiva de Dados ---

# Vamos focar nas variáveis numéricas principais do seu dataset amostra:
# temperature_2m_mean, temperature_2m_max, wind_direction_10m_dominant, precipitation_sum, rain_sum

# Para cada variável de interesse, vamos calcular medidas descritivas [13, 17, 18]
variaveis_numericas <- c("temperature_2m_mean", "temperature_2m_max",
                         "wind_direction_10m_dominant", "precipitation_sum", "rain_sum")

for (coluna in variaveis_numericas) {
  cat("Análise Descritiva para:", coluna, "\n")

  # Medidas de Tendência Central [13, 17, 18]
  media <- mean(df_clima_trabalho[[coluna]], na.rm = TRUE) # Ignorar NAs no cálculo
  mediana <- median(df_clima_trabalho[[coluna]], na.rm = TRUE) # Ignorar NAs no cálculo
  # Moda pode exigir o pacote DescTools e tem suas particularidades (pode haver múltiplas modas) [13]
  # moda <- Mode(df_clima_trabalho[[coluna]], na.rm = TRUE)

  cat("  Média:", media, "\n")
  cat("  Mediana:", mediana, "\n")
  # cat("  Moda:", moda, "\n")

  # Medidas de Dispersão [17, 18]
  amplitude <- diff(range(df_clima_trabalho[[coluna]], na.rm = TRUE)) # [18]
  variancia <- var(df_clima_trabalho[[coluna]], na.rm = TRUE) # [18]
  desvio_padrao <- sd(df_clima_trabalho[[coluna]], na.rm = TRUE) # [18]
  coef_variacao <- (desvio_padrao / media) * 100 # [18]

  cat("  Amplitude:", amplitude, "\n")
  cat("  Variância:", variancia, "\n")
  cat("  Desvio Padrão:", desvio_padrao, "\n")
  cat("  Coeficiente de Variação:", coef_variacao, "%\n")

  # Medidas de Posição (Quartis) [18, 19]
  quartis <- quantile(df_clima_trabalho[[coluna]], probs = c(0.25, 0.50, 0.75), na.rm = TRUE) # [19]
  cat("  Quartis (Q1, Mediana, Q3):\n")
  print(quartis)

  cat("\n") # Pular linha para a próxima coluna
}

# Sumário estatístico completo (muito útil e rápido)
# summary(df_clima_trabalho[variaveis_numericas]) # Mostra min, Q1, mediana, média, Q3, max e NAs
3. Visualização de Dados
A visualização é fundamental para explorar e comunicar padrões nos dados. Você pode visualizar a evolução das variáveis ao longo do tempo ou a distribuição dos seus valores. O pacote ggplot2 é recomendado para gráficos de alta qualidade.
# --- PASSO 3: Visualização de Dados ---

# Converter a coluna 'date' para formato de data/hora se ainda não estiver
# Garante que o eixo X seja tratado corretamente como tempo
df_clima_trabalho$date <- as.POSIXct(df_clima_trabalho$date, tz = "UTC") # Ajuste o fuso horário se necessário

# Exemplo 1: Série Temporal da Temperatura Média
# Mostra a evolução da temperatura média ao longo do tempo
ggplot(df_clima_trabalho, aes(x = date, y = temperature_2m_mean)) + # [12]
  geom_line() + # Desenha uma linha conectando os pontos ao longo do tempo
  labs(title = "Temperatura Média ao Longo do Tempo", # Títulos [fora das fontes]
       x = "Data",
       y = "Temperatura Média (°C)") +
  theme_minimal() # Tema visual [fora das fontes]

# Exemplo 2: Série Temporal da Precipitação Total
# Mostra a precipitação diária (ou acumulada no período do registro)
ggplot(df_clima_trabalho, aes(x = date, y = precipitation_sum)) + [12]
  geom_line() +
  labs(title = "Precipitação Total ao Longo do Tempo",
       x = "Data",
       y = "Precipitação (mm)") +
  theme_minimal()

# Exemplo 3: Distribuição da Precipitação Total (Histograma ou Boxplot para variáveis quantitativas) [12]
ggplot(df_clima_trabalho, aes(x = precipitation_sum)) +
  geom_histogram(binwidth = 5, fill = "blue", color = "black") + # Ajuste binwidth conforme seus dados
  labs(title = "Distribuição da Precipitação Total",
       x = "Precipitação (mm)",
       y = "Frequência") +
  theme_minimal()

ggplot(df_clima_trabalho, aes(y = precipitation_sum)) + # Boxplot para visualizar distribuição e outliers
  geom_boxplot() +
  labs(title = "Boxplot da Precipitação Total",
       y = "Precipitação (mm)") +
  theme_minimal()

# Crie visualizações semelhantes para outras variáveis de interesse (temperatura máxima, direção do vento, etc.)
# 4. Análise de Correlação
# Entender as relações entre as variáveis climáticas pode fornecer insights sobre quais delas podem ser mais relevantes para prever enchentes [conceito geral de EDA]. Embora as fontes não apresentem código R específico para correlação neste contexto particular, calcular a matriz de correlação é uma análise estatística comum em R e fundamental na Análise Exploratória de Dados (AED).
# --- PASSO 4: Análise de Correlação ---

# Calcular a matriz de correlação para as variáveis numéricas
# A função cor() calcula a correlação entre colunas de um dataframe.
# Use use = "complete.obs" para lidar com NAs removendo pares de observações incompletas.
matriz_correlacao <- cor(df_clima_trabalho[variaveis_numericas], use = "complete.obs")

print("Matriz de Correlação das Variáveis Climáticas:")
print(matriz_correlacao)

# Visualizar a matriz de correlação (opcional, requer pacote como corrplot ou ggplot2)
# install.packages("corrplot") # Exemplo de pacote para visualização de correlação [fora das fontes]
# library(corrplot)
# corrplot(matriz_correlacao, method = "circle") # Outras opções: "number", "color"
# Nota: O uso da função cor() e pacotes como corrplot para visualizar a matriz de correlação são práticas padrão em Análise Exploratória de Dados em R, embora os trechos de código específicos para cor() e corrplot não estejam presentes nas fontes fornecidas, que focam mais em exemplos de regressão e estatística descritiva básica.
# 5. Considerações para Análise Inferencial e Espacial
# Embora a análise inferencial seja útil para testar hipóteses, e a análise espacial descritiva seja crucial para entender padrões geográficos (especialmente relevante para o seu projeto de enchentes), estas etapas não podem ser totalmente aplicadas ao seu dataset amostra tal como apresentado, pois ele contém apenas dados climáticos temporais para uma ou poucas localizações (inferido da amostra).
# •
# Análise Inferencial: Seria mais aplicável ao comparar, por exemplo, as condições climáticas (médias de precipitação, temperatura, etc.) em dias/períodos com enchentes versus dias/períodos sem enchentes. Isso exigiria que você combinasse seu dataset climático com dados dos eventos de enchentes que você extraiu do disasterscharter.org (após obter as coordenadas via geocodificação) [discussão anterior]. As fontes discutem testes de hipóteses como base da inferência.
# •
# Análise Espacial: A análise de coordenadas e geolocalizações e a estatística espacial descritiva são vitais para entender como as variáveis climáticas e os eventos de enchentes se distribuem no espaço e se há autocorrelação espacial (como o Índice de Moran ou LISA, mencionados nas fontes). No entanto, seu dataset amostra não inclui colunas de latitude e longitude, que são essenciais para esse tipo de análise. A Análise Exploratória de Dados Espaciais (AEDE) e a visualização em mapas são ferramentas poderosas que você poderá usar quando tiver as coordenadas associadas aos dados climáticos ou aos eventos de enchente.
# --- PASSO 5: Considerações para Análise Futura ---

# Análise Inferencial:
# - Você pode querer realizar testes de hipóteses [27, 31] mais tarde.
# - Exemplo: Testar se a média de precipitação nos dias de enchente é estatisticamente maior
#   do que nos dias sem enchente. Isso requer combinar este dataset com seus dados de eventos
#   de enchente (que você obterá as coordenadas via geocodificação) [discussão anterior].

# Análise Espacial:
# - Crucial para o seu projeto, mas requer dados de localização (latitude, longitude) [28].
# - Seu dataset amostra não possui essas colunas.
# - Quando tiver dados georreferenciados, poderá usar pacotes R de estatística espacial
#   e visualizar dados em mapas [30]. As fontes mencionam o cálculo de índices espaciais [29].