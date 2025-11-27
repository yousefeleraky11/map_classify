# MapClassify

## Overview

    Performs map classification and returns the classified data as GeoJSON.
    This endpoint takes classification parameters, fetches the data from GeoServer,
    applies the chosen mapclassify method, and returns a GeoJSON object with the
    classification results, including the assigned colors for each feature.

**BaseURL:** `http://127.0.0.1:8000/classify`

---

## Endpoints

### 1 get_columns

**Method** `GET`
**URL** `/get_columns`

#### Request Body Parameters

|      Name        | Type   | Required |          Description                         |
|------------------|--------|----------|----------------------------------------------|
| layername        | str    | yes      | layername in geoserver                       |
| workspapce       | str    | yes      | workspace name in geoserver                  |



### Example Request

```json
{
    "layername":"map_classify",
"workspace":"cite"
}
```



### 2 classify

**Method:**  `POST`
**URL:** `/classify`

#### Request body parameters

|      Name  | Type   | Required |          Description                         |
|------------|--------|----------|----------------------------------------------|
| column     | str    | yes      | the column name that you want to classify    |
| layername  | str    | yes      | layername in geoserver                       |
| K_classes  | int    | no       | number of classes for classification         |
| workspapce | str    | yes      | workspace name in geoserver                  |
| method     | str    | yes      | the method type for map classification       |
| color      | list   | yes      | the color scheme                             |
| bins       | list   | no       | the class ranges for classification          |


#### Example Request 

POST `http://127.0.0.1:8000/classify`

request body

```json
{"layername":"map_classify",
"workspace":"cite",
 "column":"SID79",
"method":"Quantiles",
 "K_classes":3 ,
 "color":[
    
    "#b3a9a9ff",
    "#3c19daff",
    "#eb0505ff"
 ]
}
```