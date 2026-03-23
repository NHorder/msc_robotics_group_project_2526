from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'wall_painting_robot'



# All the individual files which needs to be copied to the install directory
data_files=[
        ('share/ament_index/resource_index/packages',['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.*')),
        (os.path.join('lib', package_name, 'include'), glob('wall_painting_robot/include/*.*')),
    ]

# This custom funciton allows us to recursively copy all the files in the folders to the install directory
def package_files(data_files, directory_list):
    paths_dict = {}
    for directory in directory_list:
        for (path, directories, filenames) in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(path, filename)
                install_path = os.path.join('share', package_name, path)
                if install_path in paths_dict.keys():
                    paths_dict[install_path].append(file_path)
                else:
                    paths_dict[install_path] = [file_path]
    for key in paths_dict.keys():
        data_files.append((key, paths_dict[key]))
    return data_files


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    

    data_files = package_files(data_files, ['worlds/', 'meshes/', 'urdf/', 'config/']),

    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='lucas',
    maintainer_email='lucas.naury@sfr.fr',
    description='ROS2 Package for all code running on the Ground Control Station and Rover',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'webcam = wall_painting_robot.webcam:main',
            'qr_code_detection = wall_painting_robot.qr_code_detection:main',
            'feature_detection = wall_painting_robot.feature_detection:main',
            'robot_monitor = wall_painting_robot.robot_monitor:main',
            'joystick_commands = wall_painting_robot.joystick_commands:main',
            'picam = wall_painting_robot.picam:main',
            'odom_tf_publish = wall_painting_robot.odom_tf_publish:main',
            'odom_to_tf = wall_painting_robot.odom_to_tf:main'
        ],
    },
)
