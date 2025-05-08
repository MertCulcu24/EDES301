# Etch-a-Sketch PCB Project

## Project Overview
This project is a PCB design for an Etch-a-Sketch game using the PocketBeagle as the main processor. The design includes a custom PCB that connects the PocketBeagle to various components to create a functional electronic version of the classic Etch-a-Sketch toy.

## Features
- **SPI Display**: Shows the drawing created by the user
- **Dual Potentiometers**: Control horizontal and vertical movement
- **Push Buttons**: Reset the drawing and change colors
- **RGB LEDs**: Indicate the currently selected color
- **USB Port**: Provides power and potential connectivity for expansion

## Repository Structure
```
project_02/
├── EAGLE/
│   ├── etch_a_sketch.lbr  # Custom component library
│   ├── etch_a_sketch.sch  # Schematic design
│   └── etch_a_sketch.brd  # PCB layout
├── docs/
│   ├── mechanical_diagram.pdf  # Physical layout diagram
│   ├── top_layer_screenshot.png  # PCB top layer view
│   └── bottom_layer_screenshot.png  # PCB bottom layer view
├── MFG/
│   ├── etch_a_sketch_bom.csv  # Bill of Materials
│   └── [gerber files]  # Manufacturing files for PCB production
└── README.md 
```

## Design Specifications
- **Board Size**: 4" x 5" maximum
- **Layers**: 4-layer PCB design
- **Design Rules**:
  - Signal traces: 10 mil width / 10 mil spacing
  - Power/ground traces: 15 mil width / 15 mil spacing
  - Vias: 12 mil drill / 24 mil pad

## Component List
- PocketBeagle single-board computer
- 2.8" SPI TFT Display
- 2x 10kΩ potentiometers (for X and Y control)
- 2x push buttons (reset and color change)
- 3x LEDs (red, green, blue)
- USB connector
- Various resistors and supporting components

## How to Use
1. Assemble the PCB with all components listed in the BOM
2. Power the board via USB
3. Press the color button to change drawing color
4. Press the reset button to clear the screen

## Manufacturing
This PCB was designed to be manufactured using standard PCB fabrication processes. The Gerber files in the MFG folder can be sent to any PCB manufacturer for production.

## Course Information
- **Course**: EDES301 - PCB Design
- **Due Date**: May 6, 2025
- **Instructor**: Dr. Welsh

## License
All design files are provided for educational purposes.

## Contact
mc205@rice.edu