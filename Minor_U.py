import os
import pikepdf

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod

# --- CONFIG ---
# original_pdf_path = "./Test.pdf"
original_pdf_path = "./sample.pdf"
repaired_pdf_path = "./Repaired_Test.pdf"
# name_without_suff = os.path.splitext(os.path.basename(original_pdf_path))[0]
# local_image_dir = "D:/Output/img"
# local_md_dir = "D:/Output"
# image_dir = os.path.basename(local_image_dir)
#
# # --- Ensure output dirs exist ---
# os.makedirs(local_image_dir, exist_ok=True)
#
# # --- Repair PDF ---
# try:
#     with pikepdf.open(original_pdf_path) as pdf:
#         pdf.save(repaired_pdf_path)
#     print(f"PDF repaired successfully: {repaired_pdf_path}")
# except Exception as e:
#     print(f"Failed to repair PDF: {e}")
#     exit(1)
#
# # --- Read PDF bytes ---
# reader = FileBasedDataReader("")
# pdf_bytes = reader.read(repaired_pdf_path)
#
# # --- Create Writers ---
# image_writer = FileBasedDataWriter(local_image_dir)
# md_writer = FileBasedDataWriter(local_md_dir)
#
# # --- Dataset and Inference ---
# ds = PymuDocDataset(pdf_bytes)
#
# if ds.classify() == SupportedPdfParseMethod.OCR:
#     infer_result = ds.apply(doc_analyze, ocr=True)
#     pipe_result = infer_result.pipe_ocr_mode(image_writer)
# else:
#     infer_result = ds.apply(doc_analyze, ocr=False)
#     pipe_result = infer_result.pipe_txt_mode(image_writer)
#
# # --- Draw model result (with error protection) ---
# try:
#     infer_result.draw_model(os.path.join(local_md_dir, f"{name_without_suff}_model.pdf"))
# except Exception as e:
#     print(f"Error drawing model PDF: {e}")
#
# # --- Draw other results ---
# pipe_result.draw_layout(os.path.join(local_md_dir, f"{name_without_suff}_layout.pdf"))
# pipe_result.draw_span(os.path.join(local_md_dir, f"{name_without_suff}_spans.pdf"))
#
# # --- Save outputs ---
# # Markdown
# md_content = pipe_result.get_markdown(image_dir)
# pipe_result.dump_md(md_writer, f"{name_without_suff}.md", image_dir)
#
# # Content List
# content_list_content = pipe_result.get_content_list(image_dir)
# pipe_result.dump_content_list(md_writer, f"{name_without_suff}_content_list.json", image_dir)
#
# # Middle JSON
# middle_json_content = pipe_result.get_middle_json()
# pipe_result.dump_middle_json(md_writer, f"{name_without_suff}_middle.json")
#
# print("PDF processing completed successfully.")


import os

from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze

# args
pdf_file_name = "./sample.pdf"  # replace with the real pdf path
name_without_suff = pdf_file_name.split(".")[0]

# prepare env
local_image_dir, local_md_dir = "D:/Output/img", "D:/Output"
image_dir = str(os.path.basename(local_image_dir))

os.makedirs(local_image_dir, exist_ok=True)

image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(
    local_md_dir
)

# read bytes
reader1 = FileBasedDataReader("")
pdf_bytes = reader1.read(pdf_file_name)  # read the pdf content

# proc
## Create Dataset Instance
ds = PymuDocDataset(pdf_bytes)

## inference
if ds.classify() == SupportedPdfParseMethod.OCR:
    ds.apply(doc_analyze, ocr=True).pipe_ocr_mode(image_writer).dump_md(
    md_writer, f"{name_without_suff}.md", image_dir
)

else:
    ds.apply(doc_analyze, ocr=False).pipe_txt_mode(image_writer).dump_md(
    md_writer, f"{name_without_suff}.md", image_dir
)

print("PDF processing completed successfully.")
