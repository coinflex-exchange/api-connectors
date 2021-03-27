import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coinflex-ws",
    version="0.1.0",
    author="Philipp Chvetsov",
    author_email="philipp.c@coinflex.com",
    license="MIT",
    description="Simple WebSocket adapter for CoinFLEX's WebSocket API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["coinflex_ws"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=["coinflex_ws"],
    install_requires=["websocket-client==0.53.0"]
)
