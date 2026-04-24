function TH = Inverse(MDH, Base, Target, Disp, name)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function TH = Inverse(MDH, Base, Target, App)
%
% Task: Determine the Inverse Kinematics of a 6DOF Robot
%
% Inputs:
%	- MDH: Modified Denavit-Hartenberg table of the Robot
%	- Base: Position of the base of the Robot in the workstation
%	- Target: Position of the target of the Robot in the workstation
%	- App: Orientation of the end effector at the target
%   - Disp: Display the angles and the resulting position if true (for verification)
%
% Output: 
%	- TH: Vector of all the Theta values
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 29/03/2026
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Extract the UR dimentions from its MDH table

L1 = MDH(1,3);
L2 = MDH(3,2);
L3 = MDH(4,2);
L4 = MDH(5,2);
L5 = MDH(6,2);

%% Target position on the robot frame

xPR = Target(1,1) - Base(1,1) - 54 - L5;
yPR = Target(2,1) - Base(2,1);
zPR = Target(3,1) - Base(3,1) - L1; % Remove the Link 1 height

%% Theta 1

TH1 = atan(yPR / xPR);   % Calculate temporary angles

TH1 = double(vpa(TH1)); % Express the angle value as numerical double

%% Theta 2

OAxy = sqrt(xPR^2 + yPR^2) - L4; % Distance frame1 - frame 3 (top view)

OA = sqrt(OAxy^2 + zPR^2); % Distance frame 1 - frame 3 (side view)

c = L2;
a = L3;
b = OA;

alpha = acos((b^2 + c^2 - a^2) / (2 * b * c));
beta = acos((a^2 + c^2 - b^2) / (2 * a * c));
gama = acos((a^2 + b^2 - c^2) / (2 * a * b));

TH2 = -pi/2 +atan(zPR/OAxy) + alpha;

TH2 = double(vpa(TH2)); % Express the angle value as numerical double

%% Theta 3

TH3 = - pi + beta;

TH3 = double(vpa(TH3)); % Express the angle value as numerical double

%% Theta 4

TH4 = -pi/2 - TH2 - TH3; % Calculate Theta 4 as a function of Theta 2 and 3 so that link 5 if perfecly horizontal

TH4 = double(vpa(TH4)); % Express the angle value as numerical double

%% Theta 5

TH5 = -TH1;   % Calculate Theta 5 as a function of Theta 1 so that the end-effector if perfecly aligned with the x axis

%% Display

if Disp == true
    fprintf('Position values (mm) for ')
    fprintf(name)
    fprintf(" position, with respect to the base of VISNAT:\n")
    
    fprintf('x: %.5f\ny: %.5f\nz: %.5f\n\n', xPR+L5+54, yPR, zPR+L1);

    dTH1 = vpa(TH1 * 180/pi, 5);    % Express Theta 1 in degree
    dTH2 = vpa(TH2 * 180/pi, 5);    % Express Theta 2 in degree
    dTH3 = vpa(TH3 * 180/pi, 5);    % Express Theta 3 in degree
    dTH4 = vpa(TH4 * 180/pi, 5);    % Express Theta 4 in degree
    dTH5 = vpa(TH5 * 180/pi, 5);    % Express Theta 5 in degree

    fprintf('Theta values (degrees) for ');
    fprintf(name)
    fprintf(" position:\n")
    
    fprintf('TH1: %.5f\nTH2: %.5f\nTH3: %.5f\nTH4: %.5f\nTH5: %.5f\n\n', dTH1, dTH2, dTH3, dTH4, dTH5);
end

%% Create the vector with all the angles

TH = [TH1; TH2; TH3; TH4; TH5];