import random, time

class SimStage:
    def __init__(self, move_time=0.1, fail_rate=0.05):
        self.move_time = move_time
        self.fail_rate = fail_rate
 
    def move_to(self, x: float, y: float):
        """Sleep for move_time; fail with TimeoutError at random."""
        time.sleep(self.move_time)
        if random.random() < self.fail_rate:
            raise TimeoutError(f"Stage timeout moving to ({x:.2f},{y:.2f})")
        # otherwise succeed


class SimSensor:
    def __init__(self, base_signal=1.0, noise_level=0.2, fail_rate=0.03):
        self.base = base_signal
        self.noise = noise_level
        self.fail_rate = fail_rate

    def measure(self) -> float:
        """Return a signal or None/ValueError to simulate bad reads."""
        if random.random() < self.fail_rate:
            if random.choice([True, False]):
                return None
            else:
                raise ValueError("Sensor read error")
        return self.base + random.gauss(0, self.noise)

