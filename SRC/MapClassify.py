import mapclassify
import geopandas as gpd
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re

class MapClassify:
    """
    A utility class for classifying geospatial data using various mapclassify methods.

    This class reads a geospatial file, classifies a specified numeric column
    using a chosen mapclassify method, and prepares a GeoDataFrame with
    classification results, including class ranges and assigned colors.
    """

    def __init__(self, file, method, column, colors, K_classes=None, bins=None):
        """
        Initializes the MapClassify object.

        Args:
            file (str): The path to the geospatial file (e.g., shapefile, GeoJSON).
            method (str): The mapclassify method to use for classification.
                Must be one of the available mapclassify.CLASSIFIERS.
            column (str): The name of the numeric column to be classified.
            colors (list): A list of colors to assign to each class.
            K_classes (int, optional): The number of classes for classification methods that
                require it (e.g., EqualInterval, FisherJenks). Defaults to None.
            bins (list, optional): A list of custom bin edges for specific methods
                (e.g., UserDefined, Percentiles). Defaults to None.
        
        Raises:
            ValueError: If an unknown classification method is provided.
        """
        self.file = file
        self.K_classes = K_classes
        self.method = method
        self.column = column
        self.gdf = None
        self.bins = bins
        self.colors = colors
        self._read_file()
        if self.method not in mapclassify.CLASSIFIERS:
            raise ValueError('unknown method, please provide a valid mapclassify method.')

    def _read_file(self):
        """
        Reads the geospatial file into a GeoDataFrame.

        This is an internal method and should not be called directly.
        """
        self.gdf = gpd.read_file(self.file)

    def _classify(self):
        """
        Classifies the specified column using the selected mapclassify method.

        This is an internal method that handles the logic of calling the
        correct mapclassify classifier with the appropriate parameters.

        Raises:
            ValueError: If the specified column is not numeric.
            ValueError: If an error occurs during the classification process.

        Returns:
            mapclassify.MapClassifier: The classification object.
        """
        if not is_numeric_dtype(self.gdf[self.column]):
            raise ValueError('column must be numeric')
        try:
            param_map = {
                'HeadTailBreaks': {},
                'Percentiles': {'pct': self.bins},
                'UserDefined': {'bins': self.bins},
            }

            classifier_class = getattr(mapclassify, self.method)
            params = {'y': self.gdf[self.column]}
            if self.method in param_map:
                params.update(param_map[self.method])
            else:
                params['k'] = self.K_classes
            return classifier_class(**params)
        except Exception as e:
            raise ValueError(f'error classifying data: {e}')

    def prepare_data(self):
        """
        Prepares a GeoDataFrame with the classification results and colors.

        This method performs the classification, extracts the class ranges,
        and merges the classification results and colors back into a
        new GeoDataFrame.

        Raises:
            ValueError: If an error occurs during data preparation.

        Returns:
            gpd.GeoDataFrame: A GeoDataFrame containing the 'geometry',
                              'class', 'count', 'range', and 'color' columns.
        """
        try:
            classify = self._classify()
            filterd_gdf = self.gdf[['geometry']]
            ranges = []
            for x in classify.get_legend_classes():
                low, high = map(float, re.findall(r"[-+]?\d*\.\d+|\d+", x))
                ranges.append([low, high])
            
            df_classes = pd.DataFrame({
                "class": range(len(classify.counts)),
                "count": classify.counts,
                "range": ranges,
                "color": [self.colors[x] for x in range(len(ranges))]
            })
            
            filterd_gdf = filterd_gdf.merge(df_classes, left_index=True, right_on="class")
            return filterd_gdf
        except Exception as e:
            raise ValueError(f'cannot prepare data: {e}')

