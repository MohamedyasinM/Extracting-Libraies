from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)
# rendered = converter("./Test.pdf")
rendered  = converter ("./sample.pdf")
text, _, _ = text_from_rendered(rendered)

print(text)

# D:/docling/utils/testing_doc2.pdf