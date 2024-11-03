from setuptools import setup, find_packages

setup(
    name='FreeDictation',
    version='0.0.1',
    description='A cross-platform speech-to-text application using Whisper',
    author='Mathieu',
    author_email='research@mgravey.com',
    packages=find_packages(),
    install_requires=[
        'sounddevice',
        'numpy',
        'openai-whisper',
        'pynput',
        'soundfile',
        # Mac-specific dependencies
        'rumps; platform_system == "Darwin"',
        'pyobjc-framework-Quartz; platform_system == "Darwin"',
        'pyobjc-framework-AppKit; platform_system == "Darwin"',
        # Windows and Linux dependencies
        'pystray; platform_system == "Windows" or platform_system == "Linux"',
        'pillow; platform_system == "Windows" or platform_system == "Linux"',
        'keyboard; platform_system == "Windows" or platform_system == "Linux"',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)
