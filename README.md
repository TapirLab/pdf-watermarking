# A PDF Watermarking Script

![Tapir Lab.](http://tapirlab.com/wp-content/uploads/2020/10/tapir_logo.png)

## Description

This repository enables users to add watermark and encrypt PDFs. Currently, it is used to create watermarked and encrypted versions of Tapir Lab.'s lecture notes. This process consists of four steps: (i) blurring pages to prevent OCR, (ii) adding watermark, (iii) converting the content of pages to images, and (iv) encrypting to set permissions. Each of these steps has its own function, and the pipeline can be modified as it is needed. However, since lecture notes are mostly written on A4 papers, whatever your input is, output is scaled down to A4 paper dimensions. Also, user need to provide orientation information manually due to the inconsistent configurations of documents.

## Prerequisites

* Python3
* Other necessary packages can be installed via `pip install -r requirements.txt`

**Note:**  *requirements.txt* includes opencv-python package. This package only includes fundamental functionalities of OpenCV library. Therefore, in case of need OpenCV should be installed separately.

## Folder Structure

```
pdf-watermarking
|── processed
|   |── Original files are moved into this folder after the watermarkingç
|── sample_input
|   |── PDFs to be processed.
|── sample_output
|   |── Processed PDFs will be saved into this folder.
|── tmp
|   |── A temporary folder to save midproducts during the process.
|── watermarks
|   |── This folder includes `portrait` and `landscape` A4 watermarks
|── add_watermark.py
|── LICENSE
|── pdf_operations.py
|── README.md
|── requirements.txt
```

## Example

`add_watermark.py` can be used as a working example. If you want to perform watermarking and encryption as it is explained in the [Description](#description), you need to place all your A4 PDF(s) to the sample_input folder and set `orientation` parameter in the script. `add_watermark.py` will save watermarked and encrypted (with owner password `your_pass`) versions of PDF(s) to the `sample_output` folder and move original files to the `processed_folder`.

## License

The software is licensed under the MIT License.
