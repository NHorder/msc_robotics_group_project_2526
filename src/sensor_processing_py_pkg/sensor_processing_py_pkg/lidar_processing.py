
#%% Imports
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import json
import numpy as np
from sensor_msgs.msg import LaserScan
import pandas as pd
import holoviews as hv
from enum import Enum

#%%

## Helper Classes
class Dir(Enum):
    NONE = 1
    DELTA_X = 2
    DELTA_Y = 3
    DELTA_BOTH = 4

class Line:
    start = []
    end = []
    dir = Dir.NONE



# Main Class
class Lidar_Processing(Node):

    def __init__(self):
        super().__init__('lidar_processing')
        self.wall_algorithm = DetermineWalls()

        self._calculate_walls = True

        self.subscriber = self.create_subscription(LaserScan,'/scan',self._Process,10)
        self.subscriber = self.create_subscription(Bool,'/wall/recalculate',self._Recalculate,10) # Will need someone to determine room dimensions, if room dimensions change, then rescan for walls
        self.publisher_wall_designation = self.create_publisher(String,'/wall/designation',10)
        self.publisher_main = self.create_publisher(LaserScan,'/processed/scan',10)


    def _Recalculate(self,msg):
        self._calculate_walls = True

    def _Process(self,msg):

        # Format the data
        df = self._FormatForProcessing(msg)
        
        # Clean the data and retreive it's points
        df, points = self._Clean(df)

        # If calculating the walls (on first receive, or on request by operator)
        if (self._calculate_walls):

            # Set to false, only do so ONCE (unless further requests are made)
            self._calculate_walls = False

            # Determine walls and clean them
            lines = self.wall_algorithm.DetermineLines(points)
            lines_part2 = self.wall_algorithm.RemoveLines_Distance(lines)
            lines_part3 = self.wall_algorithm.JoinCorners(lines_part2)
            lines_part4 = self.wall_algorithm.ConnectListEdge(lines_part3)
            lines_final = self.wall_algorithm.RemoveLines_Distance(lines_part4)
            
            # Format output message (Wall data)
            out_msg = self._Format_Wall_Msg(lines_final,df['timestamp'[0]]) # All timestamps are the same
            self._Publish(out_msg,False)
        

        # Format output message (No wall data)
        out_msg = self._FormatMsg(df,points,msg)

        self._Publish(out_msg)


    def _FormatForProcessing(self,msg):

        # Prepare dataframe
        df = pd.DataFrame()

        # Extract range data from msg, and put into dataframe
        # One range = one row in df
        ranges = list(msg.ranges)
        df['ranges'] = ranges

        # Then calulate angle for each range
        angle_min = msg.angle_min                            # Extract minimum angle
        angle_increment = msg.angle_increment                # Extract angle increment
        angles = []                                          # Define angles
        for i in range(0,len(df['ranges'])):                 # Loop through all ranges
            angles.append(angle_min + i * angle_increment)   # Add angle based on index
        df['bearing'] = angles                               # Add angles to df as 'bearing'

        # Add timestamp - not used, but important metadata for debugging
        df['timestamp'] = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9


        print('Success!')

        # Return the dataframe
        return df

    def _Clean(self,df:pd.DataFrame):
        """
        Method to clean the provided dataset
        - Assumes 'ranges' is a present value
        Arguments: pd.DataFrame || Must contain 'ranges' and 'bearing' values
        - range can be nan
        - each range must have bearing

        Returns: (x,y) coordinate data for each range (and angle) provided
        """

        # Identify mean and standard deviation, set all values above mean + 3std to nan 
        # (All values over 99.7% of the data spread, assumes normal distribution)
        mean = np.mean(df['ranges'])
        std = np.std(df['ranges'])
        df[df['ranges'] > mean + (3*std)] = np.nan

        # Identify mean and standard deviations, set threshold at mean + 3std, anything above that set to nan
        # Same as previous section, except on a smaller 'local' scale, involving 5 units either side of the point
        df['rolling_mean'] = df['ranges'].rolling(11,1,True).mean()
        df['rolling_std'] = df['ranges'].rolling(11,1,True).std()
        df['thd'] = df['rolling_mean'] + 3 * df['rolling_std']
        df.loc[df['ranges'] > df['thd'],'ranges'] = np.nan
        
        # Call display and discard the graph, retain the points (x,y) positions
        _, points = self.wall_algorithm.Display(df)

        # Return the points
        return df,points

    
    def _FormatMsg(self,df,msg):
        """
        Method for formatting the standard message
        Imports modified ranges from df into msg

        Note: Assumes ranges in df are np.floats (containing np.nan)
        """
        # Import updated ranges into the message in the correct format
        msg.ranges = df['ranges'].tolist()

        # Return message
        return msg

    def _Format_Wall_Msg(self,lines:list,timestamp):

        # Determine wall number
        n = 1
        txt = "Wall "

        # Prepare walls message
        walls = []
        
        # Append timestamp (important for debugging)
        walls.append(timestamp)

        # Loop through all walls, append [start, end, name]
        for line in lines:
            start = line.start
            end = line.end
            walls.append([start,end,txt+str(n)])

        # Convert to JSON string
        msg = json.dump(walls)

        # Return message for publication
        return msg

    
    def _Publish(self,msg,range_only:Bool = True):

        if range_only: 
            self.publisher_main.publish(msg)
        else: 
            self.publisher_wall_designation.publish(msg)


# Main class for determining walls
# Made as separate in case it's useful for other processes
class DetermineWalls():
    
    def __init__(self,min_line_dist:float = 0.2,dist_max_corner_join:float = 0.2,max_connection_dist: float = 0.1):

        # Minimum length of line (Line-02: Remove lines of small distance)
        self._distance_lines = min_line_dist 

        # Maximum distance between lines at corners to join
        self._distance_line_corner_join = dist_max_corner_join

        # Maximum distance of parallel lines to join
        self._distance_line_join = max_connection_dist
        
    # Line-01: Determine initial lines
    def DetermineLines(self,points):
        """
        Lines-01: The first stage of determining lines

        Primary function: Determines possible start and end-points for many lines
        - Uses orientation class (Dir) to do so
        - Might work for diagonals (Untested)

        """

        # Define intial values
        line = Line()           # This is the current line being tracked
        lines = []              # All lines identified
        current_dir = Dir.NONE  # Current direction of the line (The line has no start or end, hence it's NONE)

        # Loop through all points
        for point in points:

            # If the line has no start, give it a start, then skip rest of the loop
            if line.start == []:
                line.start = list(point)
                continue
            
            # If the line has no end, give it an end, DO NOT skip rest of loop (needed for direction)
            if line.end == []:
                line.end = list(point)
            
            # Determine change through coordinates, using line end as reference
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
            # Essentially, use the current line direction, compare to where the new point is
            if current_dir != line.dir:
                lines.append(line)
                line = Line()
                line.start = list(point) # Maybe omit
                line.dir = current_dir

            # Otherwise, it's part of the same line
            else:
                line.end = list(point)
        
        # As loop has ended, append the last line being handled
        lines.append(line)

        # return data
        return lines

    # Line-02: Remove lines of small distance
    def RemoveLines_Distance(self,lines):
        """

        Line-02: Stage 2 of determining lines

        Secondary Function: Removes all lines with distance of 0.2 meters.
        - Walls are assumed to be larger than 0.2 m in length. 
        - Some lines may be of distance 0.0 m due to use of directional change

        """
        # Prepare filtered lines
        lines_filtered = []

        # Loop through all lines
        for line in lines:

            # Determine distance from start to end
            # Distance will always be positive
            del_x = line.end[0] - line.start[0]
            del_y = line.end[1] - line.start[1]
            dist = np.sqrt(del_x**2 + del_y**2)

            # Append all lines with a distance larger than 0.2 meters
            if (dist > self._distance_lines):
                lines_filtered.append(line)
        
        # Return the filtered lines
        return lines_filtered

    # Line-03: Join Corners
    def JoinCorners(self,lines):
        """

        Line-03: Stage 3 of determining lines

        Secondary Function: Connects lines at edges (to form a polygon)
        - Polygon will not be full enclosed due to gaps
            - Gaps are caused by doorways or missing sensor data (potential for windows, etc depending on sensor height)

        """

        # Initialise previous line and final lines
        prev_line = []
        filtered_lines = []

        # Loop through each line
        for line in lines:

            # If previous line is empty, add the first line and set previous line, skip rest of loop
            # - Assumption first line is NOT on an edge, joining of lines is handled in Line-04 (ConnectListEdge)
            if prev_line == []:
                filtered_lines.append(line)
                prev_line = line
                continue

            # Determine distance from the end of previous to current line
            # Each line has a different orientation (see Line-01 (DetermineLines))
            del_x = prev_line.end[0] - line.start[0]
            del_y = prev_line.end[1] - line.start[1]
            dist = np.sqrt(del_x**2 + del_y**2)
            
            # Joins Corners if distance is minimal
            if dist <= self._distance_line_corner_join:
                # Overwrite end of previous, Overwrite start of current
                # - Naive approach, aims for maximum distance (best corners)

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
                # Possible indication of a gap - or lines are incompatable 
                pass

            # Append the current line (modified or not)
            filtered_lines.append(line)
            prev_line = line
        
        # Return filtered lines
        return filtered_lines

    # Line-04: Connect Lines Looped
    def ConnectListEdge(self,lines):
        """

        Line-04: Fourth stage of determining walls

        Secondary function: Join lines based on minimal distance
        - Assumes lines are within 0.1 meters of each other to join, and 
          have the same orientation
        """
        # Define replacement
        replacement = 0

        # Loop through all lines
        for i in range(1,len(lines)):

            # Identify if replacement is needed
            # lines[i-1] = lineA    lines[i]: lineB
            replacement = self.ConnectLines(lines[i-1],lines[i])

            # If replacement is needed
            if replacement != 0:
                lines.pop(i-1) # Remove lineA
                lines.pop(i) # Remove lineB
                lines.insert(i-1,replacement) # Replace with replacement line

        # Forced replacement check
        # Links the last and first lines (as they may be on the same wall, depends on LiDAR used)
        replacement = self.ConnectLines(lines[-1],lines[0])
        if replacement != 0:
            lines.pop(0) # Remove first line (LineA)
            lines.pop() # Remove last line (LineB)
            lines.insert(0,replacement) # Insert the newly connected line
        
        # Return list of lines
        return lines

    # Lines: Part 4.5: Connect Lines
    def ConnectLines(self,lineA:Line, lineB:Line):
        """

        Line-04.5: Fourth stage of determing walls, sub process

        Tertiary function: Determine if a replacement line is required, and return replacement if applicable
        - Lines can only be joined if both have the same direction and have a small distance
        - Assumes lineA connects to lineB

        """
        # Define replacement with default variable
        replacement = 0

        # Determine distance from lineA to lineB
        del_x = lineA.end[0] - lineB.start[0]
        del_y = lineA.end[1] - lineB.start[1]
        dist = np.sqrt(del_x**2 + del_y**2)

        # Determine if line is less than or equal to the allowed connection distance
        # AND has the same orientation as the other line
        if (dist <= self._distance_line_join and lineA.dir == lineB.dir):
            # If True, lines are close together and face the same direction
            # Hence they can be connected, resulting in a single line

            # Define a new line
            line = Line()
            line.start = lineA.start # Set the start of lineA
            line.end = lineB.end # Set the end of lineB
            line.dir = lineA.dir # Set direction (LineA.dir == LineB.dir)
            replacement = line # Update replacement
        
        # Return replacement line
        return replacement

    def Display(data,item = 'ranges',color='blue'):
        """

        Display function: Called by 'Lidar_Processing._Clean) to retrieve points

        Returns: Holoviews plot of Lidar points and the points as coordinates [ [x1,y1], [x2,y2], ..., [xn,yn] ]

        """
        # Prepare variables
        points = []
        i = 0

        # Loop through all items
        for i in range(len(data[item])):

            # If the item is nan, skip rest of the loop (ignore it)
            if np.isnan(data[item][i]):
                continue

            # Determine x and y locations
            # NOTE: Restiction to 1dp is required, although data accuracy is lost - it allows for lines to be
            # more easily determined - Lidar data is noisy and dense, hence this 'smooths' it, allowing for 
            # easier wall identification
            x = round(data[item][i] * np.cos(data['bearing'][i]),1)
            y = round(data[item][i]  * np.sin(data['bearing'][i]),1)

            # Save x,y coordinates
            points.append([x,y])

        # Return holoviews scatter graph and points
        return hv.Scatter(points).opts(color=color), points


def main(args=None):
    rclpy.init(args=args)
    
    # Load node
    node = Lidar_Processing()

    # Spin node
    try:
        node.get_logger().info("SensorProcesssing-Lidar || Status: Active")
        rclpy.spin(node)
    except KeyboardInterrupt:
        # On keyboard interrupt, shut down the system
        pass
    finally:
        # Log deactivation of node
        node.get_logger().info("SensorProcesssing-Lidar || Status: Inactive")

        # Destroy node and shutdown
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
