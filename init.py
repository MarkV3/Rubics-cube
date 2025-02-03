import numpy as np
import yaml

color_id = {
    "EMPTY": -1,
    "WHITE": 0,
    "RED": 1,
    "BLUE": 2,
    "GREEN": 3,
    "ORANGE": 4,
    "YELLOW": 5
}

side_to_idx = {
    "UP": [[i, j] for i in range(0, 3) for j in range(3, 6)],
    "DOWN": [[i, j] for i in range(6, 9) for j in range(3, 6)],
    "FRONT": [[i, j] for i in range(3, 6) for j in range(3, 6)],
    "LEFT": [[i, j] for i in range(3, 6) for j in range(0, 3)],
    "RIGHT": [[i, j] for i in range(3, 6) for j in range(6, 9)],
    "BACK": [[i, j] for i in range(3, 6) for j in range(9, 12)]
}


def fill_cube_side(array, idx_arr, color):
    for i, j in idx_arr:
        array[i, j] = color


def get_cube():
    cube = np.full((9, 12), fill_value=-1)
    fill_cube_side(cube, side_to_idx['UP'], color_id['WHITE'])
    fill_cube_side(cube, side_to_idx['DOWN'], color_id['YELLOW'])
    fill_cube_side(cube, side_to_idx['FRONT'], color_id['BLUE'])
    fill_cube_side(cube, side_to_idx['LEFT'], color_id['RED'])
    fill_cube_side(cube, side_to_idx['RIGHT'], color_id['ORANGE'])
    fill_cube_side(cube, side_to_idx['BACK'], color_id['GREEN'])
    return cube

def get_turns_list():
    with open(f'moves.yml','r') as f:
        turns_idx = yaml.safe_load(f)


def make_turn(array, side, turns):
    flatten_array = np.ravel(array.copy())
    rotated_array = flatten_array[turns[side]]
    return np.reshape(rotated_array, array.shape)


def get_face_data(cube_data, face_index):
    if face_index == 0:  # Front face
        return cube_data[3:6, 3:6]
    elif face_index == 1:  # Back face
        return cube_data[3:6, 9:12]
    elif face_index == 2:  # Left face
        return cube_data[3:6, 0:3]
    elif face_index == 3:  # Right face
        return cube_data[3:6, 6:9]
    elif face_index == 4:  # Up face
        return cube_data[0:3, 3:6]
    elif face_index == 5:  # Down face
        return cube_data[6:9, 3:6]

'''
with open('moves.yml', 'w') as outfile:
    yaml.dump(turns_idx, outfile, default_flow_style=False)
'''