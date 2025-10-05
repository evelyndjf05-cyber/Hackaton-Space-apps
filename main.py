from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import uvicorn
from lut_processor import parse_lut_xml, apply_lut_to_array, compute_indices
from floracion_analyzer import analizar_floracion_cafe, generar_recomendaciones, detectar_patrones_temporales
import os
from datetime import datetime
import json

app = FastAPI(title="FLORABIU API", description="Sistema de monitoreo de floración en café")

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/process')
async def process(lut: UploadFile = File(...), data: UploadFile = File(...)):
    try:
        print("🌺 Procesando datos de floración...")
        
        # 1. LEER Y PROCESAR LUT
        lut_xml = await lut.read()
        lut_table = parse_lut_xml(lut_xml)
        print(f"✅ LUT cargada: {len(lut_table['gains'])} valores")
        
        # 2. LEER DATOS SATELITALES
        content = await data.read()
        from io import BytesIO
        bio = BytesIO(content)
        npz = np.load(bio)
        arr = npz['arr']
        print(f"📊 Datos cargados: {arr.shape}")
        
        # 3. APLICAR CALIBRACIÓN LUT
        calibrated = apply_lut_to_array(arr, lut_table)
        print("🎯 Calibración LUT aplicada")
        
        # 4. CALCULAR ÍNDICES DE VEGETACIÓN
        indices = compute_indices(calibrated)
        ndvi_array = indices['NDVI']
        print(f"📈 NDVI calculado: {ndvi_array.shape}")
        
        # 5. ANALIZAR FLORACIÓN ESPECÍFICA
        analisis_floracion = analizar_floracion_cafe(ndvi_array)
        
        # 6. GENERAR RECOMENDACIONES
        recomendaciones = generar_recomendaciones(analisis_floracion)
        
        # 7. DETECTAR PATRONES TEMPORALES (si hay datos históricos)
        if 'fechas' in npz:
            patrones = detectar_patrones_temporales(ndvi_array, npz['fechas'])
        else:
            patrones = {"mensaje": "No hay datos temporales para análisis histórico"}
        
        # 8. PREPARAR RESPUESTA COMPLETA
        resp = {
            'proyecto': 'FLORABIU - Monitoreo de Floración en Café',
            'fecha_procesamiento': datetime.now().isoformat(),
            'metadatos_imagen': {
                'dimensiones': calibrated.shape,
                'tipo_lut': 'LUTSIGMA',
                'pixeles_totales': calibrated.shape[0] * calibrated.shape[1]
            },
            'estadisticas_ndvi': {
                'promedio': float(np.nanmean(ndvi_array)),
                'maximo': float(np.nanmax(ndvi_array)),
                'minimo': float(np.nanmin(ndvi_array)),
                'desviacion_std': float(np.nanstd(ndvi_array)),
                'pixeles_validos': int(np.sum(~np.isnan(ndvi_array)))
            },
            'analisis_floracion': analisis_floracion,
            'recomendaciones': recomendaciones,
            'patrones_temporales': patrones,
            'alertas': generar_alertas(analisis_floracion)
        }
        
        print("✅ Análisis completado exitosamente")
        return JSONResponse(resp)
        
    except Exception as e:
        print(f"❌ Error en procesamiento: {str(e)}")
        return JSONResponse(
            {'error': f'Error en procesamiento: {str(e)}'}, 
            status_code=500
        )

def generar_alertas(analisis):
    """Genera alertas basadas en el análisis de floración"""
    alertas = []
    
    if analisis['floracion_detectada']:
        if analisis['intensidad'] > 0.8:
            alertas.append({
                'tipo': 'floracion_intensa',
                'nivel': 'alto',
                'mensaje': 'Floración intensa detectada - preparar cosecha'
            })
        
        if analisis['porcentaje_area'] < 30:
            alertas.append({
                'tipo': 'floracion_parcheada', 
                'nivel': 'medio',
                'mensaje': 'Floración irregular detectada - revisar riego'
            })
    
    if analisis['intensidad'] < 0.4:
        alertas.append({
            'tipo': 'baja_actividad',
            'nivel': 'bajo',
            'mensaje': 'Baja actividad vegetativa - verificar condiciones'
        })
    
    return alertas

@app.get('/')
async def root():
    return {"message": "FLORABIU API - Sistema de monitoreo de floración"}

if _name_ == '_main_':
    uvicorn.run(app, host='0.0.0.0', port=8000, reload=True)