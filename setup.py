from setuptools import find_packages, setup

package_name = 'turtlebot_core'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='jesus.loport',
    maintainer_email='jesus.loport@outlook.com',
    description='TurtleBot Core Package',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'toggle_led = turtlebot_core.toggle_led:main',
            'control_led = turtlebot_core.control_led:main',
        ],
    },
)
