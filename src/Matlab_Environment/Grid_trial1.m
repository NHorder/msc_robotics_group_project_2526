clc
clear
close all

%% =========================
% USER SETTINGS
%% =========================
objFile = 'ground_floor_env.obj';

% Roller stride = one paint stop spacing
stride = 0.091;   % 9.1 cm = 0.091 m

% Door reference point in top-view coordinates (EDIT THIS AFTER FIRST RUN)
% This should be the approximate centre of the entry door in the Hall.
doorPt = [0.00, -0.12];

% Initial heading when entering room:
% 1 = East, 2 = North, 3 = West, 4 = South
% "first grid to the right of the door" usually means move to +X first
initDir = 1;

% Floor extraction tolerance
zTol = 0.015;   % 1.5 cm tolerance around floor z

% Traversal safety limit
maxSteps = 8000;

%% =========================
% LOAD OBJ
%% =========================
[V,F] = readObjTri(objFile);

% Convert mm -> m
V = V/1000;

% Centre the model
V = V - mean(V,1);

%% =========================
% FIND FLOOR REGION
%% =========================
zMin = min(V(:,3));

% Vertices close to floor level
isFloorVertex = abs(V(:,3) - zMin) < zTol;

% Keep only faces whose 3 vertices lie on the floor
floorFaceMask = isFloorVertex(F(:,1)) & isFloorVertex(F(:,2)) & isFloorVertex(F(:,3));
Ffloor = F(floorFaceMask,:);

if isempty(Ffloor)
    error('No floor triangles were detected. Increase zTol slightly.')
end

% XY floor triangles only
Vxy = V(:,1:2);

%% =========================
% CREATE GRID OF CANDIDATE STOP POINTS
%% =========================
floorVertsXY = Vxy(unique(Ffloor(:)),:);

xmin = min(floorVertsXY(:,1));
xmax = max(floorVertsXY(:,1));
ymin = min(floorVertsXY(:,2));
ymax = max(floorVertsXY(:,2));

xg = xmin:stride:xmax;
yg = ymin:stride:ymax;

[XX,YY] = meshgrid(xg, yg);
candPts = [XX(:), YY(:)];

% Keep only points lying inside at least one floor triangle
insideMask = false(size(candPts,1),1);
for i = 1:size(Ffloor,1)
    tri = Vxy(Ffloor(i,:),:);
    insideMask = insideMask | pointInTriangleBatch(candPts, tri);
end

gridPts = candPts(insideMask,:);

if isempty(gridPts)
    error('No valid grid points found on the floor.')
end

%% =========================
% BUILD OCCUPANCY GRID FOR RRRR TRAVERSAL
%% =========================
% Snap valid points back to grid indices
validMap = false(length(yg), length(xg));

for i = 1:size(gridPts,1)
    ix = round((gridPts(i,1) - xmin)/stride) + 1;
    iy = round((gridPts(i,2) - ymin)/stride) + 1;

    if ix >= 1 && ix <= length(xg) && iy >= 1 && iy <= length(yg)
        validMap(iy,ix) = true;
    end
end

%% =========================
% FIND FIRST GRID POINT TO THE RIGHT OF THE DOOR
%% =========================
startIdx = findFirstGridRightOfDoor(doorPt, xmin, ymin, stride, xg, yg, validMap);

if isempty(startIdx)
    error('Could not find a valid grid point to the right of the door. Adjust doorPt.')
end

%% =========================
% RIGHT-HAND-RULE (RRRR) TRAVERSAL
%% =========================
[pathIdx, pathXY] = rightHandTraversal(validMap, xg, yg, startIdx, initDir, maxSteps);

fprintf('Number of stop points generated: %d\n', size(pathXY,1));
fprintf('Start grid point: (%.3f, %.3f)\n', pathXY(1,1), pathXY(1,2));

%% =========================
% PLOT 3D + TOP VIEW
%% =========================
figure('Color','w','Name','Environment with Paint Stop Points')

subplot(1,2,1)
patch('Vertices',V,...
      'Faces',F,...
      'FaceColor',[0 0 0],...
      'EdgeColor',[0.35 0.35 0.35],...
      'FaceAlpha',1);
hold on

% Plot stop points on floor in red
scatter3(pathXY(:,1), pathXY(:,2), zMin*ones(size(pathXY,1),1)+0.002, ...
         18, 'r', 'filled')

% Show traversal line
plot3(pathXY(:,1), pathXY(:,2), zMin*ones(size(pathXY,1),1)+0.002, ...
      'r-', 'LineWidth', 1.2)

% Mark door point and start point
plot3(doorPt(1), doorPt(2), zMin+0.005, 'bo', 'MarkerSize', 8, 'LineWidth', 2)
plot3(pathXY(1,1), pathXY(1,2), zMin+0.005, 'gs', 'MarkerSize', 8, 'LineWidth', 2)

axis equal
grid on
view(35,25)
xlabel('X (m)')
ylabel('Y (m)')
zlabel('Z (m)')
title('Environment - 3D View')

subplot(1,2,2)
patch('Vertices',V,...
      'Faces',F,...
      'FaceColor',[0 0 0],...
      'EdgeColor',[0.35 0.35 0.35],...
      'FaceAlpha',1);
hold on

% Stop points in red
scatter(pathXY(:,1), pathXY(:,2), 18, 'r', 'filled')

% Route line
plot(pathXY(:,1), pathXY(:,2), 'r-', 'LineWidth', 1.2)

% Door and starting point
plot(doorPt(1), doorPt(2), 'bo', 'MarkerSize', 8, 'LineWidth', 2)
plot(pathXY(1,1), pathXY(1,2), 'gs', 'MarkerSize', 8, 'LineWidth', 2)

view(2)
axis equal
grid on
xlabel('X (m)')
ylabel('Y (m)')
title('Environment - Top View with Paint Stop Points')

% Room labels
text(-0.23, 0.25, 'Kitchen / Breakfast', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(0.01, 0.31, 'Study', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(0.30, 0.22, 'Lounge', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(-0.26, -0.01, 'Utility Room', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(0.02, -0.01, 'Hall', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(0.13, -0.01, 'Store', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(-0.20, -0.37, 'Master Bedroom', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

text(0.28, -0.37, 'Bedroom 2', ...
    'FontWeight','bold', 'FontSize',11, ...
    'HorizontalAlignment','center', 'VerticalAlignment','middle', ...
    'Color','r')

legend('Environment','Stop points','Route','Door','Start point','Location','bestoutside')

sgtitle('Environment with Floor Stop Points and RRRR Route','FontWeight','bold')

%% =========================
% OPTIONAL: PRINT STOP POINTS
%% =========================
disp('First 20 stop points [X Y] in metres:')
disp(pathXY(1:min(20,end),:))

%% =========================================================
% LOCAL FUNCTIONS
%% =========================================================
function [V,F] = readObjTri(filename)

fid = fopen(filename,'r');

if fid == -1
    error('Could not open OBJ file')
end

V = [];
F = [];

while true
    tline = fgetl(fid);

    if ~ischar(tline)
        break
    end

    tline = strtrim(tline);

    if startsWith(tline,'v ')
        vals = sscanf(tline(3:end),'%f');
        if numel(vals) >= 3
            V(end+1,:) = vals(1:3)';
        end
    elseif startsWith(tline,'f ')
        parts = strsplit(tline);
        idx = zeros(1,numel(parts)-1);

        for i = 2:numel(parts)
            token = parts{i};
            tokenParts = strsplit(token,'/');
            idx(i-1) = str2double(tokenParts{1});
        end

        idx = idx(~isnan(idx));
        idx = idx(idx > 0);

        if numel(idx) == 3
            F(end+1,:) = idx;
        elseif numel(idx) > 3
            for k = 2:numel(idx)-1
                F(end+1,:) = [idx(1) idx(k) idx(k+1)];
            end
        end
    end
end

fclose(fid);
F = unique(F,'rows');
end

function inside = pointInTriangleBatch(P, tri)
% P = Nx2 points
% tri = 3x2 triangle vertices

A = tri(1,:);
B = tri(2,:);
C = tri(3,:);

v0 = C - A;
v1 = B - A;
v2 = P - A;

dot00 = dot(v0,v0);
dot01 = dot(v0,v1);
dot11 = dot(v1,v1);

dot02 = v2(:,1)*v0(1) + v2(:,2)*v0(2);
dot12 = v2(:,1)*v1(1) + v2(:,2)*v1(2);

invDen = 1 / (dot00*dot11 - dot01*dot01 + eps);
u = (dot11*dot02 - dot01*dot12) * invDen;
v = (dot00*dot12 - dot01*dot02) * invDen;

inside = (u >= -1e-10) & (v >= -1e-10) & (u + v <= 1 + 1e-10);
end

function startIdx = findFirstGridRightOfDoor(doorPt, xmin, ymin, stride, xg, yg, validMap)
% Find the first valid cell to the right (+X) of the door reference

ixDoor = round((doorPt(1) - xmin)/stride) + 1;
iyDoor = round((doorPt(2) - ymin)/stride) + 1;

startIdx = [];

for ix = ixDoor+1:length(xg)
    if iyDoor >= 1 && iyDoor <= length(yg)
        if validMap(iyDoor, ix)
            startIdx = [iyDoor, ix];
            return
        end
    end
end

% fallback: nearest valid point
if isempty(startIdx)
    [yy,xx] = find(validMap);
    if ~isempty(xx)
        d2 = (xx - ixDoor).^2 + (yy - iyDoor).^2;
        [~,id] = min(d2);
        startIdx = [yy(id), xx(id)];
    end
end
end

function [pathIdx, pathXY] = rightHandTraversal(validMap, xg, yg, startIdx, initDir, maxSteps)
% Right-hand-rule traversal on a 4-connected grid
%
% dir coding:
% 1 = East, 2 = North, 3 = West, 4 = South

dirs = [0 1; -1 0; 0 -1; 1 0]; % [dRow dCol] for E,N,W,S in matrix sense
cur = startIdx;
dir = initDir;

pathIdx = cur;
visitedCount = 0;

for step = 1:maxSteps
    visitedCount = visitedCount + 1;

    % Right, straight, left, back priorities
    candDirs = [turnRight(dir), dir, turnLeft(dir), turnBack(dir)];
    moved = false;

    for k = 1:4
        d = candDirs(k);
        nxt = cur + dirs(d,:);

        if isValidCell(nxt, validMap)
            cur = nxt;
            dir = d;
            pathIdx(end+1,:) = cur; %#ok<AGROW>
            moved = true;
            break
        end
    end

    if ~moved
        break
    end

    % stop once we return to start after a meaningful loop
    if size(pathIdx,1) > 10 && isequal(cur, startIdx)
        break
    end
end

% Convert grid indices to XY
pathXY = zeros(size(pathIdx,1),2);
for i = 1:size(pathIdx,1)
    iy = pathIdx(i,1);
    ix = pathIdx(i,2);
    pathXY(i,:) = [xg(ix), yg(iy)];
end

% Remove immediate duplicates if any
keep = [true; any(diff(pathXY,1,1)~=0,2)];
pathXY = pathXY(keep,:);
pathIdx = pathIdx(keep,:);
end

function ok = isValidCell(idx, validMap)
iy = idx(1);
ix = idx(2);
ok = iy >= 1 && iy <= size(validMap,1) && ix >= 1 && ix <= size(validMap,2) && validMap(iy,ix);
end

function d = turnRight(dir)
% E->S, N->E, W->N, S->W in right-hand logic
map = [4 1 2 3];
d = map(dir);
end

function d = turnLeft(dir)
map = [2 3 4 1];
d = map(dir);
end

function d = turnBack(dir)
map = [3 4 1 2];
d = map(dir);
end