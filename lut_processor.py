import numpy as np
import xml.etree.ElementTree as ET
from typing import Dict, Any

def parse_lut_xml(lut_xml: bytes) -> Dict[str, Any]:
    """Parsea archivo LUT XML y extrae parámetros de calibración"""
    try:
        root = ET.fromstring(lut_xml.decode('utf-8'))
        
        lut_data = {
            'pixel_first_value': int(root.find('pixelFirstLutValue').text),
            'step_size': int(root.find('stepSize').text),
            'number_of_values': int(root.find('numberOfValues').text),
            'offset': int(root.find('offset').text),
            'gains': np.array([float(x) for x in root.find('gains').text.split()])
        }
        
        print(f"📋 LUT parseada: {lut_data['number_of_values']} valores, step: {lut_data['step_size']}")
        return lut_data
        
    except Exception as e:
        raise Exception(f"Error parsing LUT XML: {str(e)}")

def apply_lut_to_array(image_array: np.ndarray, lut_table: Dict[str, Any]) -> np.ndarray:
    """Aplica calibración LUT a un array de imagen"""
    try:
        p0 = lut_table['pixel_first_value']
        step = lut_table['step_size']
        gains = lut_table['gains']
        
        # Para step_size = -1 (como en tu ejemplo)
        indices = p0 - image_array
        indices = np.clip(indices, 0, len(gains) - 1)
        
        # Aplicar ganancias
        calibrated_array = image_array * gains[indices.astype(int)]
        
        print(f"🎯 LUT aplicada: {image_array.shape} → {calibrated_array.shape}")
        return calibrated_array
        
    except Exception as e:
        raise Exception(f"Error applying LUT: {str(e)}")

def compute_indices(calibrated_array: np.ndarray) -> Dict[str, np.ndarray]:
    """Calcula índices de vegetación a partir de array calibrado"""
    try:
        # Asumiendo que calibrated_array tiene bandas [rojo, infrarrojo, ...]
        # Ajustar índices según tu estructura de bandas
        red_band = calibrated_array[:, :, 2]   # Banda roja
        nir_band = calibrated_array[:, :, 3]   # Banda infrarrojo
        
        # Calcular NDVI
        with np.errstate(divide='ignore', invalid='ignore'):
            ndvi = (nir_band - red_band) / (nir_band + red_band)
            ndvi = np.nan_to_num(ndvi, nan=-1, posinf=1, neginf=-1)
        
        # Calcular EVI (opcional)
        blue_band = calibrated_array[:, :, 0]  # Banda azul
        evi = 2.5 * (nir_band - red_band) / (nir_band + 6 * red_band - 7.5 * blue_band + 1)
        evi = np.nan_to_num(evi, nan=-1, posinf=1, neginf=-1)
        
        indices = {
            'NDVI': ndvi,
            'EVI': evi
        }
        
        print(f"📊 Índices calculados: NDVI range [{ndvi.min():.3f}, {ndvi.max():.3f}]")
        return indices
        
    except Exception as e:
        raise Exception(f"Error computing indices: {str(e)}")