
#%% Imports
import open3d as o3d
import numpy as np
import plotly.graph_objects as go
import holoviews as hv

# %%

#%% Retreival of dataset


data = {
    "PARAM":[],
    "SYNC":[],
    "ODOM":[],
    "FLASER":[],
    "RLASER":[],
    "TRUEPOS":[],
    "NMEA-GGA":[]

}

topics = ["ODOM","FLASER","RLASER"]

with open("intel.clf","r") as f:
    for line in f:
        if line[0] == "#":
            continue

        parts = line.strip().split()
        tag = parts[0]

        if tag in data.keys():
            tmp_list = []

            for part in parts[1:]:
                if part == 'nohost':
                    continue
                else:
                    tmp_list.append(part)
            
            data[tag].append(tmp_list)


len(data["FLASER"])
# %%
def Process(parts):
    num_measurements = int(parts[0])
    
    ranges = list(map(float,parts[1:num_measurements+1]))

    x = float(parts[num_measurements+1])
    y = float(parts[num_measurements+2])
    theta = float(parts[num_measurements+3])

    angles = np.linspace(theta, theta + num_measurements, num_measurements)

    range_x = ranges * np.cos(np.radians(angles))
    range_y = ranges * np.sin(np.radians(angles))
    

    odom_x = float(parts[num_measurements+4])
    odom_y = float(parts[num_measurements+5])
    odom_theta = float(parts[num_measurements+6])

    timestamp = parts[num_measurements+7]
    timestamp_correction = parts[num_measurements+8]

    return {"Num_Measurements":num_measurements,"range":ranges,"range_x":range_x,"range_y":range_y,"x":x,"y":y,"theta":theta,"odom_x":odom_x,"odom_y":odom_y,"odom_theta":odom_theta,"timestamp":timestamp,"timestamp_correct":timestamp_correction}

flaser = Process(data["FLASER"][1034])
flaser

def Display(dat):
    fig = go.Figure(data=[go.Scatter(
        x=dat["range_x"],
        y=dat["range_y"],
        mode='markers',
        marker=dict(size=2, color=dat["range"], colorscale='Viridis')
    )])
    fig.show()


Display(flaser)



# %%
