import random
import time

size = 40
plant_list = {}
log = []

f = open("log.csv", 'w+')

def generate_empty_map():

    map = {}
    for x in range(size):
        for y in range(size):
            map[str(x) + "," + str(y)] = [random.randint(0,1)]

    return map

def generate_plant():
    location = str(random.randint(0,size-1)) + "," + str(random.randint(0,size-1))
    efficiency = random.uniform(0,3)
    plant_size = random.uniform(0,1)
    reproductive_energy = random.uniform(5,50)

    plant = [efficiency,plant_size,reproductive_energy,0,0,0]

    plant_list[location] = [plant]
    #print(plant_size)

def reproduce_plant(genes, location):
    #location = str(random.randint(0,size-1)) + "," + str(random.randint(0,size-1))
    efficiency = min(genes[0] * random.uniform(.99,1.01),10)
    plant_size = min(genes[1] * random.uniform(.99,1.01),10)
    reproductive_energy = max(genes[2] * random.uniform(.99,1.01),5)

    #print(plant_size)
    #print(efficiency)

    plant = [efficiency,plant_size,reproductive_energy,0,0,0]

    dead_check = 0

    if location in plant_list:
        if len(plant_list[location]) > 2:
            for p in range(len(plant_list[location])):
                if plant_list[location][p] == "dead" and dead_check == 0:
                    plant_list[location][p] = plant
                    if random.random() < .1:
                        f.write(str(efficiency) + "," + str(plant_size) + "," + str(reproductive_energy) + '\n')
                    dead_check = 1

            doNothing = 1
            return ""
        else:
            plant_list[location].append(plant)
            if random.random() < .1:
                f.write(str(efficiency) + "," + str(plant_size) + "," + str(reproductive_energy) + '\n')
            return efficiency
    else:
        plant_list[location] = [plant]
        if random.random() < .1:
            f.write(str(efficiency) + "," + str(plant_size) + "," + str(reproductive_energy) + '\n')
        return efficiency


def tick():

    age_debug = []

    reproduction_queue = []

    alive_count = 0
    died_young_count = 0

    for location in plant_list:

        for i in range(len(plant_list[location])):

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
                    size_weight = .25

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
                                    reproduction_queue.append([[efficiency,plant_size,reproductive_energy],location_string])
                        else:
                            reproduction_queue.append([[efficiency,plant_size,reproductive_energy],location_string])
                    else:
                        reproduction_queue.append([[efficiency,plant_size,reproductive_energy],location_string])


                plant_list[location][i][3] = energy
                plant_list[location][i][4] = real_size
                plant_list[location][i][5] = age

                if energy < 0:
                    plant_list[location][i] = "dead"
                    age_debug.append(age)
                    alive_count -= 1
                if age > 25:
                    plant_list[location][i] = "dead"
                    age_debug.append(age)
                    alive_count -= 1

                if age == 1 and energy < 0:
                    died_young_count += 1

    for i in range(len(reproduction_queue)):
        log.append(reproduce_plant(reproduction_queue[i][0],reproduction_queue[i][1]))

    print(str(alive_count) + ", " + str(died_young_count))
    if alive_count == 0:
        generate_plant()

    return age_debug

map = generate_empty_map()
generate_plant()

age_debug = []

start = time.time()
for i in range(100000):
    #print(str(i))
    age_debug += tick()
    #print(plant_list)
    #rint(len(plant_list))
end = time.time()
print(end - start)
#print(sum(age_debug)/len(age_debug))

f.close()

# printlog = []
#
# for i in range(len(log)):
#     if log[i] != "":
#         printlog.append(log[i])
#
# f = open("log.csv",'w+')
# for i in range(len(printlog)):
#     f.write(str(i) + "," + str(printlog[i]) + '\n')
# f.close()
