%%
t = tcpclient("172.22.196.95",5000)
while true
    % Read data from the TCP client
    if t.NumBytesAvailable > 0
        msg = readline(t);
        disp(msg)
    end
    pause(0.01)
end


%%
t = tcpclient("172.22.196.95",5001);
writeline(t,"Hello from MATLAB!")


%%
controlNode = ros2node("/matlabNode");
matlabNode = ros2subscriber(controlNode,"/ros_testing","std_msgs/String");


while true

    dat = receive(matlabNode,30)
    disp(dat.data)
end