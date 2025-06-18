import numpy as np
from data_processing import rolling_average_2d, fast_rolling_average, detect_global_peak, find_local_peaks

def test_rolling_average_2d_basic():
    data = np.array([[1, 2, 3],
                     [4, 5, 6],
                     [7, 8, 9]], dtype=float)
    result = rolling_average_2d(data, 3)
    assert np.isclose(result[1, 1], 5.0)

def test_fast_rolling_average_matches_slow():
    # test fast vs slow rolling average to ensure optimized (fast) version matches the reference (slow) implementation, validating correctness.
    data = np.random.rand(5, 5)
    slow = rolling_average_2d(data, 3)
    fast = fast_rolling_average(data, 3)
    # assert_allclose with equal_nan handles floating-point errors and NaN propagation
    np.testing.assert_allclose(slow,  fast, equal_nan=True, rtol=1e-5)

def test_detect_global_peak():
    data = np.array([[1, 2], [3, 9]])
    peak = detect_global_peak(data)
    assert peak == (1, 1)

def test_find_local_peaks():
    # threshold=4 ensures only the true local peak (center) is detected, not the edges.
    data = np.array([[0, 2, 0],
                     [2, 5, 2],
                     [0, 2, 0]], dtype=float)
    peaks = find_local_peaks(data, threshold=4)
    assert (1, 1) in peaks

def test_nan_handling():
    # test all-NaN input to ensure robust error handling—peak detection should raise an error if all values are invalid.
    data = np.full((3, 3), np.nan)
    try:
        detect_global_peak(data)
    except ValueError:
        pass  # Expected
    else:
        assert False, "Should raise ValueError for all-NaN input"



































































#  Rolling Average Edge Cases
def test_rolling_average_2d_with_nans():
    """Test with NaNs in the Window """
    data = np.array([[1, np.nan, 3],
                     [4, 5, 6],
                     [np.nan, 8, 9]], dtype=float)
    result = rolling_average_2d(data, 3)
    # Center should average only valid numbers: (1+3+4+5+6+8+9)/7 = 5.142857...
    assert np.isclose(result[1, 1], np.nanmean([1,3,4,5,6,8,9]))
    # Where all values are NaN, result should be NaN
    data = np.full((3,3), np.nan)
    result = rolling_average_2d(data, 3)
    assert np.isnan(result[1,1])

def test_rolling_average_2d_window_one():
    """ Test with Small Window Size (1)"""
    data = np.array([[1, 2], [3, 4]], dtype=float)
    result = rolling_average_2d(data, 1)
    # Should be identical to input
    assert np.allclose(result, data, equal_nan=True)

# Fast Rolling Average Edge Cases
def test_fast_rolling_average_all_nans():
    # Test with All NaNs
    data = np.full((4, 4), np.nan)
    result = fast_rolling_average(data, 3)
    assert np.isnan(result).all()

def test_fast_rolling_average_zeros_and_nans():
    # Test with Zeros and NaNs
    data = np.array([[0, np.nan], [np.nan, 0]], dtype=float)
    result = fast_rolling_average(data, 2)
    # Should average only the zeros where possible
    assert np.allclose(result[~np.isnan(result)], 0)

# Peak Detection Edge Cases
def test_detect_global_peak_multiple_max():
    # Test detect_global_peak with Multiple Maxima
    data = np.array([[1, 2], [3, 3]])
    peak = detect_global_peak(data)
    # Should return the first occurrence of the max (row-major order)
    assert peak in [(1,0), (1,1)]

def test_find_local_peaks_none():
    # Test find_local_peaks with No Peaks Above Threshold
    data = np.array([[1, 1], [1, 1]], dtype=float)
    peaks = find_local_peaks(data, threshold=2)
    assert peaks == []

def test_find_local_peaks_all_nans():
    # Test find_local_peaks with All NaNs
    data = np.full((3, 3), np.nan)
    peaks = find_local_peaks(data, threshold=0)
    assert peaks == []

# General Robustness
def test_rolling_average_empty():
    # Test with Empty Array
    data = np.array([[]], dtype=float)
    result = rolling_average_2d(data, 3)
    assert result.shape == data.shape

def test_rolling_average_large_window():
    # Test with Window Larger Than Array
    data = np.array([[1]], dtype=float)
    result = rolling_average_2d(data, 5)
    # Should just return the mean of the available value
    assert np.isclose(result[0,0], 1)







