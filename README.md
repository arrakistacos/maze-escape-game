# ⏱️ 30-Second Maze Escape 🏃

A high-pressure maze escape game where you have just 30 seconds to trace the correct path from start to finish. Touch the green start marker, drag your finger through the maze to the red finish marker before time runs out!

## 🎮 How to Play

1. **Touch the GREEN marker** to start
2. **Drag your finger** to trace a path through the maze
3. **Reach the RED marker** before the 30-second timer hits zero
4. **Don't touch walls!** If you hit a wall or let go, you fail
5. **Escape** before time runs out!

## 🎯 Features

- **3D Procedural Maze**: Generated using recursive backtracking algorithm in Blender
- **30-Second Timer**: High-pressure countdown with danger animation under 5 seconds
- **Touch/Finger Tracing**: Draw your path through the maze
- **Collision Detection**: Instant fail if you touch walls
- **Atmospheric 3D**: Dark purple theme with glowing markers
- **Win/Lose States**: Confetti celebration or try again
- **Responsive**: Works on mobile (touch) and desktop (mouse)

## 🛠️ Tech Stack

- **Blender 4.2.3** - Procedural maze generation with Python
- **Three.js** - 3D rendering with touch interaction
- **GitHub Pages** - Free hosting

## 🚀 Play Now

**Live Game**: https://arrakistacos.github.io/maze-escape-game

## 📁 Files

| File | Description |
|------|-------------|
| `index.html` | The complete game with Three.js |
| `maze.glb` | 3D maze model (generated procedurally) |
| `create_maze.py` | Blender Python script for maze generation |

## 🎨 Maze Design

- **Size**: 15x15 grid
- **Algorithm**: Recursive backtracking (perfect maze)
- **Visual**: Dark purple walls, subtle path tiles
- **Markers**: Glowing green (start) and red (finish)
- **Atmosphere**: Fog, point lights, dramatic lighting

## 📝 Controls

| Action | Mobile | Desktop |
|--------|--------|---------|
| Start | Touch green marker | Click green marker |
| Trace | Drag finger | Drag mouse |
| Reset | "Play Again" button | "Play Again" button |
| Camera | Auto-rotates | Auto-rotates |

## 🏆 Tips

- **Plan your route** before starting - the timer starts when you touch the start marker
- **Stay in the center** of paths to avoid walls
- **Don't lift your finger/mouse** until you reach the finish!

---

Created with ⚡ by AI (OpenClaw + Blender + Three.js)