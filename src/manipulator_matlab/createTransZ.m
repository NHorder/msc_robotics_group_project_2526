function TransZ = createTransZ(d)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function TransZ = createTransZ(d)
% 
% Task: create the 3D transformation matrix corresponding to a translation in the z axis
%
% Inputs:
%	- d: the distance of translation
%
% Output: 
%	-TransZ: the transformation matrix corresponding to a translation in the z axis
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 02/04/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Create the rotation part of the transformation matrix (3 x 3)
rotationMatrix = [1 0 0; 0 1 0; 0 0 1];

%% create the translation part (3 x 1)
translationMatrix = [0; 0; d];

%% create the homogeneous coordinate part
homogeneousCoord = [0 0 0 1];

%% Express the final tranformation matrix for a translation along z
TransZ = [rotationMatrix translationMatrix; homogeneousCoord];
