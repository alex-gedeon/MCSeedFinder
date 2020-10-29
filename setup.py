"""
Seed finder.
"""

from setuptools import setup

setup(
    name='seed_finder',
    version='0.0.1',
    # packages=['DiscordTracker'],
    include_package_data=True,
    install_requires=[
        "click",
        "pillow",
        "pylint",
        "autopep8",
        "pycodestyle",
        "pydocstyle"
    ],
    # entry_points={
    #     'console_scripts': [
    #         'DiscordTracker = DiscordTracker.main.__main__:main'
    #     ]
    # },
)