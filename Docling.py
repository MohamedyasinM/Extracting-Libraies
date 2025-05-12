from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.backend.docling_parse_backend import DoclingParseDocumentBackend
from docling. datamodel.base_models import InputFormat
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core. types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    OcrMacOptions,
    PdfPipelineOptions,
    RapidOcrOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
)
import time
import requests
from pathlib import Path
from IPython.display import display
import pandas as pd
import matplotlib.pyplot as plt
import math
import os
from PIL import Image
import numpy as np

Image.MAX_IMAGE_PIXELS = None

#----------------------------------------------------------------------
# Setting up a parser pipeline

IMAGE_RESOLUTION_SCALE = 20
input_doc_path = Path("./sample.pdf")

# Set pipeline options
pipeline_options = PdfPipelineOptions()
pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True

# Create document converter with format options
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# Perform conversion and measure time
start_time = time.time()
conv_res = doc_converter.convert(input_doc_path)
end_time = time.time() - start_time

#------------------------------------------------------------
# Extract metadata

print(f"Total time taken for parsing: {end_time:.2f} seconds.")
print("Document Name:", conv_res.document.origin.filename)
print("Document Type:", conv_res.document.origin.mimetype)
print("Number of Pages:", len(conv_res.document.pages))
print("Number of Text Blocks:", len(conv_res.document.texts))
print("Number of Tables:", len(conv_res.document.tables))
print("Number of Images:", len(conv_res.document.pictures))
print(conv_res.document.export_to_markdown())

# ---------------------------------------------------
#  Iterate through text units

results_body = conv_res.document.export_to_dict()
texts = results_body.get("texts", [])
dict_list = []
for t in texts:
    ref = t.get("self_ref", "")
    text_content = t.get("text", "")
    page = t.get("page", "")
    dict_list.append({
        "text_reference": ref,
        "page": page,
        "text_content(first 500 chars)": text_content[:500]
    })
df = pd.DataFrame(dict_list)
display(df)

#--------------------------------------------------
# Iterate through table units

tables = results_body.get("tables", [])
dict_list1 = []

for t in tables:
    ref = t.get("self_ref", "")
    page = t.get("page", "")
    table_data = t.get("data", "")

    table_captions = t.get("captions", [])

    if len(table_captions) > 0 and isinstance(table_captions[0], dict) and 'cref' in table_captions[0].keys():
        caption = table_captions[0].get('text', 'No Caption')
    else:
        caption = "No Caption"

    dict_list1.append({
        "table_reference": ref,
        "page": page,
        "table_captions": caption,
        "table_data(first 500 chars)": str(table_data)[:500]
    })

# df = pd.DataFrame(dict_list1)
# display(df)

#--------------------------------------------------
# Iterate through image units

images = results_body.get("pictures", [])
dict_list2 = []

for i in images:
    ref = i.get("self_ref", "No Reference")
    page = i.get("page", "Unknown")
    image_captions = i.get("captions", [])

    if image_captions and isinstance(image_captions[0], dict) and "cref" in image_captions[0]:
        image_caption = image_captions[0].get("cref", "No Caption")
    else:
        image_caption = "No Caption"

    image_data = i.get("data", "")
    dict_list2.append({
        "image_reference": ref,
        "page": page,
        "image_caption": image_caption,
        "image_data (first 500 chars)": str(image_data)[:500]
    })

df = pd.DataFrame(dict_list2)
display(df)

#---------------------------------------------------
# Iterate through the pages of the document

def display_images(images, images_per_row=5, figsize=(15, 8)):
    if isinstance(images, dict):
        images = list(images.values())

    num_images = len(images)
    num_rows = (num_images + images_per_row - 1) // images_per_row

    fig, axes = plt.subplots(num_rows, images_per_row, figsize=figsize)
    if num_rows == 1:
        axes = axes if isinstance(axes, (list, np.ndarray)) else [axes]
    else:
        axes = axes.flatten()

    for ax, image in zip(axes, images):
        ax.imshow(image)
        ax.axis('off')

    for ax in axes[len(images):]:
        ax.axis('off')

    plt.tight_layout()
    plt.show()

page_images = {page_no: page.image.pil_image for page_no, page in conv_res.document.pages.items()}
display_images(page_images, images_per_row=5, figsize=(15, 8))

# Save page images to D local directory
dir_path = "output_pages"
os.makedirs(dir_path, exist_ok=True)
for page_no, page in conv_res.document.pages.items():
    page_image_filename = f"{page_no}.png"
    with open(os.path.join(dir_path, page_image_filename), "wb") as fp:
        page.image.pil_image.save(fp, format="PNG")

#--------------------------------------------------------------------
# Extract all the images from the document.

dir_path = "./images"
os.makedirs(dir_path, exist_ok=True)

images_list = []
image_number = 1

for element, _level in conv_res.document.iterate_items():
    if isinstance(element, PictureItem):
        image_filename = os.path.join(dir_path, f"image_{image_number}.png")
        with open(image_filename, "wb") as fp:
            image = element.get_image(conv_res.document)
            image.save(fp, "PNG")
            images_list.append(image)
        image_number += 1
display_images(images_list, images_per_row=5, figsize=(15, 8))

# -------------------------------------------------------------------
# Extract all the tables from the document

dir_paths = ["./tables/images", "./tables/CSVs", "./tables/HTMLs"]

for path in dir_paths:
    os.makedirs(path, exist_ok=True)

table_list = []
table_number = 1
for element, _level in conv_res.document.iterate_items():
    if isinstance(element, TableItem):
        table_image_filename = os.path.join(dir_paths[0], f"table_{table_number}.png")
        with open(table_image_filename, "wb") as fp:
            table_image = element.get_image(conv_res.document)
            table_image.save(fp, "PNG")
            table_list.append(table_image)

        table_df = element.export_to_dataframe()
        table_csv_filename = os.path.join(dir_paths[1], f"table_{table_number}.csv")
        table_df.to_csv(table_csv_filename, index=False)

        table_html = element.export_to_html()
        table_html_filename = os.path.join(dir_paths[2], f"table_{table_number}.html")
        with open(table_html_filename, "w") as fp:
            fp.write(table_html)

        table_number += 1

#------------------------------------------------------------------------------------
# Build OCR enabled pipeline

def OCR_parsing(doc_path):
    input_doc = Path(doc_path)

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True  # Enable OCR
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True

    ocr_options = EasyOcrOptions(force_full_page_ocr=True)
    pipeline_options.ocr_options = ocr_options

    pipeline_options.generate_page_images = True

    start_time = time.time()

    converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )

    result = converter.convert(input_doc)

    end_time = time.time()
    print(f"Total time taken for parsing: {end_time - start_time:.2f} seconds.")

    return result


# OCR Example

ocr_result = OCR_parsing("./sample.pdf")

extract = ocr_result.document.export_to_markdown()
print("Docling Extract")
print(extract)
page_images1 = {page_no: page.image.pil_image for page_no, page in ocr_result.document.pages.items()}

print("Actual Document")
display_images(page_images, images_per_row=2, figsize=(100, 50))
