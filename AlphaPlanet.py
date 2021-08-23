import random
import time

map_size = 100
plant_list = {}

#world traits
sun_color = .5
sun_intensity = 1
gravity = 1


f = open("log.csv", 'w+')
f.write("efficiency,max_size,max_age,reproductive_chance,reproductive_energy,fiber,reproductive_range\n")

def generate_empty_map():

    map = {}
    for x in range(map_size):
        for y in range(map_size):
            map[str(x) + "," + str(y)] = [random.randint(0,1)]

    return map

def update_traits(genes):

    color = genes[0]
    growth_rate = genes[1]
    woodiness = genes[2]
    food_tendency = genes[3]
    poison_tendency = genes[4]
    reproduction_age = genes[5]

    efficiency = max(2,1/abs(sun_color - color))*sun_intensity
    max_size = woodiness / gravity
    max_age = woodiness / growth_rate #add constant?
    reproductive_chance = (max_size + max_age + poison_tendency) * .3 #add constant?
    reproductive_energy = (food_tendency + poison_tendency) / growth_rate
    fiberiness = 1 - woodiness
    reproductive_range = (max_size - poison_tendency + food_tendency) #add constant?

    traits = [efficiency, max_size, max_age, reproductive_chance, reproductive_energy, fiberiness, reproductive_range]

    return traits

def generate_plant():

    location = str(random.randint(0,map_size-1)) + "," + str(random.randint(0,map_size-1))

    #genes
    color = random.uniform(0,1)
    growth_rate = random.uniform(0,1)
    woodiness = random.uniform(0,1)
    food_tendency = random.uniform(0,1)
    poison_tendency = random.uniform(0,1)
    reproduction_age = random.uniform(0,50)

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
    food_tendency = genes[3] * random.uniform(.99,1.01)
    poison_tendency = genes[4] * random.uniform(.99,1.01)
    reproduction_age = genes[5] * random.uniform(.99,1.01)

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
                    size_weight = 0.25

                age += 1
                energy += efficiency * size_weight #may wish to curve somehow?
                energy -= plant_size
                plant_size += growth_rate
                plant_size = min(max_size, plant_size)

                if energy >= reproductive_energy and random.random() < reproductive_chance:

                    energy -= reproductive_energy
                    seed_location = location.split(",")

                    rangeint = int(reproductive_range)
                    seed_location[0] = max(0,min(map_size-1, int(seed_location[0]) + random.randint(-rangeint, rangeint)))
                    seed_location[1] = max(0,min(map_size-1, int(seed_location[1]) + random.randint(-rangeint, rangeint)))

                    dead_check = 0

                    location_string = (str(seed_location[0]) + "," + str(seed_location[1]))

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


                stats[0] = age
                stats[1] = plant_size
                stats[2] = energy #also called food_amount

                if energy < 0:
                    plant_list[location][i] = "dead"
                    alive_count -= 1

                if age > max_age:
                    plant_list[location][i] = "dead"
                    alive_count -= 1

                if age == 1 and energy < 0:
                    died_young_count += 1

    for i in range(len(reproduction_queue)):
        reproduce_plant(reproduction_queue[i][0],reproduction_queue[i][1])

    print(str(alive_count) + ", " + str(died_young_count))

    if alive_count == 0:
        generate_plant()


map = generate_empty_map()
generate_plant()


start = time.time()
for i in range(20000):
    #print(str(i))
    tick()
    #print(plant_list)
    #rint(len(plant_list))
end = time.time()
print(end - start)
#print(sum(age_debug)/len(age_debug))

f.close()
