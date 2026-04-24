function Verify(Path, T06, J, LinJ, print, robot)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% function Verify(Path, T06, Det, print, robot)
% 
% Task: Verify the Inverse Kinematics and if we have singularities or are close to one
%
% Inputs:
%	- Path: Matrix containing all of the path's targets
%   - T06: The final transformation matrix of the robot
%   - Det: The determinant of the Jacobian of the robot
%   - print: boolean if you want to print the results or not
%   - robot: the robot model
%
% author: Sébastien Dubois, s.j.dubois.116@cranfield.ac.uk
% date: 12/12/2025
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% Calculate the transformation matrix with the angles found in the Path
if print
    for i = 1:size(Path, 2)
        T = double(T06(Path(1, i), Path(2, i), Path(3, i), Path(4, i), Path(5, i)));    % Calculate the transformation matrix with the current angle set to verify with our calculations
        fprintf('Transformation Matrix T for the %s at target %d:\n', robot, i);
        disp(T);
    end
end

%% Calculate the determinant with the angle configurations in the Path
Sing = false;
Close = false;
for i = 1:size(Path, 2)
    r = rank(double(LinJ(Path(1, i), Path(2, i), Path(3, i), Path(4, i), Path(5, i))));
    s = svd(double(LinJ(Path(1, i), Path(2, i), Path(3, i), Path(4, i), Path(5, i))));
    rFull = rank(double(J(Path(1, i), Path(2, i), Path(3, i), Path(4, i), Path(5, i))));
    sFull = svd(double(LinJ(Path(1, i), Path(2, i), Path(3, i), Path(4, i), Path(5, i))));
    if  r < 3 || rFull < 5
        fprintf('Determinant of the %s is zero at target %d, singular configuration.\n', robot, i);   % Print the target number if you are at a singularity
        Sing = true;
    elseif min(s) < 1e-4 || min(sFull) < 1e-4
        fprintf('Determinant = %d is close to zero at target %d, potential singular configuration for the %s.\n', D, i, robot); % Print the target number if you are close to singularity
        Close = true;
    end
end

%% Print necessary informations about the path
if Sing
    fprintf('\nYour path is not safe as you are at a singularity at some point\n\n');
elseif Close
    fprintf('\nYour path may not be safe as you are close to singularity\n\n');
else
    fprintf('\nYour path is completely safe\n\n')
end