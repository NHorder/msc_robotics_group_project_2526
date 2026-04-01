# %% Start
import pandas as pd
import numpy as np
import holoviews as hv
hv.extension('bokeh')
data = pd.read_csv("./ranges_raw.csv")
min_angle = -3.141590118408203
max_angle = 3.141590118408203
angle_increment =  0.003929443191736937
angles = []
for i in range(0,len(data['ranges'])):
    angles.append(min_angle + i * angle_increment)
data['bearing'] = angles

def Display(data,item = 'ranges',color='blue'):

    points = []
    i = 0
    group_x = []
    group_y = []

    for i in range(len(data[item])):

        if np.isnan(data[item][i]):
            continue

        group_x.append(round(data[item][i] * np.cos(data['bearing'][i]),1))
        group_y.append(round(data[item][i]  * np.sin(data['bearing'][i]),1))

        points.append((np.mean(group_x),np.mean(group_y)))
        group_x.clear()
        group_y.clear()

    return hv.Scatter(points).opts(color=color), points


# Apply a standardised anomaly removal (anything above mean+3*std) on a global scale
mean = np.mean(data['ranges'])
std = np.std(data['ranges'])
data[data['ranges'] > mean + (3*std)] = np.nan

# Apply the same anomly removal on a local scale
data['rolling_mean'] = data['ranges'].rolling(11,1,True).mean()
data['rolling_std'] = data['ranges'].rolling(11,1,True).std()
data['thd'] = data['rolling_mean'] + 3 * data['rolling_std']
data.loc[data['ranges'] > data['thd'],'ranges'] = np.nan
     
_, points = Display(data)


# Remove any points exceeding global std.
data['diff'] = data['ranges'].diff(1)
data[data['diff'] > std] = np.nan

_, points = Display(data)

quirk_point = []
for point in points:
    if point[0] <= -3:
        quirk_point.append(point)
        print("Found it B")


#%% Lines: Part 1
# Attempt at getting corners (it works, need to merge liness now - might be able to do angle checks, idk)

# This part is the issue - it's sometimes incorrectly labelling items, as it's carrying over the last direction

from enum import Enum
class Dir(Enum):
    NONE = 1
    DELTA_X = 2
    DELTA_Y = 3
    DELTA_BOTH = 4

class Line:
    start = []
    end = []
    dir = Dir.NONE

# Lines: Part 1  Determine intial lines
def DetermineLines(points):
    line = Line()
    lines = []
    current_dir = Dir.NONE

    for point in points:
        #current_dir = Dir.NONE

        # If the line has no start, give it a start
        if line.start == []:
            line.start = list(point)
            continue
        
        # If the line has no end, give it an end
        if line.end == []:
            line.end = list(point)
        
        # Determine change in coordinates

        if point[0] != line.end[0] and point[1] != line.end[1]: current_dir = Dir.DELTA_BOTH
        elif point[0] != line.end[0]: current_dir = Dir.DELTA_X
        elif point[1] != line.end[1]: current_dir = Dir.DELTA_Y

        # If the end is the same as the current point
        # update the line dir and end point
        if line.end == point:
            line.dir = current_dir
            line.end = list(point)
            continue

        # If the direction changes, it's a new line
        if current_dir != line.dir:
            lines.append(line)
            line = Line()
            line.start = list(point) # Maybe omit
            line.dir = current_dir

        # Otherwise, it's part of the same line
        else:
            line.end = list(point)
        
    lines.append(line)

    return lines


# Lines: Part 2 Remove lines of small distance
def RemoveLines_Distance(lines):
    return_lines = []
    for line in lines:
        del_x = line.end[0] - line.start[0]
        del_y = line.end[1] - line.start[1]

        dist = np.sqrt(del_x**2 + del_y**2)
        if (dist > 0.2):
            return_lines.append(line)
    
    return return_lines

# Lines: Part 3: Join Corners
def JoinCorners(lines):
    prev_line = []
    final_lines = []
    for line in lines:
        if prev_line == []:
            final_lines.append(line)
            prev_line = line
            continue

        del_x = prev_line.end[0] - line.start[0]
        del_y = prev_line.end[1] - line.start[1]
        dist = np.sqrt(del_x**2 + del_y**2)
        

        # Joins Corners if distance is minimal
        if dist <= 0.2:
            # Override end of previous, override start of current

            # If the x is negative, take the least x
            # else take the highest value
            if line.start[0] < 0 and prev_line.end[0] < 0:
                line.start[0] = min(line.start[0],prev_line.end[0])
                prev_line.end[0] = min(line.start[0],prev_line.end[0])
            else:
                line.start[0] = max(line.start[0],prev_line.end[0])
                prev_line.end[0] = max(line.start[0],prev_line.end[0])
            
            # If the y is negative, take the least y
            # else take the highest value
            if line.start[1] < 0 and prev_line.end[1] < 0:
                line.start[1] = min(line.start[1],prev_line.end[1])
                prev_line.end[1] = min(line.start[1],prev_line.end[1])
        
            else:
                line.start[1] = max(line.start[1],prev_line.end[1])
                prev_line.end[1] = max(line.start[1],prev_line.end[1])
            
        else:
            # Do nothing, leave as separate
            pass

        final_lines.append(line)
        prev_line = line

    return final_lines

# Lines: Part 4: Connect Lines
def ConnectListEdge(lines):
    lineA = lines[-1]
    lineB = lines[0]
    replacement = 0

    for i in range(1,len(lines)):
        replacement = ConnectLines(lines[i-1],lines[i])

        if replacement != 0:
            lines.pop(i-1)
            lines.pop(i)
            lines.insert(i-1,replacement)

    
    replacement = ConnectLines(lines[-1],lines[0])
    if replacement != 0:
        lines.pop(0) # Remove first line (LineA)
        lines.pop() # Remove last line (LineB)
        lines.insert(0,replacement) # Insert the newly connected line
    
    return lines

    del_x = lineA.end[0] - lineB.start[0]
    del_y = lineA.end[1] - lineB.start[1]
    dist = np.sqrt(del_x**2 + del_y**2)

    if (dist <= 0.1 and lineA.dir == lineB.dir):
        line = Line()
        line.start = lineA.start
        line.end = lineB.end
        line.dir = lineA.dir
        replacement = line
    
    if replacement != 0:
        lines.pop(0) # Remove first line (LineA)
        lines.pop() # Remove last line (LineB)
        lines.insert(0,replacement) # Insert the newly connected line

    # Return lines
    return lines

def ConnectLines(lineA, lineB):
    replacement = 0
    del_x = lineA.end[0] - lineB.start[0]
    del_y = lineA.end[1] - lineB.start[1]
    dist = np.sqrt(del_x**2 + del_y**2)

    if (dist <= 0.1 and lineA.dir == lineB.dir):
        line = Line()
        line.start = lineA.start
        line.end = lineB.end
        line.dir = lineA.dir
        replacement = line

    return replacement


#%% Remove Lines of small distance
lines_part2 = RemoveLines_Distance(lines)
lines_part3 = JoinCorners(lines_part2)
lines_part4 = ConnectListEdge(lines_part3)
finale = RemoveLines_Distance(lines_part4)
PlotLines(lines_part4)

import json
def _Format_Wall_Msg(self,lines):
    n = 1
    txt = "Wall "
    walls = []
    for line in lines:
        start = line.start
        end = line.end
        walls.append(start,end,txt+str(n))

    msg = json.dump(walls)
    return msg


# %%