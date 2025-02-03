import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# ===========================
# 1. Library Import
# ===========================

# Pygame for window management and event handling
# PyOpenGL for 3D rendering
# NumPy for mathematical operations

# ===========================
# 2. Cube Initialization
# ===========================

# Define colors for cube faces (R, G, B)
colors_dict = {
    'W': (1, 1, 1),    # Up face (White)
    'Y': (1, 1, 0),    # Down face (Yellow)
    'R': (1, 0, 0),    # Front face (Red)
    'O': (1, 0.5, 0),  # Back face (Orange)
    'G': (0, 1, 0),    # Right face (Green)
    'B': (0, 0, 1),    # Left face (Blue)
    'K': (0, 0, 0)     # Black (for cubie base)
}

# Define the vertices of a cubie centered at the origin (full size)
cubie_size = 1.0  # Full size cubie
half_size = cubie_size / 2

cube_vertices = [
    [-half_size, -half_size, -half_size],  # 0
    [ half_size, -half_size, -half_size],  # 1
    [ half_size,  half_size, -half_size],  # 2
    [-half_size,  half_size, -half_size],  # 3
    [-half_size, -half_size,  half_size],  # 4
    [ half_size, -half_size,  half_size],  # 5
    [ half_size,  half_size,  half_size],  # 6
    [-half_size,  half_size,  half_size]   # 7
]

# Define the 6 faces of the cube, each face is a list of 4 vertex indices
# Ensure all faces have consistent vertex winding (counter-clockwise)
cube_faces = [
    [0, 1, 2, 3],  # Back face (z = -half_size)
    [4, 5, 6, 7],  # Front face (z = +half_size)
    [0, 4, 5, 1],  # Bottom face (y = -half_size)
    [3, 2, 6, 7],  # Top face (y = +half_size)
    [1, 5, 6, 2],  # Right face (x = +half_size)
    [0, 3, 7, 4]   # Left face (x = -half_size)
]

# Map faces to their normal vectors
face_normals = [
    (0, 0, -1),  # Back
    (0, 0, 1),   # Front
    (0, -1, 0),  # Bottom
    (0, 1, 0),   # Top
    (1, 0, 0),   # Right
    (-1, 0, 0)   # Left
]

# Map face normals to color codes
face_colors = {
    (0, 0, -1): 'O',  # Back face (Orange)
    (0, 0, 1): 'R',   # Front face (Red)
    (0, -1, 0): 'Y',  # Bottom face (Yellow)
    (0, 1, 0): 'W',   # Top face (White)
    (1, 0, 0): 'G',   # Right face (Green)
    (-1, 0, 0): 'B'   # Left face (Blue)
}

# Sticker size scale (fraction of the cubie face)
sticker_scale = 0.9  # Adjusted to ensure stickers don't overhang

# Offset to prevent Z-fighting
sticker_offset = 0.002  # Increased to avoid stickers being too deep

# Cubie class represents each small cube in the Rubik's Cube
class Cubie:
    def __init__(self, position):
        self.initial_position = np.array(position, dtype=float)
        self.position = np.array(position, dtype=float)
        self.rotation_matrix = np.identity(3)
        self.faces = []
        self.stickers = []
        self.create_faces_and_stickers()
        self.animating = False  # Flag to indicate if the cubie is animating
        self.animation_axis = None
        self.animation_angle_remaining = 0
        self.animation_speed = 0

    def create_faces_and_stickers(self):
        x, y, z = self.position
        for i, normal in enumerate(face_normals):
            nx, ny, nz = normal
            # Check if the face should have a sticker (on the outer layer)
            has_sticker = False
            if nx == 1 and x == 1:
                has_sticker = True
            elif nx == -1 and x == -1:
                has_sticker = True
            elif ny == 1 and y == 1:
                has_sticker = True
            elif ny == -1 and y == -1:
                has_sticker = True
            elif nz == 1 and z == 1:
                has_sticker = True
            elif nz == -1 and z == -1:
                has_sticker = True

            face = {
                'indices': cube_faces[i],
                'normal': np.array(normal, dtype=float),
            }
            self.faces.append(face)

            if has_sticker:
                # Precompute sticker vertices
                sticker_vertices = []
                face_vertices = [np.array(cube_vertices[vertex_index], dtype=float) for vertex_index in cube_faces[i]]
                face_center = np.mean(face_vertices, axis=0)
                normal = face['normal']
                for vertex in face_vertices:
                    direction = vertex - face_center
                    sticker_vertex = face_center + direction * sticker_scale
                    # Move the sticker slightly outward along the normal to avoid Z-fighting
                    sticker_vertex += normal * sticker_offset
                    sticker_vertices.append(sticker_vertex)
                sticker = {
                    'vertices': sticker_vertices,
                    'color_code': face_colors[tuple(normal)]
                }
                self.stickers.append(sticker)

    def start_animation(self, axis, angle, speed):
        self.animating = True
        self.animation_axis = axis
        self.animation_angle_remaining = angle
        self.animation_speed = speed

    def update(self):
        if self.animating:
            angle_step = np.sign(self.animation_angle_remaining) * min(abs(self.animation_speed), abs(self.animation_angle_remaining))
            self.rotate(self.animation_axis, angle_step)
            self.animation_angle_remaining -= angle_step
            if abs(self.animation_angle_remaining) < 0.01:
                self.animating = False
                self.animation_angle_remaining = 0
                self.animation_axis = None
                self.animation_speed = 0

    def rotate(self, axis, angle):
        # Update the rotation matrix
        rot_matrix = rotation_matrix(axis, angle)
        self.rotation_matrix = np.dot(rot_matrix, self.rotation_matrix)
        # Rotate position around the origin
        self.position = np.dot(rot_matrix, self.position)
        self.position = np.round(self.position, decimals=5)  # Avoid floating point errors

    def draw(self):
        glPushMatrix()
        # Move to the cubie's position
        glTranslatef(*self.position)
        # Apply the cubie's rotation
        glMultMatrixf(self.get_gl_matrix())
        # Draw the cubie as a black cube
        glBegin(GL_QUADS)
        glColor3fv(colors_dict['K'])
        for face in self.faces:
            normal = face['normal']
            glNormal3fv(normal)
            for vertex_index in face['indices']:
                vertex = cube_vertices[vertex_index]
                glVertex3fv(vertex)
        glEnd()
        # Draw the stickers
        glEnable(GL_POLYGON_OFFSET_FILL)
        glPolygonOffset(-1.0, -1.0)
        for sticker in self.stickers:
            glBegin(GL_QUADS)
            glColor3fv(colors_dict[sticker['color_code']])
            for vertex in sticker['vertices']:
                glVertex3fv(vertex)
            glEnd()
        glDisable(GL_POLYGON_OFFSET_FILL)
        glPopMatrix()

    def get_gl_matrix(self):
        # Convert the rotation matrix to a 4x4 OpenGL matrix
        mat = np.identity(4)
        mat[:3, :3] = self.rotation_matrix
        return mat.T.flatten()

# Helper function to create a rotation matrix
def rotation_matrix(axis, angle):
    axis = np.array(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)
    angle_rad = np.radians(angle)
    cos_a = np.cos(angle_rad)
    sin_a = np.sin(angle_rad)
    x, y, z = axis
    rot = np.array([
        [cos_a + x*x*(1 - cos_a),     x*y*(1 - cos_a) - z*sin_a, x*z*(1 - cos_a) + y*sin_a],
        [y*x*(1 - cos_a) + z*sin_a,   cos_a + y*y*(1 - cos_a),   y*z*(1 - cos_a) - x*sin_a],
        [z*x*(1 - cos_a) - y*sin_a,   z*y*(1 - cos_a) + x*sin_a, cos_a + z*z*(1 - cos_a)]
    ])
    return rot

# Create all cubies and store them in a list
cubies = []
for x in [-1, 0, 1]:
    for y in [-1, 0, 1]:
        for z in [-1, 0, 1]:
            cubie = Cubie((x, y, z))
            cubies.append(cubie)

# ===========================
# 3. User Interaction
# ===========================

# Initialize Pygame and PyOpenGL
pygame.init()
display = (800, 600)
pygame.display.gl_set_attribute(GL_DEPTH_SIZE, 24)  # Set depth buffer size to 24 bits
screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
pygame.display.set_caption('Rubik\'s Cube Simulator')

# Set up OpenGL perspective and camera
glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LEQUAL)  # Use less or equal depth testing
# glEnable(GL_CULL_FACE)  # Disable backface culling for now
glCullFace(GL_BACK)  # Specify culling of back faces
glFrontFace(GL_CCW)  # Set counter-clockwise vertex order as front face

# Set the background color to Visual Studio dark theme (RGB: 30, 30, 30)
glClearColor(30/255, 30/255, 30/255, 1.0)

# Variables to store the cube's rotation matrix
cube_rotation_matrix = np.identity(4, dtype=float)

# Function to rotate the entire cube
def rotate_cube(axis, angle):
    global cube_rotation_matrix
    rot_matrix = np.identity(4)
    rot_matrix[:3, :3] = rotation_matrix(axis, angle)
    cube_rotation_matrix = np.dot(rot_matrix, cube_rotation_matrix)

# Queue for face rotations (to prevent multiple rotations at once)
face_rotation_queue = []

# Function to rotate a specific face with animation
def rotate_face(face, angle_degrees):
    if face_rotation_queue:
        return  # Don't start a new rotation until the current one is finished

    angle = angle_degrees
    if face == 'F':  # Front face (z = 1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[2]) == 1]
        axis = (0, 0, 1)
    elif face == 'B':  # Back face (z = -1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[2]) == -1]
        axis = (0, 0, -1)
    elif face == 'U':  # Up face (y = 1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[1]) == 1]
        axis = (0, 1, 0)
    elif face == 'D':  # Down face (y = -1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[1]) == -1]
        axis = (0, -1, 0)
    elif face == 'R':  # Right face (x = 1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[0]) == 1]
        axis = (1, 0, 0)
    elif face == 'L':  # Left face (x = -1)
        cubies_to_rotate = [cubie for cubie in cubies if round(cubie.position[0]) == -1]
        axis = (-1, 0, 0)
    else:
        return  # Invalid face input

    # Start animation for each cubie on the face
    for cubie in cubies_to_rotate:
        cubie.start_animation(axis, angle, angle / 10.0)  # Rotate over 10 frames

    face_rotation_queue.append(True)  # Add a placeholder to indicate rotation in progress

# ===========================
# 4. State Management
# ===========================

# The internal state of the cube is maintained within each cubie.
# Each cubie has a position and a rotation matrix.
# Rotations are applied to the cubie's rotation matrix and position.

# ===========================
# 5. Algorithm Integration (Placeholder)
# ===========================

# Placeholder for integrating solving algorithms
# You can access and manipulate the cube's state using the cubies list
# Each cubie has:
# - position: cubie.position
# - rotation matrix: cubie.rotation_matrix
# - initial position: cubie.initial_position
# - faces: cubie.faces

# ===========================
# Main Loop
# ===========================

running = True
clock = pygame.time.Clock()
while running:
    clock.tick(60)  # Limit FPS to 60
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle keyboard input
        elif event.type == pygame.KEYDOWN:
            # Rotate faces with specific keys
            if event.key == pygame.K_f:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('F', -90)
                else:
                    rotate_face('F', 90)
            elif event.key == pygame.K_b:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('B', -90)
                else:
                    rotate_face('B', 90)
            elif event.key == pygame.K_u:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('U', -90)
                else:
                    rotate_face('U', 90)
            elif event.key == pygame.K_d:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('D', -90)
                else:
                    rotate_face('D', 90)
            elif event.key == pygame.K_r:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('R', -90)
                else:
                    rotate_face('R', 90)
            elif event.key == pygame.K_l:
                if event.mod & pygame.KMOD_SHIFT:
                    rotate_face('L', -90)
                else:
                    rotate_face('L', 90)

    # Continuous cube rotation with arrow keys
    keys = pygame.key.get_pressed()
    rotation_speed = 2  # Degrees per frame
    if keys[pygame.K_LEFT]:
        rotate_cube((0, 1, 0), rotation_speed)
    if keys[pygame.K_RIGHT]:
        rotate_cube((0, 1, 0), -rotation_speed)
    if keys[pygame.K_UP]:
        rotate_cube((1, 0, 0), rotation_speed)
    if keys[pygame.K_DOWN]:
        rotate_cube((1, 0, 0), -rotation_speed)

    # Update animations
    animating = False
    for cubie in cubies:
        cubie.update()
        if cubie.animating:
            animating = True

    # If no cubies are animating, clear the rotation queue
    if not animating and face_rotation_queue:
        face_rotation_queue.pop(0)

    # Clear the screen and depth buffer
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Reset the modelview matrix
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -10)

    # Apply cube rotations
    glMultMatrixf(cube_rotation_matrix.T)

    # Draw all cubies
    for cubie in cubies:
        cubie.draw()

    pygame.display.flip()

pygame.quit()
