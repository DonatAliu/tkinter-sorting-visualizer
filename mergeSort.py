import time

def merge_sort(data, drawData, timeTick, stop_signal):
    merge_sort_alg(data, 0, len(data)-1, drawData, timeTick, stop_signal)

def merge_sort_alg(data, left, right, drawData, timeTick, stop_signal):
    if left < right:
        if stop_signal.is_set():  # Check if stop signal is set
            return  # Exit the function if stop signal is set

        middle = (left + right) // 2
        merge_sort_alg(data, left, middle, drawData, timeTick, stop_signal)
        merge_sort_alg(data, middle + 1, right, drawData, timeTick, stop_signal)
        merge(data, left, middle, right, drawData, timeTick, stop_signal)

def merge(data, left, middle, right, drawData, timeTick, stop_signal):
    if stop_signal.is_set():  # Check if stop signal is set
        return  # Exit the function if stop signal is set
    
    # Draw the current state before merging
    drawData(data, getColorArray(len(data), left, middle, right))
    time.sleep(timeTick)

    # Merge the two halves
    leftPart = data[left:middle + 1]
    rightPart = data[middle + 1:right + 1]

    leftIdx = rightIdx = 0
    dataIdx = left

    while leftIdx < len(leftPart) and rightIdx < len(rightPart):
        if stop_signal.is_set():  # Check if stop signal is set
            return  # Exit the function if stop signal is set

        if leftPart[leftIdx] <= rightPart[rightIdx]:
            data[dataIdx] = leftPart[leftIdx]
            leftIdx += 1
        else:
            data[dataIdx] = rightPart[rightIdx]
            rightIdx += 1
        dataIdx += 1

    while leftIdx < len(leftPart):
        if stop_signal.is_set():  # Check if stop signal is set
            return  # Exit the function if stop signal is set

        data[dataIdx] = leftPart[leftIdx]
        leftIdx += 1
        dataIdx += 1

    while rightIdx < len(rightPart):
        if stop_signal.is_set():  # Check if stop signal is set
            return  # Exit the function if stop signal is set

        data[dataIdx] = rightPart[rightIdx]
        rightIdx += 1
        dataIdx += 1

    # Draw the sorted section after merging
    drawData(data, ["#41B06E" if left <= x <= right else "#E1D7B7" for x in range(len(data))])
    time.sleep(timeTick)

def getColorArray(length, left, middle, right):
    colorArray = []
    for i in range(length):
        if i >= left and i <= right:
            if i <= middle:
                colorArray.append("#41B06E")
            else:
                colorArray.append("#F9D689")
        else:
            colorArray.append("#E1D7B7")
    return colorArray
