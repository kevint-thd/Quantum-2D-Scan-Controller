import numpy as np
import warnings
from scipy.ndimage import uniform_filter

# Standard NumPy rolling functions work best for 1D or along a single axis
# Rolling average approach applies a window around each point in 2D, handling NaNs as missing data(peaks).

def rolling_average_2d(data: np.ndarray, window_size: int) -> np.ndarray:
    """
    Standard 2D rolling average (mean) filter, ignoring NaNs.
    This is a straightforward implementation: for each point, average over a square window.
    """
    filtered = np.full(data.shape, np.nan)  # mark missing/skipped points with NaN.
    rows, cols = data.shape
    half_win = window_size // 2
    for i in range(rows):
        for j in range(cols):
            # Window boundaries to avoid index errors and ensure the window doesn't exceed array bounds.
            i_min = max(i - half_win, 0)
            i_max = min(i + half_win + 1, rows)
            j_min = max(j - half_win, 0)
            j_max = min(j + half_win + 1, cols)
            window = data[i_min:i_max, j_min:j_max]
            # np.nanmean ignores NaNs, so missing/skipped points don't bias the average.
            if np.isnan(window).all():
                filtered[i, j] = np.nan
            else:
                filtered[i, j] = np.nanmean(window)
    return filtered

# PERFORMANCE OPTIMIZATION: Fast Rolling Average
# For large arrays, the above loop is slow. uniform_filter is highly optimized and vectorized.
# fast Rolling Average uses convolution (uniform_filter) for speed, then divides by the count of valid points to ignore NaNs.
# For even larger data, consider chunking or GPU acceleration.
def fast_rolling_average(data: np.ndarray, window_size: int) -> np.ndarray:
    """
    Fast, vectorized 2D rolling average using scipy.ndimage.uniform_filter.
    Ignores NaNs in the calculation.
    """
    # Uniform_filter can't handle NaNs, so we use a mask and fill NaNs with zero to track valid data points and adjust the sum.
    mask = ~np.isnan(data)
    filled = np.where(mask, data, 0)
    filtered = uniform_filter(filled, size=window_size, mode='constant', cval=0)
    counts = uniform_filter(mask.astype(float), size=window_size, mode='constant', cval=0)
    # Handle division by zero to avoid NaN or inf where there are no valid points in the window.
    with np.errstate(invalid='ignore'):
        result = filtered / counts
        result[counts == 0] = np.nan
    return result

def detect_global_peak(filtered_data: np.ndarray) -> tuple:
    """
    Find the index of the global maximum in a 2D filtered array, ignoring NaNs.
    Returns (row, col) index of the peak.
    """
    # Peak detection is meaningless if all data is invalid; raise an error to signal this.
    if np.all(np.isnan(filtered_data)):
        raise ValueError("All data points are invalid. Peak detection impossible (all NaN values).")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        idx = np.nanargmax(filtered_data)  # np.nanargmax ignores NaNs, so only valid data is considered.
    return np.unravel_index(idx, filtered_data.shape)

# ENHANCEMENT: Multiple Peak Detection
def find_local_peaks(data: np.ndarray, threshold: float) -> list:
    """
    Find all local peaks above a given threshold.
    Returns a list of (row, col) indices.
    """
    from scipy.ndimage import maximum_filter
    # maximum_filter compare each point to its neighborhood for peak detection.
    # maximum_filter is used in image processing for local maxima detection.
    if np.all(np.isnan(data)):
        return []
    # 3x3 window checks each point against its immediate neighbors.
    #combine two separate arrays of coordinates tuples
    neighborhood = (maximum_filter(data, size=3, mode='constant', cval=np.nan) == data)
    peaks = np.where(neighborhood & (data > threshold) & ~np.isnan(data))
    return list(zip(peaks[0], peaks[1]))

