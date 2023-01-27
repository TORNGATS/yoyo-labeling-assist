import setuptools

long_description = ''
with open("README.md", "r") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="YoYo66 Multi-layer Imagary Data Library",
    version="1.0.0",
    author="Parham Nooralishahi",
    author_email="parham.nooralishahi@gmail.com",
    description="YoYo66 is a library providing a set of functionalities and tools for working with multi-layer images including loading storing, analyzing, and converting.",
    license = "BSD",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords = "gimp openraster data_labeling conversion segmentation",
    url = "https://github.com/parham/yoyo-labeling-assist", 
    packages=setuptools.find_packages(),
    package_data={'': ['*.json']},
    entry_points={
        "console_scripts": [
            "yoyo66_analyzer = yoyo66_analyzer.__main__:main",
            "yoyo66_converter = yoyo66_converter.__main__:main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Utilities",
        'Topic :: Software Development',
    ],
    install_requires=[
        'pyora',
        'progress',
        'tifffile',
        'imagecodecs',
        'gimpformats',
        'Pillow',
        'scikit-image',
    ],
    include_package_data=True,
    python_requires='>=3.8'
)
