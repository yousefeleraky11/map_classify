"""
Module for geoserver rest setup and handling files.
"""
import os
import zipfile
from typing import Optional
from dotenv import load_dotenv
import requests


load_dotenv()

class Geoserver:
    """A class for handling GeoServer REST API processes.

    This class provides methods for interacting with GeoServer, including
    retrieving layer information and uploading raster and vector data.
    """
    def __init__(self):
        """Initializes the Geoserver client.

        The constructor loads credentials and the GeoServer URL from environment
        variables for authentication and connectivity.
        """
        self.username = os.getenv('GEOSERVER_NAME')
        self.password = os.getenv('GEOSERVER_PASSWORD')
        self.geoserver_url = os.getenv('GEOSERVER_URL')
    def get_vector_layer(self, workspace, layername):
        """Retrieves the WFS URL for a vector layer.

        :param workspace: The name of the GeoServer workspace containing the layer.
        :type workspace: str
        :param layername: The name of the vector layer.
        :type layername: str
        :returns: The WFS URL for the specified layer, formatted as JSON.
        :rtype: str
        """
        url = (f"{self.geoserver_url}/{workspace}/ows?service=WFS&version=1.0.0&request=GetFeature"
               f"&typeName={workspace}:{layername}&outputFormat=application/json")
        return url

    def get_layer(self, workspace, layername):
        """Retrieves the WCS URL for a raster layer.

        :param workspace: The name of the GeoServer workspace containing the layer.
        :type workspace: str
        :param layername: The name of the raster layer.
        :type layername: str
        :returns: The WCS URL for the layer, which can be used by GDAL.
        :rtype: str
        """
        url = (
            f"WCS:{self.geoserver_url}/wcs?service=WCS&version=1.0.0&request"
            f"=GetCoverage&coverage={workspace}:{layername}&format=GeoTIFF"
        )
        return url

    def create_coveragestore(
        self,
        path: str,
        workspace: Optional[str] = None,
        layer_name: Optional[str] = None,
        file_type: str = "GeoTIFF",
        content_type: str = "image/tiff",
        method: str = "file",
    ) -> tuple[int, str]:
        """Creates the coverage store and uploads data to the GeoServer.

        :param path: The path to the file to be uploaded.
        :type path: str
        :param workspace: The name of the workspace. Defaults to "default".
        :type workspace: Optional[str]
        :param layer_name: The name for the new coverage store. If not
            provided, the name is parsed from the filename.
        :type layer_name: Optional[str]
        :param file_type: The type of the file. Defaults to "GeoTIFF".
        :type file_type: str
        :param content_type: The content type of the file. Defaults to "image/tiff".
        :type content_type: str
        :param method: The upload method. Can be 'file', 'url', 'external', or
            'remote'. Defaults to "file".
        :type method: str
        :raises ValueError: If the file path is not provided, or if the GeoServer
            request fails.
        :returns: A tuple containing the HTTP status code and the layer name.
        :rtype: tuple[int, str]
        """
        if path is None:
            raise ValueError("You must provide the full path to the raster")

        if workspace is None:
            workspace = "default"

        if layer_name is None:
            layer_name = os.path.basename(path)
            f = layer_name.split(".")
            if len(f) > 0:
                layer_name = f[0]

        file_type = file_type.lower()
        url=(f"{self.geoserver_url}/rest/workspaces/{workspace}/"
             f"coveragestores/{layer_name}/{method}.{file_type}?coverageName={layer_name}")
        if method == "file":
            headers = {"content-type": content_type, "Accept": "application/json"}
            with open(path, "rb") as f:
                r = requests.put(url=url,
                                 headers=headers, data=f,
                                 auth=(self.username, self.password),
                                 timeout=30)
        else:
            headers = {"content-type": "text/plain", "Accept": "application/json"}
            r = requests.put(url=url,
                             headers=headers,
                             data=path,
                             auth=(self.username, self.password),timeout=30)

        if r.status_code == 201:
            return r.status_code, layer_name
        else:
            raise ValueError(r.status_code, r.content)
    def upload_raster_data(self, workspace, coveragestore, layername, file_path):
        """Uploads a raster file (GeoTIFF) to GeoServer using the REST API.
    
        :param workspace: The name of the workspace on GeoServer.
        :type workspace: str
        :param coveragestore: The name of the coverage store to create.
        :type coveragestore: str
        :param layername: The name of the raster layer to publish.
        :type layername: str
        :param file_path: The local file path of the GeoTIFF to upload.
        :type file_path: str
        :raises TimeoutError: If there is an error during the upload process.
        :returns: The HTTP status code of the successful upload.
        :rtype: int
        """
        url = (f"{self.geoserver_url}/rest/workspaces/{workspace}"
               f"/coveragestores/{coveragestore}/file.geotiff")
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
                    params=params,timeout=30
                )
                r.raise_for_status()
                return r.status_code
        except requests.exceptions.RequestException as e:
            raise ValueError(f'Error uploading the data: {e}') from e
    def create_zipfilepath(self, tmpdir) :
        """Creates the file path for a temporary zip file.

        :param tmpdir: The path of the temporary folder.
        :type tmpdir: str
        :returns: The path of the zip file to be created.
        :rtype: str
        """
        zip_file_path = os.path.join(tmpdir, "output.zip")
        return zip_file_path
    def zip_files(self, zip_file_path, tempdir):
        """Zips shapefiles from a temporary directory into a single zip file.
      
        The process includes standard shapefile components: .shp, .shx, .dbf, .prj, and .cpg.

        :param zip_file_path: The full path for the output zip file.
        :type zip_file_path: str
        :param tempdir: The path of the temporary directory containing the shapefiles.
        :type tempdir: str
        :raises ValueError: If an error occurs during the zipping process.
        """
        try:
            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, _, files in os.walk(tempdir):
                    for file in files:
                        if file.split('.')[-1] in ['shp', 'shx', 'dbf', 'prj', 'cpg']:
                            file_path = os.path.join(root, file)
                            zf.write(file_path, os.path.basename(file_path))
        except Exception as e:
            raise TimeoutError(f'cannot zip the files: {e}') from e
    def upload_shapefile(self, workspace, datastore, zip_path):
        """Uploads a zipped shapefile to GeoServer.
       
        :param workspace: The name of the GeoServer workspace.
        :type workspace: str
        :param datastore: The name of the datastore that will contain the shapefile.
        :type datastore: str
        :param zip_path: The path of the zip file to upload.
        :type zip_path: str
        :raises ValueError: If an error occurs during the upload process.
        :returns: The HTTP response from the GeoServer REST API.
        :rtype: requests.Response
        """
        try:
            url = (f"{self.geoserver_url}/rest/workspaces/"
                   f"{workspace}/datastores/{datastore}/file.shp")
            with open(zip_path, "rb") as f:
                headers = {"Content-type": "application/zip"}
                response = requests.put(
                    url,
                    data=f,
                    auth=(self.username, self.password),
                    headers=headers,
                    params={"update": "overwrite"},
                    timeout=15.0
                )
            return response
        except Exception as e:
            raise ValueError(f'cannot upload the shapefile: {e}') from e
