import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from scan_controller import MyScanController


@pytest.fixture
def config():
    # fixture for config keeps test parameters DRY and easily reusable across multiple tests.
    return {
        'x_range': {'start': 0, 'end': 1, 'steps': 2},
        'y_range': {'start': 0, 'end': 1, 'steps': 2},
        'max_retries': 2,
        'rolling_avg_window': 1,
        'smoothing': 'mean',
        'peak_threshold': 0.8
    }

def test_scan_controller_success(config):
    # patch MyStageController and MySensorController to isolate scan logic from hardware
    with patch('scan_controller.MyStageController') as MockStage, \
         patch('scan_controller.MySensorController') as MockSensor:
        # set return_value for mocks to control mock behavior; ensures "hardware" always succeeds.
        mock_stage = MockStage.return_value
        mock_stage.move_to.return_value = None

        mock_sensor = MockSensor.return_value
        mock_sensor.measure.return_value = 1.0

        scan = MyScanController(config)
        x_vals, y_vals, raw, filtered, global_peak, local_peaks, scan_time = scan.run_scan()

        # attempt_log length ensures every move and measure is logged for each point (2 per point).
        assert len(scan.attempt_log) == 2 * len(x_vals) * len(y_vals)
        # All moves/measures succeed
        for entry in scan.attempt_log:
            assert entry['status'] == 'success'
            if entry['type'] == 'measure':
                assert entry['value'] == 1.0
        # np.allclose is robust to floating-point errors; checks all data is as expected.
        assert np.allclose(raw, 1.0)
        assert np.allclose(filtered, 1.0)

def test_scan_controller_stage_failure_and_retry(config):
    with patch('scan_controller.MyStageController') as MockStage, \
         patch('scan_controller.MySensorController') as MockSensor:
        mock_stage = MockStage.return_value
        # side_effect simulates a failure on first call, success on second; tests retry logic.
        mock_stage.move_to.side_effect = [Exception("Timeout!"), None, None, None, None, None, None, None]

        mock_sensor = MockSensor.return_value
        mock_sensor.measure.return_value = 1.0

        scan = MyScanController(config)
        x_vals, y_vals, raw, filtered, global_peak, local_peaks, scan_time = scan.run_scan()

        # filter attempt_log by x/y and type to verify the retry logic is exercised for the expected point.
        first_move_attempts = [e for e in scan.attempt_log if e['type'] == 'move' and e['x'] == 0 and e['y'] == 0]
        assert first_move_attempts[0]['status'] == 'fail'
        assert first_move_attempts[1]['status'] == 'success'

def test_scan_controller_sensor_failure_and_retry(config):
    with patch('scan_controller.MyStageController') as MockStage, \
         patch('scan_controller.MySensorController') as MockSensor:
        mock_stage = MockStage.return_value
        mock_stage.move_to.return_value = None

        mock_sensor = MockSensor.return_value
        # side_effect with None first simulates a sensor failure, then success; tests retry and error handling.
        mock_sensor.measure.side_effect = [None, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

        scan = MyScanController(config)
        x_vals, y_vals, raw, filtered, global_peak, local_peaks, scan_time = scan.run_scan()

        first_measure_attempts = [e for e in scan.attempt_log if e['type'] == 'measure' and e['x'] == 0 and e['y'] == 0]
        assert first_measure_attempts[0]['status'] == 'fail'
        assert first_measure_attempts[1]['status'] == 'success'

# mocking in these tests isolate scan logic from hardware, making tests deterministic, fast, and reliable.
# patch() temporarily replaces real classes with mocks within the test scope, allowing  to control behavior and verify interactions.
# side_effect attribute of a mock specify a list of values or exceptions to return/raise on each call, simulating different behaviors for each call to the mock.
# hside_effect attribute simulate failures and recoveries, and to test retry or error handling logic without real failure.
# extend these tests by adding tests for full scan skips, logging output, or edge cases (e.g., all retries fail, all data is NaN).
# side_effect is used in mocks to simulate failures and successes on specific calls, which is essential for testing retry logic and robust error handling in scientific code.