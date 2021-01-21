from fastapi import FastAPI, File, Form, UploadFile
import pandas as pd
import json
import requests
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, Query, Body, Path
from geopy.geocoders import Nominatim, GoogleV3
from fastapi.middleware.cors import CORSMiddleware
import ortools
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def convertBytesToJson(bytes):
    df = pd.read_csv(BytesIO(bytes), sep = ";")
    parsed = convertPandasToJson(df)
    return parsed

def convertPandasToJson(data):
    result = data.to_json(orient="records")
    parsed = json.loads(result)
    return parsed

from functions import *

API_KEY_HERE = "hmSSiaijHF50NAc6cA5Pah1OQdKqzriQyfBIH_oZCdI"
API_KEY_GOOGLE = "AIzaSyD9Gzh3Q5hQtKx9G0T2dLZNW6KfVy_dzEg"
API_KEY_NOMINATIM = "9uinTsTkDhB4bXzuV6VWM5qGLBliACMS"
app = FastAPI()

origins = [
    "http://localhost:3000",
    "localhost:3000",
    "https://angel-rc.github.io"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def home():
    a=["Ayuntamiento, Cuenca"]
    df = pd.DataFrame(a, columns = ["DIRECCION"])
    df = geolocalization(df, API_KEY_NOMINATIM, API_KEY_GOOGLE)
    js = convertPandasToJson(df)
    return js



@app.post("/upload_file_fleet/")
async def upload_file_fleet(file: UploadFile = File(...)):

    # Create fleet_js
    contents = await file.read()
    fleet_df = pd.read_csv(BytesIO(contents), sep=";")
    fleet_js = convertPandasToJson(fleet_df)

    # Create depot_js
    depot_set = set(fleet_df['ORIGEN'].tolist() + fleet_df['FINAL'].tolist())
    depot_df = pd.DataFrame(depot_set, columns = ["DIRECCION"])
    depot_df["TIPO"] = "DEPOSITO"

    depot_df = geolocalization(depot_df, API_KEY_NOMINATIM, API_KEY_GOOGLE)
    depot_js = convertPandasToJson(depot_df)

    return {"depositos": depot_js, "fleet": fleet_js}


@app.post("/upload_file_locations/")
async def upload_file_locations(file: UploadFile = File(...)):

    contents = await file.read()
    nodes_df = pd.read_csv(BytesIO(contents), sep=";")
    nodes_df["TIPO"] = "DESTINO"

    nodes_df = geolocalization(nodes_df, API_KEY_NOMINATIM, API_KEY_GOOGLE)

    nodes_js = convertPandasToJson(nodes_df)

    return nodes_js


@app.put("/create_matrix/")
def HEREAPI_matrix(API_KEY : str ="hmSSiaijHF50NAc6cA5Pah1OQdKqzriQyfBIH_oZCdI",
                   nodes_js = Body(...),
                   mode: str="fastest;car",
                   summary: str="traveltime,distance"):
    graph = {}
    graph["distance_matrix"] = []
    graph["cost_matrix"] = []
    graph["time_matrix"] = []

    URL = "https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json"
    data = pd.DataFrame(nodes_js)
    for origin in data["LOCALIZACION"]:
        params = HEREAPI_create_params(API_KEY, origin, mode, data["LOCALIZACION"], summary)
        response = requests.get(url=URL, params=params)
        matrix_row = HEREAPI_matrix_row(response)

        graph["distance_matrix"].append(matrix_row["distance"])
        graph["cost_matrix"].append(matrix_row["costfactor"])
        graph["time_matrix"].append(matrix_row["traveltime"])

    return (graph)






