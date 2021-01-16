from fastapi import FastAPI, File, Form, UploadFile
import pandas as pd
import json
import requests
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Query, Body, Path
from geopy.geocoders import Nominatim, GoogleV3
from fastapi.middleware.cors import CORSMiddleware


def convertBytesToJson(bytes):
    df = pd.read_csv(BytesIO(bytes), sep = ";")
    parsed = convertPandasToJson(df)
    return parsed

def convertPandasToJson(data):
    result = data.to_json(orient="records")
    parsed = json.loads(result)
    return parsed

from functions import *

API_KEY_GOOGLE = "AIzaSyD9Gzh3Q5hQtKx9G0T2dLZNW6KfVy_dzEg"
API_KEY_NOMINATIM = "9uinTsTkDhB4bXzuV6VWM5qGLBliACMS"
app = FastAPI()


@app.get("/")
def home():
    return {"message":"Hello TutLinks.com"}

