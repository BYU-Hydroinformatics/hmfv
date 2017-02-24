import os
import sys
from setuptools import setup, find_packages
from tethys_apps.app_installation import custom_develop_command, custom_install_command

### Apps Definition ###
app_package = 'hmfv'
release_package = 'tethysapp-' + app_package
app_class = 'hmfv.app:HimalayaFloodMapVisualizer'
app_package_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tethysapp', app_package)

### Python Dependencies ###
dependencies = []

setup(
    name=release_package,
    version='1.0.0',
    tags='Flood',
    description='Flood map viewer that works in conjunction with Streamflow Prediction Tool API.',
    long_description='',
    keywords='',
    author='Sarva Pulla, Christian Kesler',
    author_email='pulla@byu.edu',
    url='tethys.byu.edu',
    license='BSD2',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['tethysapp', 'tethysapp.' + app_package],
    include_package_data=True,
    zip_safe=False,
    install_requires=dependencies,
    cmdclass={
        'install': custom_install_command(app_package, app_package_dir, dependencies),
        'develop': custom_develop_command(app_package, app_package_dir, dependencies)
    }
)
