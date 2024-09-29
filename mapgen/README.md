# MapGen

## Overview
MapGen is a tool for generating and managing a 2D world map for the GridPlanet system.
It reads a configuration file to set up the world dimensions, tile types, and their distribution, and then generates the map accordingly.
The tool also provides functionalities to validate the configuration, query tile types, and export the map to a JSON file.
It needs a bit of work still for validating config syntax and requirements, and map output conformance for realistic clustering of tile types.

## Requirements
- Python
- sqlite3: `pip install sqlite3`
- a valid config

## Config File
Look at the included and more or less, self-explanatory example config file in this repo.

```
{
    "WorldName": "FooWorld",
    "WorldSizeX": 256,
    "WorldSizeY": 256,
    "TileRealSize": 1,
    "WaterPercent": 30,
    "LandPercent": 70,
    "LandSoil": 20,
    "LandRock": 20,
    "LandGrass": 40,
    "LandTree": 15,
    "LandHole": 5
}
```
- Name is your world name, which could be the entire world you are generating or sections.
- WorldSizeX/Y is the grid size of the world on the X and Y axis
- TileRealSize is a unit of real world size mapping, for later or internal scaling use. The example is "1", which could be 1 meter per tile, 1 foot per tile.
- WaterPercent is the percentage of the map, covered in water (will be more or less contiguous)
- LandPercent is the rest. This could be omitted, because 100% minus Water = Land, but later I want to do control checks on this, and expand tile types
- The rest of your parameters named LandSoil, LandRock etc, are the percentages of 'types' that will be applied to LandPercent. These must total up to 100% and in the example config, they do.

## Instructions

Call it using your python skills on your command line:
This should be logical:
```
$ python3 mapgen.py
MapGen - A tool for GridPlanet
Usage:
  mapgen.py help                  Show this help message
  mapgen.py generate              Generate the world map using the config file
  mapgen.py validate              Validate the config file
  mapgen.py qtile X Y             Query the tile type at coordinates (X, Y)
  mapgen.py qworld                Query the world statistics
  mapgen.py dump                  Dump the world map to a JSON file
```

Query an already generated map:
```
$ python3 mapgen.py qworld
Total tiles: 65536
Water tiles: 19660
Land tiles: 45876
Landsoil tiles: 6413
Landrock tiles: 5535
Landgrass tiles: 29306
Landtree tiles: 3524
Landhole tiles: 1098
```

Query a specific tile on it:
```
 $ python3 mapgen.py qtile 23 10
Tile type at (23, 10): water
```


```
