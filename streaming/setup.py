import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deduce-stream", # Replace with your own username
    version="0.1.0",
    author="Abdelrahman Elbashandy, Devarshi Ghoshal, Lavanya Ramakrishnan",
    author_email="AAelbashandy@lbl.gov, DGhoshal@lbl.gov, lramakrishnan@lbl.gov",
    description="A framework for processing scientific data streams at scale",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deduce-dev/dac-man/tree/streaming",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=['redis==3.5.3'],
    python_requires='>=3.6',
)
