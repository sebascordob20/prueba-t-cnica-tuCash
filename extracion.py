import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Función para parsear el archivo XML y extraer las primeras 200 URLs
def parsear_xml(file_path, namespace_value):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespace = {'ns': namespace_value}
    urls = [url.find('ns:loc', namespace).text for url in root.findall('ns:url', namespace)]
    return urls[:200]

# Función para extraer información del sitio web usando Selenium
def extraer_datos_con_driver(url_pagina):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless
    chrome_options.add_argument("--disable-gpu")  # Deshabilitar la GPU para mejorar la velocidad

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url_pagina)
    driver.implicitly_wait(10) # Agregando una espera implicita mientras carga el sitio web
    
    try:
        descuento_elemento_web = driver.find_element(By.XPATH, '//*[@id="__next"]/main/section[1]/section[1]/section[2]/section/section/section[2]/div/div[1]/div/span')
        descuento_scrapping = descuento_elemento_web.text #extrayendo el texto del elemento web del descuento del producto.
    except:
        descuento_scrapping = 'N/A'
    
    try:
        unidades_elemento_web = driver.find_element(By.XPATH, '//*[@id="__next"]/main/section[1]/section[1]/section[2]/section/section/section[3]/section[1]/p/span')
        cantidad_unidades = unidades_elemento_web.text #extrayendo el texto del elemento web de la cantidad del producto.
    except:
        cantidad_unidades = 'N/A'
    
    driver.quit()
    
    return {
        'descuento': descuento_scrapping,
        'cantidad_unidades': cantidad_unidades3
    }

# Función para extraer datos de una página usando BeautifulSoup
def extraer_datos_paginas(url_pagina):
    response = requests.get(url_pagina)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'html.parser') #pasreando la respuesta de la petición a código html.
    producto_general = soup.select('a.breadcrumb_Breadcrumb__link__P9uh1') #Primer elemento que se localiza con BeautifulSoup
    
    if len(producto_general) < 3:
        return None
    
    categoria_producto = producto_general[1].text
    tipo_producto = producto_general[2].text
    tipo_producto_especifico = producto_general[3].text if len(producto_general) > 3 else 'N/A'

    id_del_producto = soup.select_one('.product-title_product-title__specification__UTjNc').text if soup.select_one('.product-title_product-title__specification__UTjNc') else 'N/A'
    titulo_del_producto = soup.select_one('.product-title_product-title__heading___mpLA').text if soup.select_one('.product-title_product-title__heading___mpLA') else 'N/A'
    precio_total = soup.select_one('.ProductPrice_container__price__XmMWA').text if soup.select_one('.ProductPrice_container__price__XmMWA') else 'N/A'
    material = soup.select_one('p[data-fs-text-specification]').text if soup.select_one('p[data-fs-text-specification]') else 'N/A'

    datos_adicionales = extraer_datos_con_driver(url_pagina)

    return {# devolvemos un JSON con la información de los textos de todos los elementos que localizamos en la página web con selenium y con BeautifulSoup
        'url': url_pagina,
        'categoria_producto': categoria_producto,
        'tipo_producto': tipo_producto,
        'tipo_producto_especifico': tipo_producto_especifico,
        'id_producto': id_del_producto,
        'titulo_producto': titulo_del_producto,
        'descuento_producto': datos_adicionales['descuento'],
        'cantidad_producto': datos_adicionales['cantidad_unidades'],
        'precio_total': precio_total,
        'material': material,
    }

# Función principal para agregar datos al CSV
def agregar_datos_csv(csv_directorio):
    urls_de_productos = parsear_xml("./resources/url-set-exito.xml", "http://www.sitemaps.org/schemas/sitemap/0.9") #Llamamos a la función que parsea el archivo XML.
    info_lista_productos = []

    for url in urls_de_productos: #Recorremos todas las URL del archivo XML.
        datos_producto = extraer_datos_paginas(url) #Guardamos todas las URL del archivo XML en una lista.
        if datos_producto:
            info_lista_productos.append(datos_producto)
        time.sleep(random.uniform(1, 3))
    
    if not os.path.exists(csv_directorio):
        os.makedirs(csv_directorio)

    ruta_archivo_csv = os.path.join(csv_directorio, 'productos.csv')

    with open(ruta_archivo_csv, mode='w', newline='', encoding='utf-8') as archivo:
        escribir_archivo = csv.writer(archivo)
        escribir_archivo.writerow(['URL', 'categoria_producto', 'tipo_producto', 'tipo_producto_especifico', 'id_producto', 'titulo_producto', 'descuento_producto', 'cantidad_producto', 'precio_total', 'material'])
        
        for info in info_lista_productos:
            escribir_archivo.writerow([
                info['url'], 
                info['categoria_producto'], 
                info['tipo_producto'], 
                info['tipo_producto_especifico'], 
                info['id_producto'], 
                info['titulo_producto'], 
                info['descuento_producto'], 
                info['cantidad_producto'], 
                info['precio_total'], 
                info['material']
            ])
    
    print(f"Datos guardados en {ruta_archivo_csv}")

# Ejecutar el script principal
if __name__ == "__main__":
    agregar_datos_csv('./productos/')
