# Author: marlonv@protonmail.com
# Version: 1.0
# MapGen - A tool for GridPlanet, MapGen

import json
import sys
import datetime
import sqlite3
import random

conn = sqlite3.connect('worldmap.db')
cursor = conn.cursor()

def read_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        sys.exit(1)
    return config

def prepare_database():
    cursor.execute('''CREATE TABLE IF NOT EXISTS tiletypes (
                        id TEXT PRIMARY KEY,
                        type TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS mapdata (
                        WorldName TEXT,
                        WorldSizeX INTEGER,
                        WorldSizeY INTEGER,
                        TileRealSize REAL,
                        GeneratedDate TEXT,
                        GenConfig TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS maptiles (
                        X INTEGER,
                        Y INTEGER,
                        tileid TEXT PRIMARY KEY,
                        tiletype TEXT)''')
    conn.commit()

def update_mapdata(config):
    mapdata = {
        'WorldName': config['WorldName'],
        'WorldSizeX': config['WorldSizeX'],
        'WorldSizeY': config['WorldSizeY'],
        'TileRealSize': config['TileRealSize'],
        'GeneratedDate': datetime.datetime.now().isoformat(),
        'GenConfig': json.dumps(config)
    }
    cursor.execute('''INSERT INTO mapdata (WorldName, WorldSizeX, WorldSizeY, TileRealSize, GeneratedDate, GenConfig)
                      VALUES (:WorldName, :WorldSizeX, :WorldSizeY, :TileRealSize, :GeneratedDate, :GenConfig)''', mapdata)
    conn.commit()

def insert_tiletypes():
    tiletypes = ['landsoil', 'landrock', 'landgrass', 'landtree', 'landhole', 'water']
    for tiletype in tiletypes:
        cursor.execute('''INSERT INTO tiletypes (id, type) VALUES (?, ?)''', (tiletype, tiletype))
    conn.commit()

def generate_map(config):
    world_size_x = config['WorldSizeX']
    world_size_y = config['WorldSizeY']
    map_tiles = []

    for y in range(world_size_y):
        for x in range(world_size_x):
            tile = {'X': x, 'Y': y, 'tileid': f'{x}-{y}', 'tiletype': 'landgrass'}
            map_tiles.append(tile)

    cursor.executemany('''INSERT INTO maptiles (X, Y, tileid, tiletype) VALUES (:X, :Y, :tileid, :tiletype)''', map_tiles)
    conn.commit()
    return map_tiles

def populate_tiles(config, map_tiles):
    total_tiles = config['WorldSizeX'] * config['WorldSizeY']
    water_tiles = int(total_tiles * config['WaterPercent'] / 100)
    land_tiles = total_tiles - water_tiles

    water_indices = random.sample(range(total_tiles), water_tiles)
    for index in water_indices:
        map_tiles[index]['tiletype'] = 'water'

    cursor.executemany('''UPDATE maptiles SET tiletype = :tiletype WHERE tileid = :tileid''', map_tiles)
    conn.commit()

    land_tiletypes = {
        'landsoil': config['LandSoil'],
        'landrock': config['LandRock'],
        'landgrass': config['LandGrass'],
        'landtree': config['LandTree'],
        'landhole': config['LandHole']
    }

    for tiletype, percent in land_tiletypes.items():
        tile_count = int(land_tiles * percent / 100)
        indices = random.sample(range(total_tiles), tile_count)
        for index in indices:
            if map_tiles[index]['tiletype'] == 'landgrass':
                map_tiles[index]['tiletype'] = tiletype
                cursor.execute('''UPDATE maptiles SET tiletype = ? WHERE tileid = ?''', (tiletype, map_tiles[index]['tileid']))
    conn.commit()

def validate_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return False

    required_fields = ['WorldName', 'WorldSizeX', 'WorldSizeY', 'TileRealSize', 'WaterPercent', 'LandPercent', 'LandSoil', 'LandRock', 'LandGrass', 'LandTree', 'LandHole']
    for field in required_fields:
        if field not in config:
            print(f"Missing required field: {field}")
            return False
    if config['WaterPercent'] + config['LandPercent'] != 100:
        print("WaterPercent and LandPercent must sum to 100")
        return False
    if config['LandSoil'] + config['LandRock'] + config['LandGrass'] + config['LandTree'] + config['LandHole'] != 100:
        print("Land tile percentages must sum to 100")
        return False
    return True

def query_tile(x, y):
    cursor.execute('''SELECT tiletype FROM maptiles WHERE X = ? AND Y = ?''', (x, y))
    tile = cursor.fetchone()
    if tile:
        return tile[0]
    else:
        return None

def query_world():
    cursor.execute('''SELECT COUNT(*) FROM maptiles''')
    total_tiles = cursor.fetchone()[0]
    cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'water' ''')
    water_tiles = cursor.fetchone()[0]
    land_tiles = total_tiles - water_tiles

    land_tiletypes = {
        'landsoil': cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'landsoil' ''').fetchone()[0],
        'landrock': cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'landrock' ''').fetchone()[0],
        'landgrass': cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'landgrass' ''').fetchone()[0],
        'landtree': cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'landtree' ''').fetchone()[0],
        'landhole': cursor.execute('''SELECT COUNT(*) FROM maptiles WHERE tiletype = 'landhole' ''').fetchone()[0]
    }

    print(f"Total tiles: {total_tiles}")
    print(f"Water tiles: {water_tiles}")
    print(f"Land tiles: {land_tiles}")
    for tiletype, count in land_tiletypes.items():
        print(f"{tiletype.capitalize()} tiles: {count}")

def dump_world():
    cursor.execute('''SELECT * FROM mapdata''')
    mapdata = cursor.fetchone()
    cursor.execute('''SELECT * FROM maptiles''')
    map_tiles = cursor.fetchall()

    worldmap = {
        'metadata': mapdata,
        'map': map_tiles
    }

    with open('worldmap.json', 'w') as file:
        json.dump(worldmap, file, default=str)

def main():
    if len(sys.argv) < 2:
        print_help()
    elif sys.argv[1] == 'help':
        print_help()
    elif sys.argv[1] == 'generate':
        config = read_config('MapGen.config')
        if not validate_config('MapGen.config'):
            return
        prepare_database()
        update_mapdata(config)
        insert_tiletypes()
        map_tiles = generate_map(config)
        populate_tiles(config, map_tiles)
    elif sys.argv[1] == 'validate':
        if not validate_config('MapGen.config'):
            print("Configuration is invalid")
        else:
            print("Configuration is valid")
    elif sys.argv[1] == 'qtile':
        if len(sys.argv) != 4:
            print("Usage: qtile X Y")
            return
        x, y = int(sys.argv[2]), int(sys.argv[3])
        tile_type = query_tile(x, y)
        if tile_type:
            print(f"Tile type at ({x}, {y}): {tile_type}")
        else:
            print(f"No tile found at ({x}, {y})")
    elif sys.argv[1] == 'qworld':
        query_world()
    elif sys.argv[1] == 'dump':
        dump_world()
    else:
        print_help()

def print_help():
    print("MapGen - A tool for GridPlanet: The Map Generator")
    print("Usage:")
    print("  mapgen.py help                  Show this help message")
    print("  mapgen.py generate              Generate a world map using the params from the config file")
    print("  mapgen.py validate              Validate the config file (or it's existence, for now)")
    print("  mapgen.py qtile X Y             Query the tile type at coordinates (X, Y)")
    print("  mapgen.py qworld                Query the world statistics")
    print("  mapgen.py dump                  Dump the world map to a JSON file")

if __name__ == "__main__":
    main()
