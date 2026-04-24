function [J, LinJ] = Jacobian(T01, T12, T23, T34, T45, T06)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function det = Inverse(MDH, Base, Target, App)
%
% Task: Determine the Jacobian and its determinant of a 6DOF Robot
%
% Inputs:
%	- T01: the transformation matrix of Link 1
%	- T12: the transformation matrix of Link 2
%	- T23: the transformation matrix of Link 3
%	- T34: the transformation matrix of Link 4
%	- T45: the transformation matrix of Link 5
%	- T06: the full transformation matrix from base to end-effector
%
% Output: 
%	- Determinant: The determinant of the Jacobian
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 12/12/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Calculate the missing Tranformation matrices from base to current link
T02 = simplify(T01 * T12);
T03 = simplify(T02 * T23);
T04 = simplify(T03 * T34);
T05 = simplify(T04 * T45);

%% Extract the rotation element of the corresponding matrix
R01 = T01(1:3, 3);
R02 = T02(1:3, 3);
R03 = T03(1:3, 3);
R04 = T04(1:3, 3);
R05 = T05(1:3, 3);

%% Extract the translation element of the corresponding matrix
D01 = T01(1:3, 4);
D02 = T02(1:3, 4);
D03 = T03(1:3, 4);
D04 = T04(1:3, 4);
D05 = T05(1:3, 4);
D06 = T06(1:3, 4);

% Calculate the difference
D16 = simplify(D06 - D01);
D26 = simplify(D06 - D02);
D36 = simplify(D06 - D03);
D46 = simplify(D06 - D04);
D56 = simplify(D06 - D05);

%% Express the velocities parameters (The first 3 rows) of each joints
J1 = simplify (cross(R01, D16));
J2 = simplify (cross(R02, D26));
J3 = simplify (cross(R03, D36));
J4 = simplify (cross(R04, D46));
J5 = simplify (cross(R05, D56));

%% Express the Jacobian matrix and its determinant
J = [J1, J2, J3, J4, J5; R01, R02, R03, R04, R05];

LinJ = J(1:3, :);