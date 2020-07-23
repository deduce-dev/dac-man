import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="deduce-stream-elbashandy", # Replace with your own username
    version="0.0.1",
    author="Abdelrahman Elbashandy, Devarshi Ghoshal",
    author_email="AAelbashandy@lbl.gov, DGhoshal@lbl.gov ",
    description="A Streaming analysis frameword",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/deduce-dev/dac-man/tree/streaming",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
