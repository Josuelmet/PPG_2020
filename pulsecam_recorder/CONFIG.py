


# define number of cameras (1 or 2)
NUM_CAM = 1
# Define number of pulse oximeter (1 or 2)
NUM_OX = 2

# Define the profile
# 0 - Surgery Room
# 1 - Sensitivity experiment
# 2 - Custom

PROFILE = 0

# Is webcam present?
WEBCAM = 1


if PROFILE==0:
    NUM_OX=1
    NUM_CAM=1


