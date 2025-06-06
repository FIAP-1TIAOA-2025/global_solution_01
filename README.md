# Previsão de Inundações no Brasil (POC)

Este projeto é uma POC (Proof Of Concept) que visa desenvolver um modelo de Inteligência Artificial para prever eventos de inundações utilizando dados climáticos e, potencialmente, dados hidrológicos e geográficos. O objetivo é fornecer uma ferramenta de alerta precoce que possa auxiliar na gestão de riscos e na proteção da população.

---

## 🚀 Visão Geral do Projeto

Inundações são desastres naturais recorrentes em muitas cidades costeiras e tropicais, como Salvador. Prever esses eventos com antecedência pode salvar vidas e reduzir danos materiais. Este projeto explora o uso de técnicas de Machine Learning, especificamente com Python e Scikit-learn, para identificar padrões em dados climáticos que precedem inundações.

O pipeline do projeto segue uma abordagem de ciência de dados estruturada:

1. Coleta e Preparação de Dados: Aquisição de dados climáticos históricos, registros de inundações e outras informações relevantes.
2. Análise Exploratória de Dados (EDA): Entendimento inicial dos dados, identificação de tendências, sazonalidade e problemas de qualidade.
3. Engenharia de Features: Criação de variáveis mais informativas (ex: precipitação acumulada, lags) a partir dos dados brutos.
4. Treinamento e Avaliação do Modelo: Seleção, treinamento e otimização de modelos de Machine Learning para prever inundações.
5. Relatórios e Visualizações: Geração de gráficos e relatórios para comunicar insights e performance do modelo.

---

## 📂 Estrutura do Projeto

A organização do projeto segue uma estrutura modular para facilitar o desenvolvimento, a manutenção e a colaboração:

```text
flood_prediction_project/
├── data/
│   ├── raw/                 # Dados brutos originais (nunca modificados)
│   └── processed/           # Dados limpos e com features engenheiradas, prontos para o modelo
│
├── notebooks/
│   ├── 01_eda_and_initial_analysis.ipynb # EDA e análise de correlação inicial
│   ├── 02_feature_engineering_exploration.ipynb # Exploração e criação de features
│   └── 03_model_experimentation.ipynb    # Treinamento e avaliação de modelos
│
├── src/
│   ├── data_ingestion.py    # Scripts para carregar/coletar dados brutos
│   ├── data_preprocessing.py # Funções para limpeza e engenharia de features
│   ├── model_training.py    # Lógica para treinamento e tuning do modelo
│   ├── model_evaluation.py  # Funções para métricas e visualizações de avaliação
│   └── prediction_api.py    # (Opcional) API para servir predições
│
├── models/
│   ├── trained_models/      # Modelos treinados e scalers salvos
│   └── checkpoints/         # Saves intermediários de modelos (se aplicável)
│
├── reports/
│   ├── figures/             # Gráficos e visualizações gerados
│   ├── final_report.md      # Relatório final do projeto
│   └── model_performance_metrics.csv # Métricas de performance do modelo final
│
├── .env                     # Variáveis de ambiente (ex: credenciais, *NÃO comitar!*)
├── requirements.txt         # Lista de dependências Python
├── README.md                # Este arquivo
└── run_pipeline.py          # Script principal para executar o pipeline completo
```

---

## 🛠️ Tecnologias Utilizadas

- Python 3.x
- Bibliotecas Python:
  - pandas: Manipulação e análise de dados
  - numpy: Computação numérica
  - scikit-learn: Modelagem de Machine Learning
  - matplotlib: Visualização de dados
  - seaborn: Visualização de dados estatísticos
  - imblearn: Para lidar com desbalanceamento de classes (SMOTE)
  - joblib: Para salvar e carregar modelos
  - python-dotenv: Para carregar variáveis de ambiente (se usar .env)
- Jupyter Notebook: Para exploração e prototipagem
- MongoDB (Local/Atlas): Para armazenamento de dados (conforme sua escolha)

---

## ⚙️ Configuração do Ambiente

Siga estes passos para configurar o ambiente de desenvolvimento e executar o projeto:

1. Clonar o Repositório:

    ```bash
    git clone https://github.com/seu_usuario/flood_prediction_project.git
    cd flood_prediction_project
    ```

2. Criar e Ativar Ambiente Virtual:
    É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.

    ```bash
    python3 -m venv .venv
    # No macOS/Linux:
    source .venv/bin/activate
    # No Windows:
    .venv\Scripts\activate
    ```

3. Instalar Dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Configurar MongoDB (Local):
    Se você optou por usar o MongoDB localmente:

    - Instale o MongoDB Community Server: Siga as instruções de instalação para seu sistema operacional no site oficial do MongoDB.
    - Inicie o servidor MongoDB: Garanta que o processo mongod esteja rodando (geralmente na porta 27017).

5. Variáveis de Ambiente (Opcional, mas Recomendado):
    Se você for usar credenciais ou caminhos sensíveis, crie um arquivo .env na raiz do projeto (o git o ignorará) e defina suas variáveis lá.
    Exemplo de .env:

    ```text
    MONGO_URI="mongodb://localhost:27017/"
    # Ou sua string do Atlas se decidir voltar:
    # MONGO_URI="mongodb+srv://<username>:<password>@<cluster-url>/?retryWrites=true&w=majority"
    ```

---

## 🚀 Como Executar o Projeto

Você pode executar o projeto de duas maneiras:

### A. Usando os Jupyter Notebooks (Para Exploração)

Para entender cada etapa em detalhes e experimentar:

1. Inicie o Jupyter Lab/Notebook:

    ```bash
    jupyter lab # ou jupyter notebook
    ```

2. Navegue até a pasta ```notebooks/```.
3. Execute os notebooks em ordem numérica:
    - 01_eda_and_initial_analysis.ipynb
    - 02_feature_engineering_exploration.ipynb
    - 03_model_experimentation.ipynb

### B. Executando o Pipeline Completo (Para Reprodução e Testes)

Uma vez que as etapas dos notebooks foram prototipadas, a lógica principal é refatorada para os scripts em src/ e orquestrada pelo run_pipeline.py.

1. Certifique-se de que seu ambiente virtual está ativado.
2. Execute o script principal:

    ```bash
    python run_pipeline.py
    ```

    Este script executará as etapas de carregamento de dados, pré-processamento, engenharia de features, treinamento do modelo e avaliação.

---

## 📊 Resultados e Análise

Os resultados das análises, gráficos gerados e a performance do modelo final serão salvos na pasta ```reports/```.

- ```reports/figures/```: Contém as visualizações (mapas de calor de correlação, gráficos de séries temporais, matrizes de confusão, curvas ROC/PR).
- ```reports/model_performance_metrics.csv```: Um resumo das métricas de avaliação do modelo final.
- ```reports/final_report.md```: Um relatório mais detalhado sobre a metodologia, achados e conclusões do projeto.
