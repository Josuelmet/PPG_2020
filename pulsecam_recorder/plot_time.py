import numpy as np 
from matplotlib import pyplot as plt 


# load timestamps 
computer_time_file = '/home/ashoklab/pulseCam_recorder/dump/d5/CameraTimeLog.txt' 
camera_time_file = '/home/ashoklab/pulseCam_recorder/dump/d5/CameraCyclesLog.txt'
#pulse_ox_time_file = 'webcam.txt'

computer_time = np.loadtxt(computer_time_file)
camera_time = np.loadtxt(camera_time_file)
# pulse_time = np.loadtxt(pulse_ox_time_file,delimiter =',')


camera_dt = np.diff(camera_time)
computer_dt = np.diff(computer_time)
# pulse_dt = np.diff(pulse_time)


camera_dt[camera_dt<0]=0.033 
#pulse_dt[pulse_dt<0.005]=0.016
#pulse_dt[pulse_dt>0.025]=0.016

computer_dt_stat = computer_dt[computer_dt<0.04] 

# new_pulse_time = pulse_time[::2]
# statistics 

mean_computer_dt = np.mean(computer_dt_stat)
std_computer_dt = np.std(computer_dt_stat)

print "Mean computer time = ", mean_computer_dt
print "Std computer time = ", std_computer_dt 


# mean_pulse_dt = np.mean(pulse_dt)
# std_pulse_dt = np.std(pulse_dt)

# print "Mean pulse time = ", mean_pulse_dt
# print "Std pulse time = ", std_pulse_dt 

#time= range(0,len(camera_dt)+1)
#t = [i * 10 for i in time]
#print(len(t))
plt.plot(camera_dt)
#plt.plot(computer_dt)
plt.xlabel('Frame count')
plt.ylabel('Seconds')
plt.show()
# plt.savefig('time_diff.png')


# plt.plot(pulse_dt)
# #plt.plot(computer_time)
# plt.xlabel('Frame counts')
# plt.ylabel('Sec')
# plt.show()
# plt.savefig('time_compare.png')