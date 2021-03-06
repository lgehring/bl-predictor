import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bl-predictor",
    version="1.0",
    author="Lukas Gehring, Anabel Stammer, Alex Brylka and "
           "Fabricio Aguilera-Galviz",
    author_email="l.gehring@student.uni-tuebingen.de",
    description="A simple application for "
                "predicting game results for the German Bundesliga",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lgehring/bl-predictor",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'bl-predictor-gui = bl_predictor.__main__:main',
        ],
    },
    include_package_data=True,
    package_data={'': ['*.csv', '*.png']},
    install_requires=['pandas~=1.1.3',
                      'setuptools~=50.3.0',
                      'statsmodels~=0.12.1',
                      'numpy~=1.19.3',
                      'scipy~=1.5.2',
                      'matplotlib~=3.3.4',
                      'pytest~=6.1.2',
                      'requests~=2.24.0',
                      'pillow~=8.1.0',
                      'lxml~=4.6.1',
                      'tabulate~=0.8.7',
                      'scikit-learn~=0.24.1',
                      'ttkthemes~=3.2.2'],
)
