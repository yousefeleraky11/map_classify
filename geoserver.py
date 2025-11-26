import requests
from dotenv import load_dotenv
import os
import zipfile
from typing import Optional


load_dotenv(dotenv_path='.env.txt')   
class Geoserver:
   
    def __init__(self):
        """ _summary_
        its a class for geoserver rest proccess
        """
        
        self.username = os.getenv('GEOSERVER_NAME')
        self.password = os.getenv('GEOSERVER_PASSWORD')
        self.geoserver_url = os.getenv('GEOSERVER_URL')
       

    def get_vector_layer(self,workspace,layername):
        url=f"{self.geoserver_url}/{workspace}/ows?service=WFS&version=1.0.0&request=GetFeature&typeName={workspace}:{layername}&outputFormat=application/json"
        return url
    def get_layer(self, workspace, layername):
        """_summary_

        Args:
            workspace (_str): workspace name on geoserver that contain the layer
            layername (_str): the name of the targeted layer

        Returns:
            _type_: wcs url that work on gdal
        """
        url = ( f"WCS:{self.geoserver_url}/wcs?service=WCS&version=1.0.0&request=GetCoverage&coverage={workspace}:{layername}&format=GeoTIFF"
        )
        return url
    def create_coveragestore(
        self,
        path,
        workspace: Optional[str] = None,
        layer_name: Optional[str] = None,
        file_type: str = "GeoTIFF",
        content_type: str = "image/tiff",
        method: str = "file",
    ):
        """
        Creates the coverage store; Data will be uploaded to the server.

        Parameters
        ----------
        path : str
            The path to the file.
        workspace : str, optional
            The name of the workspace.
        layer_name : str, optional
            The name of the coverage store. If not provided, parsed from the file name.
        file_type : str
            The type of the file.
        content_type : str
            The content type of the file.
        method : str
            file | url | external | remote

        Returns
        -------
        dict
            The response from the server.

        Notes
        -----
        the path to the file and file_type indicating it is a geotiff, arcgrid or other raster type
        """
        if path is None:
            raise Exception("You must provide the full path to the raster")

        if workspace is None:
            workspace = "default"

        if layer_name is None:
            layer_name = os.path.basename(path)
            f = layer_name.split(".")
            if len(f) > 0:
                layer_name = f[0]

        file_type = file_type.lower()
        
        
        url = "{0}/rest/workspaces/{1}/coveragestores/{2}/{3}.{4}?coverageName={2}".format(
            self.geoserver_url, workspace, layer_name, method, file_type
            )

        if method == "file":
            headers = {"content-type": content_type, "Accept": "application/json"}
            with open(path, "rb") as f:
              r=requests.put(url=url,headers=headers,data=f,auth=(self.username,self.password) )
        else:
            headers = {"content-type": "text/plain", "Accept": "application/json"}
            r=requests.put(url=url,headers=headers,data=path,auth=(self.username,self.password) )

        if r.status_code == 201:
            return r.status_code,layer_name
        else:
            raise ValueError(r.status_code, r.content)
        
    # def create_coveragestore(self,workspace,coveragestore):
    #   """_summary_  
    #   Args:
    #       workspace (_str): workspace name on geoserver that contain the layer
    #       datastore (str): datastore name that will be created  
    #   Raises:
    #       TimeoutError: error creating data store:(error reason)
    #   """
    #   try:
    #     se=requests.post(
    #         f"{self.geoserver_url}/rest/workspaces/{workspace}/coveragestores",
    #         json={"coverageStore": {
    #             "name": coveragestore,
    #             "type": "GeoTIFF",
    #             "enabled": "True",
    #             "workspace": { "name": workspace }
    #             }},
    #         headers={"Content-type": "application/json"}, 
    #         auth=(self.username,self.password) 
    #     )
    #     return se
    #   except Exception as e:
    #     raise TimeoutError(f'error creating data store:{e}')   
    
            

    
    
    def upload_raster_data(self, workspace, coveragestore, layername, file_path):    
        """
        Uploads a raster file (GeoTIFF) to GeoServer using the REST API.
    
        Args:
            workspace (str): The name of the workspace on GeoServer.
            coveragestore (str): The name of the coverage store to create.
            layername (str): The name of the raster layer to publish.
            file_path (str): The local file path of the GeoTIFF to upload.
    
        Raises:
            TimeoutError: If there's an error during the upload process.
        """
        # Use the /external.geotiff endpoint for file uploads
        url = f"{self.geoserver_url}/rest/workspaces/{workspace}/coveragestores/{coveragestore}/file.geotiff"
        
        # Define parameters for configuring and naming the layer
        params = {
            "configure": "all",
            "coverageName": layername
        }
    
        try:
            with open(file_path, "rb") as f:
                r = requests.put(
                    url,
                    data=f,
                    headers={"Content-type": "image/tiff"},
                    auth=(self.username, self.password),
                    params=params
                )
                r.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
                return r.status_code
                
        except requests.exceptions.RequestException as e:
            raise TimeoutError(f'Error uploading the data: {e}')
    def set_crs(self, workspace, coveragestore, layername, epsg_code=None):
      if epsg_code is None:
          epsg_code = self.get_layer_crs(workspace, coveragestore, layername)
  
      url = f"{self.geoserver_url}/rest/workspaces/{workspace}/coveragestores/{coveragestore}/coverages/{layername}.xml"
      data = f"<coverage><srs>{epsg_code}</srs></coverage>"
      
      r = requests.put(
          url,
          data=data,
          headers={"Content-type": "text/xml"},
          auth=(self.username, self.password)
      )
      return r.status_code

    def create_zipfilepath(self,tmpdir):
        """_summary_

        Args:
            tmpdir (str): the path of the temp folder

        Returns:
            zipfilepath: the path that contain files needed to be zipping 
        """
        zip_file_path = os.path.join(tmpdir, "output.zip")      
        return zip_file_path
    
    
    def zip_files(self,zip_file_path,tempdir):
      """this  method for zipping shapefiles  
      Args:
          zip_file_path (str): the path of dirctory that you want to zip
          tempdir (str): the path of temp dirctory  
      Raises:
          ValueError: cannot zip the files:(the reason of error)
      """
      try:
        with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(tempdir):
                    for file in files:
                        if file.split('.')[-1] in ['shp', 'shx', 'dbf', 'prj', 'cpg']:
                            file_path = os.path.join(root, file)
                            zf.write(file_path, os.path.basename(file_path))  
      except Exception as e:
          raise ValueError(f' cannot zip the files:{e}')                    
                              
    def upload_shapefile(self, workspace, datastore, zip_path):
       
      """
      this  method for uploading zip shapefile to geoserver  
      Args:
          zip_path (str): the path of zipfile that you want to upload
          workspace (_str): workspace name on geoserver that contain the layer  
          datastore (str): the data store that will contain the shapefile 
      Raises:
          ValueError: cannot upload the file: (the reason of error)
      
      """  
      try:
            
       url = f"{self.geoserver_url}/rest/workspaces/{workspace}/datastores/{datastore}/file.shp"
       with open(zip_path, "rb") as f:
           headers = {"Content-type": "application/zip"}
           response = requests.put(
               url,
               data=f,
               auth=(self.username,self.password) ,
               headers=headers,
               params={"update":"overwrite"}
           )
       return response
      except Exception as e:
          raise ValueError(f'cannot upload the file:{e}')

     
                