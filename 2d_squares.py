import pygame
import math
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Rubik's Cube with Rotations")

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Define cube properties
CUBE_SIZE = 300
SQUARE_SIZE = CUBE_SIZE // 3

class Square:
    def __init__(self, face: int, row: int, col: int, color: Tuple[int, int, int]):
        self.face = face
        self.row = row
        self.col = col
        self.color = color

    def get_corners(self) -> List[Tuple[float, float, float]]:
        x, y, z = 0, 0, 0
        offset = CUBE_SIZE / 3
        if self.face == 0:  # Front
            x, y, z = (self.col - 1) * SQUARE_SIZE, (self.row - 1) * SQUARE_SIZE, -offset
        elif self.face == 1:  # Right
            x, y, z = 2*offset, (self.row - 1) * SQUARE_SIZE, -(self.col - 1) * SQUARE_SIZE
        elif self.face == 2:  # Back
            x, y, z = -(self.col - 1) * SQUARE_SIZE, (self.row - 1) * SQUARE_SIZE, 2*offset
        elif self.face == 3:  # Left
            x, y, z = -offset, (self.row - 1) * SQUARE_SIZE, (self.col - 1) * SQUARE_SIZE
        elif self.face == 4:  # Top
            x, y, z = (self.col - 1) * SQUARE_SIZE, -offset, -(self.row - 1) * SQUARE_SIZE
        elif self.face == 5:  # Bottom
            x, y, z = (self.col - 1) * SQUARE_SIZE, 2*offset, (self.row - 1) * SQUARE_SIZE

        corners = [
            (x, y, z),
            (x + SQUARE_SIZE, y, z),
            (x + SQUARE_SIZE, y + SQUARE_SIZE, z),
            (x, y + SQUARE_SIZE, z)
        ]

        if self.face in [1, 3]:  # Right and Left faces
            corners = [
                (x, y, z),
                (x, y + SQUARE_SIZE, z),
                (x, y + SQUARE_SIZE, z + SQUARE_SIZE),
                (x, y, z + SQUARE_SIZE)
            ]
        elif self.face in [4, 5]:  # Top and Bottom faces
            corners = [
                (x, y, z),
                (x + SQUARE_SIZE, y, z),
                (x + SQUARE_SIZE, y, z + SQUARE_SIZE),
                (x, y, z + SQUARE_SIZE)
            ]

        return corners

class Cube:
    def __init__(self):
        self.squares = self._create_squares()

    def _create_squares(self) -> List[Square]:
        squares = []
        colors = [BLUE, RED, GREEN, ORANGE, WHITE, YELLOW]
        for face in range(6):
            for row in range(3):
                for col in range(3):
                    squares.append(Square(face, row, col, colors[face]))
        return squares

    def rotate_face(self, face: int, clockwise: bool):
        # Rotate the squares on the face
        face_squares = [s for s in self.squares if s.face == face]
        new_positions = {}
        for square in face_squares:
            if clockwise:
                new_row, new_col = square.col, 2 - square.row
            else:
                new_row, new_col = 2 - square.col, square.row
            new_positions[square] = (new_row, new_col)
        
        for square, (new_row, new_col) in new_positions.items():
            square.row, square.col = new_row, new_col

        # Define adjacent faces and their affected rows/columns
        adjacent_faces = {
            0: [(4, 2, 1), (1, 1, 2), (5, 0, 2), (3, 1, 0)],  # Front / Blue
            1: [(4, 1, 2), (2, 1, 0), (5, 1, 2), (0, 1, 2)],  # Right / Red
            2: [(4, 0, 1), (3, 1, 2), (5, 2, 1), (1, 1, 0)],  # Back / Green
            3: [(4, 1, 0), (0, 1, 0), (5, 1, 0), (2, 1, 2)],  # Left / Orange
            4: [(2, 0, 1), (1, 0, 1), (0, 0, 1), (3, 0, 1)],  # Top / White
            5: [(0, 2, 1), (1, 2, 1), (2, 2, 1), (3, 2, 1)]   # Bottom / Yellow
        }

        # Get the squares on the edges of adjacent faces
        edge_squares = []
        for adj_face, row, col in adjacent_faces[face]:
            if row == 1:  # Vertical edge
                edge_squares.append([s for s in self.squares if s.face == adj_face and s.col == col])
            else:  # Horizontal edge
                edge_squares.append([s for s in self.squares if s.face == adj_face and s.row == row])

        # Rotate edge squares
        if clockwise:
            temp = edge_squares[0][:]
            edge_squares[0][:] = edge_squares[3][::-1]
            edge_squares[3][:] = edge_squares[2][:]
            edge_squares[2][:] = edge_squares[1][::-1]
            edge_squares[1][:] = temp
        else:
            temp = edge_squares[0][:]
            edge_squares[0][:] = edge_squares[1][:]
            edge_squares[1][:] = edge_squares[2][::-1]
            edge_squares[2][:] = edge_squares[3][:]
            edge_squares[3][:] = temp[::-1]

        # Update the squares with their new positions
        for i, edge in enumerate(edge_squares):
            adj_face, row, col = adjacent_faces[face][i]
            for j, square in enumerate(edge):
                if row == 1:  # Vertical edge
                    square.face, square.row, square.col = adj_face, j, col
                else:  # Horizontal edge
                    square.face, square.row, square.col = adj_face, row, j

    def draw(self, screen: pygame.Surface, rotation_x: float, rotation_y: float):
        def rotate_point(x: float, y: float, z: float, rx: float, ry: float) -> Tuple[float, float, float]:
            # Rotate around Y-axis
            x, z = (x * math.cos(ry) - z * math.sin(ry),
                    x * math.sin(ry) + z * math.cos(ry))
            # Rotate around X-axis
            y, z = (y * math.cos(rx) - z * math.sin(rx),
                    y * math.sin(rx) + z * math.cos(rx))
            return x, y, z

        def project(x: float, y: float, z: float) -> Tuple[int, int]:
            f = 500
            scale = f / (f + z + CUBE_SIZE)
            return int(x * scale + WIDTH // 2), int(-y * scale + HEIGHT // 2)

        # Group squares by face
        face_squares = [[] for _ in range(6)]
        for square in self.squares:
            face_squares[square.face].append(square)

        # Calculate the average z-coordinate for each face
        face_z_coords = []
        for face in face_squares:
            avg_z = sum(rotate_point(*square.get_corners()[0], rotation_x, rotation_y)[2] for square in face) / len(face)
            face_z_coords.append((avg_z, face))

        # Sort faces based on their average z-coordinate
        sorted_faces = sorted(face_z_coords, key=lambda x: x[0], reverse=True)

        # Draw faces from back to front
        for _, face in sorted_faces:
            for square in face:
                corners = square.get_corners()
                rotated_corners = [rotate_point(*corner, rotation_x, rotation_y) for corner in corners]
                projected_corners = [project(*corner) for corner in rotated_corners]

                pygame.draw.polygon(screen, square.color, projected_corners)
                pygame.draw.polygon(screen, BLACK, projected_corners, 1)

def main():
    cube = Cube()
    running = True
    clock = pygame.time.Clock()
    rotation_x, rotation_y = math.pi / 6, -math.pi / 4  # Initial rotation for better view

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    cube.rotate_face(0, True)  # Rotate front face clockwise
                elif event.key == pygame.K_r:
                    cube.rotate_face(1, True)  # Rotate right face clockwise
                elif event.key == pygame.K_b:
                    cube.rotate_face(2, True)  # Rotate back face clockwise
                elif event.key == pygame.K_l:
                    cube.rotate_face(3, True)  # Rotate left face clockwise
                elif event.key == pygame.K_t:
                    cube.rotate_face(4, True)  # Rotate top face clockwise
                elif event.key == pygame.K_d:
                    cube.rotate_face(5, True)  # Rotate bottom face clockwise

        keys = pygame.key.get_pressed()
        rotation_speed = 0.02
        if keys[pygame.K_LEFT]:
            rotation_y -= rotation_speed
        if keys[pygame.K_RIGHT]:
            rotation_y += rotation_speed
        if keys[pygame.K_UP]:
            rotation_x -= rotation_speed
        if keys[pygame.K_DOWN]:
            rotation_x += rotation_speed

        screen.fill((30, 30, 30))
        cube.draw(screen, rotation_x, rotation_y)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()