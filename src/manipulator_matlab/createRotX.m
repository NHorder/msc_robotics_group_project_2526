function RotX = createRotX(a)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function RotX = createRotX(a)
% 
% Task: create the 3D transformation matrix corresponding to a rotation around the x axis
%
% Inputs:
%	- a: the angle of rotation
%
% Output: 
%	- RotX: the transformation matrix corresponding to a rotation around the x axis
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 02/04/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Create the rotation part of the transformation matrix (3 x 3)
rotationMatrix = [1 0 0;
    0 cos(a) -sin(a)
    0 sin(a) cos(a)];

%% Create the translation part (3 x 1)
translationMatrix = [0; 0; 0];

%% Create the homogeneous coordinate part (1 x 4)
homogeneousCoord = [0 0 0 1];

%% Express the final tranformation matrix for a rotation around x
RotX = [rotationMatrix translationMatrix; homogeneousCoord];
