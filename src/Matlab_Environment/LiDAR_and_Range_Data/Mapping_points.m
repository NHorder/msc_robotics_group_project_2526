clc;
clear;
close all;

%% ---------------- USER SETTINGS ----------------
lidarFile = 'lidar_raw.csv';
rangeFile = 'ranges_raw.csv';

offset = 0.75;   % 75 cm inward from wall A
offset = 0.50; % 50 cm inward from Wall B
step   = 0.95;   % 75 cm spacing

%% ---------------- CHECK FILES ----------------
if ~exist(lidarFile,'file')
    error('File not found: %s', lidarFile);
end

if ~exist(rangeFile,'file')
    error('File not found: %s', rangeFile);
end

%% ---------------- RANGE PARAMETERS ----------------
angle_min       = -3.141590118408203;
angle_increment =  0.003929443191736937;

%% ---------------- WALL DEFINITIONS ----------------
wallA_start = [-1.00,  6.00];
wallA_end   = [ 5.50,  6.00];

wallB_start = [ 7.16,  6.00];
wallB_end   = [ 8.74,  6.00];

wallC_start = [ 8.74,  6.00];
wallC_end   = [ 8.80, -1.37];

wallD_start = [ 8.80, -1.37];
wallD_end   = [-1.00, -1.39];

wallE_start = [-1.00, -1.39];
wallE_end   = [-1.00,  6.00];

%% ---------------- LOAD LIDAR XY ----------------
lidarXY = readmatrix(lidarFile);

if isempty(lidarXY) || size(lidarXY,2) < 2
    error('lidar_raw.csv must contain at least 2 numeric columns [X Y].');
end

lidarXY = lidarXY(:,1:2);
lidarXY = lidarXY(all(isfinite(lidarXY),2), :);

%% ---------------- LOAD RANGE DATA ----------------
ranges = readmatrix(rangeFile);

if isempty(ranges)
    error('ranges_raw.csv is empty or unreadable.');
end

ranges = ranges(:);
ranges = ranges(isfinite(ranges));

N = numel(ranges);
angles = angle_min + (0:N-1)' * angle_increment;

M = min(numel(ranges), numel(angles));
ranges = ranges(1:M);
angles = angles(1:M);

rangeX = ranges .* cos(angles);
rangeY = ranges .* sin(angles);

%% ---------------- FIRST POINT CHECK ----------------
firstPoint = [wallA_start(1) + offset, wallA_start(2) - offset];
diagDist = norm(firstPoint - wallA_start);

fprintf('\n=================================================\n');
fprintf(' FIRST POINT CHECK\n');
fprintf('=================================================\n');
fprintf('First point = (%.3f, %.3f) m\n', firstPoint(1), firstPoint(2));
fprintf('Diagonal from Wall A start = %.3f m\n', diagDist);
fprintf('Expected approx = 1.06 m\n');

%% ---------------- GENERATE INSIDE POINTS ----------------
% Wall A -> inward = down
ptsA = computeWallPoints(wallA_start, wallA_end, offset, step, 'right');

% Wall C -> inward = left
ptsC = computeWallPoints(wallC_start, wallC_end, offset, step, 'right');

% Wall D -> inward = up
ptsD = computeWallPoints(wallD_start, wallD_end, offset, step, 'right');

% Wall E -> inward = right
ptsE = computeWallPoints(wallE_start, wallE_end, offset, step, 'right');

%% ---------------- PRINT POINTS ----------------
fprintf('\n=================================================\n');
fprintf(' WALL A POINTS\n');
fprintf('=================================================\n');
for i = 1:size(ptsA,1)
    fprintf('A%02d = (%.3f, %.3f)\n', i, ptsA(i,1), ptsA(i,2));
end

fprintf('\n=================================================\n');
fprintf(' WALL C POINTS\n');
fprintf('=================================================\n');
for i = 1:size(ptsC,1)
    fprintf('C%02d = (%.3f, %.3f)\n', i, ptsC(i,1), ptsC(i,2));
end

fprintf('\n=================================================\n');
fprintf(' WALL D POINTS\n');
fprintf('=================================================\n');
for i = 1:size(ptsD,1)
    fprintf('D%02d = (%.3f, %.3f)\n', i, ptsD(i,1), ptsD(i,2));
end

fprintf('\n=================================================\n');
fprintf(' WALL E POINTS\n');
fprintf('=================================================\n');
fprintf('E1 is shared with D%d at (%.3f, %.3f)\n', size(ptsD,1), ptsD(end,1), ptsD(end,2));
for i = 1:size(ptsE,1)
    fprintf('E%02d = (%.3f, %.3f)\n', i+1, ptsE(i,1), ptsE(i,2));
end

%% ---------------- SAVE POINTS TO CSV ----------------
wallNames = [
    repmat("WallA", size(ptsA,1), 1)
    repmat("WallC", size(ptsC,1), 1)
    repmat("WallD", size(ptsD,1), 1)
    "WallE"
    repmat("WallE", size(ptsE,1), 1)
];

allPts = [
    ptsA
    ptsC
    ptsD
    ptsD(end,:)   % shared point = E1
    ptsE
];

pointLabels = [
    "A" + string((1:size(ptsA,1))')
    "C" + string((1:size(ptsC,1))')
    "D" + string((1:size(ptsD,1))')
    "E1"
    "E" + string((2:size(ptsE,1)+1))'
];

T = table(wallNames, pointLabels, allPts(:,1), allPts(:,2), ...
    'VariableNames', {'Wall','Point','X_m','Y_m'});

writetable(T, 'robot_wall_points.csv');
fprintf('\nSaved generated points to: robot_wall_points.csv\n');

%% ---------------- PLOT ----------------
figure('Color','w','Name','Robot Wall Points from LiDAR and Range Data');
hold on;
axis equal;
grid on;
box on;

% LiDAR XY
plot(lidarXY(:,1), lidarXY(:,2), '.', ...
    'Color', [0.20 0.20 0.20], 'MarkerSize', 7);

% Range XY
plot(rangeX, rangeY, '.', ...
    'Color', [0.65 0.80 1.00], 'MarkerSize', 5);

% Walls
plot([wallA_start(1) wallA_end(1)], [wallA_start(2) wallA_end(2)], 'k-', 'LineWidth', 2);
plot([wallB_start(1) wallB_end(1)], [wallB_start(2) wallB_end(2)], 'k-', 'LineWidth', 2);
plot([wallC_start(1) wallC_end(1)], [wallC_start(2) wallC_end(2)], 'k-', 'LineWidth', 2);
plot([wallD_start(1) wallD_end(1)], [wallD_start(2) wallD_end(2)], 'k-', 'LineWidth', 2);
plot([wallE_start(1) wallE_end(1)], [wallE_start(2) wallE_end(2)], 'k-', 'LineWidth', 2);

% Red points
plot(ptsA(:,1), ptsA(:,2), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
plot(ptsC(:,1), ptsC(:,2), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
plot(ptsD(:,1), ptsD(:,2), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');
plot(ptsE(:,1), ptsE(:,2), 'ro', 'MarkerSize', 8, 'MarkerFaceColor', 'r');

% Connect sequences
plot(ptsA(:,1), ptsA(:,2), 'r--', 'LineWidth', 1.0);
plot(ptsC(:,1), ptsC(:,2), 'r--', 'LineWidth', 1.0);
plot(ptsD(:,1), ptsD(:,2), 'r--', 'LineWidth', 1.0);

% For Wall E, connect shared E1 -> ptsE
plot([ptsD(end,1); ptsE(:,1)], [ptsD(end,2); ptsE(:,2)], 'r--', 'LineWidth', 1.0);

% Highlight first point
plot(firstPoint(1), firstPoint(2), 'rs', ...
    'MarkerSize', 10, 'MarkerFaceColor', 'y', 'LineWidth', 1.5);

% Wall labels
text(mean([wallA_start(1), wallA_end(1)]), wallA_start(2)+0.18, 'Wall A', ...
    'FontWeight','bold', 'HorizontalAlignment','center');
text(mean([wallB_start(1), wallB_end(1)]), wallB_start(2)+0.18, 'Wall B', ...
    'FontWeight','bold', 'HorizontalAlignment','center');
text(wallC_start(1)+0.25, mean([wallC_start(2), wallC_end(2)]), 'Wall C', ...
    'FontWeight','bold', 'Rotation',90, 'HorizontalAlignment','center');
text(mean([wallD_start(1), wallD_end(1)]), mean([wallD_start(2), wallD_end(2)])-0.25, 'Wall D', ...
    'FontWeight','bold', 'HorizontalAlignment','center');
text(wallE_start(1)-0.28, mean([wallE_start(2), wallE_end(2)]), 'Wall E', ...
    'FontWeight','bold', 'Rotation',90, 'HorizontalAlignment','center');

% Point labels: Wall A
for i = 1:size(ptsA,1)
    text(ptsA(i,1)+0.05, ptsA(i,2)+0.05, sprintf('A%d',i), ...
        'Color','r', 'FontSize',8, 'FontWeight','bold');
end

% Point labels: Wall C
for i = 1:size(ptsC,1)
    text(ptsC(i,1)+0.05, ptsC(i,2)+0.05, sprintf('C%d',i), ...
        'Color','r', 'FontSize',8, 'FontWeight','bold');
end

% Point labels: Wall D
for i = 1:size(ptsD,1)
    text(ptsD(i,1)+0.05, ptsD(i,2)+0.05, sprintf('D%d',i), ...
        'Color','r', 'FontSize',8, 'FontWeight','bold');
end

% Shared corner label cleanly shown as D(end) = E1
text(ptsD(end,1)-1.10, ptsD(end,2)-0.35, sprintf('D%d = E1', size(ptsD,1)), ...
    'Color','r', 'FontSize',8, 'FontWeight','bold');

% Wall E generated points become E2, E3, ...
for i = 1:size(ptsE,1)
    text(ptsE(i,1)+0.05, ptsE(i,2)+0.05, sprintf('E%d', i+1), ...
        'Color','r', 'FontSize',8, 'FontWeight','bold');
end

% First point annotation
text(firstPoint(1)+0.08, firstPoint(2)-0.12, ...
    sprintf('P1 (diag = %.2f m)', diagDist), ...
    'Color','r', 'FontWeight','bold');

xlabel('X (m)');
ylabel('Y (m)');
title('LiDAR / Range Data with Robot Points Marked in Red');

legend({'LiDAR XY','Range XY','Wall A','Wall B','Wall C','Wall D','Wall E', ...
        'Wall A Points','Wall C Points','Wall D Points','Wall E Points'}, ...
        'Location','bestoutside');

%% ---------------- SUMMARY ----------------
fprintf('\n=================================================\n');
fprintf(' SUMMARY\n');
fprintf('=================================================\n');
fprintf('Wall A points: %d\n', size(ptsA,1));
fprintf('Wall C points: %d\n', size(ptsC,1));
fprintf('Wall D points: %d\n', size(ptsD,1));
fprintf('Wall E points: %d generated + 1 shared point (E1)\n', size(ptsE,1));
fprintf('Total saved points : %d\n', size(allPts,1));
fprintf('Done.\n');

%% =========================================================
%  LOCAL FUNCTION
%% =========================================================
function pts = computeWallPoints(p1, p2, offset, step, sideChoice)

    dirVec = p2 - p1;
    L = norm(dirVec);
    unitVec = dirVec / L;

    leftNormal  = [-unitVec(2),  unitVec(1)];
    rightNormal = [ unitVec(2), -unitVec(1)];

    switch lower(sideChoice)
        case 'left'
            normalVec = leftNormal;
        case 'right'
            normalVec = rightNormal;
        otherwise
            error('sideChoice must be either "left" or "right".');
    end

    % Start one spacing away from the corner
    tVals = step:step:(L - step);

    pts = zeros(numel(tVals), 2);

    for k = 1:numel(tVals)
        pts(k,:) = p1 + tVals(k)*unitVec + offset*normalVec;
    end
end