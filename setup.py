import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyscab",
    version="0.0.3",
    author="Simon Kojima",
    author_email="simon.kojima@outlook.com",
    description="python implementation of scab (stimulation controller for auditory brain-computer interface)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/simonkojima/scab-python",
    project_urls={
        "Bug Tracker": "https://github.com/simonkojima/scab-python/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [
        'pyaudio>=0.2.11',
        'numpy>=1.22.3',
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)