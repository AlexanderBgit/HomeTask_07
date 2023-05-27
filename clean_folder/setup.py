from setuptools import setup

setup(
    name='clean_folder',
    version='0.1',
    packages=['clean_folder'],
    entry_points={
        'console_scripts': [
            'clean-folder = clean_folder.clean:main'
        ]
    },
)