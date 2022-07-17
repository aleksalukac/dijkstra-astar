from random import randrange
import json
import haversine as hs
import matplotlib.pyplot as plt
from copy import deepcopy
from os import listdir
from os.path import isfile, join
import math
import random
from haversine import haversine, Unit

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
    return haversine(node1, node2, unit=Unit.KILOMETERS)
    #return math.sqrt((node1[0] - node2[0])**2 + (node1[1] - node2[1])**2)

def add_to_connected(node1, node2, maxspeed = 50):
    try:
        maxspeed = float(maxspeed)
    except:
        maxspeed = 50
    node1 = tuple([round(float(x), 3) for x in node1])
    node2 = tuple([round(float(x), 3) for x in node2])
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

        neighbours[node1].append((node2,maxspeed))
        neighbours[node2].append((node1,maxspeed))        

path = './serbia/serbia_maxspeed/'
def read_data_from_geojson(filename):
    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for filename in files:
        with open(f'{path}{filename}', 'r') as file:
            data = json.load(file)
            
            for street in data:
                previous_node = None
                for node in street['geometry']['coordinates']:
                    if previous_node:
                        maxspeed = 50
                        if 'maxspeed' in street['feature']:
                            maxspeed = street['feature']['maxspeed']
                        add_to_connected(node, previous_node, maxspeed)
                    previous_node = node

def read_country_borders(filename):
    with open(filename, encoding="utf8") as file:
        data = json.load(file) 
        countries = data["features"]
        for country in countries:
            for border_part in country["geometry"]["coordinates"]:
                previous_point = border_part[-1]

                #draw lower resolution border for performance
                i = -1
                for point in border_part:
                    i += 1
                    if i % 7 == 0:
                        draw_line(previous_point, point, 'peru', 0.3)
                        previous_point = point

class Node:
    def __init__(self, coords, parent, maxspeed = 1):
        self.coords = coords
        self.parent = parent
        self.maxspeed = maxspeed

        if parent == None:
            self.source_distance = 0
        else:
            self.source_distance = parent.source_distance + get_distance(coords, parent.coords) / maxspeed

    def distance_to_target(self, target):
        return get_distance(self.coords, target)

candidates = []
checked_candidates = []

def way_to_start(node):
    path = []
    while node:
        path.append([node.coords, node.maxspeed])
        node = node.parent
    
    return path

def a_star(start, end, shortest):
    n = Node(start, None)
    candidates = [n]

    while len(candidates) > 0:
        current_node = candidates.pop(0)

        count_130 = 0
        for can in candidates:
            if can.maxspeed == 130:
                count_130 += 1
                break
                
        if count_130 == 0:
            wsw = 1

        if current_node.coords[0] == 20.15:
            smt = 4

        if current_node.coords in checked_candidates:
            continue

        checked_candidates.append(current_node.coords)

        new_candidates = (Node(x[0], current_node, x[1]) for x in neighbours[current_node.coords])

        for new_candidate in new_candidates:
            if new_candidate.coords == end:
                return way_to_start(new_candidate)
            
            candidates.append(new_candidate)
        
        if(shortest):
            candidates.sort(key=lambda x: x.source_distance + x.distance_to_target(end), reverse=False)
        else:
            candidates.sort(key=lambda x: road_potential_speed(x), reverse=False)

    return None

def road_potential_speed(x):
    heuristic = x.source_distance + x.distance_to_target(end) / x.maxspeed
    return heuristic

def find_closest(node):
    min_distance = -1
    closest_node = None
    for n in neighbours:
        if min_distance == -1 or get_distance(n, node) < min_distance:
            min_distance = get_distance(n, node)
            closest_node = n
    
    return closest_node

if __name__ == "__main__":
    read_data_from_geojson("export.geojson")

    read_country_borders("serbia_borders.geojson")

    #start, end = random.sample(list(neighbours.keys()), 2)
    #start = (19.82, 45.25) #Novi Sad
    start = (19.9442, 45.3386) #Subotica
    #end = (21.38, 43.94) #Kragujevac
    end = (21.6, 43.2) #Somewhere

    start, end = find_closest(start), find_closest(end)
    print(start)
    print(end)
    #end = (19.93, 43.98) #Cacak
    
    for connection in connected:
        draw_line(connection[0], connection[1])
    
    shortest_path = a_star(start, end, shortest=False)

    if shortest_path:
        print('There is a path')

        for i in range(len(shortest_path) - 1):
            if shortest_path[i][1] > 50:
                draw_line(shortest_path[i][0], shortest_path[i + 1][0], color='green')
            else:
                draw_line(shortest_path[i][0], shortest_path[i + 1][0], color='red')
        
        draw_point(shortest_path[0][0])
        draw_point(shortest_path[-1][0])

    plt.axis('equal')
    plt.show()
