from random import randrange
import json
import haversine as hs
import matplotlib.pyplot as plt
from copy import deepcopy
from os import listdir
from os.path import isfile, join
import math
import random

start_city_coords = [ 20.91925, 44.0130251] #Kragujevac
end_city_coords = [19.8451756, 45.2551338] #Novi Sad

connected = {}
neighbours = {}

def draw_point(coords):
    # Draw a point at the location (coords) with size 100
    plt.scatter(coords[0], coords[1], s=40, color="dodgerblue")
    # Set size of tick labels.
    plt.tick_params(axis='both', which='major', labelsize=9)

def draw_line(point1, point2, color = 'skyblue', alpha = 0.5):
    # List to hold x values.
    x_number_values = [point1[0], point2[0]]
    # List to hold y values.
    y_number_values = [point1[1], point2[1]]
    # Plot the number in the list and set the line thickness.
    plt.plot(x_number_values, y_number_values, linewidth=1, color=color, alpha=alpha)
    # Set the x, y axis tick marks text size.
    plt.tick_params(axis='both', labelsize=9)

def order_nodes(node1, node2):
    if(node2[0] < node1[0]):
        return (node2, node1)
    return (node1, node2)

def get_distance(node1, node2):
    return math.sqrt((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)

def add_to_conneced(node1, node2):
    node1 = tuple([round(float(x), 2) for x in node1])
    node2 = tuple([round(float(x), 2) for x in node2])
    if(node1 == node2):
        return
    distance = get_distance(node1, node2)

    sorted_nodes = order_nodes(node1, node2)

    if sorted_nodes not in connected or distance < connected[sorted_nodes]:
        connected[sorted_nodes] = distance
        
        if node1 not in neighbours:
            neighbours[node1] = []
        if node2 not in neighbours:
            neighbours[node2] = []

        neighbours[node1].append(node2)
        neighbours[node2].append(node1)        

path = './serbia/serbia/'
def read_data_from_geojson(filename):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for filename in files:
        with open(f'{path}{filename}', 'r') as file:
            data = json.load(file)
            
            for street in data:
                previous_node = None
                for node in street['geometry']['coordinates']:
                    if previous_node:
                        add_to_conneced(node, previous_node)
                    previous_node = node

def read_country_borders(filename):
    with open(filename, encoding="utf8") as file:
        data = json.load(file) 
        countries = data["features"]
        for country in countries:
            for border_part in country["geometry"]["coordinates"]:
                print(f"Granica: {len(border_part)} ")
                previous_point = border_part[-1]

                #draw lower resolution border for performance
                i = -1
                for point in border_part:
                    i += 1
                    if i % 7 == 0:
                        draw_line(previous_point, point, 'peru', 0.3)
                        previous_point = point

class Node:
    def __init__(self, coords, parent):
        self.coords = coords
        self.parent = parent

        if parent == None:
            self.source_distance = 0
        else:
            self.source_distance = parent.source_distance + get_distance(coords, parent.coords)

    def distance_to_target(self, target):
        return get_distance(self.coords, target)

candidates = []
checked_candidates = []

def way_to_start(node):
    path = []
    while node:
        path.append(node.coords)
        node = node.parent
    
    return path

def a_star(start, end):
    n = Node(start, None)
    candidates = [n]

    while len(candidates) > 0:
        current_node = candidates.pop(0)

        if current_node.coords in checked_candidates:
            continue

        checked_candidates.append(current_node.coords)

        new_candidates = (Node(x, current_node) for x in neighbours[current_node.coords])

        for new_candidate in new_candidates:
            if new_candidate.coords == end:
                return way_to_start(new_candidate)
            
            candidates.append(new_candidate)
        
        candidates.sort(key=lambda x: x.source_distance + x.distance_to_target(end), reverse=False)

    return None

if __name__ == "__main__":
    read_data_from_geojson("export.geojson")

    read_country_borders("serbia_borders.geojson")

    #start, end = random.sample(list(neighbours.keys()), 2)
    start = (19.83, 45.3) #Novi Sad
    end = (21.38, 43.94) #Kragujevac

    for connection in connected:
        draw_line(connection[0], connection[1])
    
    path = a_star(start, end)

    if path:
        print('There is a path')

        for i in range(len(path) - 1):
            draw_line(path[i], path[i + 1], color='red')
        
        draw_point(path[0])
        draw_point(path[-1])

    #for city in cities:
    #    draw_point(city.coords)
    
    plt.axis('equal')
    plt.show()
