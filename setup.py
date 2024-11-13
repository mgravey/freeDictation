from setuptools import setup, find_packages


from setuptools import setup, find_packages

setup(
    name='freeDictation',
    version='1.0.0',
    description='A cross-platform speech-to-text application using Whisper',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/freeDictation',  # Update with your repository
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
        'pyobjc-core; platform_system == "Darwin"',
        # Windows and Linux dependencies
        'pystray; platform_system == "Windows" or platform_system == "Linux"',
        'pillow; platform_system == "Windows" or platform_system == "Linux"',
        'keyboard; platform_system == "Windows" or platform_system == "Linux"',
    ],
    entry_points={
        'console_scripts': [
            'freeDictation = freeDictation.__main__:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        # Additional classifiers can be added here
    ],
    python_requires='>=3.9',  # Specify your Python version compatibility
    include_package_data=True,  # Include additional files specified in MANIFEST.in
)