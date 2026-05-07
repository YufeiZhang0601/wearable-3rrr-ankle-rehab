from glob import glob
from os.path import join

from setuptools import setup

package_name = 'rh1'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        (join('share', package_name), ['package.xml']),
        (join('share', package_name, 'launch'), glob('launch/*.py')),
        (join('share', package_name, 'urdf'), glob('urdf/*')),
        (join('share', package_name, 'rviz'), glob('rviz/*')),
        (join('share', package_name, 'meshes', 'collision'), glob('meshes/collision/*')),
        (join('share', package_name, 'meshes', 'visual'), glob('meshes/visual/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros-industrial',
    maintainer_email='olmer@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'ankle_rehab_joint_state_player = rh1.ankle_rehab_joint_state_player:main',
        ],
    },
)
