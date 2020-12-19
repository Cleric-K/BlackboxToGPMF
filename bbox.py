import csv
import numpy as np

def read(f, camera_angle):
    reader = csv.reader(f)
    ca_rad = camera_angle*np.pi/180
    sn = np.sin(ca_rad)
    cs = np.cos(ca_rad)
    rot=np.array([[cs, 0, -sn], [0, 1, 0], [sn, 0, cs]])
    time_index = None
    gyro_index = None
    time_at_arm = None
    t = []
    gyro = []
    for row in reader:
        if not gyro_index and len(row) > 2:
            # read the positions of the columns of interest
            time_index = row.index('time') # should be 1
            gyro_index = row.index('gyroADC[0]')
        elif gyro_index:
            tm = float(row[time_index]) / 1e6 # usec to sec
            if time_at_arm is None:
                time_at_arm = tm
            t.append(tm - time_at_arm)
            gyros = tuple(map(lambda x: float(x)*np.pi/180, row[gyro_index:gyro_index+3]))
            #gyros = tuple(map(lambda x: float(x), row[gyro_index:gyro_index+3]))
            gyros = np.matmul(rot, gyros)
            # degrees/sec to rad/sec
            gyro.append(gyros)
    #print(gyro[-1])
    gyro.insert(0, (0,0,0))
    gyro.append((0,0,0))
    t.insert(0, t[0]-.0001)
    t.append(t[-1]+.0001)
    return np.array(t), np.array(gyro)


def map_time(t, offset1, time1=None, offset2=None, time2=None):
    if time2 is None:
        a = 0
        b = offset1
    else:
        a = (offset2 - offset1)/(time2 - time1)
        b = offset1 - a*time1

    t = t + a*t + b

    return t

def map_gyro(t, gyro, num_chunks, chunk_time, samples_per_chunk):
    vt = np.linspace(0, num_chunks*chunk_time, int(num_chunks*samples_per_chunk))
    return np.transpose(np.array([ np.interp(vt, t, gyro_axis) for gyro_axis in np.transpose(gyro) ])), vt