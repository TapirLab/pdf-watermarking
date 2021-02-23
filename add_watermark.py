# -*- coding: utf-8 -*-
"""
This program executes a sample watermarking and encryption procedure. Following
steps are applied to produce watermarked and encrypted PDF:
1. Pages converted to images, Gaussian noise added and Gaussian blurring applied.
2. Watermark is added to pages.
3. Pages converted to images and then drawn on pages again to embed content.
4. Metadata is added, permissions are restricted and the file is encrypted with
an owner password. The user does not require a password to read and print PDF.

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
import pdf_operations as po

if __name__ == '__main__':
    orientation = 'landscape'  # Orientation of input PDF(s)
    input_folder = os.path.join('.', 'sample_input')  # Input PDF(s) should be placed into this folder
    tmp_folder = os.path.join('.', 'tmp')  # Temporary files will be saved into this folder
    output_folder = os.path.join('.', 'sample_output')  # Output(s) will be saved into this folder
    processed_folder = os.path.join('.', 'processed')  # Original PDF(s) will be moved into this folder
    watermark = os.path.join('.', 'watermarks', orientation + "_A4.pdf")  # Path to watermark PDF
    
    # `remove_artifacts` and `remove_originals` PARAMETERS SHOULD BE SET CAREFULLY!
    # IN CASE OF MISCONFIGURATION OF PARAMETERS, YOU MAY LOSE YOUR ORIGINAL FILE!
    # Read all the PDFs in `sample_input` folder. Make sure that your file ending with ".pdf"
    files = sorted(glob.glob(os.path.join(input_folder, '*.pdf')))
    for input_pdf in files:  # Apply followings on each PDF
        # This function adds Gaussian noise with `sigma` parameter to the pages.
        # Then performs a Gaussian blurring with provided kernel size.
        # Finally converts images to pdfs and merges them all.
        # Returns path of the output.
        blurred_pdf = po.blur_pages_of_pdf(input_pdf,
                                           orientation,
                                           tmp_folder,
                                           output_folder,
                                           dpi=100,
                                           kernel=(5,5),
                                           sigma=0.5,
                                           remove_artifacts=True,
                                           )
        # This function adds watermark to the each page.
        # Returns path of the output.
        # `remove_artifacts` and `remove_originals` PARAMETERS SHOULD BE SET CAREFULLY!
        # IN CASE OF MISCONFIGURATION OF PARAMETERS, YOU MAY LOSE YOUR ORIGINAL FILE!
        blurred_watermarked_pdf = po.add_watermark(blurred_pdf,
                                                   watermark,
                                                   output_folder,
                                                   remove_original=True,
                                                   )
        # This function converts PDFs to images, then images to PDFs.
        # `remove_artifacts` and `remove_originals` PARAMETERS SHOULD BE SET CAREFULLY!
        # IN CASE OF MISCONFIGURATION OF PARAMETERS, YOU MAY LOSE YOUR ORIGINAL FILE!
        blurred_watermarked_img_pdf = po.pdf_to_image_to_pdf(blurred_watermarked_pdf,
                                                             tmp_folder,
                                                             output_folder,
                                                             orientation,
                                                             remove_original=True,
                                                             remove_artifacts=True,
                                                             )
        # This function encrypts PDFs with given user and owner passwords.
        # Metadata and permissions are defined inside the function.
        # After encryption only permission that the user has is printing and
        # content copying for accessibility.
        # `remove_artifacts` and `remove_originals` PARAMETERS SHOULD BE SET CAREFULLY!
        # IN CASE OF MISCONFIGURATION OF PARAMETERS, YOU MAY LOSE YOUR ORIGINAL FILE!
        po.encrypt_and_add_metadata(blurred_watermarked_img_pdf,
                                    output_folder,
                                    usr_pass="",
                                    owner_pass="your_pass",
                                    remove_original=True,
                                    )
        # This function moves input pdfs to processed folder.
        po.move_processed_pdf(input_pdf, processed_folder)
