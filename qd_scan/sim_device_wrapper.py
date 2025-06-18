import logging
from sim_devices import SimStage, SimSensor

class MyStageController:
    """
    Controller for simulated 2D stage with retry logic on movement failures.
    """

    def __init__(self, max_retries, stage_fail_rate=0.05):
        # max_retries make retry policy configurable and easy to adjust for different hardware or experiments.
        self.stage = SimStage(fail_rate=stage_fail_rate)
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    def move_to(self, x, y):
        """
        Attempt to move the stage to (x, y), retrying on TimeoutError.
        Returns True if successful, False otherwise.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                # Only TimeoutError is expected from SimStage; catching only what's expected prevents hiding bugs.
                self.stage.move_to(x, y)
                self.logger.info(f"Successfully moved to ({x}, {y}) on attempt {attempt}.")
                return True
            except TimeoutError as error:
                self.logger.warning(f"Attempt {attempt} failed: {error}")
                # Could implement exponential backoff or random sleep to avoid hammering hardware to optimize further.
        self.logger.error(f"Failed to move to ({x}, {y}) after {self.max_retries} attempts.")
        return False
 
class MySensorController:
    """
    Controller for simulated sensor with retry logic on measurement failures.
    """

    def __init__(self, max_retries,sensor_fail_rate=0.03):
        self.sensor = SimSensor(fail_rate=sensor_fail_rate)
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)

    def measure(self):
        """
        Attempt to measure sensor value, retrying on failure or None reading.
        Returns the measured value if successful, None otherwise.
        """
        for attempt in range(1, self.max_retries + 1):
            try:
                sensor_reading = self.sensor.measure()
                if sensor_reading is None:
                    raise ValueError("Received None from sensor reading")
                self.logger.info(f"Measurement successful on attempt {attempt}: {sensor_reading:.3f}")
                return sensor_reading
            except ValueError as error:
                self.logger.warning(f"Failed to measure sensor data on attempt {attempt}: {error}")
                # Only ValueError is expected for None readings; catching all could hide real bugs.
        self.logger.error(f"Failed to measure sensor data after all {self.max_retries} attempts.")
        return None

# Separate controller classes for stage and sensor to make mocking and future hardware integration easier.
# Only catch specific exceptions to ensures only anticipated errors are retried.
# Optimize retry logic by adding exponential backoff, random jitter, or alerting after repeated failures.
# Controllers can be easily mocked, and retry logic can be tested in isolation during unit testing.
