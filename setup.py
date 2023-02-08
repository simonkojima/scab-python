import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

def parse_requirements_file(fname):
    requirements = list()
    with open(fname, 'r') as fid:
        for line in fid:
            req = line.strip()
            if req.startswith('#'):
                continue
            # strip end-of-line comments
            req = req.split('#', maxsplit=1)[0].strip()
            requirements.append(req)
    return requirements

#install_requires = parse_requirements_file("requirements.txt")

install_requires=[
    'pyaudio>=0.2.11',
    'numpy>=1.15.4',
]

setuptools.setup(
    name="pyscab",
    version="1.0.1",
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
    install_requires = install_requires,
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)