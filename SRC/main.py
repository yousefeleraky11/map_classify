from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional,List
from MapClassify import MapClassify
from geoserver import Geoserver
import json
import geopandas as gpd

app=FastAPI()


class Inputs(BaseModel):
    layername:str
    workspace:str
    column:Optional[str]=None
    K_classes:Optional[int]=None
    method:Optional[str]=None
    color:Optional[List]=None
    bins:Optional[List]=None

@app.get('/get_columns')
def get_columns(inputs:Inputs):
      """
    Fetches the column names of a vector layer from GeoServer.

    This endpoint retrieves the specified layer from GeoServer and returns
    a list of its column names, which can be used to inform the classification.

    Args:
        inputs (Inputs): The input model containing layername and workspace.

    Returns:
        List[str]: A list of column names for the specified layer.
    """
      geoserver=Geoserver()
      url=geoserver.get_vector_layer(workspace=inputs.workspace,layername=inputs.layername)
      gdf=gpd.read_file(url)
      columns=gdf.columns.to_list()
      return columns
@app.post('/classify')
def classify(inputs:Inputs):
    """
    Performs map classification and returns the classified data as GeoJSON.

    This endpoint takes classification parameters, fetches the data from GeoServer,
    applies the chosen mapclassify method, and returns a GeoJSON object with the
    classification results, including the assigned colors for each feature.

    Args:
        inputs (Inputs): The input model with all classification parameters.

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
      map_classify=MapClassify(file=url,colors=inputs.color,K_classes=inputs.K_classes,bins=inputs.bins,method=inputs.method,column=inputs.column)
      gdf=map_classify.prepare_data()
      gdf_json=json.loads(gdf.to_json())
      
      return gdf_json
    except Exception as e:
       return {"error":str(e)}