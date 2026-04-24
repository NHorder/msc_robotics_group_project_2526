%% =========================================================
%  MAZE-SOLVING ROBOT – Right-Hand Rule (RRRR Algorithm)
% =========================================================
clc; clear; close all;

%% ---------------- ROOM DEFINITIONS ----------------

DR.name='Dining Room'; DR.centre=[0.38,-0.175]; DR.W=3.8; DR.H=3.0;
DR.walls(1)=struct('label','North','door_to','Hall');
DR.walls(2)=struct('label','East','door_to','');
DR.walls(3)=struct('label','South','door_to','');
DR.walls(4)=struct('label','West','door_to','');
DR.dx=DR.W/2*0.8; DR.dy=DR.H/2*0.8;

HL.name='Hall'; HL.centre=[0.02,-0.01]; HL.W=4.2; HL.H=3.7;
HL.walls(1)=struct('label','South','door_to','Dining Room');
HL.walls(2)=struct('label','West','door_to','Kitchen');
HL.walls(3)=struct('label','North','door_to','Study');
HL.walls(4)=struct('label','East','door_to','Lounge');
HL.dx=HL.W/2*0.8; HL.dy=HL.H/2*0.8;

LG.name='Lounge'; LG.centre=[0.30,0.22]; LG.W=5.2; LG.H=3.8;
LG.walls(1)=struct('label','West','door_to','Hall');
LG.walls(2)=struct('label','North','door_to','');
LG.walls(3)=struct('label','East','door_to','');
LG.walls(4)=struct('label','South','door_to','');
LG.dx=LG.W/2*0.8; LG.dy=LG.H/2*0.8;

ST.name='Study'; ST.centre=[0.01,0.31]; ST.W=2.7; ST.H=2.4;
ST.walls(1)=struct('label','South','door_to','Hall');
ST.walls(2)=struct('label','West','door_to','');
ST.walls(3)=struct('label','North','door_to','');
ST.walls(4)=struct('label','East','door_to','');
ST.dx=ST.W/2*0.8; ST.dy=ST.H/2*0.8;

KT.name='Kitchen'; KT.centre=[-0.23,0.25]; KT.W=4.7; KT.H=3.1;
KT.walls(1)=struct('label','East','door_to','Hall');
KT.walls(2)=struct('label','South','door_to','Utility Room');
KT.walls(3)=struct('label','West','door_to','');
KT.walls(4)=struct('label','North','door_to','');
KT.dx=KT.W/2*0.8; KT.dy=KT.H/2*0.8;

UT.name='Utility Room'; UT.centre=[-0.26,-0.01]; UT.W=2.5; UT.H=1.6;
UT.walls(1)=struct('label','North','door_to','Kitchen');
UT.walls(2)=struct('label','East','door_to','');
UT.walls(3)=struct('label','South','door_to','');
UT.walls(4)=struct('label','West','door_to','');
UT.dx=UT.W/2*0.8; UT.dy=UT.H/2*0.8;

SR.name='Store'; SR.centre=[0.13,-0.01]; SR.W=1.2; SR.H=1.2;
SR.walls(1)=struct('label','West','door_to','Hall');
SR.walls(2)=struct('label','North','door_to','');
SR.walls(3)=struct('label','East','door_to','');
SR.walls(4)=struct('label','South','door_to','');
SR.dx=SR.W/2*0.8; SR.dy=SR.H/2*0.8;

GR.name='Garage'; GR.centre=[-0.20,-0.37]; GR.W=4.9; GR.H=3.7;
GR.walls(1)=struct('label','East','door_to','Hall');
GR.walls(2)=struct('label','South','door_to','EXIT');
GR.walls(3)=struct('label','West','door_to','');
GR.walls(4)=struct('label','North','door_to','');
GR.dx=GR.W/2*0.8; GR.dy=GR.H/2*0.8;

roomMap=containers.Map({'Dining Room','Hall','Lounge','Study','Kitchen','Utility Room','Store','Garage'},...
{DR,HL,LG,ST,KT,UT,SR,GR});

%% ---------------- NAVIGATION ----------------
RHR_ORDER=[2 3 4 1];
currentRoom='Dining Room'; cameFrom='';
allXY=[]; allLbl={};

for i=1:40
    room=roomMap(currentRoom);

    allXY(end+1,:)=room.centre;
    allLbl{end+1}=[room.name ' centre'];

    for w=1:4
        wp=wallWaypoint(room.centre,room.dx,room.dy,room.walls(w).label);
        allXY(end+1,:)=wp;
    end

    chosen=0;
    for t=1:4
        wi=RHR_ORDER(t);
        dest=room.walls(wi).door_to;
        if ~isempty(dest)
            if strcmp(dest,cameFrom)&&t<4, continue; end
            chosen=wi; next=dest; break;
        end
    end

    doorWP=wallWaypoint(room.centre,room.dx,room.dy,room.walls(chosen).label);
    allXY(end+1,:)=doorWP;

    if strcmp(next,'EXIT')
        allXY(end+1,:)=doorWP+[0 -0.15];
        break;
    end

    cameFrom=currentRoom;
    currentRoom=next;
end

%% ---------------- PLOT ----------------
figure;
plot(allXY(:,1),allXY(:,2),'-o','LineWidth',2);
axis equal; grid on;
title('Robot Path');

%% ---------------- FUNCTIONS ----------------
function wp=wallWaypoint(c,dx,dy,label)
switch label
    case 'North', wp=c+[0 dy];
    case 'South', wp=c+[0 -dy];
    case 'East',  wp=c+[dx 0];
    case 'West',  wp=c+[-dx 0];
    otherwise,    wp=c;
end
end