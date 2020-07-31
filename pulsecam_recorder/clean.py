import os
import shutil
# Delete stray files resulting from this experiment
shutil.rmtree('cam_flea3_0', ignore_errors=True)
os.remove('CameraCyclesLog0.txt') if os.path.exists('CameraCyclesLog0.txt') else None
os.remove('CameraBufferSize0.txt') if os.path.exists('CameraBufferSize0.txt') else None
os.remove('CameraFrame0.txt') if os.path.exists('CameraFrame0.txt') else None
os.remove('CameraTimeLog0.txt') if os.path.exists('CameraTimeLog0.txt') else None
os.remove('Config0.txt') if os.path.exists('Config0.txt') else None
os.remove('Setup0.log') if os.path.exists('Setup0.log') else None
os.remove('FlyCap0.log') if os.path.exists('FlyCap0.log') else None

shutil.rmtree('cam_flea3_1', ignore_errors=True)
os.remove('CameraCyclesLog1.txt') if os.path.exists('CameraCyclesLog1.txt') else None
os.remove('CameraBufferSize1.txt') if os.path.exists('CameraBufferSize1.txt') else None
os.remove('CameraFrame1.txt') if os.path.exists('CameraFrame1.txt') else None
os.remove('CameraTimeLog1.txt') if os.path.exists('CameraTimeLog1.txt') else None
os.remove('Config1.txt') if os.path.exists('Config1.txt') else None
os.remove('Setup1.log') if os.path.exists('Setup1.log') else None
os.remove('FlyCap1.log') if os.path.exists('FlyCap1.log') else None