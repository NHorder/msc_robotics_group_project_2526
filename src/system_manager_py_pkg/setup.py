from setuptools import find_packages, setup

package_name = 'system_manager_py_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/'+package_name+'/launch',['launch/system_launch.py'])
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='n_horder',
    maintainer_email='nathanhorder@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'health = system_manager_py_pkg.system_health_manager:main',
        ],
    },
)
