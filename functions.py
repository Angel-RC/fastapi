
def geocode_2_options(geolocator_1, geolocator_2, address):
    """

    :param geolocator_1: Option 1 of geolocator
    :param geolocator_2: Option 2 of geolocator
    :param address: String what you wantgeocode
    :return: geocoded address
    """
    try:
        location = geolocator_1.geocode(address)
        if location == None:
            location = geolocator_2.geocode(address)
    except:
        try:
            location = geolocator_2.geocode(address)
        except:
            return None

    return [location.latitude,location.longitude]

def HEREAPI_create_params(API_KEY, origin, mode, destination_list, summary):
    params = {"apiKey": API_KEY}
    params["start0"] = str(origin[0]) + "," + str(origin[1])
    params["metricSystem"] = "imperial"
    params["mode"] = mode
    params["summaryAttributes"] = summary
    for index in range(len(destination_list)):
        ds = str(destination_list[index][0]) + "," + str(destination_list[index][1])
        params["destination" + str(index)] = ds
    return(params)

def HEREAPI_matrix_row(response):
    distance = []
    traveltime = []
    costfactor = []
    for route_summary in response.json()["response"]["matrixEntry"]:
        distance = distance + [route_summary["summary"]["distance"]]
        traveltime = traveltime + [route_summary["summary"]["travelTime"]]
        costfactor = costfactor + [route_summary["summary"]["costFactor"]]

    return{"distance": distance, "costfactor": costfactor, "traveltime": traveltime}

#a=HEREAPI_matrix(API_KEY, destination_list=[[42.84237923231346, -1.639314631197623],[41.38661824682026, 2.201626982814753]], mode="fastest;car")