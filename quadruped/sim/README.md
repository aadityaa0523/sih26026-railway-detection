# Quadruped walking simulation (MuJoCo, exact exported CAD)

`mujoco_walk.py` loads the STLs in `../cad/` (chassis parts as-is; the LF leg mirrored for
RF/LH/RH as `assemble_robot.py` does), joint axes/masses from `leg_kinematics.json`, hip
points and total mass from `params.py`, and drives 12 torque-limited (DS3225 stall) position
servos through a numerical-IK trot. Output: `out/quadruped_walk.mp4`.

    pip install mujoco trimesh imageio imageio-ffmpeg pillow numpy
    MUJOCO_GL=glfw xvfb-run -a python3 mujoco_walk.py     # on Windows: just `python mujoco_walk.py`

Result (14 s run): stays upright (max roll 4.3 deg, pitch 5.5 deg), body height 151-158 mm,
about 7 cm/s forward, ~7 deg yaw drift (open-loop gait, no heading control).

## What the CAD shows (found while building this -- not simulation artefacts)
- `leg_kinematics.json` puts the joint axes at hip-frame x=0, but the leg meshes span x=0..40
  and the bearing pockets / knee horn are cut at x=20 (BAR_X/2). Hip-pitch horn bolt circle
  is at x=0. The two ends of one joint are therefore not collinear. The sim uses the JSON axes.
- The JSON claims foot offset y=55 mm (HIP_TO_FOOT_Y_TARGET) but the shin mesh sits at
  y=100..122 mm, so the real foot is ~111 mm from the ab/ad axis (HIP_TO_FOOT_Y_MAX is 75).
  The sim uses the real mesh foot tip, so the robot stands wide-track.
- `leg_module_report.txt` still ends `RESULT: FAIL` (worst Z 165.7 mm vs LEG_MAX_Z 60 mm).
- The LiDAR envelope in `payload.stl` floats above the top deck (no mast/pedestal modelled).
