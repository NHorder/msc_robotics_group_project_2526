function RotZ = createRotZ(th, thoff)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function RotZ = createRotZ(th)
% 
% Task: create the 3D transformation matrix corresponding to a rotation around the z axis
%
% Inputs:
%	- th: the angle of rotation
%   - thoff: the offset of rotation
%
% Output: 
%	- RotZ: the transformation matrix corresponding to a rotation around the z axis
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 12/12/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Create the rotation part of the transformation matrix (3 x 3)
if thoff==-pi/2
    rotationMatrix = [sin(th) cos(th) 0;
        -cos(th) sin(th) 0
        0 0 1];
elseif thoff==pi/2
    rotationMatrix = [-sin(th) -cos(th) 0;
        cos(th) -sin(th) 0
        0 0 1];
else
    rotationMatrix = [cos(th) -sin(th) 0;
        sin(th) cos(th) 0
        0 0 1];
end

%% create the translation part (3 x 1)
translationMatrix = [0; 0; 0];

%% create the homogeneous coordinate part
homogeneousCoord = [0 0 0 1];

%% Express the final tranformation matrix for a rotation around z
RotZ = [rotationMatrix translationMatrix; homogeneousCoord];