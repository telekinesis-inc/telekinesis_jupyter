import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telekinesis_jupyter",
    version="0.0.1",
    author="Telekinesis, Inc.",
    author_email="support@telekinesis.cloud",
    description="Helper functions to interface with telekinesis_compute from jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/telekinesis-inc/telekinesis_jupyter",
    packages=setuptools.find_packages(),
    install_requires=["telekinesis"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
