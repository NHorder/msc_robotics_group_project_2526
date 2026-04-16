# visnat_task_coordinator.py
# author : Viksit Sachdeva
# Date:  16 Apr
# Version : 1.0
"""
VISNAT task coordinator : VISNAT_integration_code.py
-----------------------
Process flow :
1. UI/user selects wall (action selection by operator)
2. Start Paint button (in ui) triggers this coordinator
3. Coordinator runs mobile-base demo first
4. Coordinator then runs manipulator
5. Respective Statues printed 
"""
#%%
from enum import Enum, auto
import traceback
from mobile_base.AllWalls import run_mobile_demo
from mobile_base.WallsADE import run_mobile_demo_ADE
from manipulator.visnat_arm import run_manipulator_demo

#%%

class VISNATState(Enum):
    IDLE = auto()
    MOBILE_BASE_PLANNING = auto()
    MANIPULATOR_PAINTING = auto()
    COMPLETE = auto()
    ERROR = auto()


class VISNATTaskCoordinator:
    def __init__(self):
        self.state = VISNATState.IDLE
        self.selected_walls = []
        #----------------------------
        # Mutual exclusion flags
        #----------------------------
        self.mobile_base_busy = False
        self.manipulator_busy = False

    def set_state(self, state: VISNATState):
        self.state = state
        print(f"[VISNAT INTEGRATOR] State -> {self.state.name}")
    
    # Mutual Exclusion methods start -------------------------------------------------------
    
    def start_mobile_base(self):
        """
        THIS METHOD ENSURES : Mobile base to start only if manipulator is not active.
        """
        if self.manipulator_busy:
            raise RuntimeError("Cannot start mobile base while manipulator is active.")
    
        self.mobile_base_busy = True
        self.manipulator_busy = False
        self.set_state(VISNATState.MOBILE_BASE_PLANNING)
        print("[VISNAT INTEGRATOR] Rule : manipulator stopped, mobile base allowed to run.")

    def stop_mobile_base(self):
        self.mobile_base_busy = False
        print("[VISNAT INTEGRATOR] Mobile base stage finished.")

    def start_manipulator(self):
        """
        THIS CODE ENSURES manipulator to start only if mobile base is not active.
        """
        if self.mobile_base_busy:
            raise RuntimeError("Cannot start manipulator while mobile base is active.")

        self.manipulator_busy = True
        self.mobile_base_busy = False
        self.set_state(VISNATState.MANIPULATOR_PAINTING)
        print("[VISNAT INTEGRATOR] Rule enforced: mobile base stopped, manipulator allowed to run.")

    def stop_manipulator(self):
        self.manipulator_busy = False
        print("[VISNAT INTEGRATOR] Manipulator stage finished")
        
    #--mutual exclusion methods end--------------------------------------------------
    
    def run_task(self, selected_walls):
        try:
            self.selected_walls = [str(w).upper().strip() for w in selected_walls]
            print("\n" + "=" * 70)
            print(f"Starting VISNAT OPERATION for Walls {self.selected_walls}")
            print("=" * 70)

            # ----------------------------------------------------------
            # Mobile base planning
            # ----------------------------------------------------------
            self.start_mobile_base()
            
            selected_set = set(self.selected_walls)
            
            if selected_set == {"A", "B", "C", "D", "E"}:
                print(f"Using AllWalls.py for walls {self.selected_walls}")
                mobile_result = run_mobile_demo(selected_walls=self.selected_walls)
            
            elif selected_set == {"A", "D", "E"}:
                print(f"Using WallsADE.py for walls {self.selected_walls}")
                mobile_result = run_mobile_demo_ADE(selected_walls=self.selected_walls)
            
            else:
                raise ValueError(
                    f"Unsupported wall combination {self.selected_walls}. "
                    "Supported demo sets are ['A','B','C','D','E'] and ['A','D','E']."
                )
            
            self.stop_mobile_base()
            
            print("Mobile-base stage complete.")
            if mobile_result is not None:
                print(f"Mobile-base result: {mobile_result}")
                
            # ----------------------------------------------------------
            # Manipulator painting
            # ----------------------------------------------------------

            for wall in self.selected_walls:
                self.start_manipulator()

                print(f"Start Manipulator painting for Wall {wall}...")
                arm_result = run_manipulator_demo(wall)

                self.stop_manipulator()

                print(f"Manipulator stage complete for Wall {wall}.")
                if arm_result is not None:
                  print(f"Manipulator result keys for Wall {wall}: {list(arm_result.keys())}")

            # ----------------------------------------------------------
            # Both Complete
            # ----------------------------------------------------------
            self.set_state(VISNATState.COMPLETE)
            print(f"Task complete for Walls {self.selected_walls}.")
            return True

        except Exception as exc:
            self.mobile_base_busy = False
            self.manipulator_busy = False
            self.set_state(VISNATState.ERROR)
            print(f"ERROR while running task for walls {self.selected_walls}: {exc}")
            traceback.print_exc()
            return False


def on_start_paint(selected_walls): # this function will be called from UI
    coordinator = VISNATTaskCoordinator()
    return coordinator.run_task(selected_walls)


if __name__ == "__main__":
    # Test run without UI
    success = on_start_paint(["A", "B", "C", "D", "E"])
    success = on_start_paint(["A", "D", "E"])
    print(f"\nCoordinator finished with success = {success}")
# %%
