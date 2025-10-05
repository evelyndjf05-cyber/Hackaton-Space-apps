import numpy as np
import os

print("🚀 CREANDO DATOS .NPZ PARA FLORABIU")
print("=" * 45)

# Crear datos satelitales
forma = (100, 100, 4)
datos_satelitales = np.zeros(forma, dtype=np.uint16)

print("🌿 Generando patrones de floración...")

for i in range(forma[0]):
    for j in range(forma[1]):
        dist_x = abs(i - 50)
        dist_y = abs(j - 50)
        distancia = np.sqrt(dist_x*2 + dist_y*2)
        
        if distancia < 25:
            # Floración INTENSA
            datos_satelitales[i,j,0] = 1800
            datos_satelitales[i,j,1] = 4200  
            datos_satelitales[i,j,2] = 2200
            datos_satelitales[i,j,3] = 7800
            
        elif distancia < 45:
            # Floración MODERADA
            datos_satelitales[i,j,0] = 2200
            datos_satelitales[i,j,1] = 3800
            datos_satelitales[i,j,2] = 3200
            datos_satelitales[i,j,3] = 5800
            
        elif distancia < 65:
            # Vegetación NORMAL
            datos_satelitales[i,j,0] = 2800
            datos_satelitales[i,j,1] = 3500
            datos_satelitales[i,j,2] = 4000
            datos_satelitales[i,j,3] = 4500
            
        else:
            # Suelo
            datos_satelitales[i,j,0] = 3500
            datos_satelitales[i,j,1] = 3200
            datos_satelitales[i,j,2] = 4800
            datos_satelitales[i,j,3] = 3200

# Añadir ruido
ruido = np.random.normal(0, 150, forma).astype(np.int16)
datos_satelitales = np.clip(datos_satelitales + ruido, 0, 16368)

print(f"✅ Datos: {datos_satelitales.shape}")
print(f"📏 Rango: {datos_satelitales.min()} - {datos_satelitales.max()}")

# Guardar
os.makedirs('datos_prueba', exist_ok=True)
archivo_salida = 'datos_prueba/datos_satelitales.npz'

np.savez(archivo_salida,
         arr=datos_satelitales,
         bandas=['azul', 'verde', 'rojo', 'infrarrojo'],
         forma='100x100x4')

print(f"💾 ARCHIVO CREADO: {archivo_salida}")
print("🎉 LISTO!")
