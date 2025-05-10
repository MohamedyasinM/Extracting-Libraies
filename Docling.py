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

print(f"Total time taken for parsing: {end_time:.2f} seconds.")
print("Document Name:", conv_res.document.origin.filename)
print("Document Type:", conv_res.document.origin.mimetype)
print("Number of Pages:", len(conv_res.document.pages))
print("Number of Text Blocks:", len(conv_res.document.texts))
print("Number of Tables:", len(conv_res.document.tables))
print("Number of Images:", len(conv_res.document.pictures))
print(conv_res.document.export_to_markdown())



