clc; clear; close all;

%% ----------------------------------------------------------
%  1.  ROOM DATABASE
%      Each entry: rooms{i} = struct with
%        .name      – room label
%        .centre    – [x, y] in metres (from the OBJ coordinate frame)
%        .doors     – cell array of {neighbour_name, wall_number}
%                     listed clockwise from Wall 1
% ----------------------------------------------------------
rooms = struct();

% Dining Room  (start)
rooms.DiningRoom.name   = 'Dining Room';
rooms.DiningRoom.centre = [0.285, -0.175];   % right-centre of plan
rooms.DiningRoom.doors  = {{'Hall', 1}};      % single door → Hall, Wall 1

% Hall  (hub)
rooms.Hall.name   = 'Hall';
rooms.Hall.centre = [0.02, -0.01];
rooms.Hall.doors  = { ...
    {'DiningRoom',  1}, ...   % Wall 1 → Dining Room  (robot enters from here)
    {'Lounge',      2}, ...   % Wall 2 → Lounge
    {'Study',       3}, ...   % Wall 3 → Study
    {'Kitchen',     4}, ...   % Wall 4 → Kitchen/Breakfast
    {'UtilityRoom', 4}, ...   % Wall 4 → Utility Room (via Kitchen corridor)
    {'Store',       2}, ...   % Wall 2 → Store (small alcove)
    {'Garage',      1}  ...   % Wall 1 → Garage / exit
    };

% Lounge
rooms.Lounge.name   = 'Lounge';
rooms.Lounge.centre = [0.30, 0.22];
rooms.Lounge.doors  = {{'Hall', 1}};

% Study
rooms.Study.name   = 'Study';
rooms.Study.centre = [0.01, 0.31];
rooms.Study.doors  = {{'Hall', 1}};

% Kitchen / Breakfast Room
rooms.Kitchen.name   = 'Kitchen/Breakfast Room';
rooms.Kitchen.centre = [-0.23, 0.25];
rooms.Kitchen.doors  = { ...
    {'Hall',        1}, ...
    {'UtilityRoom', 2}  ...
    };

% Utility Room
rooms.UtilityRoom.name   = 'Utility Room';
rooms.UtilityRoom.centre = [-0.26, -0.01];
rooms.UtilityRoom.doors  = {{'Kitchen', 1}};

% Store
rooms.Store.name   = 'Store';
rooms.Store.centre = [0.13, -0.01];
rooms.Store.doors  = {{'Hall', 1}};

% Double Garage  (EXIT)
rooms.Garage.name   = 'Double Garage';
rooms.Garage.centre = [-0.20, -0.37];
rooms.Garage.doors  = { ...
    {'Hall',   1}, ...   % internal door → Hall
    {'EXIT',   2}  ...   % Wall 2 → outside (garage door = EXIT)
    };

%% ----------------------------------------------------------
%  2.  RIGHT-HAND RULE NAVIGATION  (graph / room-level)
%
%  State = (currentRoom, facingNeighbour)
%  The robot always faces the direction it came from (Wall 1
%  in the new room).  It then applies RHR to choose the next
%  door.
%
%  Door list in each room is stored in CLOCKWISE order from
%  Wall 1, so:
%    right  = Wall 1 index + 1  (mod n_doors)
%    straight = same index (current facing)
%    left   = Wall 1 index - 1  (mod n_doors)
%    back   = Wall 1 index  (the door it entered through)
% ----------------------------------------------------------

startRoom  = 'DiningRoom';
goalMarker = 'EXIT';
maxSteps   = 200;

path       = {startRoom};        % visited room names
directions = {};                 % turn descriptions

currentRoom  = startRoom;
cameFrom     = '';               % no previous room at start

fprintf('\n=== RIGHT-HAND RULE MAZE SOLVER ===\n');
fprintf('Start : %s\n', rooms.(startRoom).name);
fprintf('Goal  : Exit through Garage door\n\n');

solved = false;

for step = 1:maxSteps
    rDoors = rooms.(currentRoom).doors;   % doors of current room
    nDoors = numel(rDoors);

    % --- Find index of the door we came through (Wall 1 = back) ---
    backIdx = 0;
    for d = 1:nDoors
        if strcmp(rDoors{d}{1}, cameFrom)
            backIdx = d;
            break;
        end
    end
    % If no back door found (start room), treat Wall 1 as "back"
    if backIdx == 0
        backIdx = 1;
    end

    % --- RHR priority: right → straight → left → back ---
    % "right" in clockwise list = next index CW
    % Clockwise order: 1→2→3→...→n→1
    % right  = backIdx - 1  (one step CCW from back = right when facing back)
    % Actually for RHR: facing INTO room from back wall,
    %   right  = clockwise  neighbor in door list
    %   left   = counter-clockwise neighbor
    % We define: facing direction = opposite of backIdx
    %   right  = (backIdx)     mod nDoors + 1   → one CW step from entry
    %   straight = (backIdx+1) mod nDoors + 1
    %   left   = (backIdx+2)   mod nDoors + 1
    %   back   = backIdx

    tryOrder = zeros(1, nDoors);
    for k = 0:nDoors-1
        tryOrder(k+1) = mod(backIdx - 1 + k, nDoors) + 1;
        % starts CW from the door immediately right of entry
    end
    % Remove the back door (we only go back if truly stuck)
    tryOrderNB = tryOrder(tryOrder ~= backIdx);
    tryFull    = [tryOrderNB, backIdx];   % back is last resort

    turnLabels = {'RIGHT', 'STRAIGHT', 'LEFT', 'BACK'};

    moved = false;
    for t = 1:numel(tryFull)
        chosenIdx  = tryFull(t);
        chosenDest = rDoors{chosenIdx}{1};
        chosenWall = rDoors{chosenIdx}{2};

        % Determine turn label
        if     t == 1, turnStr = 'TURN RIGHT';
        elseif t == 2, turnStr = 'GO STRAIGHT';
        elseif t == 3, turnStr = 'TURN LEFT';
        else,          turnStr = 'TURN BACK (dead-end)';
        end

        fprintf('Step %3d | Room: %-25s | %s → Wall %d → %s\n', ...
            step, rooms.(currentRoom).name, turnStr, chosenWall, chosenDest);

        directions{end+1} = turnStr; %#ok<SAGROW>

        if strcmp(chosenDest, 'EXIT')
            path{end+1} = 'EXIT'; %#ok<SAGROW>
            solved = true;
            fprintf('\n*** GOAL REACHED: Robot exited through Garage door! ***\n');
            break;
        end

        cameFrom    = currentRoom;
        currentRoom = chosenDest;
        path{end+1} = currentRoom; %#ok<SAGROW>
        moved = true;
        break;
    end

    if solved, break; end
    if ~moved
        fprintf('  [STUCK – no valid move from %s]\n', currentRoom);
        break;
    end
end

if ~solved
    fprintf('\n[WARNING] Goal not reached within %d steps.\n', maxSteps);
end

%% ----------------------------------------------------------
%  3.  PRINT FULL PATH SUMMARY
% ----------------------------------------------------------
fprintf('\n--- PATH SUMMARY (%d rooms visited) ---\n', numel(path));
for i = 1:numel(path)
    if strcmp(path{i},'EXIT')
        fprintf('  %2d.  EXIT (outside)\n', i);
    else
        fprintf('  %2d.  %s\n', i, rooms.(path{i}).name);
    end
end

%% ----------------------------------------------------------
%  4.  VISUALISE IN THE OBJ ENVIRONMENT
%      (loads the same OBJ used in the provided scaffold)
% ----------------------------------------------------------
objFile = 'ground_floor_env.obj';

if exist(objFile, 'file')
    [V, F] = readObjTri(objFile);
    V = V / 1000;
    V = V - mean(V, 1);
else
    warning('OBJ file "%s" not found – showing schematic only.', objFile);
    V = []; F = [];
end

fig = figure('Color','w','Name','RHR Maze Solver – Ground Floor');

%% -- Subplot 1: 3D view --
ax3d = subplot(1,2,1);
if ~isempty(V)
    patch('Vertices',V,'Faces',F, ...
        'FaceColor',[0 0 0],'EdgeColor',[0.35 0.35 0.35],'FaceAlpha',1);
end
axis equal; grid on; view(35,25);
xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)');
title('Environment – 3D View');

%% -- Subplot 2: Top view with robot path --
ax2d = subplot(1,2,2);
if ~isempty(V)
    patch('Vertices',V,'Faces',F, ...
        'FaceColor',[0 0 0],'EdgeColor',[0.35 0.35 0.35],'FaceAlpha',1);
end
axis equal; grid on; view(2); hold on;
xlabel('X (m)'); ylabel('Y (m)');
title('Top View – Robot Path (RHR)');

% Room labels
roomNames = fieldnames(rooms);
for i = 1:numel(roomNames)
    rn = roomNames{i};
    c  = rooms.(rn).centre;
    text(c(1), c(2), rooms.(rn).name, ...
        'FontSize',7,'Color',[1 0.6 0], ...
        'HorizontalAlignment','center','FontWeight','bold');
end

% Collect path coordinates
pathXY = zeros(numel(path), 2);
for i = 1:numel(path)
    if strcmp(path{i},'EXIT')
        % Place EXIT slightly outside garage door
        pathXY(i,:) = rooms.Garage.centre + [0, -0.12];
    else
        pathXY(i,:) = rooms.(path{i}).centre;
    end
end

% Draw path
plot(pathXY(:,1), pathXY(:,2), '-', ...
    'Color',[0.2 0.8 1], 'LineWidth', 2.5);

% Waypoint markers
scatter(pathXY(:,1), pathXY(:,2), 60, ...
    linspace(0,1,size(pathXY,1))', ...
    'filled','MarkerEdgeColor','w','LineWidth',0.5);
colormap(ax2d, cool);

% Start marker
plot(pathXY(1,1), pathXY(1,2), 'g^', ...
    'MarkerSize',12,'MarkerFaceColor','g','DisplayName','Start');

% End marker
plot(pathXY(end,1), pathXY(end,2), 'r*', ...
    'MarkerSize',14,'LineWidth',2,'DisplayName','Exit');

% Step numbers along path
for i = 1:size(pathXY,1)
    text(pathXY(i,1)+0.01, pathXY(i,2)+0.015, num2str(i), ...
        'FontSize',7,'Color','w','FontWeight','bold');
end

legend({'Path','Waypoints','Start','Exit'}, ...
    'Location','southeast','FontSize',8,'TextColor','k');

sgtitle(sprintf('Right-Hand Rule – %d steps to exit', numel(path)-1), ...
    'FontWeight','bold');

%% ----------------------------------------------------------
%  5.  ANIMATION  – robot dot moving along path
% ----------------------------------------------------------
figure('Color','w','Name','RHR Animation');
if ~isempty(V)
    patch('Vertices',V,'Faces',F, ...
        'FaceColor',[0.08 0.08 0.08],'EdgeColor',[0.4 0.4 0.4],'FaceAlpha',1);
end
hold on; axis equal; view(2); grid on;
xlabel('X (m)'); ylabel('Y (m)');
title('Robot Animation – Right-Hand Rule');

% Draw full path as faded trail
plot(pathXY(:,1), pathXY(:,2), '--', ...
    'Color',[0.3 0.3 0.3],'LineWidth',1.2);

% Room labels
for i = 1:numel(roomNames)
    rn = roomNames{i};
    c  = rooms.(rn).centre;
    text(c(1), c(2), rooms.(rn).name, ...
        'FontSize',7,'Color',[1 0.8 0.3], ...
        'HorizontalAlignment','center','FontWeight','bold');
end

hBot   = plot(pathXY(1,1), pathXY(1,2), 'o', ...
    'MarkerSize',14,'MarkerFaceColor',[0 0.8 1],'MarkerEdgeColor','w','LineWidth',1.5);
hTrail = plot(pathXY(1,1), pathXY(1,2), '-', ...
    'Color',[0 0.8 1],'LineWidth',2);
hInfo  = text(-0.45, 0.50, '', 'Color','w','FontSize',9,'FontWeight','bold');

for i = 1:size(pathXY,1)
    % Update trail
    set(hTrail, 'XData', pathXY(1:i,1), 'YData', pathXY(1:i,2));
    % Update robot position
    set(hBot,   'XData', pathXY(i,1),   'YData', pathXY(i,2));

    % Info text
    if strcmp(path{i},'EXIT')
        infoStr = sprintf('Step %d/%d\nLOCATION: EXIT\n*** GOAL! ***', ...
            i, numel(path));
        set(hBot,'MarkerFaceColor','g');
    else
        if i <= numel(directions)
            dirStr = directions{i};
        else
            dirStr = 'START';
        end
        infoStr = sprintf('Step %d/%d\nRoom: %s\nAction: %s', ...
            i, numel(path), rooms.(path{i}).name, dirStr);
    end
    set(hInfo,'String',infoStr);

    drawnow;
    pause(0.7);
end

fprintf('\n=== SIMULATION COMPLETE ===\n');

%% =========================================================
%  LOCAL FUNCTION  –  OBJ loader (same as provided scaffold)
% =========================================================
function [V, F] = readObjTri(filename)
    fid = fopen(filename, 'r');
    if fid == -1
        error('Could not open OBJ file: %s', filename);
    end
    V = []; F = [];
    while true
        tline = fgetl(fid);
        if ~ischar(tline), break; end
        tline = strtrim(tline);
        if startsWith(tline, 'v ')
            vals = sscanf(tline(3:end), '%f');
            if numel(vals) >= 3
                V(end+1, :) = vals(1:3)'; %#ok<AGROW>
            end
        elseif startsWith(tline, 'f ')
            parts = strsplit(tline);
            idx   = zeros(1, numel(parts)-1);
            for i = 2:numel(parts)
                token      = parts{i};
                tokenParts = strsplit(token, '/');
                idx(i-1)   = str2double(tokenParts{1});
            end
            idx = idx(~isnan(idx));
            idx = idx(idx > 0);
            if numel(idx) == 3
                F(end+1, :) = idx; %#ok<AGROW>
            elseif numel(idx) > 3
                for k = 2:numel(idx)-1
                    F(end+1, :) = [idx(1) idx(k) idx(k+1)]; %#ok<AGROW>
                end
            end
        end
    end
    fclose(fid);
    F = unique(F, 'rows');
end