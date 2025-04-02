import time

def quick_sort(data, drawData, timeTick, stop_signal):
    quick_sort_alg(data, 0, len(data) - 1, drawData, timeTick, stop_signal)

def quick_sort_alg(data, low, high, drawData, timeTick, stop_signal):
    if low < high:
        if stop_signal.is_set():  # Stop sorting if signal is set
            return
        
        pivot_index = partition(data, low, high, drawData, timeTick, stop_signal)
        quick_sort_alg(data, low, pivot_index - 1, drawData, timeTick, stop_signal)
        quick_sort_alg(data, pivot_index + 1, high, drawData, timeTick, stop_signal)

def partition(data, low, high, drawData, timeTick, stop_signal):
    pivot = data[high]
    i = low - 1

    for j in range(low, high):
        if stop_signal.is_set():  # Stop sorting if signal is set
            return
        
        if data[j] < pivot:
            i += 1
            data[i], data[j] = data[j], data[i]
            drawData(data, getColorArray(len(data), low, high, i, j, True))
            time.sleep(timeTick)

    data[i + 1], data[high] = data[high], data[i + 1]
    drawData(data, getColorArray(len(data), low, high, i + 1, high, False))
    time.sleep(timeTick)
    return i + 1

def getColorArray(length, low, high, pivot, curr, isSwapping):
    colorArray = []
    for i in range(length):
        if i >= low and i <= high:
            if i == pivot:
                colorArray.append("#4c1130")  # Pivot color
            elif i == curr:
                colorArray.append("#41B06E" if isSwapping else "#E1D7B7")  # Comparing/swapping color
            else:
                colorArray.append("#3282B8")  # Sorting range color
        else:
            colorArray.append("#E1D7B7")  # Default bar color
    return colorArray
