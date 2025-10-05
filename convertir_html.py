import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import json
import re
import os

print(\"🔄 CONVERSOR HTML a NPZ para FLORABIU\")
print(\"=\" * 50)

def convertir_html_a_npz(archivo_html, salida_dir='datos_prueba'):
    '''Convierte datos de HTML a .npz para FLORABIU'''
    
    print(f\"📖 Leyendo: {archivo_html}\")
    
    # Crear directorio de salida
    os.makedirs(salida_dir, exist_ok=True)
    
    # Leer HTML
    with open(archivo_html, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    datasets_creados = 0
    
    # 1. BUSCAR TABLAS
    print(\"\\n🔍 Buscando tablas HTML...\")
    tablas = soup.find_all('table')
    
    for i, tabla in enumerate(tablas):
        try:
            # Leer tabla con pandas
            dfs = pd.read_html(str(tabla))
            for j, df in enumerate(dfs):
                if not df.empty and df.shape[0] > 1 and df.shape[1] > 1:
                    # Convertir a números
                    array_datos = df.select_dtypes(include=[np.number]).to_numpy()
                    
                    if array_datos.size > 0:
                        nombre_archivo = f'{salida_dir}/datos_satelitales_tabla_{i+1}.npz'
                        np.savez(nombre_archivo,
                                datos_satelitales=array_datos,
                                bandas=['banda_1', 'banda_2', 'banda_3', 'banda_4'],
                                forma_original=array_datos.shape,
                                tipo='tabla_html')
                        print(f\"   ✅ Tabla {i+1}: {array_datos.shape} -> {nombre_archivo}\")
                        datasets_creados += 1
        except Exception as e:
            print(f\"   ⚠ Tabla {i+1}: {e}\")
    
    # 2. BUSCAR DATOS NUMÉRICOS
    print(\"\\n🔍 Extrayendo números...\")
    texto_completo = soup.get_text()
    numeros = re.findall(r'[-+]?\d*\.\d+|\d+', texto_completo)
    
    if len(numeros) >= 100:  # Suficientes para imagen
        try:
            array_numeros = np.array([float(x) for x in numeros], dtype=np.float32)
            
            # Crear array 2D (50x50 píxeles, 4 bandas)
            total_necesario = 50 * 50 * 4  # 10,000 valores
            if len(array_numeros) >= total_necesario:
                datos_imagen = array_numeros[:total_necesario].reshape((50, 50, 4))
                
                np.savez(f'{salida_dir}/datos_satelitales_numeros.npz',
                        datos_satelitales=datos_imagen,
                        bandas=['azul', 'verde', 'rojo', 'infrarrojo'],
                        forma='50x50x4',
                        tipo='numeros_extraidos')
                print(f\"   ✅ Datos numéricos: {datos_imagen.shape}\")
                datasets_creados += 1
        except Exception as e:
            print(f\"   ⚠ Error números: {e}\")
    
    # 3. CREAR DATOS DE PRUEBA SI NO HAY DATOS VÁLIDOS
    if datasets_creados == 0:
        print(\"\\n📝 Creando datos de prueba...\")
        datos_prueba = np.random.randint(0, 10000, (50, 50, 4), dtype=np.uint16)
        
        np.savez(f'{salida_dir}/datos_satelitales_prueba.npz',
                datos_satelitales=datos_prueba,
                bandas=['azul', 'verde', 'rojo', 'infrarrojo'],
                forma='50x50x4',
                tipo='datos_prueba')
        print(f\"   ✅ Datos de prueba: {datos_prueba.shape}\")
        datasets_creados += 1
    
    print(f\"\\n🎉 CONVERSIÓN TERMINADA!\")
    print(f\"📊 Archivos .npz creados: {datasets_creados}\")
    print(f\"📁 Carpeta: {salida_dir}\")
    
    # Mostrar archivos creados
    print(\"\\n📋 Archivos .npz disponibles:\")
    for archivo in os.listdir(salida_dir):
        if archivo.endswith('.npz'):
            print(f\"   📄 {archivo}\")
    
    return datasets_creados

# EJECUCIÓN PRINCIPAL
if _name_ == \"_main_\":
    # Buscar archivos HTML en la carpeta actual
    archivos_html = [f for f in os.listdir('.') if f.endswith('.html')]
    
    if archivos_html:
        print(f\"📁 Archivos HTML encontrados: {archivos_html}\")
        for archivo_html in archivos_html:
            convertir_html_a_npz(archivo_html)
    else:
        print(\"❌ No se encontraron archivos HTML en la carpeta actual.\")
        print(\"💡 Copia tu archivo HTML a: florabiu_project/\")
        print(\"💡 O ejecuta: python convertir_html.py tu_archivo.html\")
