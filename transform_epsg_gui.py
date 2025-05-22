"""EPSG Transformation GUI Tool

This script provides a simple graphical user interface to transform
coordinate columns in a CSV file from one EPSG code to another.

Requirements:
    - Python 3
    - tkinter (usually included with Python)
    - pyproj (install via `pip install pyproj`)

Usage:
    Run the script with Python. A file dialog will prompt for the CSV
    file to transform. After selecting the columns and EPSG codes, the
    transformed CSV will be saved with a suffix containing the target
    EPSG code.
"""

import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from pyproj import Transformer
except ImportError:  # pragma: no cover - pyproj may not be installed in this environment
    raise SystemExit(
        "pyproj is required to run this script. Install it with 'pip install pyproj'."
    )


def load_csv(path):
    """Return header and all rows from a CSV file."""
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("Empty CSV file")
    header = rows[0]
    return header, rows


class ColumnSelector(tk.Tk):
    OPTIONS = ["Ignore", "Easting", "Northing", "Elevation"]

    def __init__(self, path, header, sample_rows, all_rows):
        super().__init__()
        self.title("EPSG Converter")
        self.path = path
        self.header = header
        self.sample_rows = sample_rows
        self.all_rows = all_rows
        self.option_vars = []
        self._build_ui()

    def _build_ui(self):
        # Create option menus and preview data
        for j, col in enumerate(self.header):
            var = tk.StringVar(value="Ignore")
            om = tk.OptionMenu(self, var, *self.OPTIONS)
            om.grid(row=0, column=j, padx=5, pady=2)
            tk.Label(self, text=col, font=("Arial", 10, "bold")).grid(
                row=1, column=j, padx=5, pady=2
            )
            for i, row in enumerate(self.sample_rows):
                tk.Label(self, text=row[j]).grid(row=2 + i, column=j, padx=5, pady=2)
            self.option_vars.append(var)

        base_row = 2 + len(self.sample_rows)
        tk.Label(self, text="Source EPSG:").grid(row=base_row, column=0, sticky="e")
        self.src_epsg = tk.Entry(self)
        self.src_epsg.insert(0, "32630")
        self.src_epsg.grid(row=base_row, column=1, sticky="w")

        tk.Label(self, text="Target EPSG:").grid(row=base_row + 1, column=0, sticky="e")
        self.tgt_epsg = tk.Entry(self)
        self.tgt_epsg.insert(0, "29903")
        self.tgt_epsg.grid(row=base_row + 1, column=1, sticky="w")

        convert_btn = tk.Button(self, text="Convert", command=self.convert)
        convert_btn.grid(row=base_row + 2, column=len(self.header) - 1, pady=10, sticky="e")

    def convert(self):
        src = self.src_epsg.get().strip()
        tgt = self.tgt_epsg.get().strip()
        if not src.isdigit() or not tgt.isdigit():
            messagebox.showerror("Error", "EPSG codes must be numeric")
            return

        e_idx = n_idx = z_idx = None
        for idx, var in enumerate(self.option_vars):
            val = var.get()
            if val == "Easting":
                e_idx = idx
            elif val == "Northing":
                n_idx = idx
            elif val == "Elevation":
                z_idx = idx

        if e_idx is None or n_idx is None:
            messagebox.showerror(
                "Error", "Please select columns for Easting and Northing"
            )
            return

        transformer = Transformer.from_crs(
            f"EPSG:{src}", f"EPSG:{tgt}", always_xy=True
        )

        for row in self.all_rows[1:]:
            try:
                x = float(row[e_idx])
                y = float(row[n_idx])
                if z_idx is not None and row[z_idx] != "":
                    z = float(row[z_idx])
                    x2, y2, z2 = transformer.transform(x, y, z)
                    row[e_idx] = f"{x2:.3f}"
                    row[n_idx] = f"{y2:.3f}"
                    row[z_idx] = f"{z2:.3f}"
                else:
                    x2, y2 = transformer.transform(x, y)
                    row[e_idx] = f"{x2:.3f}"
                    row[n_idx] = f"{y2:.3f}"
            except Exception as exc:  # pragma: no cover - UI error path
                messagebox.showerror("Error", f"Failed to transform row: {exc}")
                return

        filename = os.path.splitext(os.path.basename(self.path))[0]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"{filename}_EPSG{tgt}.csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if save_path:
            with open(save_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(self.all_rows)
            messagebox.showinfo("Saved", f"File saved to: {save_path}")


def main():
    root = tk.Tk()
    root.withdraw()  # hide root window during file selection
    path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
    )
    if not path:
        return
    try:
        header, rows = load_csv(path)
    except Exception as exc:
        messagebox.showerror("Error", str(exc))
        return

    sample_rows = rows[1:11]
    root.destroy()
    app = ColumnSelector(path, header, sample_rows, rows)
    app.mainloop()


if __name__ == "__main__":
    main()
