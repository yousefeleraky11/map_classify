# Map Classiffication

## Overview

    Performs map classification and returns the classified data as GeoJSON
    This tool takes classification parameters, fetches the data from GeoServer,
    applies the chosen mapclassify method, and returns a GeoJSON object with the
    classification results, including the assigned colors for each feature.

## Structure

```plaintext


| 
├──DEP/
|    ├──Requirements.txt
|
├──DOC/
|    ├──API Documentation.md
|    ├──Postman_collection
|
├──SRC/
|     ├──main.py
|     ├──geoserver.py
|     ├──MapClassify.py
|
├──README.md

```

## Usage

    first run geoserver
    install requirements.txt
    then on cmd type " uvicorn main:app --reload"
    once the server is running you can use tool like
    postman or `curl` to make request to the api
    choose the method for classify
    enter the data that you want to classyify
    choose the column
    read the methods descriptions

## Features

    This tool reads a geospatial file, classifies a specified numeric column
    using a chosen mapclassify method, and prepares a GeoDataFrame with
    classification results, including class ranges and assigned colors.

## Requirements

    check the requirements.txt
