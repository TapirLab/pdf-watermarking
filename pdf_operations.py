# -*- coding: utf-8 -*-
"""
This program includes functions to add watermark to A4 PDFs. Also, miscellaneous
functions are provided to harden OCR (Optical Character Recognition) process and
make encryption possible.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% A PDF Watermarking Script
%% -------------------
%% $Author: Halil Said Cankurtaran$,
%% $Date: January 10th, 2020$,
%% $Revision: 1.0$
%% Tapir Lab.
%% Copyright: Tapir Lab.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

import os
import glob
from datetime import datetime

import cv2
import numpy as np
import pikepdf

from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from PyPDF2 import PdfFileWriter, PdfFileReader, PdfFileMerger


def set_page(name, orientation):
    """Create an empty A4 PDF page with `name` based on the `orientation`"""

    if orientation == 'landscape':
        empty_page = canvas.Canvas(name, pagesize=landscape(A4))
    else:
        empty_page = canvas.Canvas(name, pagesize=A4)

    return empty_page


def draw_image(canvas_, image, orientation):
    """Draw given image by scaling to the size of canvas the in the correct orientation

    `canvas_` is the page created with `set_page` function. In case of need,
    reportlab.pdfgen.canvas can be used to create a custom canvas. However,
    since this function draws images after scaling to A4 paper dimensions, the
    drawn image may not be properly scaled to the size of a custom canvas.
    """

    if orientation == 'landscape':
        canvas_.drawImage(image, 0, 0, width=A4[1], height=A4[0])
    else:
        canvas_.drawImage(image, 0, 0, width=A4[0], height=A4[1])


def blur_image(page, kernel=(5,5), sigma=1):
    """Adds Gaussian noise w. `sigma` and applies Gaussian blur w. `kernel`

    If `sigma=0` then it is calculated based on kernel size with following:
        sigma = 0.3*((ksize-1)*0.5 - 1) ~~ 1.1 if ksize = 5

    Args:
        page (PIL.PngImagePlugin.PngImageFile):
            Page of PDF that is converted to 'PNG' with
            `pdf2image.convert_from_path` function.
        kernel (tuple, optional): Gaussian blur kernel size. Defaults to (5,5).
        sigma (float, optional): Gaussian blur sigma value. Defaults to 1.

    Returns:
        np.ndarray, dtype=np.uint8: Blurred image
    """
    img = np.asarray(page)  # Convert pages object to numpy array
    gauss = np.random.normal(0, sigma, img.size)  # Create gaussian noise
    gauss = gauss.reshape(img.shape[0], img.shape[1], img.shape[2]).astype('uint8')
    img_gauss = cv2.add(img,gauss)  # Add gaussian noise
    blurred_image = cv2.GaussianBlur(img_gauss, kernel, sigma)  # Blur image

    return blurred_image


def pdf_to_image(path_to_pdf, output_folder, dpi=100, blur=True, kernel=(5,5), sigma=1):
    """Converts pages to image, blurs if True and saves to output_folder.

    Args:
        path_to_pdf (str): path to input PDF
        output_folder (str): path of the folder that images will be saved
        dpi (int, optional): Dots Per Inch, conversion parameter. Default = 100.
        blur (bool, optional): Whether blur is needed or not. Defaults to True.
        kernel (tuple, optional): Gaussian blur kernel size. Defaults to (5,5).
        sigma (float, optional): Gaussian blur sigma value. Defaults to 1.
    """
    pages = convert_from_path(path_to_pdf, dpi, fmt='PNG')  # Convert to PNGs
    for (page, j) in zip(pages, range(len(pages))): # Iterate over pages
        png_output = os.path.join('.', os.path.join(output_folder, f'_{j}.png'))
        # Required to harden optical character recognition (OCR) process
        if blur:
            blurred_image = blur_image(page, kernel, sigma)  # Apply blurring
            cv2.imwrite(png_output, blurred_image)  # Save blurred image
        else:
            page.save(png_output, 'PNG')  # Save non-blurry image


def image_to_pdf(images_folder, output_folder, orientation, remove_artifacts=False):
    """Writes PNG images in the input_folder onto A4 pages by scaling the size.

    If images are not proportional to the dimensions of A4, the written image may be
    distorted. If you want to remove images after converting them to PDF,
    set `remove_artifacts` to `True`.

    Args:
        images_folder (str): Path to the folder that includes images.
        output_folder (str): Path to the folder that PDFs will be saved
        orientation (str): Orientation of page 'landscape' or 'portrait'.
        remoremove_artifacts (bool, optional):
            Whether to remove the input images or not. Defaults to False.
    """
    # Read all "*.png" images in the images_folder
    path_to_images = sorted(glob.glob(os.path.join(images_folder,'*.png')))
    # Iterate over images and save them seperate A4 PDFs
    for (image,j) in zip(path_to_images, range(len(path_to_images))):
        canvas_ = set_page(os.path.join(output_folder,f'tmp_{j}.pdf'), orientation)
        draw_image(canvas_, image, orientation)  # Draw image to page
        canvas_.save()  # save PDF
        if remove_artifacts:
            os.remove(image)


def merge_pdfs(input_folder, path_to_output_pdf, remove_artifacts=False):
    """Merges given input PDFs and writes merged version to `output_pdf`

    If `remove_artifacts` is `True`, then function removes input PDFs.

    Args:
        input_folder (str): PDFs that will be merged should be in this folder
        output_pdf (str): the path to output PDF, it both includes path and name
        remove_artifacts (bool, optional):
            Whether to remove the input file(s) or not. Defaults to False.
    """
    pdf_merger = PdfFileMerger()
    input_pdfs = sorted(glob.glob(os.path.join(input_folder, "*.pdf")))
    for path in input_pdfs:
        pdf_merger.append(path)

    with open(path_to_output_pdf, 'wb') as output_pdf:
        pdf_merger.write(output_pdf)

    pdf_merger.close()

    if remove_artifacts:
        for pdf in input_pdfs:
            os.remove(pdf)


def pdf_to_image_to_pdf(input_pdf,
                        tmp_folder,
                        output_folder,
                        orientation,
                        remove_original=False,
                        remove_artifacts=False):
    """Converts PDF to images and merges as a PDF without blurring.

    Set the `remove_artifacts` parameter to clear temporary files created during
    the conversions. If it is `True`, temporary images and PDFs will be removed.
    Set the `remove_original` to `True' if you want to remove the input PDF.

    Args:
        input_pdf (str): Path to input PDF.
        output_folder (str): Path to the folder that processed PDF will be saved.
        remove_original (bool, optional):
            Whether remove input_pdf or not. Defaults to False.
        remove_artifacts (bool, optional):
            Whether to remove the prior processed file(s) or not. Default=False.

    Returns:
        str: Path of processed PDF.
    """
    file_name = input_pdf.split(os.sep)[-1].split('.')[0]
    output_pdf = os.path.join(output_folder, file_name + '_im2pdf' + '.pdf')

    pdf_to_image(input_pdf, tmp_folder, blur=False)
    image_to_pdf(tmp_folder, tmp_folder, orientation, remove_artifacts)
    merge_pdfs(tmp_folder, output_pdf, remove_artifacts)

    if remove_original:
        os.remove(input_pdf)

    return output_pdf


def blur_pages_of_pdf(input_pdf,
                      orientation,
                      tmp_folder,
                      output_folder,
                      dpi=100,
                      kernel=(5,5),
                      sigma=1,
                      remove_artifacts=False,
                      ):
    """Converts content of PDFs to images, blurs and then merges again

    Set the `remove_artifacts` parameter to `True` if you want to clear
    temporary files created during the conversion operations.

    Args:
        input_pdf (str): Path to input PDF
        orientation (str): Orientation of page 'landscape' or 'portrait'
        tmp_folder (str): Path to tmp folder that midproducts will be saved.
        output_folder (str): Path to the folder that processed PDF will be saved.
        dpi (int, optional): Dots Per Inch, conversion parameter. Default = 100.
        kernel (tuple, optional): Gaussian blur kernel size. Defaults to (5,5).
        sigma (float, optional): Gaussian blur sigma value. Defaults to 1.
        remove_artifacts (bool, optional):
            Whether to remove the prior processed file(s) or not. Default=False.

    Returns:
        [str]: path of output PDF
    """
    file_name = input_pdf.split(os.sep)[-1].split('.')[0]
    output_pdf = os.path.join(output_folder, file_name + '_blurred' + '.pdf')
    # Convert pages of PDF to images and save to `tmp_folder`
    pdf_to_image(input_pdf, tmp_folder, dpi, True, kernel, sigma)
    # Write images to A4 PDF pages with `orientation` and save to `tmp_folder`
    image_to_pdf(tmp_folder, tmp_folder, orientation, remove_artifacts)
    # Merge PDFs in `tmp_folder` and write to `output_folder`
    # Remove PDFs in tmp_folder after writing operation
    merge_pdfs(tmp_folder, output_pdf, remove_artifacts)

    return output_pdf


def add_watermark(input_pdf, watermark, output_folder, remove_original=False):
    """Adds watermark to each page of PDF and saves as '*_watermarked.pdf'

    Set the `remove_original` parameter to `True` if you want to remove, original
    `input_pdf` after watermarking operation.

    Args:
        input_pdf (str): Path to input PDF.
        watermark (str): Path to watermark.
        output_folder (str): The folder that processed PDFs will be saved.
        remove_original (bool, optional):
            Whether to remove the original file or not after watermarking.
            The default setting is False.

    Returns:
        str: Path of output PDF.
    """
    file_name = input_pdf.split(os.sep)[-1].split('.')[0]  # remove '.pdf'
    output_pdf = os.path.join(output_folder, file_name + '_watermarked' + '.pdf')
    watermark_page = PdfFileReader(watermark).getPage(0)  # Read watermark

    pdf_reader = PdfFileReader(input_pdf)  # Create reader object
    pdf_writer = PdfFileWriter()  # Create writer object

    for i in range(pdf_reader.getNumPages()):  # Add watermark to each page
        page = pdf_reader.getPage(i)  # Get the page with number i
        page.mergePage(watermark_page)  # Add watermark
        pdf_writer.addPage(page)  # add page to the writer object

    with open(output_pdf, 'wb') as out:
        pdf_writer.write(out)  # Write all watermarked pages to out file

    if remove_original:
        os.remove(input_pdf)

    return output_pdf


def move_processed_pdf(input_pdf, processed_folder):
    """Moves `input_pdf` to `processed_folder`.

    If there is a PDF with same name in the `processed_folder`, instead of
    overwriting the PDF in the `processed_folder`, this function adds a postfix
    constructed as `"_exists_" + f'{rnd}' + ".pdf"`. `rnd` is a uniformly
    generated random number which takes values in [0,100].

    Args:
        input_pdf (str): Path to input PDF.
        processed_folder (str): Path to folder PDF will be moved.
    """
    # Extract file name
    file_name = input_pdf.split(os.sep)[-1].split('.')[0]
    # Define path to move PDF
    new_path_to_input_pdf = os.path.join(processed_folder, file_name + '.pdf')
    if os.path.exists(new_path_to_input_pdf):  # Check whether PDF exists or not
        rnd = np.random.randint(0,100)  # Generate a random number to postfix
        try:
            postfix = "_exists_" + f'{rnd}' + ".pdf"  # Create postfix
            file_name = file_name + postfix  # Add postfix to file_name
            # Define path to move postfix added PDF
            if_input_pdf_is_exists = os.path.join(processed_folder, file_name)
            os.rename(input_pdf, if_input_pdf_is_exists)  # Move PDF
        except Exception as error:
            print("Bad luck, random function returned an existing number\n")
            raise error
    else:
        os.rename(input_pdf, new_path_to_input_pdf)


def encrypt_and_add_metadata(input_pdf,
                             output_folder,
                             usr_pass,
                             owner_pass,
                             remove_original=False):
    """Encrypts PDF, changes permissions and adds metadata to PDF.

    Default permissions let the user to print PDF but all other operations are
    restricted. In case you do not want to allow reading without a password,
    specify `usr_pass`. If you want to remove the original PDF after encryption
    set the `remove_original` parameter to `True`

    Args:
        input_pdf (str): path to input PDF
        output_folder (str): path to output folder
        usr_pass (str): user password to open PDF, if "", no pass required.
        owner_pass (str): owner password to edit PDF
        remove_original (bool, optional):
            Whether remove prior processed file(s) or not. Defaults to False.
    """
    # Extract file_name from the path
    file_name = input_pdf.split(os.sep)[-1].split('.')[0]
    # Set output path of PDF
    output_pdf = os.path.join(output_folder, file_name + '_final' + '.pdf')

    # Metadata sections of PDF. For more information visit the link below.
    # https://www.adobe.io/open/standards/xmp.html#!adobe/xmp-docs/master/Namespaces.md
    # Dublin Core namespace: dc:title, dc:creator, dc:description, dc:subject, dc:format, dc:rights
    # XMP basic namespace: xmp:CreateDate, xmp:CreatorTool, xmp:ModifyDate, xmp:MetadataDate
    # XMP rights management namespace: xmpRights:WebStatement, xmpRights:Marked
    # XMP media management namespace: xmpMM:DocumentID
    pdf  = pikepdf.Pdf.open(input_pdf)  # Read PDF
    with pdf.open_metadata() as meta:  # Add Metadata
        meta['dc:title'] = 'Lecture Notes'
        meta['dc:creator'] = 'Serhan Yarkan, Tapir Lab.'  # Author
        meta['dc:description'] = 'Tapir Lab. Fall-2020 Lecture Notes'
        meta['dc:subject'] = 'Probability, statistics, communications...\n\
            ALL HAIL TAPIR!\n\
            tapirlab.com'  # Keywords
        meta['dc:rights'] = 'Tapir Lab. License'
        meta['xmp:CreateDate'] = datetime.today().isoformat()
        meta['xmp:ModifyDate'] = datetime.today().isoformat()
        meta['xmp:CreatorTool'] = "Tapir Lab.'s Automatic Watermarking Script"
        meta['xmpRights:WebStatement'] = "http://www.tapirlab.com"

    # Set permissions of user
    permissions = pikepdf.Permissions(
        accessibility=False,
        extract=False,
        modify_annotation=False,
        modify_assembly=False,
        modify_form=False,
        modify_other=False,
        print_lowres=True,
        print_highres=True,
        )

    # Save PDF with added metadata and restricted permissions.
    pdf.save(output_pdf, encryption=pikepdf.Encryption(user=usr_pass,
                                                       owner=owner_pass,
                                                       allow=permissions,
                                                       ))
    # Close PDF object
    pdf.close()

    if remove_original:  # Remove original file if True
        os.remove(input_pdf)
