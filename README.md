
# YoYo Labeling Assist

YoYo Labeling Assist is a python module providing required functionalities to view/edit/modify labeled data using photo editing softwares like GIMP. The library supports various file formats such as xcf (gimp) and ora (OpenRaster). 

## Features

* A customized version of OpenRaster file (*.orax).
* A File loader for multi-layer imagery files (the loader load the file to a in-memory structure containing the layers, original image, metadata, and other properties)
* Extension of the file loader for XCF files (*.xcf)
* Extension of the file loader for ORA files (*.ora)
* Extension of the file loader for ORAX files (*.orax)
* Extension of the file loader for RLE files.
* A File writer for multi-layer imagery files (updating the file structure based on the modifications made)
* The in-memory structure should have lazy loading of the layers.
* The in-memory structure should provide access to the metadata using [string index].
* A Sequential loader for processing files inside a folder.
* Convert from a multi-layer format to another multi-layer format.
* A tool for opening the ORAX files in gimp (including the gimp plugin, linux file handler, and script to install the file handler).
* A tool for converting all files in a folder from a file format to another file format.