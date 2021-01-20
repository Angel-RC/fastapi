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
    contents = await file.read()
    fleet_json = convertBytesToJson(contents)


    data = {}
    data['distance_matrix'] = [
        [0, 100, 9, 100, 4],
        [9, 0, 2, 1, 1],
        [5, 1, 0, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 1, 0]

    ]

    data['time_matrix'] = [
        [0, 1, 9, 3, 99],
        [9, 0, 2, 99, 99],
        [5, 1, 0, 99, 99],
        [99, 99, 0, 0, 1],
        [1, 99, 99, 99, 0]
    ]

    data['demands'] = [0, 1, 1, 1, 1]
    data['time_windows'] = [
        (0, 230),  # depot
        (7, 120),  # 1
        (3, 11),  # 2
        (7, 120),  # 3
        (5, 120)  # 4

    ]
    data['vehicle_capacities'] = [1, 3]
    data['vehicle_limit_distance'] = [1000, 1000]
    data['vehicle_final_time'] = [995, 910]
    data['num_vehicles'] = 2
    data['depot'] = 0
    data["vehicle_horary"] = [[None, 100], [None, 100]]
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['time_matrix']),
                                           data['num_vehicles'],
                                           data['depot'])
    return {"fleet": fleet_json}


@app.post("/upload_file_locations/")
async def upload_file_locations(file: UploadFile = File(...),
                               API_KEY_GOOGLE: str = API_KEY_GOOGLE,
                               API_KEY_NOMINATIM: str = API_KEY_NOMINATIM
                               ):
    contents = await file.read()
    nodes_df = pd.read_csv(BytesIO(contents), sep=";")


    geolocator_nominatim = Nominatim(user_agent=API_KEY_NOMINATIM)
    geolocator_google = GoogleV3(api_key=API_KEY_GOOGLE)

    nodes_df['LOCALIZACION'] = nodes_df['DESTINO'].apply(lambda DESTINOS: geocode_2_options(geolocator_nominatim, geolocator_google, DESTINOS))


    nodes_js = convertPandasToJson(nodes_df)

    return(nodes_js)


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






