import random
import time

size = 40
plant_list = {}

#world traits
sun_color = .5
sun_intensity = 1
gravity = 1


f = open("log.csv", 'w+')

def generate_empty_map():

    map = {}
    for x in range(size):
        for y in range(size):
            map[str(x) + "," + str(y)] = [random.randint(0,1)]

    return map

def update_traits(genes):

    color = genes[0]
    growth_rate = genes[1]
    woodiness = genes[2]
    food_tendency = genes[3]
    poison_tendency = genes[4]
    reproduction_age = genes[5]

    efficiency = abs(sun_color - color) / sun_color
    max_size = woodiness / gravity
    max_age = woodiness / growth_rate #add constant?
    reproductive_chance = (max_size + max_age + poison) * .3 #add constant?
    reproductive_energy = (food_tendency + poison_tendency) / growth_rate
    fiberiness = 1 - woodiness
    reproductive_range = (size - poison_tendency + food_tendency) #add constant?

    traits = [efficiency, max_size, max_age, reproductive_chance, reproductive_energy, fiberiness, reproduction_range]

    return traits

def generate_plant():

    location = str(random.randint(0,size-1)) + "," + str(random.randint(0,size-1))

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
    size = 0
    food_amount = 0
    poison_amount = 0
    fiber_amount = 0
    dye_amount = 0
    wood_amount = 0

    stats = [age, size, food_amount, poison_amount, fiber_amount, dye_amount, wood_amount]

    plant = [genes, traits, stats]

    plant_list[location] = [plant]

def reproduce_plant(genes, location):

    #Mutate genes
    color = genes[0] * random.uniform(.99,1.01)
    growth_rate = genes[1] * random.uniform(.99,1.01)
    woodiness = genes[2] * random.uniform(.99,1.01)
    food_tendency = genes[3] * random.uniform(.99,1.01)
    poison_tendency = genes[4] * random.uniform(.99,1.01)
    reproduction_age = genes[5] * random.uniform(.99,1.01)

    genes = [color,growth_rate,woodiness,food_tendency,poison_tendency,reproduction_age]

    #update traits
    traits = update_traits(genes)

    #stats
    age = 0
    size = 0
    food_amount = 0
    poison_amount = 0
    fiber_amount = 0
    dye_amount = 0
    wood_amount = 0

    stats = [age, size, food_amount, poison_amount, fiber_amount, dye_amount, wood_amount]

    plant = [genes, traits, stats]

    dead_check = 0

    if location in plant_list:
        if len(plant_list[location]) > 2:
            for p in range(len(plant_list[location])):
                if plant_list[location][p] == "dead" and dead_check == 0:
                    plant_list[location][p] = plant
                    if random.random() < .1:
                        f.write(str(traits[0]) + "," + str(traits[1]) + "," + str(traits[2]) + '\n')
                    dead_check = 1

        else:
            plant_list[location].append(plant)
            if random.random() < .1:
                f.write(str(traits[0]) + "," + str(traits[1]) + "," + str(traits[2]) + '\n')
    else:
        plant_list[location] = [plant]
        if random.random() < .1:
            f.write(str(traits[0]) + "," + str(traits[1]) + "," + str(traits[2]) + '\n')

def plant_actions(location):

    for i in range(plant_list[location]):

        if plant_list[location][i] != "dead":

            alive_count += 1
            efficiency = plant_list[location][i][0]
            plant_size = plant_list[location][i][1]
            reproductive_energy = plant_list[location][i][2]
            energy = plant_list[location][i][3]
            real_size = plant_list[location][i][4]
            age = plant_list[location][i][5]

            if len(plant_list[location]) > 1:

                try:
                    plant_heights = [plant_list[location][0][4],plant_list[location][1][4],plant_list[location][2][4]]

                except IndexError:

                    try:
                        plant_heights = [plant_list[location][0][4],plant_list[location][1][4]]

                    except IndexError:
                        plant_heights = [real_size]
            else:
                plant_heights = [real_size]

            plant_heights.sort(reverse=True)


            if real_size == plant_heights[0]:
                size_weight = 1
            elif real_size == plant_heights[1]:
                size_weight = 0.5
            elif real_size ==plant_heights[2]:
                size_weight = 0.25

            age += 1
            energy += (efficiency**.5) * size_weight
            energy -= plant_size * 2
            real_size += real_size + efficiency
            real_size = min(plant_size, real_size)

            if energy >= reproductive_energy:

                energy -= reproductive_energy
                seed_location = location.split(",")

                seed_location[0] = max(0,min(size-1, int(seed_location[0]) + random.randint(-5,5))) #reproduction range, change later
                seed_location[1] = max(0,min(size-1, int(seed_location[1]) + random.randint(-5,5))) #reproduction range, change later

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


            plant_list[location][i][3] = energy
            plant_list[location][i][4] = real_size
            plant_list[location][i][5] = age

            if energy < 0:
                plant_list[location][i] = "dead"
                alive_count -= 1

            if age > max_age:
                plant_list[location][i] = "dead"
                alive_count -= 1

            if age == 1 and energy < 0:
                died_young_count += 1


def tick():

    age_debug = []

    reproduction_queue = []

    alive_count = 0
    died_young_count = 0

    for location in plant_list:

        for i in range(plant_list[location]):

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
                max size = traits[1]
                max age = traits[2]
                reproductive chance = traits[3]
                reproductive energy = traits[4]
                fiber = traits[5]
                reproductive range = traits[6]

                #stats
                age = stats[0]
                real_size = stats[1]
                energy = stats[2] #also called food amount

                age += 1
                energy += efficiency * size_weight #may wish to curve somehow?
                energy -= plant_size
                real_size += growth_rate
                real_size = min(max_size, real_size)

                #checks if tallest in square
                if len(plant_list[location]) > 1:

                    try:
                        plant_heights = [plant_list[location][0][2][2],plant_list[location][1][2][2],plant_list[location][2][2][2]]

                    except IndexError:

                        try:
                            plant_heights = [plant_list[location][0][2][2],plant_list[location][1][2][2]]

                        except IndexError:
                            plant_heights = [real_size]
                else:
                    plant_heights = [real_size]

                plant_heights.sort(reverse=True)


                if real_size == plant_heights[0]:
                    size_weight = 1
                elif real_size == plant_heights[1]:
                    size_weight = 0.5
                elif real_size ==plant_heights[2]:
                    size_weight = 0.25

                if energy >= reproductive_energy and random.random() < reproductive_chance:

                    energy -= reproductive_energy
                    seed_location = location.split(",")

                    seed_location[0] = max(0,min(size-1, int(seed_location[0]) + random.randint(-reproduction_range,reproduction_range)))
                    seed_location[1] = max(0,min(size-1, int(seed_location[1]) + random.randint(-reproduction_range,reproduction_range)))

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
                stats[1] = real_size
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
for i in range(1000):
    #print(str(i))
    tick()
    #print(plant_list)
    #rint(len(plant_list))
end = time.time()
print(end - start)
#print(sum(age_debug)/len(age_debug))

f.close()
