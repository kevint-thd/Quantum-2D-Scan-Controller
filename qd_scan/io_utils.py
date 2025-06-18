import os
import csv
import matplotlib.pyplot as plt
import numpy as np

def save_csv(filename, x_vals, y_vals, raw_data, filtered_data):
    """
    Save scan results to a CSV file.
    Each row contains: x, y, raw_value, filtered_value.
    """
    dir_path = os.path.dirname(filename)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['x', 'y', 'raw_value', 'filtered_value'])
        # nested loops over y and then x, to match the 2D data structure (row-major order); each (x, y) pair is saved.
        for i, y in enumerate(y_vals):
            for j, x in enumerate(x_vals):
                # missing data is empty, not 'nan' string.
                writer.writerow([f"{x:.6g}", f"{y:.6g}",
                                 f"{raw_data[i,j]:.6g}" if not np.isnan(raw_data[i,j]) else "",
                                 f"{filtered_data[i,j]:.6g}" if not np.isnan(filtered_data[i,j]) else ""])

# ENHANCEMENT: Visualization—Overlay Peaks on Heatmap
def save_heatmap_with_peaks(filename, filtered_data, x_vals, y_vals, peaks):
    """
    Save a heatmap of the filtered data as an image file, overlaying detected peaks.
    """
    # imshow gives full control over axes, colormap, and overlays than  seaborn.heatmap(nm).
    plt.imshow(filtered_data, extent=[x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]],
               origin='lower', aspect='auto', cmap='viridis')
    plt.colorbar(label='Filtered Signal')
    plt.xlabel('X position')
    plt.ylabel('Y position')
    plt.title('Filtered Data Heatmap')
    if peaks:
        for (i, j) in peaks:
            plt.plot(x_vals[j], y_vals[i], 'ro', markersize=8, label='Peak')
        # Avoid duplicate legend entries if multiple peaks are plotted.
        plt.legend(['Peak'])
    plt.tight_layout()
    # tight_layout prevents labels from being cut off in the saved image.
    plt.savefig(filename)
    # frees memory and prevents figure overlap when saving multiple images in a script.
    plt.close() 

# extend the visualization by adding contour lines, custom color maps.
