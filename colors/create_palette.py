import struct
import argparse
import os

def hex_to_rgb(hex_color):
    """Convert hex color to RGB (0-1 range for ASE, 0-255 for ACO)"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def create_ase(colors_with_names, filename):
    """Create Adobe Swatch Exchange (.ase) file"""
    with open(filename, 'wb') as f:
        # Header
        f.write(b'ASEF')  # Signature
        f.write(struct.pack('>HH', 1, 0))  # Version (1.0)
        f.write(struct.pack('>I', len(colors_with_names)))  # Number of blocks
        
        for name, hex_color in colors_with_names:
            r, g, b = hex_to_rgb(hex_color)
            # Convert to 0-1 range
            r, g, b = r/255.0, g/255.0, b/255.0
            
            # Color entry block
            f.write(struct.pack('>H', 0x0001))  # Block type (color entry)
            
            # Name (UTF-16BE encoded with null terminator)
            name_utf16 = (name + '\0').encode('utf-16-be')
            block_length = 4 + len(name_utf16) + 2 + 4 + 3*4 + 2
            f.write(struct.pack('>I', block_length))
            f.write(struct.pack('>H', len(name) + 1))  # Name length
            f.write(name_utf16)
            
            # Color mode (RGB)
            f.write(b'RGB ')
            # RGB values (32-bit floats)
            f.write(struct.pack('>fff', r, g, b))
            # Color type (0 = Global, 1 = Spot, 2 = Normal)
            f.write(struct.pack('>H', 2))

def create_aco(colors_with_names, filename):
    """Create Adobe Color (.aco) file"""
    with open(filename, 'wb') as f:
        # Version 1
        f.write(struct.pack('>HH', 1, len(colors_with_names)))
        for _, hex_color in colors_with_names:
            r, g, b = hex_to_rgb(hex_color)
            # ACO uses 16-bit values (0-65535)
            r16 = int(r * 257)
            g16 = int(g * 257)
            b16 = int(b * 257)
            f.write(struct.pack('>H', 0))  # Color space (RGB)
            f.write(struct.pack('>HHHH', r16, g16, b16, 0))
        
        # Version 2 (with names)
        f.write(struct.pack('>HH', 2, len(colors_with_names)))
        for name, hex_color in colors_with_names:
            r, g, b = hex_to_rgb(hex_color)
            r16 = int(r * 257)
            g16 = int(g * 257)
            b16 = int(b * 257)
            f.write(struct.pack('>H', 0))  # Color space (RGB)
            f.write(struct.pack('>HHHH', r16, g16, b16, 0))
            # Name (UTF-16BE with length and null terminator)
            name_utf16 = (name + '\0').encode('utf-16-be')
            f.write(struct.pack('>H', len(name) + 1))
            f.write(name_utf16)

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Generate Adobe palette files (.ase/.aco)'
)
parser.add_argument(
    '-a', '--all',
    action='store_true',
    help='Generate an additional file with all colors combined'
)
parser.add_argument(
    '--grayscale-name',
    default='grayscale',
    help='Name for grayscale palette files (default: grayscale)'
)
parser.add_argument(
    '--colors-name',
    default='colors',
    help='Name for colors palette files (default: colors)'
)
parser.add_argument(
    '--all-name',
    default='all',
    help='Name for combined palette files (default: all)'
)
parser.add_argument(
    '--dnsimple-name',
    default='dnsimple',
    help='Name for dnsimple palette files (default: dnsimple)'
)
args = parser.parse_args()

# Create output directory
os.makedirs('out', exist_ok=True)

# Grayscale palette
grayscale_colors = [
    ("black", "#2d2a2e"),
    ("one", "#3f3a3f"),
    ("two", "#514a50"),
    ("three", "#625a60"),
    ("four", "#746b6f"),
    ("five", "#857b7e"),
    ("six", "#978c8c"),
    ("seven", "#a89e9c"),
    ("eight", "#b9b1ad"),
    ("nine", "#cbc5be"),
    ("ten", "#dcd9cf"),
    ("eleven", "#eeede0"),
    ("white", "#fdfff1")
]

# Color palettes (light, normal, dark)
color_palettes = [
    ("light", [
        ("light red", "#fdaeab"), ("light orange", "#f7c7ab"),
        ("light yellow", "#faebc3"), ("light green", "#e0f3c8"),
        ("light teal", "#c2eddb"), ("light blue", "#beeae8"),
        ("light purple", "#bab7cb"), ("light pink", "#fac7d2")
    ]),
    ("normal", [
        ("red", "#FC5C65"), ("orange", "#F19066"),
        ("yellow", "#F7D794"), ("green", "#c3e69f"),
        ("teal", "#87dcc6"), ("blue", "#7ED6DF"),
        ("purple", "#786FA6"), ("pink", "#F78FB3")
    ]),
    ("dark", [
        ("dark red", "#94434a"), ("dark orange", "#8f5d4a"),
        ("dark yellow", "#928161"), ("dark green", "#788867"),
        ("dark teal", "#5a837a"), ("dark blue", "#558087"),
        ("dark purple", "#524d6a"), ("dark pink", "#925d71")
    ])
]

# DNSimple palette
dnsimple_colors = [
    ("light_red", "#ff7d79"),
    ("light_blue", "#72c3d2"),
    ("light_yellow", "#ffdf83"),
    ("light_pink", "#E5698F"),
    ("light_green", "#72C8B1"),
    ("blue", "#1a5ec6"),
    ("red", "#f05751"),
    ("orange", "#ff9138")
]

# Combine all color palettes
all_colors = []
for palette_name, colors in color_palettes:
    all_colors.extend(colors)

# Generate grayscale files
create_ase(grayscale_colors, f"out/{args.grayscale_name}.ase")
create_aco(grayscale_colors, f"out/{args.grayscale_name}.aco")
print(f"Created out/{args.grayscale_name}.ase with {len(grayscale_colors)} colors")
print(f"Created out/{args.grayscale_name}.aco with {len(grayscale_colors)} colors")

# Generate color files
create_ase(all_colors, f"out/{args.colors_name}.ase")
create_aco(all_colors, f"out/{args.colors_name}.aco")
print(f"Created out/{args.colors_name}.ase with {len(all_colors)} colors")
print(f"Created out/{args.colors_name}.aco with {len(all_colors)} colors")

# Generate dnsimple files
create_ase(dnsimple_colors, f"out/{args.dnsimple_name}.ase")
create_aco(dnsimple_colors, f"out/{args.dnsimple_name}.aco")
print(f"Created out/{args.dnsimple_name}.ase with {len(dnsimple_colors)} colors")
print(f"Created out/{args.dnsimple_name}.aco with {len(dnsimple_colors)} colors")

# Generate combined file if -a flag is set
if args.all:
    combined_colors = grayscale_colors + all_colors
    create_ase(combined_colors, f"out/{args.all_name}.ase")
    create_aco(combined_colors, f"out/{args.all_name}.aco")
    print(f"Created out/{args.all_name}.ase with {len(combined_colors)} colors")
    print(f"Created out/{args.all_name}.aco with {len(combined_colors)} colors")