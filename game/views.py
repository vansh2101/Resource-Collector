import time
from django.shortcuts import render
import random

# Create your views here.

#? global vars
START = 0
INITIAL_STEPS = 50
INITIAL_ENERGY = 3
STEP_PER_DAY = 16

MAP = {
    0: {38, 1},
    1: {2, 0},
    2: {3, 1},
    3: {4, 2},
    4: {5, 3},
    5: {47, 6, 4},
    6: {7, 5},
    7: {8, 6},
    8: {9, 7},
    9: {10, 8},
    10: {48, 11, 9},
    11: {12, 10},
    12: {13, 11},
    13: {53, 14, 12},
    14: {15, 13},
    15: {16, 14},
    16: {17, 15},
    17: {60, 18, 16},
    18: {19, 17},
    19: {20, 18},
    20: {21, 19},
    21: {61, 22, 20},
    22: {23, 21},
    23: {24, 22},
    24: {25, 23},
    25: {26, 24},
    26: {27, 25},
    27: {28, 26},
    28: {29, 27},
    29: {30, 28},
    30: {31, 29},
    31: {72, 32, 30},
    32: {33, 31},
    33: {34, 32},
    34: {35, 33},
    35: {39, 36, 34},
    36: {37, 35},
    37: {38, 36},
    38: {37, 0},
    39: {40, 35},
    40: {41, 39},
    41: {42, 40},
    42: {43, 41},
    43: {69, 44, 42},
    44: {45, 43},
    45: {49, 48, 46, 44},
    46: {47, 45},
    47: {46, 5},
    48: {45, 10},
    49: {50, 45},
    50: {51, 49},
    51: {52, 50},
    52: {55, 54, 53, 51},
    53: {52, 13},
    54: {66, 52},
    55: {56, 52},
    56: {63, 57, 55},
    57: {58, 56},
    58: {59, 57},
    59: {61, 60, 58},
    60: {59, 17},
    61: {59, 21},
    62: {},
    63: {64, 56},
    64: {70, 65, 63},
    65: {66, 64},
    66: {67, 65, 54},
    67: {68, 66},
    68: {69, 67},
    69: {68, 43},
    70: {71, 64},
    71: {72, 70},
    72: {71, 31},
}

DOTTED = {
    3: {42},
    13: {45},
    28: {62},
    33: {66},
    42: {3},
    45: {13},
    58: {62},
    62: {28, 58},
    66: {33},
}

RESOURCES = {
    3: "Food",
    7: "Antenna",
    13: "Automatic Guns",
    17: "Solar Panel",
    26: "Manual",
    33: "Circuit",
    45: "Tools",
    56: "Medication",
    62: "Space Satellite",
    66: "Fuel",
    21: "KEY"
}

OBJECTIVES = {
    "Food",
    "Antenna",
    "Automatic Guns",
    "Solar Panel",
    "Manual",
    "Circuit",
    "Tools",
    "Medication",
    "Space Satellite",
    "Fuel",
}

INF = float('inf')

def shortest_path(ACTION):
    visited = [False] * 100
    path = []

    track = []
    totaldays = []
    count = [0]

    def solve(index, inventory, steps, energy, time, ACTION, launch=0, days=0, idle=2):
        if visited[index]:
            return INF

        if time == 0:
            if (index != START) and (index not in RESOURCES):
                return INF

            days += 1
            steps += 5
            energy = 3
            time = 16

        if index in RESOURCES:
            inventory = tuple(sorted(set(inventory + (RESOURCES[index],))))

        if index in ACTION:
            if ACTION[index] == 'negative':
                steps -= 5

            if ACTION[index] == 'lock':
                if "KEY" not in inventory:
                    return INF

            if ACTION[index] == 'swords':
                energy -= 1

            if ACTION[index] == 'launch':
                launch += 1

        if energy <= 0:
            return INF

        if all(item in inventory for item in OBJECTIVES):
            path.append(index)
            days += 1

            track.append(path[count[-1]:])
            totaldays.append(days)
            count.append(len(path))

            return days

        if steps <= 0:
            return INF

        mini = INF

        if launch > 0 and (index in DOTTED):
            for dotted_adjacent in DOTTED[index]:
                visited[index] = True
                path.append(index)
                mini = min(mini, solve(dotted_adjacent, inventory, steps-1, energy, time-1, ACTION, launch-1, days, idle))

                if mini == INF:
                    path.pop()
                else:
                    pass

                visited[index] = False

        for adjacent in MAP[index]:
            visited[index] = True
            path.append(index)
            mini = min(mini, solve(adjacent, inventory, steps-1, energy, time-1, ACTION, launch, days, idle))

            if mini == INF:
                path.pop()

            visited[index] = False

        if idle:
            mini = min(mini, solve(index, inventory, steps, energy, 0, ACTION, launch, days, idle-1))

        return mini

    res = solve(index=START, inventory=(), steps=INITIAL_STEPS, energy=INITIAL_ENERGY, time=STEP_PER_DAY, ACTION=ACTION)

    try:
        shortest = track[totaldays.index(min(totaldays))]
    except ValueError:
        shortest = 'No path Possible'

    return res, shortest


def generate_blocks(block):
    pos = random.randint(1, 72)

    if pos in RESOURCES:
        pos = generate_blocks(block)

    return pos


def home(request):
    return render(request, 'home.html')


def game(request):
    ACTION = {}

    data = {'negative': request.POST['negative'], 'swords': request.POST['swords'], 'launch': request.POST['launch'], 'lock': request.POST['lock']}

    for block in data:
            for i in range(int(data[block])):
                ACTION[generate_blocks(block)] = block

    time.sleep(1.5)

    shortest = shortest_path(ACTION)

    return render(request, 'game.html', {'blocks': list(ACTION.values()), 'pos': list(ACTION.keys()), 'day': shortest[0], 'path': shortest[1]})