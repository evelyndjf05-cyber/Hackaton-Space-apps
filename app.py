from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
import uvicorn
from lut_utils import parse_lut_xml, apply_lut_to_array, compute_indices
from model import load_or_train_model, predict_changes
import os

app = FastAPI(title="NASA LUT RCM API")

app.mount("/static", StaticFiles(directory="../frontend"), name="static")

@app.post('/process')
async def process(lut: UploadFile = File(...), data: UploadFile = File(...)):
    lut_xml = await lut.read()
    lut_table = parse_lut_xml(lut_xml)
    content = await data.read()
    from io import BytesIO
    bio = BytesIO(content)
    npz = np.load(bio)
    arr = npz['arr']
    calibrated = apply_lut_to_array(arr, lut_table)
    indices = compute_indices(calibrated)
    resp = {
        'shape': calibrated.shape,
        'ndvi_mean': float(np.nanmean(indices['NDVI']))
    }
    return JSONResponse(resp)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
