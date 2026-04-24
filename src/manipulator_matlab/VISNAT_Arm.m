function [th, overlapingRatio] = VISNAT_Arm(topL, botR)
% VISNAT_Arm([445.2, 500, 2700]', [445.2, -500, 100]')

clc

warning('off','all')

%% Targets and Path Planning

% Robots infos
syms th1 th2 th3 th4 th5  % Express variables as symbolic so we can make calculations while keeping them as unknown

MDH = [   0,     0,     300, th1, 0;       % Express the MDH Table of VISNAT
          pi/2,  0,     0,   th2, pi/2;
          0,     900,   0,   th3, 0;
          0,     1300,  0,   th4, 0;
          -pi/2, 100,   0,   th5, 0;
          0,     156.5, 0,   0,   0];

Pos = [0; 0; 300];  % The position of the robot in the workstation

[T01, T12, T23, T34, T45, T56, T06] = Forward(MDH); % Compute the Forward Kinematics of VISNAT

baseSize = 304.8;
RollerSize = 228.6;
movingSpeed = 500;  % mm/s
paintingSpeed = 70; % mm/s best speed for painting 620 sqrfeet/h 250 max

% Robot's Targets
Home = [710.5; 0; 400];     % Create the Home position in the x, y and z coordinates

ymaxL = topL(2,1) - (RollerSize/2) - 20;
ymaxR = botR(2,1) + (RollerSize/2) + 20;
ymax = ymaxL - ymaxR;
nbPath = ceil(ymax/(RollerSize-10));
ydisp = ymax/(nbPath);

oneOverlap = RollerSize-ydisp;
totalOverlap = oneOverlap*nbPath;
overlapingRatio = ymax/totalOverlap;

xmaxL = topL(1,1) + baseSize;
xmaxR = botR(1,1) + baseSize;
xmax = xmaxL - xmaxR;
xdisp = xmax/(nbPath);

zmax = topL(3,1) - 60;
zmin = botR(3,1) + 60;

posPath = [Home; movingSpeed];

i=0;

nbPath = nbPath + 1;

while i<nbPath
    apptop = [xmaxL+i*xdisp-10; ymaxL-i*ydisp; zmax; movingSpeed];      % Create the path going down
    top = [xmaxL+i*xdisp; ymaxL-i*ydisp; zmax; paintingSpeed];
    bot = [xmaxL+i*xdisp; ymaxL-i*ydisp; zmin; paintingSpeed];
    appbot = [xmaxL+i*xdisp-10; ymaxL-i*ydisp; zmin; paintingSpeed];
    posPath = [posPath, apptop, top, bot, appbot];
    i = i+1;
    if i+1<=nbPath
        appbot = [xmaxL+i*xdisp-10; ymaxL-i*ydisp; zmax; paintingSpeed];    % Create the path going up
        bot = [xmaxL+i*xdisp; ymaxL-i*ydisp; zmax; paintingSpeed];
        top = [xmaxL+i*xdisp; ymaxL-i*ydisp; zmin; paintingSpeed];
        apptop = [xmaxL+i*xdisp-10; ymaxL-i*ydisp; zmin; movingSpeed];
        posPath = [posPath, apptop, top, bot, appbot];
        i = i+1;
    end
end

posPath = [posPath, [Home; movingSpeed]];

% plot straight lines path
plot3(posPath(1,:), posPath(2,:), posPath(3,:), '-x')
grid on
xlabel('X')
ylabel('Y')
zlabel('Z')
title('Robot XYZ Path')
axis equal

%% Path Calculations

dt = 0.5;   % time between each steps
targetPos = [Home; movingSpeed];

for i=2:length(posPath)
    segDist = sqrt((posPath(1,i-1)-posPath(1,i))^2 + (posPath(2,i-1)-posPath(2,i))^2 + (posPath(3,i-1)-posPath(3,i))^2);    % Distance of the dirrent segment
    segNbPos = ceil(segDist/(dt*posPath(4,i)));                                                                             % Number of position for the segment
    for j=1:segNbPos
        targetPos = [targetPos, posPath(:,i-1) + (posPath(:,i) - posPath(:,i-1)) * (j/segNbPos)];
    end
end

%% Calculate the theta for every points in the path

th = [];    % Create the matrix for the angles

for i=1:length(targetPos)
    th = [th, Inverse(MDH, Pos, targetPos(1:3,i), false, 'VISNAT')];
end

th  % Send theta angles for simulation

%% Singularity verification of each points to see if the path is safe or not

[J, LinJ] = Jacobian(T01, T12, T23, T34, T45, T06);  % Compute the Jacobian of the VISNAT
J(th1, th2, th3, th4, th5) = J;
LinJ(th1, th2, th3, th4, th5) = LinJ;              % Set the parameters to use it for verification

Verify(th, T06, J, LinJ, false, 'VISNAT')