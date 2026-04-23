#!/usr/bin/env python3
"""
cartesian_painter.py — Wall painter using joint-space control with base movement.

Flow:
  1. Paint 5 sweeps at current position
  2. Move base forward 95cm (or remaining distance if < 95cm)
  3. Repeat until wall is complete

HOME POSITION (bottom):
  j1=0, j2=-0.10, j3=-2.55, j4=1.0, j5=0
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float64
from geometry_msgs.msg import Pose, PolygonStamped, Twist
from visualization_msgs.msg import MarkerArray, Marker
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped

import math
import time
import threading

# ── Sweep parameters (WORKING VERSION) ───────────────────────────────────────
J3_BOTTOM = -2.55
J3_TOP = -0.70

# ══════════════════════════════════════════════════════════════════════════════
# j2 profile (from trajectory data - WORKING):
#   BOTTOM: 0.30 (INCREASED - start further from wall to avoid collision)
#   PEAK at 8%: 0.62
#   TOP: 0.15 (REDUCED - was swinging too far from wall)
# ══════════════════════════════════════════════════════════════════════════════
J2_AT_BOTTOM = 0.30
J2_PEAK = 0.62
J2_PEAK_T = 0.08
J2_AT_TOP = 0.15

# ══════════════════════════════════════════════════════════════════════════════
# j4 profile (linear - WORKING):
#   BOTTOM: 1.0
#   TOP: -0.9
# ══════════════════════════════════════════════════════════════════════════════
J4_AT_BOTTOM = 1.0
J4_AT_TOP = -0.9

# ══════════════════════════════════════════════════════════════════════════════
# j1/j5 for multi-sweep (5 sweeps total):
#   Sweep 1: j1 = +0.6, j5 = -0.6
#   Sweep 2: j1 = +0.3, j5 = -0.3
#   Sweep 3: j1 = 0.0,  j5 = 0.0
#   Sweep 4: j1 = -0.3, j5 = +0.3
#   Sweep 5: j1 = -0.6, j5 = +0.6
# ══════════════════════════════════════════════════════════════════════════════
J1_SWEEP1 = 0.6
J5_SWEEP1 = -0.6
J1_SWEEP2 = 0.3
J5_SWEEP2 = -0.3
J1_SWEEP3 = 0.0
J5_SWEEP3 = 0.0
J1_SWEEP4 = -0.3
J5_SWEEP4 = 0.3
J1_SWEEP5 = -0.6
J5_SWEEP5 = 0.6

# Timing
N_STEPS = 60
STEP_DELAY = 0.12
N_TRANSITION = 30
TRANSITION_PAUSE = 5.0

# ══════════════════════════════════════════════════════════════════════════════
# Base movement parameters
# ══════════════════════════════════════════════════════════════════════════════
BASE_MOVE_DISTANCE = 2.0     # meters per move
BASE_MOVE_SPEED = 0.5        # m/s
MIN_MOVE_DISTANCE = 0.10     # minimum distance worth moving
SAFETY_MARGIN = 0.30         # stop this far from wall end


class CartesianPainter(Node):
    def __init__(self):
        super().__init__('cartesian_painter')
        self.declare_parameter('wall_key', '')
        self._wall_key = self.get_parameter('wall_key').get_parameter_value().string_value

        self._pose = None
        self._odom_pose = None  # For movement tracking
        self._robot_yaw = 0.0
        self._corners = None
        self._pid = 0
        
        # Track position along wall
        self._start_pos = None
        self._total_moved = 0.0
        self._wall_length = 0.0
        
        # Track paint position offset (cumulative from each cycle)
        self._paint_offset = 0.0
        self._current_cycle = 1  # Track cycle for paint density

        # Subscriptions
        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', self._pose_cb, 10)
        self.create_subscription(Odometry, '/odom', self._odom_cb, 10)
        self.create_subscription(PolygonStamped, '/wall_corners', self._corners_cb, 10)
        self.create_subscription(String, '/wall_selector/status', self._status_cb, 10)

        # Publishers
        self._done_pub = self.create_publisher(String, '/wall_painter/status', 10)
        self._paint_pub = self.create_publisher(MarkerArray, '/paint_marks', 10)

        # Direct cmd_pos publishers for arm
        base = '/model/wall_painting_robot'
        self._jpub = [self.create_publisher(Float64, f'{base}/joint{i}/cmd_pos', 10)
                      for i in range(1, 6)]
        
        # cmd_vel publisher for base movement
        self._cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.get_logger().info('CartesianPainter ready. Home = bottom.')

        if self._wall_key:
            threading.Thread(target=self._start, args=(self._wall_key,), daemon=True).start()

    def _pose_cb(self, msg):
        self._pose = msg.pose.pose
        q = msg.pose.pose.orientation
        self._robot_yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y**2 + q.z**2))

    def _odom_cb(self, msg):
        # Always update odom_pose for movement tracking (updates at high frequency)
        self._odom_pose = msg.pose.pose
        # Only use odom for initial pose if AMCL hasn't provided one yet
        if not self._pose:
            self._pose = msg.pose.pose
            q = msg.pose.pose.orientation
            self._robot_yaw = math.atan2(2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y**2 + q.z**2))

    def _corners_cb(self, msg):
        if len(msg.polygon.points) >= 4:
            self._corners = [(p.x, p.y) for p in msg.polygon.points]

    def _status_cb(self, msg):
        if msg.data.startswith('arrived:') and not hasattr(self, '_started'):
            self._started = True
            key = msg.data.split(':')[1].strip()
            threading.Thread(target=self._start, args=(key,), daemon=True).start()

    def _start(self, key):
        self._wall_key = key
        self.get_logger().info(f'Starting painting on wall {key}')

        for _ in range(20):
            time.sleep(0.5)
            if self._pose:
                break

        time.sleep(1.0)
        
        # Signal that painting is starting — wall_selector will release arm control
        m = String()
        m.data = f'started:{self._wall_key}'
        self._done_pub.publish(m)
        self.get_logger().info('Signaled painting started — taking arm control')
        time.sleep(0.5)
        
        # Calculate wall length and save start position
        self._calculate_wall_length()
        self._start_pos = (self._pose.position.x, self._pose.position.y)
        self._total_moved = 0.0
        
        self.get_logger().info(f'Wall length: {self._wall_length:.2f}m')
        self.get_logger().info(f'Start position: ({self._start_pos[0]:.2f}, {self._start_pos[1]:.2f})')
        
        # Main painting loop
        self._paint_wall_loop()

    def _calculate_wall_length(self):
        """Calculate wall length from corners based on wall_key."""
        if not self._corners or len(self._corners) < 4:
            self.get_logger().warn('No wall corners available, using default length')
            self._wall_length = 7.6  # Default ~7.6m
            return
        
        # Get wall extent based on which wall we're painting
        xs = [c[0] for c in self._corners]
        ys = [c[1] for c in self._corners]
        
        wall_key = self._wall_key.upper() if self._wall_key else 'B'
        
        # Wall B and D run along Y axis, A and C run along X axis
        if wall_key in ['B', 'D']:
            self._wall_length = max(ys) - min(ys)
        else:
            self._wall_length = max(xs) - min(xs)
        
        self.get_logger().info(f'Calculated wall length: {self._wall_length:.2f}m')

    def _go_home(self):
        """Move manipulator to home pose (safe for base movement)."""
        self.get_logger().info('Moving to HOME pose for base movement...')
        # HOME: j1=0, j2=0.30, j3=-2.55, j4=1.0, j5=0
        for _ in range(20):  # Send multiple times to ensure it takes
            self._send_joints(j2=0.30, j3=J3_BOTTOM, j4=J4_AT_BOTTOM, j1=0.0, j5=0.0)
            time.sleep(0.1)
        time.sleep(2.0)  # Wait for arm to settle
        self.get_logger().info('HOME pose reached.')

    def _get_remaining_distance(self):
        """Calculate remaining distance to paint."""
        return max(0, self._wall_length - self._total_moved - SAFETY_MARGIN)

    def _move_base_forward(self, distance):
        """Move the base along the wall using closed-loop control.
        
        Uses odometry feedback to ensure accurate movement.
        Robot is facing along the wall, so linear.x moves it along the wall.
        """
        if distance < MIN_MOVE_DISTANCE:
            self.get_logger().info(f'Distance {distance:.2f}m too small, skipping move')
            return
        
        self.get_logger().info(f'Moving base {distance:.2f}m along wall...')
        
        # Use odom for movement tracking (more frequent updates)
        pose = self._odom_pose if self._odom_pose else self._pose
        start_x = pose.position.x
        start_y = pose.position.y
        
        # Control loop - drive until we've moved the target distance
        tolerance = 0.05  # 5cm tolerance
        # Much higher max iterations - robot moves slower than commanded
        max_iterations = int(distance / BASE_MOVE_SPEED * 200)  # 4x margin
        
        for i in range(max_iterations):
            # Use odom for position tracking during movement
            pose = self._odom_pose if self._odom_pose else self._pose
            
            # Calculate distance moved
            dx = pose.position.x - start_x
            dy = pose.position.y - start_y
            dist_moved = math.sqrt(dx*dx + dy*dy)
            
            if dist_moved >= distance - tolerance:
                self.get_logger().info(f'Target reached! Moved {dist_moved:.3f}m')
                break
            
            # Calculate speed - keep high speed until close to target
            remaining = distance - dist_moved
            if remaining > 0.2:
                speed = BASE_MOVE_SPEED  # Full speed until last 20cm
            else:
                speed = max(0.08, 0.4 * remaining)  # Slow down near target
            
            # Publish velocity
            twist = Twist()
            twist.linear.x = speed
            self._cmd_vel_pub.publish(twist)
            
            # Log progress periodically
            if i % 90 == 0:
                self.get_logger().info(f'  moved={dist_moved:.2f}m, remaining={remaining:.2f}m, speed={speed:.2f}')
            
            time.sleep(0.033)  # ~30 Hz
        
        # Stop
        twist = Twist()
        for _ in range(10):
            self._cmd_vel_pub.publish(twist)
            time.sleep(0.02)
        
        time.sleep(0.5)  # Let it settle
        
        # Calculate actual distance moved
        pose = self._odom_pose if self._odom_pose else self._pose
        dx = pose.position.x - start_x
        dy = pose.position.y - start_y
        actual_moved = math.sqrt(dx*dx + dy*dy)
        
        self._total_moved += actual_moved
        self.get_logger().info(f'Move complete. Actual: {actual_moved:.2f}m, Total: {self._total_moved:.2f}m')

    def _paint_wall_loop(self):
        """Main loop: paint 5 sweeps, move base, repeat until wall done."""
        cycle = 1
        
        # Sweep width = spacing from sweep 1 to next cycle's sweep 1
        # 5 sweeps with spacing 0.45m each = 5 * 0.45 = 2.25m to avoid overlap
        SWEEP_WIDTH = 2.25
        
        # 3-sweep partial cycle covers 0.9m + 0.45m gap = 1.35m
        THREE_SWEEP_WIDTH = 1.35
        
        while True:
            # Calculate remaining wall to paint
            remaining_paint = self._wall_length - self._paint_offset - SAFETY_MARGIN
            remaining_move = self._get_remaining_distance()
            
            self.get_logger().info('=' * 60)
            self.get_logger().info(f'PAINT CYCLE {cycle}')
            self.get_logger().info(f'Remaining wall to paint: {remaining_paint:.2f}m')
            self.get_logger().info(f'Remaining move distance: {remaining_move:.2f}m')
            self.get_logger().info(f'Paint offset: {self._paint_offset:.2f}m')
            self.get_logger().info('=' * 60)
            
            # Check if we should do a partial 3-sweep cycle
            # If remaining paint < full cycle (2.25m) but > 3-sweep coverage (1.35m)
            if remaining_paint < SWEEP_WIDTH and remaining_paint >= THREE_SWEEP_WIDTH:
                self.get_logger().info('LAST CYCLE - doing 3 sweeps only')
                
                # Move robot further forward to position for 3 sweeps
                extra_move = remaining_paint - THREE_SWEEP_WIDTH + 0.3  # Position well for final sweeps
                if extra_move > MIN_MOVE_DISTANCE and remaining_move > extra_move:
                    self.get_logger().info(f'Moving extra {extra_move:.2f}m for final position')
                    self._go_home()
                    self._move_base_forward(extra_move)
                    time.sleep(1.0)
                
                # Paint only 3 sweeps (sweeps 3, 4, 5)
                self._do_3_sweeps()
                
                # Increment paint offset for 3-sweep cycle
                self._paint_offset += THREE_SWEEP_WIDTH
                
                self.get_logger().info('Wall painting complete (3-sweep finish)!')
                break
            
            # Check if not enough space even for 3 sweeps
            if remaining_paint < THREE_SWEEP_WIDTH:
                self.get_logger().info('Not enough wall remaining for more painting')
                self.get_logger().info('Wall painting complete!')
                break
            
            # Full 5-sweep cycle
            self._do_5_sweeps()
            
            # Increment paint offset for next cycle
            self._paint_offset += SWEEP_WIDTH
            
            # Check remaining distance for movement
            remaining_move = self._get_remaining_distance()
            
            if remaining_move < MIN_MOVE_DISTANCE:
                self.get_logger().info('Wall painting complete!')
                break
            
            # Calculate move distance
            move_dist = min(BASE_MOVE_DISTANCE, remaining_move)
            
            self.get_logger().info(f'5 sweeps done. Preparing to move {move_dist:.2f}m...')
            
            # Go to home pose before moving (arm safe and tucked)
            self._go_home()
            
            # Move base along wall
            self._move_base_forward(move_dist)
            
            time.sleep(2.0)  # Pause after moving before next paint cycle
            cycle += 1
        
        # Return to home pose at end
        self._go_home()
        
        # Signal done
        m = String()
        m.data = f'done:{self._wall_key}'
        self._done_pub.publish(m)
        self.get_logger().info('WALL PAINTING COMPLETE!')

    def _send_joints(self, j2, j3, j4, j1=0.0, j5=0.0):
        """Send joint commands to Gazebo, with clamping to limits."""
        j1 = max(-0.70, min(0.70, j1))
        j2 = max(-0.56, min(1.27, j2))
        j3 = max(-3.05, min(-0.66, j3))
        j4 = max(-1.09, min(1.60, j4))
        j5 = max(-0.70, min(0.70, j5))
        
        values = [j1, j2, j3, j4, j5]
        for idx, val in enumerate(values):
            m = Float64()
            m.data = val
            self._jpub[idx].publish(m)

    def _compute_joints(self, t):
        """
        Compute j2 and j4 for position t in sweep [0, 1].
        """
        # j2: Piecewise quadratic
        if t <= J2_PEAK_T:
            t_norm = t / J2_PEAK_T
            j2 = J2_AT_BOTTOM + (J2_PEAK - J2_AT_BOTTOM) * (2*t_norm - t_norm*t_norm)
        else:
            t_norm = (t - J2_PEAK_T) / (1.0 - J2_PEAK_T)
            j2 = J2_PEAK + (J2_AT_TOP - J2_PEAK) * (t_norm * t_norm)
        
        # j4: Linear interpolation
        j4 = J4_AT_BOTTOM + t * (J4_AT_TOP - J4_AT_BOTTOM)
        
        return j2, j4

    def _do_5_sweeps(self):
        """Execute 5 painting sweeps with j1/j5 transitions."""
        
        # ======================================================================
        # PHASE 1: Move UP while transitioning j1/j5 (NO PAINTING)
        # ======================================================================
        self.get_logger().info(f'Phase 1 (UP - no paint): j1: 0 -> {J1_SWEEP1}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_BOTTOM + t_ease * (J3_TOP - J3_BOTTOM)
            j2, j4 = self._compute_joints(t_ease)
            j1 = t_ease * J1_SWEEP1
            j5 = t_ease * J5_SWEEP1
            
            # Pull back slightly during Phase 1 to avoid wall collision
            j2 += 0.08
            
            self._send_joints(j2, j3, j4, j1=j1, j5=j5)
            time.sleep(STEP_DELAY)
        
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 1: Paint DOWN with j1=0.6, j5=-0.6
        # ======================================================================
        self.get_logger().info(f'SWEEP 1 (DOWN): j1={J1_SWEEP1}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_TOP + t_ease * (J3_BOTTOM - J3_TOP)
            t_pos = 1.0 - t_ease
            j2, j4 = self._compute_joints(t_pos)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP1, j5=J5_SWEEP1)
            
            self._paint_mark(self._estimate_z(1.0 - t), J1_SWEEP1)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: 0.6 -> 0.3
        j2, j4 = self._compute_joints(0.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP1 + t * (J1_SWEEP2 - J1_SWEEP1)
            j5 = J5_SWEEP1 + t * (J5_SWEEP2 - J5_SWEEP1)
            self._send_joints(j2, J3_BOTTOM, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 2: Paint UP with j1=0.3, j5=-0.3
        # ======================================================================
        self.get_logger().info(f'SWEEP 2 (UP): j1={J1_SWEEP2}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_BOTTOM + t_ease * (J3_TOP - J3_BOTTOM)
            j2, j4 = self._compute_joints(t_ease)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP2, j5=J5_SWEEP2)
            
            self._paint_mark(self._estimate_z(t), J1_SWEEP2)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: 0.3 -> 0.0
        j2, j4 = self._compute_joints(1.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP2 + t * (J1_SWEEP3 - J1_SWEEP2)
            j5 = J5_SWEEP2 + t * (J5_SWEEP3 - J5_SWEEP2)
            self._send_joints(j2, J3_TOP, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 3: Paint DOWN with j1=0.0, j5=0.0
        # ======================================================================
        self.get_logger().info(f'SWEEP 3 (DOWN): j1={J1_SWEEP3}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_TOP + t_ease * (J3_BOTTOM - J3_TOP)
            t_pos = 1.0 - t_ease
            j2, j4 = self._compute_joints(t_pos)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP3, j5=J5_SWEEP3)
            
            self._paint_mark(self._estimate_z(1.0 - t), J1_SWEEP3)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: 0.0 -> -0.3
        j2, j4 = self._compute_joints(0.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP3 + t * (J1_SWEEP4 - J1_SWEEP3)
            j5 = J5_SWEEP3 + t * (J5_SWEEP4 - J5_SWEEP3)
            self._send_joints(j2, J3_BOTTOM, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 4: Paint UP with j1=-0.3, j5=0.3
        # ======================================================================
        self.get_logger().info(f'SWEEP 4 (UP): j1={J1_SWEEP4}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_BOTTOM + t_ease * (J3_TOP - J3_BOTTOM)
            j2, j4 = self._compute_joints(t_ease)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP4, j5=J5_SWEEP4)
            
            self._paint_mark(self._estimate_z(t), J1_SWEEP4)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: -0.3 -> -0.6
        j2, j4 = self._compute_joints(1.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP4 + t * (J1_SWEEP5 - J1_SWEEP4)
            j5 = J5_SWEEP4 + t * (J5_SWEEP5 - J5_SWEEP4)
            self._send_joints(j2, J3_TOP, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 5: Paint DOWN with j1=-0.6, j5=0.6
        # ======================================================================
        self.get_logger().info(f'SWEEP 5 (DOWN): j1={J1_SWEEP5}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_TOP + t_ease * (J3_BOTTOM - J3_TOP)
            t_pos = 1.0 - t_ease
            j2, j4 = self._compute_joints(t_pos)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP5, j5=J5_SWEEP5)
            
            self._paint_mark(self._estimate_z(1.0 - t), J1_SWEEP5)
            
            time.sleep(STEP_DELAY)
        
        self.get_logger().info('5 sweeps complete!')

    def _do_3_sweeps(self):
        """Execute only sweeps 3, 4, 5 for the last partial cycle."""
        
        # ======================================================================
        # PHASE 1: Move UP to sweep 3 position (j1=0) - NO PAINTING
        # ======================================================================
        self.get_logger().info(f'Phase 1 (UP - no paint): j1: 0 -> {J1_SWEEP3}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_BOTTOM + t_ease * (J3_TOP - J3_BOTTOM)
            j2, j4 = self._compute_joints(t_ease)
            # Stay at j1=0, j5=0 (sweep 3 position)
            j1 = J1_SWEEP3
            j5 = J5_SWEEP3
            
            # Pull back slightly during Phase 1 to avoid wall collision
            j2 += 0.08
            
            self._send_joints(j2, j3, j4, j1=j1, j5=j5)
            time.sleep(STEP_DELAY)
        
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 3: Paint DOWN with j1=0.0, j5=0.0
        # ======================================================================
        self.get_logger().info(f'SWEEP 3 (DOWN): j1={J1_SWEEP3}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_TOP + t_ease * (J3_BOTTOM - J3_TOP)
            t_pos = 1.0 - t_ease
            j2, j4 = self._compute_joints(t_pos)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP3, j5=J5_SWEEP3)
            
            # Paint marks for last cycle
            self._paint_mark(self._estimate_z(1.0 - t), J1_SWEEP3)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: 0.0 -> -0.3
        j2, j4 = self._compute_joints(0.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP3 + t * (J1_SWEEP4 - J1_SWEEP3)
            j5 = J5_SWEEP3 + t * (J5_SWEEP4 - J5_SWEEP3)
            self._send_joints(j2, J3_BOTTOM, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 4: Paint UP with j1=-0.3, j5=0.3
        # ======================================================================
        self.get_logger().info(f'SWEEP 4 (UP): j1={J1_SWEEP4}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_BOTTOM + t_ease * (J3_TOP - J3_BOTTOM)
            j2, j4 = self._compute_joints(t_ease)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP4, j5=J5_SWEEP4)
            
            # Paint marks for last cycle
            self._paint_mark(self._estimate_z(t), J1_SWEEP4)
            
            time.sleep(STEP_DELAY)
        
        # TRANSITION: j1: -0.3 -> -0.6
        j2, j4 = self._compute_joints(1.0)
        for step in range(N_TRANSITION + 1):
            t = step / N_TRANSITION
            j1 = J1_SWEEP4 + t * (J1_SWEEP5 - J1_SWEEP4)
            j5 = J5_SWEEP4 + t * (J5_SWEEP5 - J5_SWEEP4)
            self._send_joints(j2, J3_TOP, j4, j1=j1, j5=j5)
            time.sleep(0.1)
        time.sleep(TRANSITION_PAUSE)
        
        # ======================================================================
        # SWEEP 5: Paint DOWN with j1=-0.6, j5=0.6
        # ======================================================================
        self.get_logger().info(f'SWEEP 5 (DOWN): j1={J1_SWEEP5}')
        
        for step in range(N_STEPS + 1):
            t = step / N_STEPS
            t_ease = t * t * (3.0 - 2.0 * t)
            
            j3 = J3_TOP + t_ease * (J3_BOTTOM - J3_TOP)
            t_pos = 1.0 - t_ease
            j2, j4 = self._compute_joints(t_pos)
            
            self._send_joints(j2, j3, j4, j1=J1_SWEEP5, j5=J5_SWEEP5)
            
            # Paint marks for last cycle
            self._paint_mark(self._estimate_z(1.0 - t), J1_SWEEP5)
            
            time.sleep(STEP_DELAY)
        
        self.get_logger().info('3 sweeps complete (final cycle)!')

    def _estimate_z(self, t):
        # Wall height is ~2.7m, paint from 0.5m to 2.4m
        z_bottom = 0.5
        z_top = 2.4
        return z_bottom + t * (z_top - z_bottom)

    def _paint_mark(self, z_world, j1_angle=0.0):
        """Place a paint mark on the wall at the correct position."""
        if not self._pose:
            return

        px = self._pose.position.x
        py = self._pose.position.y

        STANDOFF = 1.95
        # Use linear j1 angle directly (not tan) for even spacing between sweeps
        LATERAL_MULT = 1.5
        lateral_offset = LATERAL_MULT * j1_angle  # Linear, not tan()
        
        # Get wall boundaries from corners
        if self._corners and len(self._corners) >= 4:
            xs = [c[0] for c in self._corners]
            ys = [c[1] for c in self._corners]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
        else:
            # Fallback based on detected room: BL(-3.49,-5.08) TR(4.26,5.97)
            min_x, max_x = -3.49, 4.26
            min_y, max_y = -5.08, 5.97
        
        wall_key = self._wall_key.upper() if self._wall_key else 'B'
        
        # Small offset so marks appear ON wall surface
        WALL_INSET = 0.05
        
        # Max j1 angle used in sweep 1
        MAX_J1 = 0.6
        
        # Small inset from corner so first sweep is visible
        CORNER_INSET = 0.2
        
        # Calculate position along wall using cumulative _paint_offset
        # Each cycle adds to _paint_offset so paint continues along wall
        # Sweep 1 (j1=+0.6) should be at the corner, sweep 5 (j1=-0.6) furthest from corner
        if wall_key == 'A':
            # South wall at min_y, start from east corner (higher X), move west
            mark_x = max_x + lateral_offset - MAX_J1 * LATERAL_MULT - self._paint_offset - CORNER_INSET
            mark_y = min_y + WALL_INSET
        elif wall_key == 'B':
            # East wall at max_x, start from north corner (higher Y), move south
            mark_x = max_x - WALL_INSET
            mark_y = max_y + lateral_offset - MAX_J1 * LATERAL_MULT - self._paint_offset - CORNER_INSET
        elif wall_key == 'C':
            # North wall at max_y, start from west corner (lower X), move east
            mark_x = min_x - lateral_offset + MAX_J1 * LATERAL_MULT + self._paint_offset + CORNER_INSET
            mark_y = max_y - WALL_INSET
        elif wall_key == 'D':
            # West wall at min_x, start from south corner (lower Y), move north
            mark_x = min_x + WALL_INSET
            mark_y = min_y - lateral_offset + MAX_J1 * LATERAL_MULT + self._paint_offset + CORNER_INSET
        else:
            mark_x = max_x - WALL_INSET
            mark_y = py

        mk = Marker()
        mk.header.frame_id = 'map'
        mk.header.stamp = self.get_clock().now().to_msg()
        mk.ns = 'paint'
        mk.id = self._pid
        self._pid += 1
        mk.type = Marker.CUBE
        mk.action = Marker.ADD
        mk.lifetime.sec = 0
        mk.pose.orientation.w = 1.0
        mk.color.r = 1.0
        mk.color.g = 1.0
        mk.color.b = 0.0
        mk.color.a = 1.0
        mk.pose.position.x = mark_x
        mk.pose.position.y = mark_y
        mk.pose.position.z = z_world
        # Wider marks for better coverage
        mk.scale.x = 0.06
        mk.scale.y = 0.45  # Wider for overlap between sweeps
        mk.scale.z = 0.04
        
        ma = MarkerArray()
        ma.markers.append(mk)
        self._paint_pub.publish(ma)


def main(args=None):
    rclpy.init(args=args)
    node = CartesianPainter()
    rclpy.spin(node)
    node.destroy_node()
    try:
        rclpy.shutdown()
    except Exception:
        pass


if __name__ == '__main__':
    main()
