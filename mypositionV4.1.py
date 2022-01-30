global tgt_id, gps_file, target_file, gps_output

# PARAMETERS TO EDIT BY USER
##########################################################
# Target set to display distance and time. List of targets is on target_file
tgt_id = 11
# Working file paths
gps_file = '/home/user/Downloads/gps_stream'
target_file = '/home/user/Downloads/targets_gps'
gps_output = '/home/user/Downloads/gps_output'
##########################################################

# $GPDTM,W84,,00.0000,N,00.0000,E,,W84*41
# $GPAPB,A,A,99.99,L,N,V,V,281.7,T,1001,255.9,T,,T*3B
# $GPGGA,173312,2009.2659,N,03321.3953,W,1,9,1.6,18,M,,M,,*5E
# $GPVTG,87.8,T,100.2,M,12.6,N,23.3,K*7D
# $GPZDA,173312,24,11,2021,00,00*4A

# Open file and read
import os
import numpy as np


def read_total_lines(path):
    fin = open(path, 'r')
    n = 0
    if fin:
        for line in fin:
            n = n + 1
    fin.close()

    return n

# Parse data and get LAT LON V HDG
def read_gps(path, num):
    fin = open(path, 'r')
    i = 0
    if fin:
        while i < num:
            line = fin.readline()
            if not line:
                break
            if '$GPGGA' in line:
                position_string = line
            if '$GPVTG' in line:
                speed_string = line
    data = [position_string,speed_string]

    return data

def num2digit(num):
    if num == 0:
        n = '00'
    elif num < 10:
        n = '0' + str(num)
    else:
        n = str(num)

    return n

def time_string(hh,mm,ss):
    stime = num2digit(hh) + ':' + num2digit(mm) + ':' + num2digit(ss) + ' UTC '
    return stime

def get_time(rtime):
    hh = int(int(rtime) / 10000)
    mm = int( ( int(rtime) % 10000 ) / 100 )
    ss = int( int(rtime) % 100 )
    stime = time_string(hh,mm,ss)
    
    return stime

def deg(x):
    lx = len(str(int(float(x))))
    xdeg = str(int(float(x)))
    if ( lx == 3):
        return xdeg[0:1]
    elif ( lx == 4):
        return xdeg[0:2]
    elif ( lx == 5):
        return xdeg[0:3]

def minu(x):
    lx = len(str(int(float(x))))
    xmin = str(float(x))
    if (lx == 3):
        return xmin[1:]
    elif (lx == 4):
        return xmin[2:]
    elif (lx == 5):
        return xmin[3:]   

def string_lat(lat,ns):
    lat_deg = deg(lat)
    lat_min = minu(lat)
    mylat = lat_deg + ' ' + lat_min + "'" + ns

    return mylat

def string_lon(lon,ew):
    lon_deg = deg(lon)
    lon_min = minu(lon)
    mylon = lon_deg + ' ' + lon_min + "'" + ew

    return mylon

def lat_deg2dec(lat_deg,lat_min, ns):
    a = 1
    if ns == 'N': a = 1
    if ns == "S": a = -1
    return (int(lat_deg) + float(lat_min)/60)*a

def lon_deg2dec( lon_deg,lon_min, ew):
    a = 1
    if ew == 'E': a = 1
    if ew == "W": a = -1
    return (int(lon_deg) + float(lon_min)/60)*a

def parse_position(line):
    linelst = line.split(',')
    raw_time = linelst[1] # time UTC 143509 14:35:09
    raw_lat = linelst[2] # lat ddmm.mmmm
    raw_ns = linelst[3] # N S 
    raw_lon = linelst[4] # lon ddmm.mmmm
    raw_ew = linelst[5] # E W
    stime = get_time(raw_time)
    slat = string_lat(raw_lat, raw_ns)
    slon = string_lon(raw_lon, raw_ew)
    dlat = lat_deg2dec(deg(raw_lat), minu(raw_lat), raw_ns)
    dlon = lon_deg2dec(deg(raw_lon), minu(raw_lon), raw_ew)

    mypos = [stime, slat, slon, dlat, dlon ]

    return mypos

def parse_speed(line):
    linelst = line.split(',')
    raw_heading = linelst[1] # True track made good
    raw_speedn = linelst[5] # speed over ground knots
    raw_speedk = linelst[7] # speed over ground km/h
    myspeed = [raw_heading, raw_speedk, raw_speedn]

    return myspeed

# 1 Test_CTD_0_(000) 24.613175 -68.14362
def get_target_position(path,n, tgt_id):
    ftgt = open(path, 'r')
    lat = ''
    lon = ''
    name = ''
    if ftgt:
        i = 0
        while i < n:
            line = ftgt.readline()
            line = line.replace("\n","")
            linelst = line.split(" ")
            if linelst[0] == str(tgt_id):
                lat = linelst[2]
                lon = linelst[3]
                name = linelst[1]
            i = i+1
    ftgt.close()
    target = [name, lat, lon]

    return target

# Spherical Law of Cosines - distance between 2 locations
def dist2target(lat1, lon1, lat2, lon2):
    p1 = np.deg2rad(lat1) # lat1
    p2 = np.deg2rad(lat2) # lat2
    dg = np.deg2rad( lon2 - lon1 ) # delta long
    R = 6371E3 # Earth radius in m
    d = np.arccos(np.sin(p1)*np.sin(p2)+np.cos(p1)*np.cos(p2)*np.cos(dg))*R
    return float(d) # in m

def get_target_time(speed,dist):
    time = (dist / 1000.0) / float(speed) # hs
    if time < 1.0:
        stime = "{:.1f}".format(time*60.0) + ' minutes'
    elif time < 24.0:
        stime = "{:.1f}".format(time) + ' hs'
    else:
        stime = "{:.1f}".format(time/24.0) + ' days'
    return stime

def get_target_distance(dist):
    if dist < 1000.0:
        sdist = "{:.1f}".format(dist) + ' m'
    else:
        sdist = "{:.1f}".format(dist/1000.0) + ' km'

    return sdist 

def update_gps_conky(path,text):
    fout = open(path, 'w+')
    fout.write(text)
    fout.close()


def main():
    gps_file = '/home/user/Downloads/gps_stream'
    target_file = '/home/user/Downloads/targets_gps'
    gps_output = '/home/user/Downloads/gps_output'
    
    command = 'timeout 2 nc -ulp 10005 > ' + gps_file
    os.system(command)

    num1 = read_total_lines(target_file)    

    num = read_total_lines(gps_file)
    data_lines = read_gps(gps_file, num) # GPGGA, GPVTG
    mypos = parse_position(data_lines[0]) # time_string, string_lat, string_lon, dec_lat, dec_lon
    myspeed = parse_speed(data_lines[1]) # True heading, speed km/h, speed knots
   
    if not tgt_id == '':   
        target = get_target_position(target_file,num1, tgt_id) # name, dec_lat, dec_lon
        dist = dist2target(float(mypos[3]),float(mypos[4]), float(target[1]), float(target[2])) # dist in m
        target_time = get_target_time(myspeed[1],dist) # hs or days to target
        target_distance = get_target_distance(dist) # m or km

    line1 = mypos[0] + '  LAT:' + mypos[1] + ' LON:' + mypos[2]
    line2 = 'SOG:' + myspeed[2] + 'kn - ' + myspeed[1] + 'km/h ' + '  HDG:' + myspeed[0]
   
    if not tgt_id == '':
        line3 =  target[0] + '-> ' + target_distance + '  ' + target_time

    if not tgt_id == '':
        line3 = target_distance + ' ' + target_time + ' to ' + target[0]
    else:
        line3 = ''
    
    text =  line1 + "\n" + line2 + "\n" + line3 + '\nChange target on mypositionV4.py'
    text = text + '\nList of targets on ' + target_file
    update_gps_conky(gps_output, text)

# Bottom code
if __name__ == "__main__":
    main() 

