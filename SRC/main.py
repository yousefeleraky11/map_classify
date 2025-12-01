"""
Module for FastAPI setup and handling geospatial classification and GeoServer operations.
"""
import json
from typing import Optional,List
from fastapi import FastAPI
from pydantic import BaseModel
import geopandas as gpd
from MapClassify import Mapclassify
from geoserver import Geoserver

app=FastAPI()


class Inputs(BaseModel):
    """
    Input schema for classification requests.

    Attributes:
        layername (str): Name of the GeoServer layer to classify.
        workspace (str): Workspace where the layer is hosted.
        column (str): Attribute column used for classification.
        K_classes (Optional[int]): Number of classes (used for methods that require K).
        method (str): Classification method (e.g., 'quantile', 'natural_breaks', etc.).
        color (List): List of colors to apply to the classified output.
        bins (Optional[List]): Custom bin ranges for manual classification.
    """
    layername:str
    workspace:str
    column:str
    K_classes:Optional[int]=None
    method:str
    color:List
    bins:Optional[List]=None

@app.get('/get_columns')
def get_columns(workspace:str,layername:str):
    """
    Fetches the column names of a vector layer from GeoServer.

    This endpoint retrieves the specified layer from GeoServer and returns
    a list of its column names, which can be used to inform the classification.

    Args:
        workspace(str):workspace name on geoserver
        layername(str):the layer name on geoserver

    Returns:
        List[str]: A list of column names for the specified layer.
    """
    geoserver=Geoserver()
    url=geoserver.get_vector_layer(workspace=workspace,layername=layername)
    gdf=gpd.read_file(url)
    columns=gdf.columns.to_list()
    return columns
@app.post('/classify')
def classify(inputs:Inputs):
    """
     Performs map classification and returns the classified data as GeoJSON 
     This endpoint takes classification parameters, fetches the data from GeoServer,
     applies the chosen mapclassify method, and returns a GeoJSON object with the
     classification results, including the assigned colors for each feature 
     Args:
         inputs (Inputs): The input model with all classification parameters 
     Returns:
         dict: A GeoJSON object representing the classified data, or a JSON object
               with an 'error' message if an exception occurs.
     """
    try:
        if inputs.method in ['Percentiles','UserDefined'] and len(inputs.color)!= len(inputs.bins):
            raise ValueError('color layers must equal number of classes')
        if inputs.K_classes and len(inputs.color)!= inputs.K_classes:
            raise ValueError('color layers must equal number of classes')
        geoserver=Geoserver()
        url=geoserver.get_vector_layer(workspace=inputs.workspace,layername=inputs.layername)
        map_classify=Mapclassify(file=url,colors=inputs.color,
                                 k_classes=inputs.K_classes,bins=inputs.bins,
                                 method=inputs.method,column=inputs.column)
        gdf=map_classify.prepare_data()
        gdf_json=json.loads(gdf.to_json())
        return gdf_json
    except Exception as e:
        return {"error":str(e)}
if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host='0.0.0.0',port=9091)
      