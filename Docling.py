from docling.document_converter import DocumentConverter , PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.base_models import InputFormat
# # from utils.sitemap import get_sitemap_urls



pipeline_options = PdfPipelineOptions()
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2
pipeline_options.do_picture_classification = True

converter = DocumentConverter(format_options={
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

result = converter.convert("./sample.pdf")
# result = converter.convert("./Test.pdf")
document = result.document
markdown_output = document.export_to_markdown()
json_output = document.export_to_dict()
print(markdown_output)

with open("output.md", "w", encoding="utf-8") as f:
    f.write(document.export_to_markdown())

# import os
# os.environ['HF_HOME'] = os.path.abspath('./hf_cache')  # Or any safe directory
# os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
# os.makedirs("figures", exist_ok=True)
# import streamlit as st
#
# # Example usage
# # converter = DocumentConverter()
# result = converter.convert("D:/docling/utils/testing_doc2.pdf")
#
# document = result.document
# markdown_output = document.export_to_markdown()
# json_output = document.export_to_dict()
#
# # Show the markdown on frontend
# st.markdown(markdown_output, unsafe_allow_html=True)  # if HTML tags are inside markdown
#
# # Optionally show JSON too
# st.json(json_output)

# --------------------------------------------------------------
# Basic HTML extraction
# --------------------------------------------------------------

# result = converter.convert("https://docling-project.github.io/docling/concepts/docling_document/")
#
# document = result.document
# markdown_output = document.export_to_markdown()
# print(markdown_output)
#
# # --------------------------------------------------------------
# # Scrape multiple pages using the sitemap
# # --------------------------------------------------------------
#
# sitemap_urls = get_sitemap_urls("https://docling-project.github.io/docling/concepts/docling_document/")
# conv_results_iter = converter.convert_all(sitemap_urls)
#
# docs = []
# for result in conv_results_iter:
#     if result.document:
#         document = result.document
#         docs.append(document)
