# Quantum-2D-Scan-Controller

# QuantumDiamonds 2D Scan Controller - Quantumsensor, Quantum Diamonds, NV Center
'More information available below and PowerPoint presentation' attached. Thank you

## Overview

Simulates a 2D scan using a translation stage and noisy sensor, with robust retry logic, configurable smoothing, and advanced data analysis. 

## Features
- Simulated hardware with realistic failure modes
- Configurable scan area, retries, and smoothing method
- Fast, vectorized rolling average 
- Global and local peak detection
- Heatmap visualization with peaks overlay
- Robust logging and error handling
- Command-line interface

## Quick Start

### 1. Install Dependencies
python -m venv .venv     # create the Virtual Environment
.\.venv\Scripts\Activate # Activate the Virtual Environment

pip install -r requirements.txt

### 2. Run the Scan
python cli.py --config config.yaml


### 3. Outputs

- `out/scan_results.csv`: Raw and filtered scan data
- `out/heatmap.png`: Heatmap image with detected peaks
- `scan.log`: Log file with scan details

## Configuration

Edit `config.yaml` to adjust scan parameters, smoothing method, peak threshold, and output files.

Example:
x_range:
    start: 0.0
    end: 5.0
    steps: 6
y_range:
    start: 0.0
    end: 5.0
    steps: 6
max_retries: 3
rolling_avg_window: 3
smoothing: fast_mean # Options: 'mean', 'fast_mean'
peak_threshold: 0.8  # Only for multiple peak detection
logging:
    level: INFO
    file: scan.log
output:
    csv_file: out/scan_results.csv
    heatmap_file: out/heatmap.png

## Parameter explanations
- `x_range`/`y_range`: Start, end, and number of steps for scan grid (creates an N×N grid).
- `max_retries`: Retries for hardware failures before skipping a point.
- `rolling_avg_window`: Window size for smoothing filter.
- `smoothing`: Smoothing method (`mean` or `fast_mean`).
- `peak_threshold`: Minimum value for local peak detection.
- `logging`: Log level and file.
- `output`: Output file paths.

## Project Structure
qd_scan
├── cli.py
├── config.yaml
├── data_processing.py
├── io_utils.py
├── scan_controller.py
├── sim_devices.py
├── sim_device_wrapper.py
├── requirements.txt
├── tests/
│   ├── test_data_processing.py
│   └── test_scan_controller.py
└── README.md

## Testing

Install test dependencies if needed: pip install pytest
Run all unit tests: pytest tests/

## Extending

- Add new smoothing methods in `data_processing.py`
- Integrate with real hardware by replacing `sim_devices.py`
- Adjust CLI or YAML for more advanced workflows


