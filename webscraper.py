import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import csv

# --- CONFIGURATION ---
BASE = "https://disasterscharter.org"
EVENT = None
PAGE = f"{BASE}/activations/flood-in-braz-1{EVENT and "-"}"
OUTPUT_DIR = f"./data/raw/{EVENT or 'flood-in-braz-1'}"

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

# Tenta clicar no botão "Load all products"
try:
    load_btn = driver.find_element(By.XPATH, "//button[contains(., 'Load all products')]")
    load_btn.click()
    time.sleep(10)  # Aguarda carregar os produtos
except Exception as e:
    print("*** Botão 'Load all products' não encontrado ou erro ao clicar: ***", e)

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

# --- DOWNLOAD DAS IMAGENS ---
img_tags = soup.select("picture img[src]")
downloaded = set()
for img in img_tags:
    src = img["src"]
    if "/_next/image?url=" in src:
        full_url = urljoin(BASE, src)
        if full_url in downloaded:
            continue
        downloaded.add(full_url)
        print(f"Downloading {full_url}...")
        r = requests.get(full_url, headers={"User-Agent": "ImageScraper/1.0"})
        r.raise_for_status()
        # Usa timestamp para nome único
        fname = f"{int(time.time() * 1000)}.jpeg"
        path = os.path.join(OUTPUT_DIR, fname)
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"→ saved as {path}")
        time.sleep(0.01)  # Garante nomes diferentes mesmo em execuções rápidas

print(f"Done: {len(downloaded)} images saved in ./{OUTPUT_DIR}/")
