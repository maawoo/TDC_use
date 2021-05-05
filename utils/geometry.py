import geojson

def geojson_x_y(geojson_path):
    """Reads a GeoJSON file and returns a list with an (x_min, x_max) and (y_min, y_max) tuple.
    These can then easily be used with dc.load()"""
        
    with open(geojson_path) as f:
        geo = geojson.load(f)
        
    coord_list = list(geojson.utils.coords(geo))
    
    ## Adapted from https://gis.stackexchange.com/a/313023
    box = []
    for i in (0,1):
        res = sorted(coord_list, key=lambda x:x[i])
        box.append((res[0][i],res[-1][i]))
        
    return box
