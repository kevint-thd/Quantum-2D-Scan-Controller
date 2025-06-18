import logging
import numpy as np
import time
from sim_device_wrapper import MyStageController, MySensorController
from data_processing import rolling_average_2d, fast_rolling_average, detect_global_peak, find_local_peaks

class MyScanController:
    """
    Main controller for orchestrating a 2D scan using simulated hardware.
    Handles retry logic, data collection, smoothing, and peak detection.
    """

    def __init__(self, config):
        """
        Initialize the scan controller with configuration and device interfaces.

        Args:
            config (dict): Dictionary containing scan parameters and settings.
        """
        self.config = config
        # Read fail rates from config, with defaults if not set
        stage_fail_rate = config.get('stage_fail_rate', 0.05)
        sensor_fail_rate = config.get('sensor_fail_rate', 0.03)

        # Device controllers are initialized with max_retries.
        # This allows for easy configuration and future extension to real hardware.
    
        self.stage = MyStageController(config['max_retries'], stage_fail_rate=stage_fail_rate)
        self.sensor = MySensorController(config['max_retries'], sensor_fail_rate=sensor_fail_rate)

        # Logging is flexible, can be redirected to files, filtered by level.
        self.logger = logging.getLogger(__name__)

        # Store a full log of every move/measure attempt for traceability and debugging.
        self.attempt_log = []

    def run_scan(self):
        """
        Execute the 2D scan, applying retry logic for both movement and measurement.
        Applies data smoothing and peak detection after scan is complete.

        Returns:
            x_vals (np.ndarray): X axis scan points
            y_vals (np.ndarray): Y axis scan points
            raw_data (np.ndarray): Raw sensor readings
            filtered_data (np.ndarray): Smoothed data
            global_peak (tuple): Indices of global peak in filtered data
            local_peaks (list): List of local peak indices
            scan_time (float): Total scan duration in seconds
        """
        # Generate scan grid. Using np.linspace ensures evenly spaced points.
        # Can easily change to logspace or meshgrid for more complex scans.
        x_vals = np.linspace(self.config['x_range']['start'],
                             self.config['x_range']['end'],
                             self.config['x_range']['steps'])
        y_vals = np.linspace(self.config['y_range']['start'],
                             self.config['y_range']['end'],
                             self.config['y_range']['steps'])

        # Initialize data array with NaN to mark skipped or failed points.
        raw_data = np.full((len(y_vals), len(x_vals)), np.nan)

        # Track scan duration for performance analysis.
        start_time = time.perf_counter()
        skipped_points = 0

        # --- Main scan loop: iterate over each (x, y) point ---
        for i, y in enumerate(y_vals):
            for j, x in enumerate(x_vals):

                # ---- Stage movement with retry logic ----
                move_success = False
                for attempt in range(1, self.config['max_retries'] + 1):
                    try:
                        # Move stage to (x, y). May randomly raise TimeoutError.
                        # Real hardware may have transient errors (e.g., timeouts); retrying increases robustness.
                        self.stage.move_to(x, y)
                        move_success = True
                        msg = f"Move to ({x:.2f},{y:.2f}) succeeded on attempt {attempt}"
                        self.logger.info(msg)
                        # Log every attempt for traceability.
                        self.attempt_log.append({
                            'x': x, 'y': y, 'type': 'move', 'status': 'success',
                            'attempt': attempt, 'reason': ''
                        })
                        break
                    except Exception as error:
                        # SimStage may raise different errors; want robust handling. To optimze further
                        # catch specific exceptions, add exponential backoff, or alert user after repeated failures.
                        msg = f"Attempt {attempt} failed: Stage timeout moving to ({x:.2f},{y:.2f}) - {error}"
                        self.logger.warning(msg)
                        self.attempt_log.append({
                            'x': x, 'y': y, 'type': 'move', 'status': 'fail',
                            'attempt': attempt, 'reason': str(error)
                        })
                if not move_success:
                    # All retries failed; skip this point.
                    # To keep scan robust and not block on one bad point.
                    self.logger.error(f"Skipping point ({x:.2f},{y:.2f}) after {self.config['max_retries']} move attempts")
                    skipped_points += 1
                    continue

                # ---- Sensor measurement with retry logic ----
                measure_success = False
                for attempt in range(1, self.config['max_retries'] + 1):
                    try:
                        sensor_reading = self.sensor.measure()
                        # SimSensor may return None on failure, which is not a valid value.
                        if sensor_reading is None:
                            raise ValueError("Received None from sensor reading")
                        self.logger.info(
                            f"Measure at ({x:.2f},{y:.2f}) succeeded on attempt {attempt}: {sensor_reading:.3f}")
                        self.attempt_log.append({
                            'x': x, 'y': y, 'type': 'measure', 'status': 'success',
                            'attempt': attempt, 'reason': '', 'value': sensor_reading
                        })
                        raw_data[i, j] = sensor_reading
                        measure_success = True
                        break
                    except Exception as error:
                        # Log both fail and value=None for full traceability and easier debugging of flaky sensors.
                        self.logger.warning(
                            f"Failed to measure sensor data on attempt {attempt}: {error}")
                        self.attempt_log.append({
                            'x': x, 'y': y, 'type': 'measure', 'status': 'fail',
                            'attempt': attempt, 'reason': str(error), 'value': None
                        })
                if not measure_success:
                    # All retries failed; skip this point and move forward to next points.
                    self.logger.error(
                        f"Skipping point ({x:.2f},{y:.2f}) after {self.config['max_retries']} measure attempts")
                    skipped_points += 1
                    continue

        # --- Data smoothing (rolling average) and peak analysis ---
        # 'fast_mean' uses a faster algorithm for large datasets; 'mean' is more general.
        if self.config.get('smoothing', 'mean') == 'fast_mean':
            filtered_data = fast_rolling_average(raw_data, self.config['rolling_avg_window'])
        else:
            filtered_data = rolling_average_2d(raw_data, self.config['rolling_avg_window'])

        # --- Peak detection ---
        # Global peak is main result; local peaks just for scientific interest.
        global_peak = detect_global_peak(filtered_data)
        local_peaks = find_local_peaks(filtered_data, self.config.get('peak_threshold', 0.8))
 
        # Calculate scan duration for performance reporting.
        scan_time = time.perf_counter() - start_time

        # --- Logging: print a summary of all attempts for traceability ---
        print("\n--- Full Scan Attempt Log ---")
        for entry in self.attempt_log:
            if entry['type'] == 'move':
                print(f"Move:   x={entry['x']:.2f}, y={entry['y']:.2f}, status={entry['status']}, "
                      f"attempt={entry['attempt']}, reason={entry['reason']}")
            elif entry['type'] == 'measure':
                print(f"Measure: x={entry['x']:.2f}, y={entry['y']:.2f}, status={entry['status']}, "
                      f"attempt={entry['attempt']}, reason={entry['reason']}, value={entry.get('value', '')}")

        print(f"\nScan complete in {scan_time:.2f} seconds.")
        print(f"Global peak at x={x_vals[global_peak[1]]:.2f}, y={y_vals[global_peak[0]]:.2f}, value={filtered_data[global_peak]:.3f}")
        print(f"Found {len(local_peaks)} local peaks above threshold.")
        print(f"Skipped points: {skipped_points}")

        # --- Return all relevant results for further processing or saving ---
        # Enables downstream analysis, saving, or plotting in CLI/notebook.
        return x_vals, y_vals, raw_data, filtered_data, global_peak, local_peaks, scan_time

