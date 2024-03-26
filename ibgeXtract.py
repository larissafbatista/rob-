from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
import time
import pandas as pd
import zipfile
import geopandas as gpd
from shapely.geometry import Point


################## MÓDULO 01

pasta_fonte = 'C:\\ggpro\\'

df = pd.read_excel(pasta_fonte + 'cod_municipios_ibge.xls')

# Converter todos os itens da primeira coluna para maiúsculas
df['MUNICÍPIOS'] = df['MUNICÍPIOS'].str.upper()

# Solicitar ao usuário o nome do município de interesse
municipio_interesse = input('Digite o nome do município de interesse: ').upper()

# Procurar o código correspondente ao município de interesse
codigo = df.loc[df['MUNICÍPIOS'] == municipio_interesse, 'CÓDIGOS'].iloc[0]
# Construir o XPath com base no código fornecido
xpath = f'//a[contains(text(), "{codigo}.zip")]'

# Exibir o código correspondente ao município de interesse
print(f'O código para {municipio_interesse} é: {codigo}')


################## MÓDULO 02

# Lê a tabela de códigos p/ achar o município de interesse e seu respectivo código
df = pd.read_excel(pasta_fonte + 'cod_municipios_ibge.xls')

# Converte todos os itens da primeira coluna para maiúsculas
df['MUNICÍPIOS'] = df['MUNICÍPIOS'].str.upper()

# Define o diretório de download
download_dir = 'C:\\ggpro\\downloads\\'

# Configura o diretório de download
chrome_options = Options()
prefs = {'download.default_directory': download_dir}
chrome_options.add_experimental_option('prefs', prefs)

# Inicia o driver do Chrome com as opções configuradas
driver = webdriver.Chrome(options=chrome_options)

# Abre uma página de onde será realizado o download
driver.get('https://www.ibge.gov.br/estatisticas/downloads-estatisticas.html?caminho=Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Coordenadas_enderecos/Municipio') # Navegar até uma pg específica


timeout = 60
# Define um tempo limite (timeout) em segundos
try:
    # Localiza o elemento para iniciar o download e clica nele
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cookie-btn"]')))
    action = ActionChains(driver)
    time.sleep(30)
    action.move_to_element(element).click().perform()
    print('Elemento encontrado: cookies liberados.')
except TimeoutException:
    # Lida com o caso de timeout
    print('Timeout ao esperar pelo elemento.')


# Define um tempo limite (timeout) em segundos
timeout = 60
try:
    # Espera até que um elemento seja visível (exemplo: aguardando a presença de um elemento com o id "element_id")
    # Localiza neste caso a PASTA DO ESTADO DE PERNAMBUCO)
    element = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.XPATH, '//*[@id="Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Coordenadas_enderecos/Municipio/26_PE_anchor"]/i')))
    # Realiza outras operações após o elemento ser encontrado
    print('Elemento encontrado: estado de interesse.')
    element.click()
except TimeoutException:
    # Lida com o caso de timeout
    print('Timeout ao esperar pelo elemento.')


timeout = 60
try:
    # Espera até que um elemento seja visível (exemplo: aguardando a presença de um elemento com o id "element_id")
    element = WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    # Realiza outras operações após o elemento ser encontrado
    print('Elemento encontrado: município de interesse.')
    element.click()
except TimeoutException:
    # Lida com o caso de timeout
    print('Timeout ao esperar pelo elemento.')

print('Em processamento...')

time.sleep(30)
driver.quit()
print('Download concluído com sucesso.')

################## MÓDULO 03

# Caminho para o arquivo zip contendo os pontos
caminho_zip = download_dir + f'{codigo}.zip'

# Extrair o arquivo zip
with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
    zip_ref.extractall('C:\\ggpro\\downloads')
print('Arquivos extraídos do zip.')

# Caminho para o arquivo CSV
caminho_csv = download_dir + f'{codigo}.csv'

# Ler o arquivo CSV como um GeoDataFrame
geodf = gpd.read_file(caminho_csv)

# Verificar se os dados são pontos (se não forem, converta para pontos)
if geodf.geometry.geom_type[0] != 'Point':
    # Se os dados não são pontos, você precisa convertê-los para pontos
    # Por exemplo, usando as colunas de latitude e longitude:
    geodf['geometry'] = [Point(x, y) for x, y in zip(geodf['LONGITUDE'], geodf['LATITUDE'])]

# Exibir as primeiras linhas do GeoDataFrame
print(geodf.head())
print('\nGeadataframe criado com sucesso.\n')

# Definir o sistema de coordenadas de referência (CRS) se necessário
geodf.crs = "EPSG:4674"  # SIRGAS 2000
print(f'Sistema de coordenadas definido: {geodf.crs}')

# Salvar os pontos como um shapefile
caminho_saida_shapefile = download_dir + f'{municipio_interesse}.shp'
geodf.to_file(caminho_saida_shapefile, driver='ESRI Shapefile')
print('Shapefile salvo na pasta com sucesso!')

