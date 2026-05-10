from glob import glob
from os.path import join

from setuptools import setup

package_name = 'rh1'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (join('share', package_name), ['package.xml']),
        (join('share', package_name, 'config'), glob('config/*')),
        (join('share', package_name, 'launch'), glob('launch/*.py')),
        (join('share', package_name, 'urdf'), glob('urdf/*')),
        (join('share', package_name, 'rviz'), glob('rviz/*')),
        (join('share', package_name, 'meshes', 'collision'), glob('meshes/collision/*')),
        (join('share', package_name, 'meshes', 'visual'), glob('meshes/visual/*')),
        (join('share', package_name, 'params'), glob('params/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Yufei Zhang',
    maintainer_email='yz4917@columbia.edu',
    description='Wearable 3-RRR spherical parallel ankle rehabilitation robot: '
                'URDF, parallel inverse kinematics, and ROS 2 control demos.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ankle_rehab_joint_state_player = rh1.ankle_rehab_joint_state_player:main',
            'parallel_ik_pose_demo = rh1.parallel_ik_pose_demo:main',
        ],
    },
)
