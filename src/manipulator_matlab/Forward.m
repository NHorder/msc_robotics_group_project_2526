function [T01, T12, T23, T34, T45, T56, T06] = Forward(MDH)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function [T01, T12, T23, T34, T45, T56, T06] = Forward(MDH)
%
% Task: Create the Forward Kinematics of a 6 DOF Robot from its MDH table
%
% Inputs:
%	- MDH: the Modified Denavit-Hartenberg table of the Robot
%
% Output: 
%	- T01: the transformation matrix of Link 1
%	- T12: the transformation matrix of Link 2
%	- T23: the transformation matrix of Link 3
%	- T34: the transformation matrix of Link 4
%	- T45: the transformation matrix of Link 5
%	- T56: the transformation matrix of Link 6
%	- T06: the full transformation matrix from base to end-effector
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 12/12/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Express the Tranformation matrices of the joints

% Transform matrix joint 1
A1 = createRotX(MDH(1,1));              % Call a function to create a transformation matrix for a rotation around x
B1 = createTransX(MDH(1,2));            % Call a function to create a transformation matrix for a translation along x
C1 = createTransZ(MDH(1,3));            % Call a function to create a transformation matrix for a translation along z
D1 = createRotZ(MDH(1,4), MDH(1,5));    % Call a function to create a transformation matrix for a rotation around z
T01 = A1*B1*C1*D1;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 1

% Transform matrix joint 2
A2 = createRotX(MDH(2,1));              % Call a function to create a transformation matrix for a rotation around x
B2 = createTransX(MDH(2,2));            % Call a function to create a transformation matrix for a translation along x
C2 = createTransZ(MDH(2,3));            % Call a function to create a transformation matrix for a translation along z
D2 = createRotZ(MDH(2,4), MDH(2,5));    % Call a function to create a transformation matrix for a rotation around z
T12 = A2*B2*C2*D2;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 2

% Transform matrix joint 3
A3 = createRotX(MDH(3,1));              % Call a function to create a transformation matrix for a rotation around x
B3 = createTransX(MDH(3,2));            % Call a function to create a transformation matrix for a translation along x
C3 = createTransZ(MDH(3,3));            % Call a function to create a transformation matrix for a translation along z
D3 = createRotZ(MDH(3,4), MDH(3,5));    % Call a function to create a transformation matrix for a rotation around z
T23 = A3*B3*C3*D3;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 3

% Transform matrix joint 4
A4 = createRotX(MDH(4,1));              % Call a function to create a transformation matrix for a rotation around x
B4 = createTransX(MDH(4,2));            % Call a function to create a transformation matrix for a translation along x
C4 = createTransZ(MDH(4,3));            % Call a function to create a transformation matrix for a translation along z
D4 = createRotZ(MDH(4,4), MDH(4,5));    % Call a function to create a transformation matrix for a rotation around z
T34 = A4*B4*C4*D4;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 4

% Transform matrix joint 5
A5 = createRotX(MDH(5,1));              % Call a function to create a transformation matrix for a rotation around x
B5 = createTransX(MDH(5,2));            % Call a function to create a transformation matrix for a translation along x
C5 = createTransZ(MDH(5,3));            % Call a function to create a transformation matrix for a translation along z
D5 = createRotZ(MDH(5,4), MDH(5,5));    % Call a function to create a transformation matrix for a rotation around z
T45 = A5*B5*C5*D5;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 5

% Transform matrix joint 6
A6 = createRotX(MDH(6,1));              % Call a function to create a transformation matrix for a rotation around x
B6 = createTransX(MDH(6,2));            % Call a function to create a transformation matrix for a translation along x
C6 = createTransZ(MDH(6,3));            % Call a function to create a transformation matrix for a translation along z
D6 = createRotZ(MDH(6,4), MDH(6,5));    % Call a function to create a transformation matrix for a rotation around z
T56 = A6*B6*C6*D6;                      % Multiply the created transformation matrices to get the final transformation matrix for joint 6

%% Combine them to get the Forward Kinematics result: Final Transform matrix

T06 = simplify(T01 * T12 * T23 * T34 * T45 * T56);  % Use the simplify function to simplify the equations in the matices