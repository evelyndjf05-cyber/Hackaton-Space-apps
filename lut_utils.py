import xml.etree.ElementTree as ET
import numpy as np

def parse_lut_xml(xml_bytes):
    root = ET.fromstring(xml_bytes)
    lut = {}
    for table in root.findall('.//Table'):
        name = table.get('name') or 'table'
        rows = []
        for row in table.findall('.//Row'):
            vals = [float(x.text) for x in row.findall('.//V')]
            rows.append(vals)
        lut[name] = np.array(rows)
    return lut

def apply_lut_to_array(arr, lut):
    a = np.array(arr)
    if a.ndim == 3:
        T = 1
        a = a[None, ...]
    else:
        T = a.shape[0]
    gains = lut.get('gain') if 'gain' in lut else None
    offsets = lut.get('offset') if 'offset' in lut else None
    calibrated = a.astype('float32')
    if gains is not None:
        calibrated = calibrated * gains.reshape((1,) + gains.shape)
    if offsets is not None:
        calibrated = calibrated + offsets.reshape((1,) + offsets.shape)
    return calibrated.squeeze()

def compute_indices(calibrated):
    a = np.array(calibrated)
    if a.ndim == 3:
        a = a[None, ...]
    R = a[..., 2]
    NIR = a[..., 3]
    ndvi = (NIR - R) / (NIR + R + 1e-8)
    B = a[..., 1]
    G = 2.5
    C1 = 6.0
    C2 = 7.5
    L = 1.0
    evi = G * (NIR - R) / (NIR + C1 * R - C2 * B + L + 1e-8)
    return {'NDVI': ndvi, 'EVI': evi}
