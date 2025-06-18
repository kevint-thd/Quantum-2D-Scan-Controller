"""
CLI entry point for running a 2D scan using simulated devices(scan-focused).
Loads configuration, sets up logging, runs the scan, and saves results.
"""

import yaml
import logging
import argparse
from scan_controller import MyScanController
from io_utils import save_csv, save_heatmap_with_peaks

def parse_args():
    parser = argparse.ArgumentParser(description="2D Scan Controller CLI")
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    # Extend to more CLI options to override config.yaml values directly.
    return parser.parse_args()

def main():
    """
    Load configuration, configure logging, run the scan, and save results.
    """
    args = parse_args()
     # YAML supports nested structures.
    with open(args.config) as f:
        config = yaml.safe_load(f)

    log_level = config['logging']['level'].upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        filename=config['logging']['file'],
        format='%(asctime)s %(levelname)s: %(message)s'
    )

    try:
        # Instantiate controller to separate CLI logic from scan logic; makes testing and reuse easier.
        scan = MyScanController(config)
        x_vals, y_vals, raw, filtered, global_peak, local_peaks, scan_time = scan.run_scan()
        # CSV for data analysis, heatmap for visualization.
        save_csv(config['output']['csv_file'], x_vals, y_vals, raw, filtered)
        save_heatmap_with_peaks(config['output']['heatmap_file'], filtered, x_vals, y_vals, local_peaks)
        print(f"Scan complete in {scan_time:.2f} seconds.")
        print(f"Global peak at x={x_vals[global_peak[1]]:.2f}, y={y_vals[global_peak[0]]:.2f}, value={filtered[global_peak]:.3f}")
        print(f"Found {len(local_peaks)} local peaks above threshold.")
    except Exception as e:
        logging.exception("Critical error during scan execution.")
        print(f"Scan failed: {e}")

if __name__ == '__main__':
    # Ensures main() only runs when script is executed directly, not when imported as a module.
    main()

# argparse is standard for CLI, YAML is readable and flexible for configs.getattr is a built-in Python function that gets an attribute from an object
# extend this CLI byadding more arguments (e.g., --x-start, --x-end) to override config, or add subcommands for different scan types.
