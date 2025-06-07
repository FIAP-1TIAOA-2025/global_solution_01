import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv

def load_raw_data():
    # --- CONFIGURATION ---
    BASE = "https://disasterscharter.org"
    PAGE = f"{BASE}/activations/flood-in-brazil-activation-875-"
    OUTPUT_DIR = f"./data/raw/flood-in-brazil"

    # create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Configura o Selenium para rodar sem abrir janela
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(PAGE)   

    # Espera a página carregar
    time.sleep(3)

    # Pega o HTML após carregar tudo
    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    # --- EXTRAÇÃO DO ARTIGO PRINCIPAL ---
    article = soup.find("article")
    if article:
        article_text = article.get_text(separator="\n", strip=True)
        with open(os.path.join(OUTPUT_DIR, "article.txt"), "w", encoding="utf-8") as f:
            f.write(article_text)
        print("Artigo salvo em article.txt")
    else:
        print("Artigo não encontrado.")

    # --- EXTRAÇÃO DOS DADOS DA ATIVAÇÃO (EXEMPLO: TÍTULO, DATA, ETC) ---
    activation_data = {}
    # Título
    title_tag = soup.find("h1")
    if title_tag:
        activation_data["title"] = title_tag.get_text(strip=True)
    # Data (procura por <time>)
    time_tag = soup.find("time")
    if time_tag:
        activation_data["date"] = time_tag.get("datetime", time_tag.get_text(strip=True))
    # Outros dados podem ser extraídos conforme a estrutura da página

    with open(os.path.join(OUTPUT_DIR, "activation_data.txt"), "w", encoding="utf-8") as f:
        for k, v in activation_data.items():
            f.write(f"{k}: {v}\n")
    print("Dados da ativação salvos em activation_data.txt")

    # --- EXTRAÇÃO DO <dl> COMO METADADOS ---
    dl_tag = soup.find("dl")
    if dl_tag:
        # Extrai dt e dd em pares
        dt_tags = dl_tag.find_all("dt")
        dd_tags = dl_tag.find_all("dd")
        if len(dt_tags) == len(dd_tags):
            rows = []
            for dt, dd in zip(dt_tags, dd_tags):
                key = dt.get_text(strip=True)
                value = dd.get_text(separator=" ", strip=True)
                rows.append((key, value))
            # Salva como CSV
            csv_path = os.path.join(OUTPUT_DIR, "metadata_dl.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Key", "Value"])
                writer.writerows(rows)
            print("Elemento <dl> salvo em metadata_dl.csv")
        else:
            print("Quantidade de <dt> e <dd> não bate, não foi possível salvar como CSV.")
    else:
        print("Elemento <dl> não encontrado.")
