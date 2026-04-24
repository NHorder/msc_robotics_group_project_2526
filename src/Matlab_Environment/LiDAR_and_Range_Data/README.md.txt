Hi Tanish,

I've attached the raw LiDAR and range data. For the LiDAR (first coordinate is X, second is Y). 


IMPORTANT: Apparently the range distance is measured in metres, meaning (1,1) = 1m x 1m from sensor (sensor at (0,0)

Range angle min: -3.141590118408203 rad
Range angle max: 3.141590118408203 rad
Range angle increment: 0.003929443191736937 rad

Hence:
heading of measurement = angle_min + i × angle_increment

And here are the walls

(x_start, y_start)   (x_end, y_end)  name
(-1,6)                  (5.5,6)      Wall A
(7.16, 6)              (8.74, 6)     Wall B 
(8.74,6)              (8.8, -1.37)   Wall C 
(8.8, -1.37)           (-1, -1.39)   Wall D
(-1,-1.39)               (-1,6)      Wall E

Note: Wall B is 'part' of Wall A and is separated by a doorway, it would be classified as a different wall (or same with some difficulty)



