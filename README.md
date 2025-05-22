# Codex

Utility scripts and experiments.

## Coordinate Conversion Tool

`transform_epsg_gui.py` provides a graphical interface for converting
coordinate columns in a CSV file from one EPSG code to another.

### Requirements

- Python 3
- `tkinter` (typically included with Python)
- `pyproj` (install with `pip install pyproj`)

### Usage

Run the script with Python:

```bash
python3 transform_epsg_gui.py
```

You will be prompted to select a CSV file, choose the columns that
represent easting, northing, and elevation, set the source and target
EPSG codes, and save the transformed output.
