import glob
import os
import sys
import random
import time
import numpy as np
import cv2 

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla 

IM_WIDTH = 640
IM_HEIGHT = 480
actor_list = []

def image(image):
    matrix_representation_data = np.array(image.raw_data)
    reshapeofimage = matrix_representation_data.reshape((IM_HEIGHT,IM_WIDTH,4))
    livefeedfromcam  = reshapeofimage[:,:,:3]
    cv2.imshow("",livefeedfromcam)
    cv2.waitKey(1)
    return

def camera(get_blueprint_of_world):
    camera_sensor = get_blueprint_of_world.find('sensor.camera.rgb') 
    camera_sensor.set_attribute('image_size_x', f'{IM_WIDTH}')
    camera_sensor.set_attribute('image_size_y', f'{IM_HEIGHT}')
    camera_sensor.set_attribute('fov', '110')
    return camera_sensor

try:
    client = carla.Client('localhost', 2000)
    client.set_timeout(3.0)
    world = client.get_world()
    get_blueprint_of_world = world.get_blueprint_library()
    car_model = get_blueprint_of_world.filter('model3')[0]
    spawn_point = random.choice(world.get_map().get_spawn_points())
    dropped_vehicle = world.spawn_actor(car_model, spawn_point)

    dropped_vehicle.set_autopilot(True)  # if you just wanted some NPCs to drive.
    simulator_camera_location_rotation = carla.Transform(spawn_point.location, spawn_point.rotation)
    simulator_camera_location_rotation.location += spawn_point.get_forward_vector() * 30
    simulator_camera_location_rotation.rotation.yaw += 180
    simulator_camera_view = world.get_spectator()
    simulator_camera_view.set_transform(simulator_camera_location_rotation)
    
    camera_sensor = camera(get_blueprint_of_world)
    sensor_camera_spawn_point = carla.Transform(carla.Location(x=2.5, z=0.7))
    sensor = world.spawn_actor(camera_sensor, spawn_point, attach_to=dropped_vehicle)
    actor_list.append(sensor)
    sensor.listen(lambda camera_data:image(camera_data))
    speed  = lambda speed:carla.VehicleControl(throttle = speed)
    dropped_vehicle.apply_control(speed(0.5))
    time.sleep(11)
    steering = lambda steer:carla.VehicleControl(steer = steer)
    dropped_vehicle.apply_control(steering(0.5))
    time.sleep(5)
    actor_list.append(dropped_vehicle)

    ## camera sensor
    
finally:
    print('destroying actors')
    for actor in actor_list:
        actor.destroy()
    print('done.')