import random
import time
import json
import matplotlib.pyplot as plt

run_length = 10000
map_size = 250

plant_list = {}

#world_traits
sun_color = .5
sun_intensity = 5

climate_shift = .01
drastic_chance = .001
drastic_shift = .3

gravity = 1
gene_limit = 8

equator_heat = 8
latitude_weight = 1
longitude_weight = 1.001
noise_chance = 0 #chance of totally random tile
tile_randomness = 0.05
water_level = 1
world_wetness = 1.1
world_altitude = 1


f = open("log.csv", 'w+')
f.write("efficiency,max_size,max_age,reproductive_chance,reproductive_energy,fiber,reproductive_range\n")

def generate_empty_map():

    map = {}
    for x in range(map_size):
        for y in range(map_size):

            map[str(x) + "," + str(y)] = [(sun_intensity + (equator_heat / (abs((x + 1) - (map_size/2)) + 1))) * random.uniform(1 - tile_randomness, 1 + tile_randomness)]

            wetness = random.uniform(0, 2)
            altitude = random.uniform(0, 2 / gravity)

            if random.random() < noise_chance:

                doNothing = 1 #keeps random above

            else:
                if x > 0 and y > 0:

                    y_wet = map[str(x) + "," + str(y-1)][1]
                    x_wet = map[str(x-1) + "," + str(y)][1]

                    y_alt = map[str(x) + "," + str(y-1)][2]
                    x_alt = map[str(x-1) + "," + str(y)][2]

                    altitude = (x_alt*latitude_weight + y_alt*longitude_weight) / (2 * latitude_weight * longitude_weight) * random.uniform(.95 - tile_randomness, 1.05 + tile_randomness)
                    wetness = (x_wet*latitude_weight + y_wet*longitude_weight) / (2 * latitude_weight * longitude_weight) * random.uniform(.95 - tile_randomness, 1.05 + tile_randomness)

                    if altitude > water_level:
                        wetness = min(wetness,1)

                elif x > 0:
                    wetness = map[str(x-1) + "," + str(y)][1] * random.uniform(.95 - tile_randomness, 1.05 + tile_randomness)
                    altitude = map[str(x-1) + "," + str(y)][2] * random.uniform(.95 - tile_randomness, 1.05 + tile_randomness)


            wetness = min(world_wetness*wetness,2)
            altitude = min(altitude,2 / gravity)

            if altitude > water_level:
                wetness = min(wetness,1)

            map[str(x) + "," + str(y)].append(wetness)
            map[str(x) + "," + str(y)].append(altitude)

    map_data = open("map_data.json","w+")
    json.dump(map, map_data)
    map_data.close()

    return map

def update_traits(genes):

    color = genes[0]
    growth_rate = genes[1]
    woodiness = genes[2]
    food_tendency = genes[3] #also storage efficiency
    poison_tendency = genes[4]
    reproduction_age = genes[5]

    efficiency = min(100,(1/1 + abs(sun_color - color)))
    max_size = woodiness / gravity * 20
    max_age = woodiness / growth_rate * 20 #add constant?
    reproductive_chance = (max_size + max_age + poison_tendency) / 100 #add constant?
    reproductive_energy = (food_tendency + poison_tendency)/growth_rate * (sun_intensity / 2)
    fiberiness = 1 - woodiness
    reproductive_range = (max_size - poison_tendency + food_tendency) #add constant?
    thirstiness = (max_size + food_tendency + color / 3)
    ideal_altitude = (woodiness + max_size) / (fiberiness + growth_rate)

    traits = [efficiency, max_size, max_age, reproductive_chance, reproductive_energy, fiberiness, reproductive_range,thirstiness,ideal_altitude]

    return traits

def generate_plant():

    location = str(random.randint(0,map_size-1)) + "," + str(random.randint(0,map_size-1))

    while map[location][1] > 1.5:
        location = str(random.randint(0,map_size-1)) + "," + str(random.randint(0,map_size-1))

    #genes
    color = random.uniform(0,1)
    growth_rate = random.uniform(0,1)
    woodiness = random.uniform(0,1)
    food_tendency = random.uniform(0,1)
    poison_tendency = random.uniform(0,1)
    reproduction_age = random.uniform(2,50)

    genes = [color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age]

    while sum(genes) - reproduction_age > gene_limit:
        color = random.uniform(0,1)
        growth_rate = random.uniform(0,1)
        woodiness = random.uniform(0,1)
        food_tendency = random.uniform(0,1)
        poison_tendency = random.uniform(0,1)
        reproduction_age = random.uniform(2,50)

        genes = [color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age]

    #traits
    traits = update_traits(genes)

    #stats
    age = 0
    plant_size = 0
    food_amount = 0
    poison_amount = 0
    fiber_amount = 0
    dye_amount = 0
    wood_amount = 0

    stats = [age, plant_size, food_amount, poison_amount, fiber_amount, dye_amount, wood_amount]

    plant = [genes, traits, stats]

    plant_list[location] = [plant]

def reproduce_plant(genes, location):

    #Mutate genes
    color = genes[0] * random.uniform(.99,1.01)
    growth_rate = genes[1] * random.uniform(.99,1.01)
    woodiness = max(0,min(1,genes[2] * random.uniform(.99,1.01)))
    food_tendency = min(1,genes[3] * random.uniform(.99,1.01))
    poison_tendency = genes[4] * random.uniform(.99,1.01)
    reproduction_age = max(2,genes[5] * random.uniform(.99,1.01))

    genes = [color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age]

    while sum(genes) - reproduction_age > gene_limit:
        color = genes[0] * random.uniform(.99,1.01)
        growth_rate = genes[1] * random.uniform(.99,1.01)
        woodiness = max(0,min(1,genes[2] * random.uniform(.99,1.01)))
        food_tendency = min(1,genes[3] * random.uniform(.99,1.01))
        poison_tendency = genes[4] * random.uniform(.99,1.01)
        reproduction_age = max(2,genes[5] * random.uniform(.99,1.01))

        genes = [color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age]

    #update traits
    traits = update_traits(genes)

    #stats
    age = 0
    plant_size = 0
    food_amount = 0
    poison_amount = 0
    fiber_amount = 0
    dye_amount = 0
    wood_amount = 0

    stats = [age, plant_size, food_amount, poison_amount, fiber_amount, dye_amount, wood_amount]

    plant = [genes, traits, stats]

    dead_check = 0

    if location in plant_list:
        if len(plant_list[location]) > 2:
            for p in range(len(plant_list[location])):
                if plant_list[location][p] == "dead" and dead_check == 0:
                    plant_list[location][p] = plant
                    if random.random() < .1:
                        for t in range(len(traits)):
                            f.write(str(traits[t]) + ",")
                        f.write("\n")
                    dead_check = 1

        else:
            plant_list[location].append(plant)
            if random.random() < .1:
                for t in range(len(traits)):
                    f.write(str(traits[t]) + ",")
                f.write("\n")
    else:
        plant_list[location] = [plant]
        if random.random() < .1:
            for t in range(len(traits)):
                f.write(str(traits[t]) + ",")
            f.write("\n")



def tick():

    age_debug = []

    reproduction_queue = []

    alive_count = 0
    died_young_count = 0

    for location in plant_list:

        for i in range(len(plant_list[location])):

            if plant_list[location][i] != "dead":

                genes = plant_list[location][i][0]
                traits = plant_list[location][i][1]
                stats = plant_list[location][i][2]

                alive_count += 1

                #genes
                color = genes[0]
                growth_rate = genes[1]
                woodiness = genes[2]
                food_tendency = genes[3]
                poison_tendency = genes[4]
                reproduction_age = genes[5]

                #traits
                efficiency = traits[0]
                max_size = traits[1]
                max_age = traits[2]
                reproductive_chance = traits[3]
                reproductive_energy = traits[4]
                fiber = traits[5]
                reproductive_range = traits[6]
                thirstiness = traits[7]
                ideal_altitude = traits[8]

                #stats
                age = stats[0]
                plant_size = stats[1]
                energy = stats[2] #also called food amount

                #checks if tallest in square
                if len(plant_list[location]) > 1:

                    try:
                        plant_heights = [plant_list[location][0][2][1],plant_list[location][1][2][1],plant_list[location][2][2][1]]

                    except IndexError:

                        try:
                            plant_heights = [plant_list[location][0][2][1],plant_list[location][1][2][1]]

                        except IndexError:
                            plant_heights = [plant_size]
                else:
                    plant_heights = [plant_size]

                plant_heights.sort(reverse=True)


                if plant_size == plant_heights[0]:
                    size_weight = 1
                elif plant_size == plant_heights[1]:
                    size_weight = 0.5
                elif plant_size == plant_heights[2]:
                    size_weight = 0.1

                age += 1
                energy += efficiency * size_weight * map[location][0] * (1/(abs(thirstiness - map[location][1]) + 1)) * (1/(abs(ideal_altitude - map[location][2]) + 1)) #may wish to curve somehow?
                #print(str(energy))

                energy -= plant_size**2 * 2
                #print(str(energy))

                plant_size += growth_rate
                plant_size = min(max_size, plant_size)

                if energy >= reproductive_energy and age > reproduction_age and random.random() < reproductive_chance:

                    energy -= reproductive_energy
                    seed_location = location.split(",")

                    rangeint = int(reproductive_range)
                    seed_location[0] = max(0,min(map_size-1, int(seed_location[0]) + random.randint(-rangeint, rangeint)))
                    seed_location[1] = max(0,min(map_size-1, int(seed_location[1]) + random.randint(-rangeint, rangeint)))

                    dead_check = 0

                    location_string = (str(seed_location[0]) + "," + str(seed_location[1]))

                    if map[location_string][1] < 1.5:
                        if location_string in plant_list:
                            if len(plant_list[location_string]) > 2:
                                for p in range(len(plant_list[location_string])):
                                    if plant_list[location_string][p] == "dead" and dead_check == 0:
                                        dead_check = 1
                                        reproduction_queue.append([genes,location_string])
                            else:
                                reproduction_queue.append([genes,location_string])
                        else:
                            reproduction_queue.append([genes,location_string])

                energy *= food_tendency
                energy = min(plant_size, energy)

                stats[0] = age
                stats[1] = plant_size
                stats[2] = energy #also called food_amount

                if energy < 0:
                    #print(str(age))
                    plant_list[location][i] = "dead"
                    alive_count -= 1

                if age > max_age:
                    plant_list[location][i] = "dead"
                    alive_count -= 1

                if age == 1 and energy < 0:
                    died_young_count += 1

    for i in range(len(reproduction_queue)):
        reproduce_plant(reproduction_queue[i][0],reproduction_queue[i][1])

    if alive_count == 0:
        generate_plant()

    return(alive_count)

map = generate_empty_map()

generate_plant()

start = time.time()

x_graph = []
y_graph = []
climate_graph = []

alive_count = 0
world_age = 0
tick_count = 0

while world_age < run_length:

    world_age += 1
    tick_count += 1

    if world_age > 1:
        sun_intensity += random.uniform(-climate_shift, climate_shift)
        if random.random() < drastic_chance:
            sun_intensity += random.uniform(-drastic_shift, drastic_shift)
            sun_color += random.uniform(-.1,.1)

        sun_intensity = max(.1,sun_intensity)

    alive_count = tick()

    print(str(alive_count) + ", " + str(world_age) + ", " + str(tick_count))

    if alive_count < 5:
        world_age -= 1
    else:
        x_graph.append(world_age)
        y_graph.append(alive_count)
        climate_graph.append(sun_intensity)

    if alive_count == 0:
        generate_plant()

    if y_graph != []:
        if max(y_graph) > 100:
            if alive_count == 0:

                print("planet dead after " + str(world_age) + " years")
                world_age = run_length + 10

    if tick_count > 20000 and alive_count < 1:
        map = generate_empty_map()
        tick_count = 0

    #print(plant_list)
    #rint(len(plant_list))
end = time.time()
print(end - start)
#print(sum(age_debug)/len(age_debug))

f.close()

f = open("survey.csv","w+")

#print(plant_list)

f.write("x coord,y coord,color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age,efficiency,max_size,max_age,reproductive_chance,reproductive_energy,fiberiness,reproductive_range,thirstiness,ideal_altitude\n")
for location in plant_list:
    for i in range(len(plant_list[location])):
        if plant_list[location][i] != "dead":
            f.write(str(location) + ",")
            for x in range(len(plant_list[location][i][0])):
                f.write(str(plant_list[location][i][0][x]))
                if x < len(plant_list[location][i][0]):
                    f.write(",")
            for x in range(len(plant_list[location][i][1])):
                f.write(str(plant_list[location][i][1][x]))
                if x < len(plant_list[location][i][1]):
                    f.write(",")
            f.write("\n")

f.close()

plant_data = open("plant_data.json","w+")
json.dump(plant_list, plant_data)
plant_data.close()

plt.plot(x_graph, y_graph)
plt.show()

plt.plot(x_graph, climate_graph)
plt.show()
