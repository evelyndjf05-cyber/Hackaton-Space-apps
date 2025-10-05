import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any

def analizar_floracion_cafe(ndvi_array: np.ndarray) -> Dict[str, Any]:
    """Analiza patrones específicos de floración en cultivos de café"""
    
    # Umbrales para floración en café (ajustables)
    UMBRAL_FLORACION = 0.65
    UMBRAL_FLORACION_INTENSA = 0.75
    
    # Crear máscaras para diferentes intensidades
    mascara_floracion = ndvi_array > UMBRAL_FLORACION
    mascara_floracion_intensa = ndvi_array > UMBRAL_FLORACION_INTENSA
    
    # Calcular áreas
    area_total = ndvi_array.size
    area_floracion = np.sum(mascara_floracion)
    area_floracion_intensa = np.sum(mascara_floracion_intensa)
    
    # Calcular intensidad promedio en áreas de floración
    if area_floracion > 0:
        intensidad_promedio = float(np.mean(ndvi_array[mascara_floracion]))
    else:
        intensidad_promedio = 0.0
    
    # Determinar estado de floración
    if area_floracion_intensa / area_total > 0.3:
        estado = "floracion_intensa"
    elif area_floracion / area_total > 0.1:
        estado = "floracion_detectada"
    else:
        estado = "sin_floracion"
    
    return {
        'estado': estado,
        'floracion_detectada': area_floracion > 0,
        'intensidad': intensidad_promedio,
        'area_total_pixeles': int(area_total),
        'area_floracion_pixeles': int(area_floracion),
        'area_floracion_intensa_pixeles': int(area_floracion_intensa),
        'porcentaje_area': float(area_floracion / area_total * 100),
        'porcentaje_area_intensa': float(area_floracion_intensa / area_total * 100),
        'confianza_deteccion': min(0.95, intensidad_promedio)  # Confianza basada en intensidad
    }

def generar_recomendaciones(analisis: Dict[str, Any]) -> Dict[str, Any]:
    """Genera recomendaciones basadas en el análisis de floración"""
    
    recomendaciones = {
        'riego': 'mantener',
        'fertilizacion': 'normal',
        'cosecha': 'no_aplicable',
        'monitoreo': 'rutinario',
        'mensaje_principal': ''
    }
    
    estado = analisis['estado']
    intensidad = analisis['intensidad']
    porcentaje = analisis['porcentaje_area']
    
    if estado == "floracion_intensa":
        recomendaciones.update({
            'riego': 'reducir_25porciento',
            'fertilizacion': 'aumentar_fosforo',
            'cosecha': 'preparar_60_dias',
            'monitoreo': 'intensivo',
            'mensaje_principal': 'Floración intensa detectada - preparar cosecha en 2 meses'
        })
    elif estado == "floracion_detectada":
        recomendaciones.update({
            'riego': 'mantener',
            'fertilizacion': 'balanceada', 
            'cosecha': 'preparar_90_dias',
            'monitoreo': 'frecuente',
            'mensaje_principal': 'Floración detectada - mantener condiciones actuales'
        })
    else:
        recomendaciones.update({
            'riego': 'aumentar_15porciento',
            'fertilizacion': 'estimulante_crecimiento',
            'cosecha': 'no_aplicable',
            'monitoreo': 'mejorar_condiciones',
            'mensaje_principal': 'Sin floración detectada - revisar condiciones de cultivo'
        })
    
    return recomendaciones

def detectar_patrones_temporales(ndvi_array: np.ndarray, fechas: list) -> Dict[str, Any]:
    """Detecta patrones temporales en series de NDVI"""
    
    if len(fechas) < 2:
        return {"mensaje": "Insuficientes datos temporales para análisis"}
    
    # Análisis de tendencia simple
    tendencia = "estable"
    if len(ndvi_array.shape) > 2 and ndvi_array.shape[2] == len(fechas):
        # Si tenemos múltiples fechas, calcular tendencia
        promedio_temporal = np.nanmean(ndvi_array, axis=(0, 1))
        if len(promedio_temporal) > 1:
            diferencia = promedio_temporal[-1] - promedio_temporal[0]
            if diferencia > 0.1:
                tendencia = "en_aumento"
            elif diferencia < -0.1:
                tendencia = "en_declive"
    
    # Estimación de pico de floración (simplificado)
    fecha_actual = datetime.now()
    if tendencia == "en_aumento":
        pico_estimado = fecha_actual + timedelta(days=30)
    else:
        pico_estimado = fecha_actual + timedelta(days=60)
    
    return {
        'tendencia': tendencia,
        'pico_floracion_estimado': pico_estimado.strftime('%Y-%m-%d'),
        'dias_hasta_pico': (pico_estimado - fecha_actual).days,
        'comentario': 'Análisis basado en tendencia NDVI actual'
    }