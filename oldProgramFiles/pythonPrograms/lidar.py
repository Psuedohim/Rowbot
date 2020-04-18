from FastestRplidar.source.fastestrplidar import RPlidar
# uses the default port ttyUSB0
lidar = RPlidar()

health = lidar.get_health()
print(health)

for i, scan in enumerate(lidar.iter_scans()):
    print('%d: Got %d measurments' % (i, len(scan)))
    if i > 10:
        break

# stops lidar and disconnect the driver
lidar.stopmotor()
