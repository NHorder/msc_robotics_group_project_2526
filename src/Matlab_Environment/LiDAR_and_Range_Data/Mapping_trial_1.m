clc;
clear;
close all;
lidarFile = 'lidar_raw.csv';
rangeFile = 'ranges_raw.csv';

if ~exist(lidarFile,'file')
    error('File not found: %s', lidarFile);
end
if ~exist(rangeFile,'file')
    error('File not found: %s', rangeFile);
end

%% ---------------- PARAMETERS ----------------
wallOffset   = 0.75;      % 75 cm from the painted wall (inward)
pauseTime    = 0.20;      % animation pause
wallHeight   = 3.048;     % 10 ft in metres
robotZ       = 0.10;      % robot marker height above floor
pathZ        = 0.05;      % path drawn slightly above floor
arrowLen     = 0.35;      % heading arrow length

angle_min       = -3.141590118408203;
angle_increment =  0.003929443191736937;

%% ---------------- WALL DEFINITIONS ----------------
% Wall A : horizontal top  (left → right)
wallA_start = [-1.00,  6.00];
wallA_end   = [ 5.50,  6.00];

% Wall B : horizontal top-right (left → right)
wallB_start = [ 7.16,  6.00];
wallB_end   = [ 8.74,  6.00];

% Wall C : vertical right  (top → bottom)
wallC_start = [ 8.74,  6.00];
wallC_end   = [ 8.80, -1.37];

% Wall D : horizontal bottom (right → left)
wallD_start = [ 8.80, -1.37];
wallD_end   = [-1.00, -1.39];

% Wall E : vertical left   (bottom → top)
wallE_start = [-1.00, -1.39];
wallE_end   = [-1.00,  6.00];

%% ---- Derived geometry used for side-gap constraints ----
wallA_tStart = 0.50;
wallA_tEnd   = norm(wallA_end - wallA_start) - 0.50;

wallB_tStart = 0.50;
wallB_tEnd   = norm(wallB_end - wallB_start) - 0.50;

wallC_tStart = 0.50;
wallC_tEnd   = norm(wallC_end - wallC_start) - 0.50;

wallD_tStart = 0.50;
wallD_tEnd   = norm(wallD_end - wallD_start) - 0.50;

wallE_tStart = 0.50;
wallE_tEnd   = norm(wallE_end - wallE_start) - 0.50;

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

scanPts = [lidarXY; [rangeX rangeY]];
scanPts = scanPts(all(isfinite(scanPts),2), :);

%% =========================================================
% ROBOT POINTS — centred in 1 m yellow segments
%% =========================================================
ptsA = centredRobotPoints(wallA_start, wallA_end, wallOffset, wallA_tStart, wallA_tEnd, 'right');
ptsB = centredRobotPoints(wallB_start, wallB_end, wallOffset, wallB_tStart, wallB_tEnd, 'right');
ptsC = centredRobotPoints(wallC_start, wallC_end, wallOffset, wallC_tStart, wallC_tEnd, 'right');
ptsD = centredRobotPoints(wallD_start, wallD_end, wallOffset, wallD_tStart, wallD_tEnd, 'right');
ptsE = centredRobotPoints(wallE_start, wallE_end, wallOffset, wallE_tStart, wallE_tEnd, 'right');

%% ---------------- YELLOW MEASUREMENT POINTS ----------------
measA = computeMeasurementPoints(wallA_start, wallA_end, 1.00);
measB = computeMeasurementPoints(wallB_start, wallB_end, 1.00);
measC = computeMeasurementPoints(wallC_start, wallC_end, 1.00);
measD = computeMeasurementPoints(wallD_start, wallD_end, 1.00);
measE = computeMeasurementPoints(wallE_start, wallE_end, 1.00);

%% ---------------- LOOK DIRECTION VECTORS ----------------
% Robot must look at the main wall for its current point
faceA = lookVectorToWall(wallA_start, wallA_end, 'right', arrowLen);
faceB = lookVectorToWall(wallB_start, wallB_end, 'right', arrowLen);
faceC = lookVectorToWall(wallC_start, wallC_end, 'right', arrowLen);
faceD = lookVectorToWall(wallD_start, wallD_end, 'right', arrowLen);
faceE = lookVectorToWall(wallE_start, wallE_end, 'right', arrowLen);

%% ---------------- START POSITION ----------------
startPos = ptsA(1,:);

xMin_inside = wallE_start(1) + 0.01;
xMax_inside = wallC_start(1) - 0.01;
yMin_inside = wallD_start(2) + 0.01;
yMax_inside = wallA_start(2) - 0.01;

insideMask = ...
    scanPts(:,1) > xMin_inside & scanPts(:,1) < xMax_inside & ...
    scanPts(:,2) > yMin_inside & scanPts(:,2) < yMax_inside;

insideScanPts = scanPts(insideMask,:);

if isempty(insideScanPts)
    error('No scan points were found inside the room boundary.');
end

dInside = vecnorm(insideScanPts - startPos, 2, 2);
[closestDist, idxClosest] = min(dInside);
robotInitialPos = insideScanPts(idxClosest,:);

dx = robotInitialPos(1) - startPos(1);
dy = robotInitialPos(2) - startPos(2);

fprintf('\n=================================================\n');
fprintf(' ROBOT START POSITION ANALYSIS\n');
fprintf('=================================================\n');
fprintf('Planned start point          : (%.4f, %.4f) m\n', startPos(1), startPos(2));
fprintf('Closest inside scan point    : (%.4f, %.4f) m\n', robotInitialPos(1), robotInitialPos(2));
fprintf('Horizontal offset            : %+0.4f m\n', dx);
fprintf('Vertical offset              : %+0.4f m\n', dy);
fprintf('Distance to start            : %.4f m\n', closestDist);
fprintf('=================================================\n');

fprintf('\n--- Robot Points Summary ---\n');
printWallPoints('A', ptsA);
printWallPoints('B', ptsB);
printWallPoints('C', ptsC);
printWallPoints('D', ptsD);
printWallPoints('E', ptsE);

%% ---------------- FULL PATH  A → B → C → D → E → Start ----------------
pathPts = [];
pathDirs = [];

pathPts = [pathPts; robotInitialPos];
pathDirs = [pathDirs; faceA];

pathPts = [pathPts; startPos];
pathDirs = [pathDirs; faceA];

pathPts = [pathPts; ptsA];
pathDirs = [pathDirs; repmat(faceA, size(ptsA,1), 1)];

pathPts = [pathPts; ptsB(1,:)];
pathDirs = [pathDirs; faceB];
pathPts = [pathPts; ptsB];
pathDirs = [pathDirs; repmat(faceB, size(ptsB,1), 1)];

pathPts = [pathPts; ptsC(1,:)];
pathDirs = [pathDirs; faceC];
pathPts = [pathPts; ptsC];
pathDirs = [pathDirs; repmat(faceC, size(ptsC,1), 1)];

pathPts = [pathPts; ptsD(1,:)];
pathDirs = [pathDirs; faceD];
pathPts = [pathPts; ptsD];
pathDirs = [pathDirs; repmat(faceD, size(ptsD,1), 1)];

pathPts = [pathPts; ptsE(1,:)];
pathDirs = [pathDirs; faceE];
pathPts = [pathPts; ptsE];
pathDirs = [pathDirs; repmat(faceE, size(ptsE,1), 1)];

pathPts = [pathPts; startPos];
pathDirs = [pathDirs; faceA];

%% ---------------- LABELS ----------------
pathLbl = strings(size(pathPts,1),1);
idx = 1;

pathLbl(idx) = "Robot placed at closest inside measured point"; idx = idx+1;
pathLbl(idx) = "Moving to planned start point";                 idx = idx+1;

for i = 1:size(ptsA,1)
    pathLbl(idx) = "Painting Wall A – A" + i; idx = idx+1;
end

pathLbl(idx) = "Transition to Wall B"; idx = idx+1;
for i = 1:size(ptsB,1)
    pathLbl(idx) = "Painting Wall B – B" + i; idx = idx+1;
end

pathLbl(idx) = "Transition to Wall C"; idx = idx+1;
for i = 1:size(ptsC,1)
    pathLbl(idx) = "Painting Wall C – C" + i; idx = idx+1;
end

pathLbl(idx) = "Transition to Wall D"; idx = idx+1;
for i = 1:size(ptsD,1)
    pathLbl(idx) = "Painting Wall D – D" + i; idx = idx+1;
end

pathLbl(idx) = "Transition to Wall E"; idx = idx+1;
for i = 1:size(ptsE,1)
    pathLbl(idx) = "Painting Wall E – E" + i; idx = idx+1;
end

pathLbl(idx) = "Returning to Start Position";

%% =========================================================
% 3D STATIC FIGURE
%% =========================================================
figure('Color','w','Name','3D Wall Simulation with Robot Path');
hold on; grid on; axis equal; view(40,25);
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)');
title('3D Room Simulation – Robot Faces Main Wall');

fill3([wallE_start(1) wallC_start(1) wallC_start(1) wallE_start(1)], ...
      [wallD_start(2) wallD_start(2) wallA_start(2) wallA_start(2)], ...
      [0 0 0 0], [0.92 0.92 0.92], 'FaceAlpha',0.35, 'EdgeColor','none');

drawWall3D(wallA_start, wallA_end, wallHeight, [0.7 0.7 0.7]);
drawWall3D(wallB_start, wallB_end, wallHeight, [0.7 0.7 0.7]);
drawWall3D(wallC_start, wallC_end, wallHeight, [0.7 0.7 0.7]);
drawWall3D(wallD_start, wallD_end, wallHeight, [0.7 0.7 0.7]);
drawWall3D(wallE_start, wallE_end, wallHeight, [0.7 0.7 0.7]);

plot3(lidarXY(:,1), lidarXY(:,2), zeros(size(lidarXY,1),1), '.', ...
    'Color',[0.25 0.25 0.25], 'MarkerSize',6);
plot3(rangeX, rangeY, zeros(size(rangeX,1),1), '.', ...
    'Color',[0.65 0.80 1.00], 'MarkerSize',5);

% Robot points with heading arrows
plotRobotPts3(ptsA, robotZ, 'r'); plotHeadingArrows3(ptsA, robotZ, faceA, 'r');
plotRobotPts3(ptsB, robotZ, 'r'); plotHeadingArrows3(ptsB, robotZ, faceB, 'r');
plotRobotPts3(ptsC, robotZ, 'r'); plotHeadingArrows3(ptsC, robotZ, faceC, 'r');
plotRobotPts3(ptsD, robotZ, 'r'); plotHeadingArrows3(ptsD, robotZ, faceD, 'r');
plotRobotPts3(ptsE, robotZ, 'r'); plotHeadingArrows3(ptsE, robotZ, faceE, 'r');

% Yellow measurement points
plotMeasPts3(measA, robotZ); plotMeasPts3(measB, robotZ);
plotMeasPts3(measC, robotZ); plotMeasPts3(measD, robotZ); plotMeasPts3(measE, robotZ);

% Path
plot3(pathPts(:,1), pathPts(:,2), pathZ*ones(size(pathPts,1),1), ...
    'g-', 'LineWidth',2.5);

% Markers
plot3(robotInitialPos(1), robotInitialPos(2), robotZ, 'co', ...
    'MarkerSize',10, 'MarkerFaceColor','c', 'LineWidth',1.5);
plot3(startPos(1), startPos(2), robotZ, 'ms', ...
    'MarkerSize',10, 'MarkerFaceColor','y', 'LineWidth',1.5);

% Wall labels
labelWall(wallA_start, wallA_end, wallHeight, 'Wall A', 0);
labelWall(wallB_start, wallB_end, wallHeight, 'Wall B', 0);
labelWall(wallC_start, wallC_end, wallHeight, 'Wall C', 0.15);
labelWall(wallD_start, wallD_end, wallHeight, 'Wall D', 0);
labelWall(wallE_start, wallE_end, wallHeight, 'Wall E', -0.15);

setAxLimits(wallA_start, wallA_end, wallB_start, wallB_end, ...
            wallC_start, wallC_end, wallD_start, wallD_end, ...
            wallE_start, wallE_end, wallHeight);

figure('Color',[0.08 0.08 0.10], 'Name','Raasta');
hold on; axis equal; grid on; box on; view(45,28);
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)');
title('Raasta', 'Color','w');
set(gca,'Color',[0.08 0.08 0.10], 'XColor','w', 'YColor','w', ...
    'ZColor','w', 'GridColor',[0.3 0.3 0.3]);

fill3([wallE_start(1) wallC_start(1) wallC_start(1) wallE_start(1)], ...
      [wallD_start(2) wallD_start(2) wallA_start(2) wallA_start(2)], ...
      [0 0 0 0],[0.20 0.20 0.20],'FaceAlpha',0.45,'EdgeColor','none');

drawWall3D(wallA_start, wallA_end, wallHeight, [0.90 0.90 0.90]);
drawWall3D(wallB_start, wallB_end, wallHeight, [0.90 0.90 0.90]);
drawWall3D(wallC_start, wallC_end, wallHeight, [0.90 0.90 0.90]);
drawWall3D(wallD_start, wallD_end, wallHeight, [0.90 0.90 0.90]);
drawWall3D(wallE_start, wallE_end, wallHeight, [0.90 0.90 0.90]);

plotRobotPts3(ptsA, robotZ, 'r'); plotHeadingArrows3(ptsA, robotZ, faceA, 'r');
plotRobotPts3(ptsB, robotZ, 'r'); plotHeadingArrows3(ptsB, robotZ, faceB, 'r');
plotRobotPts3(ptsC, robotZ, 'r'); plotHeadingArrows3(ptsC, robotZ, faceC, 'r');
plotRobotPts3(ptsD, robotZ, 'r'); plotHeadingArrows3(ptsD, robotZ, faceD, 'r');
plotRobotPts3(ptsE, robotZ, 'r'); plotHeadingArrows3(ptsE, robotZ, faceE, 'r');

plotMeasPts3(measA, robotZ); plotMeasPts3(measB, robotZ);
plotMeasPts3(measC, robotZ); plotMeasPts3(measD, robotZ); plotMeasPts3(measE, robotZ);

text(mean([wallA_start(1) wallA_end(1)]), wallA_start(2), wallHeight+0.08, ...
    'Wall A','Color','w','FontWeight','bold','HorizontalAlignment','center');
text(mean([wallB_start(1) wallB_end(1)]), wallB_start(2), wallHeight+0.08, ...
    'Wall B','Color','w','FontWeight','bold','HorizontalAlignment','center');
text(wallC_start(1)+0.15, mean([wallC_start(2) wallC_end(2)]), wallHeight+0.08, ...
    'Wall C','Color','w','FontWeight','bold','HorizontalAlignment','center');
text(mean([wallD_start(1) wallD_end(1)]), mean([wallD_start(2) wallD_end(2)]), wallHeight+0.08, ...
    'Wall D','Color','w','FontWeight','bold','HorizontalAlignment','center');
text(wallE_start(1)-0.15, mean([wallE_start(2) wallE_end(2)]), wallHeight+0.08, ...
    'Wall E','Color','w','FontWeight','bold','HorizontalAlignment','center');

hTrail = plot3(pathPts(1,1), pathPts(1,2), pathZ, '-','Color',[0 1 0],'LineWidth',2.5);
hBot   = plot3(pathPts(1,1), pathPts(1,2), robotZ, 'o', ...
    'MarkerSize',11,'MarkerFaceColor',[0 1 0],'MarkerEdgeColor','w','LineWidth',1.5);
hArrow = quiver3(pathPts(1,1), pathPts(1,2), robotZ, ...
    pathDirs(1,1), pathDirs(1,2), 0, 0, ...
    'Color','y', 'LineWidth',2, 'MaxHeadSize',1.8);

hInfo  = text(min(pathPts(:,1))-0.5, max(pathPts(:,2))+0.6, wallHeight+0.2, '', ...
    'Color','w','FontSize',10,'FontWeight','bold','VerticalAlignment','top');

setAxLimits(wallA_start, wallA_end, wallB_start, wallB_end, ...
            wallC_start, wallC_end, wallD_start, wallD_end, ...
            wallE_start, wallE_end, wallHeight);

for i = 1:size(pathPts,1)
    set(hTrail,'XData',pathPts(1:i,1),'YData',pathPts(1:i,2),'ZData',pathZ*ones(i,1));
    set(hBot,  'XData',pathPts(i,1),  'YData',pathPts(i,2),  'ZData',robotZ);
    set(hArrow,'XData',pathPts(i,1),'YData',pathPts(i,2),'ZData',robotZ, ...
               'UData',pathDirs(i,1),'VData',pathDirs(i,2),'WData',0);

    lbl = pathLbl(i);
    if contains(lbl,"closest inside"),     set(hBot,'MarkerFaceColor',[0 1 1],  'MarkerSize',12);
    elseif contains(lbl,"Moving to"),      set(hBot,'MarkerFaceColor',[1 1 0],  'MarkerSize',12);
    elseif contains(lbl,"Transition"),     set(hBot,'MarkerFaceColor',[1 1 0],  'MarkerSize',11);
    elseif contains(lbl,"Returning"),      set(hBot,'MarkerFaceColor',[0 1 0],  'MarkerSize',13);
    elseif contains(lbl,"Wall A"),         set(hBot,'MarkerFaceColor',[1 0.4 0.2],'MarkerSize',11);
    elseif contains(lbl,"Wall B"),         set(hBot,'MarkerFaceColor',[0.8 0.5 1],'MarkerSize',11);
    elseif contains(lbl,"Wall C"),         set(hBot,'MarkerFaceColor',[1 0.8 0.2],'MarkerSize',11);
    elseif contains(lbl,"Wall D"),         set(hBot,'MarkerFaceColor',[0.2 1 1],  'MarkerSize',11);
    elseif contains(lbl,"Wall E"),         set(hBot,'MarkerFaceColor',[1 0.2 1],  'MarkerSize',11);
    else,                                  set(hBot,'MarkerFaceColor',[0 1 0],  'MarkerSize',12);
    end

    set(hInfo,'String',sprintf('Step %d / %d\n%s', i, size(pathPts,1), lbl));
    drawnow; pause(pauseTime);
end

fprintf('\n3D simulation complete\n');

%% =========================================================
% LOCAL FUNCTIONS
%% =========================================================

function pts = centredRobotPoints(p1, p2, wallOffset, tStart, tEnd, sideChoice)
    dirVec  = p2 - p1;
    L       = norm(dirVec);
    unitVec = dirVec / L;

    leftNormal  = [-unitVec(2),  unitVec(1)];
    rightNormal = [ unitVec(2), -unitVec(1)];

    switch lower(sideChoice)
        case 'left',  normalVec = leftNormal;
        case 'right', normalVec = rightNormal;
        otherwise, error('sideChoice must be "left" or "right".');
    end

    if tEnd < tStart
        error('tEnd (%.3f) < tStart (%.3f): wall segment too short.', tEnd, tStart);
    end

    allMidpoints = 0.5 : 1.0 : (L - 0.5);
    tVals = allMidpoints(allMidpoints >= tStart & allMidpoints <= tEnd);

    if isempty(tVals)
        tVals = (tStart + tEnd) / 2;
    end

    if abs(tVals(end) - tEnd) > 1e-9
        tVals(end+1) = tEnd;
    end

    pts = zeros(numel(tVals), 2);
    for k = 1:numel(tVals)
        pts(k,:) = p1 + tVals(k)*unitVec + wallOffset*normalVec;
    end
end

function faceVec = lookVectorToWall(p1, p2, sideChoice, arrowLen)
    dirVec  = p2 - p1;
    unitVec = dirVec / norm(dirVec);

    leftNormal  = [-unitVec(2),  unitVec(1)];
    rightNormal = [ unitVec(2), -unitVec(1)];

    switch lower(sideChoice)
        case 'left'
            inward = leftNormal;
        case 'right'
            inward = rightNormal;
        otherwise
            error('sideChoice must be "left" or "right".');
    end

    % Robot stands inward of the wall, so to look AT the wall it faces opposite
    faceVec = -arrowLen * inward;
end

function pts = computeMeasurementPoints(p1, p2, measureStep)
    dirVec  = p2 - p1;
    L       = norm(dirVec);
    unitVec = dirVec / L;
    tVals   = 0 : measureStep : L;
    if ~isempty(tVals) && tVals(end) > L, tVals(end) = []; end
    pts = zeros(numel(tVals), 2);
    for k = 1:numel(tVals)
        pts(k,:) = p1 + tVals(k)*unitVec;
    end
end

function drawWall3D(p1, p2, h, faceCol)
    X = [p1(1) p2(1) p2(1) p1(1)];
    Y = [p1(2) p2(2) p2(2) p1(2)];
    Z = [0 0 h h];
    patch(X, Y, Z, faceCol, 'FaceAlpha',0.65, ...
        'EdgeColor',[0.2 0.2 0.2], 'LineWidth',1.0);
end

function plotRobotPts3(pts, rZ, col)
    plot3(pts(:,1), pts(:,2), rZ*ones(size(pts,1),1), 'o', ...
        'Color',col, 'MarkerSize',7, 'MarkerFaceColor',col);
end

function plotHeadingArrows3(pts, rZ, faceVec, col)
    quiver3(pts(:,1), pts(:,2), rZ*ones(size(pts,1),1), ...
        faceVec(1)*ones(size(pts,1),1), ...
        faceVec(2)*ones(size(pts,1),1), ...
        zeros(size(pts,1),1), ...
        0, 'Color', col, 'LineWidth', 1.4, 'MaxHeadSize', 1.4);
end

function plotMeasPts3(pts, rZ)
    plot3(pts(:,1), pts(:,2), rZ*ones(size(pts,1),1), 'yo', ...
        'MarkerSize',6, 'MarkerFaceColor','y');
end

function labelWall(p1, p2, h, lbl, xOff)
    mx = mean([p1(1) p2(1)]) + xOff;
    my = mean([p1(2) p2(2)]);
    text(mx, my, h+0.1, lbl, 'FontWeight','bold', 'HorizontalAlignment','center');
end

function setAxLimits(wAs, wAe, wBs, wBe, wCs, wCe, wDs, wDe, wEs, wEe, wH) %#ok<INUSL>
    xlim([min([wEs(1) wDe(1)])-1, max([wCs(1) wDs(1)])+1]);
    ylim([min([wDs(2) wEs(2)])-1, max([wAs(2) wEe(2)])+1]);
    zlim([0, wH+0.5]);
end

function printWallPoints(wallName, pts)
    fprintf('Wall %s: %d robot points\n', wallName, size(pts,1));
    for k = 1:size(pts,1)
        fprintf('  %s%d : (%.4f, %.4f)\n', wallName, k, pts(k,1), pts(k,2));
    end
end