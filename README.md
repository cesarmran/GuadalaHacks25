# GuadalaHacks25
This code detects and fixes automatically three type of errors in the POI's (Point of interest) ubication.
>Scenary 1: There is no POI in reality because a change in location or closure hasn't been updated
>Scenary 2: The POI is placed on the incorrect side of the road
>Scenary 3: The POI has an incorrect multiply digitised attribution

## Requirements

Install the following python libraries:

- Geopandas:
```
pip install geopandas
```

- Requests:
```
pip install requests
```

- Numpy:
```
pip install numpy   
```

- Shapely:
```
pip install shapely
```


## How It Works
- After executing it, it will print a message that says that the 3 output files were successfully created. "outputscenary1.csv" contains which POIs weren't found, "caso2final.csv" has which POIs are in the wrong side of the road (scenary 2) and "invalid_poi" is composed of the poi's name that have an incorrect multiply digitised attribution.

## Execution

Run the script from your terminal using:

```
python -u "path in which you downloaded the repository/Docsflow.py" 
```