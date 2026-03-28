import bpy
import bmesh
import math
import random
from collections import deque

# Maze configuration
MAZE_SIZE = 15  # Odd number for proper maze
cell_size = 1.0
wall_height = 2.0
wall_thickness = 0.15

def clear_scene():
    """Clear the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

def create_material(name, color, roughness=0.7, metallic=0.0, emission=0.0):
    """Create a material."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    output = nodes.new('ShaderNodeOutputMaterial')
    
    bsdf.inputs['Base Color'].default_value = color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic
    
    # Emission handled via Emission shader node for older Blender compatibility
    if emission > 0:
        emission_node = nodes.new('ShaderNodeEmission')
        emission_node.inputs['Color'].default_value = (*color[:3], 1.0)
        emission_node.inputs['Strength'].default_value = emission
        
        # Mix with Principled BSDF
        mix = nodes.new('ShaderNodeMixShader')
        mix.inputs['Fac'].default_value = 0.5
        
        mat.node_tree.links.new(bsdf.outputs['BSDF'], mix.inputs[1])
        mat.node_tree.links.new(emission_node.outputs['Emission'], mix.inputs[2])
        mat.node_tree.links.new(mix.outputs['Shader'], output.inputs['Surface'])
    
    # Only link principled if not using emission
    if emission == 0:
        mat.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    return mat

def create_wall(x, y, width, depth, height, name="Wall"):
    """Create a wall cube."""
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(x, y, height/2)
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width, depth, height)
    bpy.ops.object.shade_smooth()
    return obj

def create_floor(size, name="Floor"):
    """Create the maze floor."""
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(0, 0, -0.05)
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size * cell_size, size * cell_size, 0.1)
    bpy.ops.object.shade_smooth()
    return obj

def create_start_marker(x, y, name="Start"):
    """Create a glowing green start marker."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.3,
        depth=0.1,
        location=(x, y, 0.05)
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj

def create_end_marker(x, y, name="End"):
    """Create a glowing red end marker."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.3,
        depth=0.1,
        location=(x, y, 0.05)
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.shade_smooth()
    return obj

def generate_maze(size):
    """Generate a perfect maze using recursive backtracking."""
    # Initialize grid with all walls
    maze = [[1 for _ in range(size)] for _ in range(size)]
    
    def is_valid(x, y):
        return 0 <= x < size and 0 <= y < size
    
    def carve(x, y):
        maze[y][x] = 0  # Mark as path
        
        # Randomize directions
        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if is_valid(nx, ny) and maze[ny][nx] == 1:
                # Carve wall between
                maze[y + dy//2][x + dx//2] = 0
                carve(nx, ny)
    
    # Start from top-left corner
    carve(1, 1)
    
    # Ensure start and end are clear
    maze[1][1] = 0  # Start
    maze[size-2][size-2] = 0  # End
    
    return maze

def find_solution_path(maze, size):
    """Find the shortest path from start to end using BFS."""
    start = (1, 1)
    end = (size-2, size-2)
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        (x, y), path = queue.popleft()
        
        if (x, y) == end:
            return path
        
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size:
                if maze[ny][nx] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
    
    return []

def create_maze_scene():
    """Create the complete maze scene."""
    
    # Materials
    wall_mat = create_material("WallMat", (0.3, 0.25, 0.35, 1.0), roughness=0.9)  # Dark purple-gray
    floor_mat = create_material("FloorMat", (0.15, 0.15, 0.2, 1.0), roughness=0.95)  # Dark floor
    path_mat = create_material("PathMat", (0.25, 0.25, 0.3, 1.0), roughness=0.8)  # Slightly lighter path
    start_mat = create_material("StartMat", (0.2, 0.9, 0.3, 1.0), emission=2.0)  # Glowing green
    end_mat = create_material("EndMat", (0.9, 0.2, 0.2, 1.0), emission=2.0)  # Glowing red
    gem_mat = create_material("GemMat", (1.0, 0.8, 0.2, 1.0), roughness=0.1, metallic=0.8, emission=0.5)  # Gold gem
    
    # Generate maze
    maze = generate_maze(MAZE_SIZE)
    solution_path = find_solution_path(maze, MAZE_SIZE)
    
    print(f"Maze generated: {MAZE_SIZE}x{MAZE_SIZE}")
    print(f"Solution path length: {len(solution_path)} steps")
    
    # Calculate offset to center the maze
    offset_x = -(MAZE_SIZE * cell_size) / 2
    offset_y = -(MAZE_SIZE * cell_size) / 2
    
    # Create floor
    floor = create_floor(MAZE_SIZE, "Floor")
    floor.data.materials.append(floor_mat)
    
    # Create path indicators (subtle visual guides)
    path_cells = []
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            if maze[y][x] == 0:
                # Create subtle floor tile for path
                px = offset_x + x * cell_size
                py = offset_y + y * cell_size
                
                # Small floor tile for walkable areas
                bpy.ops.mesh.primitive_cube_add(
                    size=1,
                    location=(px, py, 0.001)
                )
                tile = bpy.context.active_object
                tile.name = f"Path_{x}_{y}"
                tile.scale = (cell_size * 0.9, cell_size * 0.9, 0.01)
                tile.data.materials.append(path_mat)
                path_cells.append((x, y, px, py))
    
    # Create walls
    walls = []
    for y in range(MAZE_SIZE):
        for x in range(MAZE_SIZE):
            if maze[y][x] == 1:
                wx = offset_x + x * cell_size
                wy = offset_y + y * cell_size
                
                wall = create_wall(
                    wx, wy,
                    cell_size, cell_size, wall_height,
                    f"Wall_{x}_{y}"
                )
                wall.data.materials.append(wall_mat)
                walls.append(wall)
    
    # Add corner pillars for visual interest
    for y in range(0, MAZE_SIZE + 1, 2):
        for x in range(0, MAZE_SIZE + 1, 2):
            px = offset_x + x * cell_size - cell_size/2
            py = offset_y + y * cell_size - cell_size/2
            
            if 0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE:
                bpy.ops.mesh.primitive_cylinder_add(
                    radius=0.12,
                    depth=wall_height + 0.2,
                    location=(px, py, wall_height/2)
                )
                pillar = bpy.context.active_object
                pillar.name = f"Pillar_{x}_{y}"
                pillar.data.materials.append(wall_mat)
    
    # Create start marker
    start_x = offset_x + 1 * cell_size
    start_y = offset_y + 1 * cell_size
    start_marker = create_start_marker(start_x, start_y, "StartMarker")
    start_marker.data.materials.append(start_mat)
    
    # Create end marker
    end_x = offset_x + (MAZE_SIZE - 2) * cell_size
    end_y = offset_y + (MAZE_SIZE - 2) * cell_size
    end_marker = create_end_marker(end_x, end_y, "EndMarker")
    end_marker.data.materials.append(end_mat)
    
    # Add a floating gem at the end
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=2,
        radius=0.25,
        location=(end_x, end_y, wall_height * 0.7)
    )
    gem = bpy.context.active_object
    gem.name = "EndGem"
    gem.data.materials.append(gem_mat)
    
    # Animate gem rotation (will be exported as static, animated in Three.js)
    
    # Create boundary walls (outer frame)
    frame_thickness = 0.3
    # Top
    create_wall(0, offset_y - cell_size/2 - frame_thickness/2, 
                MAZE_SIZE * cell_size + frame_thickness * 2, frame_thickness, wall_height, "Frame_Top")
    # Bottom  
    create_wall(0, offset_y + MAZE_SIZE * cell_size - cell_size/2 + frame_thickness/2,
                MAZE_SIZE * cell_size + frame_thickness * 2, frame_thickness, wall_height, "Frame_Bottom")
    # Left
    create_wall(offset_x - cell_size/2 - frame_thickness/2, 0,
                frame_thickness, MAZE_SIZE * cell_size, wall_height, "Frame_Left")
    # Right
    create_wall(offset_x + MAZE_SIZE * cell_size - cell_size/2 + frame_thickness/2, 0,
                frame_thickness, MAZE_SIZE * cell_size, wall_height, "Frame_Right")
    
    # Set up camera
    bpy.ops.object.select_by_type(type='CAMERA')
    bpy.ops.object.delete()
    
    bpy.ops.object.camera_add(location=(0, 0, MAZE_SIZE * cell_size * 0.9))
    camera = bpy.context.active_object
    camera.rotation_euler = (0, 0, math.radians(180))
    bpy.context.scene.camera = camera
    
    # Set up lighting
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()
    
    # Ambient
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    sun = bpy.context.active_object
    sun.data.energy = 2
    sun.data.color = (1.0, 0.95, 0.9)
    
    # Fill
    bpy.ops.object.light_add(type='AREA', location=(-5, -5, 5))
    fill = bpy.context.active_object
    fill.data.energy = 100
    fill.data.color = (0.8, 0.85, 1.0)
    
    # Start glow
    bpy.ops.object.light_add(type='POINT', location=(start_x, start_y, 1))
    start_light = bpy.context.active_object
    start_light.data.energy = 50
    start_light.data.color = (0.2, 1.0, 0.3)
    
    # End glow
    bpy.ops.object.light_add(type='POINT', location=(end_x, end_y, 1))
    end_light = bpy.context.active_object
    end_light.data.energy = 50
    end_light.data.color = (1.0, 0.2, 0.2)
    
    # Save solution path data for the game
    solution_data = []
    for x, y in solution_path:
        px = offset_x + x * cell_size
        py = offset_y + y * cell_size
        solution_data.append((px, py))
    
    print(f"Start position: ({start_x}, {start_y})")
    print(f"End position: ({end_x}, {end_y})")
    print(f"Maze size: {MAZE_SIZE}x{MAZE_SIZE}")
    
    return maze, solution_data, (start_x, start_y), (end_x, end_y)

def export_gltf(filepath):
    """Export the scene as GLTF."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        export_format='GLB',
        export_yup=True,
        export_materials='EXPORT',
        export_cameras=True,
        export_lights=True,
        export_apply=True
    )
    print(f"Exported to {filepath}")

# Main execution
if __name__ == "__main__":
    clear_scene()
    maze, solution, start_pos, end_pos = create_maze_scene()
    
    # Export maze
    export_gltf("/home/freeman/.openclaw/workspace/maze-game/maze.glb")
    
    # Save solution path for the game (will be embedded in JS)
    print("\n=== SOLUTION PATH (for game validation) ===")
    print(f"Start: {start_pos}")
    print(f"End: {end_pos}")
    print(f"Path length: {len(solution)} steps")
    print("\nMaze exported successfully!")