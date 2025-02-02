from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Configuração do Selenium para Chrome
options = Options()
options.add_argument("--headless")  # Roda o navegador sem abrir janela
options.add_argument("--disable-gpu")  # Evita erro de WebGL
options.add_argument("--no-sandbox")
options.add_argument("--log-level=3")  # Reduz mensagens no terminal
options.add_argument("--disable-software-rasterizer")  # Evita erros gráficos
options.add_argument("--disable-dev-shm-usage")  # Otimiza uso de memória
options.add_argument("start-maximized")

# Inicializar o navegador
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Acessar o site
url = "https://www.abola.pt/"
driver.get(url)

# Esperar até que a página carregue completamente
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "abola-slider"))
    )
    print("🔄 Página carregada com sucesso!")
except:
    print("⚠️ O carrossel demorou muito a carregar!")
    driver.quit()
    exit()

# Recolher links das 10 primeiras notícias
links_noticias = []
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "splide__slide"))
    )
    noticias = driver.find_elements(By.CLASS_NAME, "splide__slide")

    for i in range(min(10, len(noticias))):  # Garantir que não ultrapassa os limites
        try:
            link_element = noticias[i].find_element(By.TAG_NAME, "a")
            link = link_element.get_attribute("href")

            if link.startswith("/"):
                link = f"https://www.abola.pt{link}"  # Corrigir links relativos

            if link not in links_noticias:  # Evitar links duplicados
                links_noticias.append(link)
        except Exception as e:
            print(f"⚠️ Erro ao recolher link da notícia {i+1}: {e}")

except Exception as e:
    print(f"❌ Erro ao carregar a lista de notícias: {e}")

# Lista para armazenar os dados das notícias
dados = []

for i, link in enumerate(links_noticias, start=1):
    try:
        driver.get(link)
        time.sleep(3)  # Espera extra para carregar o conteúdo da notícia

        # Capturar o título
        try:
            titulo_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "titulo"))
            )
            titulo = titulo_element.text.strip()
        except:
            titulo = "❌ Título não encontrado"

        # Capturar o conteúdo da notícia
        try:
            conteudo_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "single-news-content"))
            )
            paragrafos = conteudo_element.find_elements(By.TAG_NAME, "p")
            conteudo = "\n".join([p.text.strip() for p in paragrafos if p.text.strip()])
        except:
            conteudo = "❌ Não foi possível recolher a notícia."

        # Adicionar os dados na lista
        dados.append({
            "Título": titulo,
            "Link": link,
            "Notícia": conteudo
        })

        print(f"✅ Notícia {i} recolhida com sucesso!")

    except Exception as e:
        print(f"⚠️ Erro ao processar notícia {i}: {e}")

# Fechar navegador
driver.quit()

# Imprimir os dados recolhidos no terminal
if not dados:
    print("❌ Nenhuma notícia foi extraída. Verifique os seletores CSS ou se o site bloqueou a raspagem.")
else:
    print("\n📢 Notícias Recolhidas:\n")
    for i, noticia in enumerate(dados, start=1):
        print(f"{i}. {noticia['Título']}")
        print(f"   📎 Link: {noticia['Link']}")
        print(f"   📰 Notícia:\n{noticia['Notícia'][:500]}...")  # Exibir os primeiros 500 caracteres
        print("-" * 100)
