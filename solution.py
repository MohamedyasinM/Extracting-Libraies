import fitz  # PyMuPDF
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import io
import os
import tabula
import warnings

# Try to import OCR libraries with fallbacks
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    warnings.warn("Tesseract not available - install with 'pip install pytesseract'")

try:
    import easyocr

    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class PDFExtractor:
    def __init__(self):
        self.ocr_reader = None
        if EASYOCR_AVAILABLE:
            self.ocr_reader = easyocr.Reader(['en'])

    def extract_text_and_tables(self, pdf_path):
        """Extract text and tables using PyMuPDF"""
        doc = fitz.open(pdf_path)
        text_output = []
        tables_output = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Extract text
            text = page.get_text("text")
            text_output.append(f"--- Page {page_num + 1} Text ---\n{text}\n")

            # Extract tables (simple approach)
            tabs = page.find_tables()
            if tabs.tables:
                for i, table in enumerate(tabs.tables):
                    table_text = table.extract()
                    tables_output.append(f"--- Page {page_num + 1} Table {i + 1} ---")
                    for row in table_text:
                        tables_output.append("\t".join(str(cell) for cell in row))
                    tables_output.append("")

        return "\n".join(text_output), "\n".join(tables_output)

    def extract_tables_with_tabula(self, pdf_path):
        """Advanced table extraction using Tabula"""
        try:
            tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
            tables_output = []

            for i, table in enumerate(tables):
                tables_output.append(f"--- Table {i + 1} ---")
                tables_output.append(table.to_string(index=False))
                tables_output.append("")

            return "\n".join(tables_output)
        except Exception as e:
            return f"Tabula table extraction failed: {str(e)}"

    def perform_ocr(self, image_path):
        """Perform OCR using available libraries"""
        if TESSERACT_AVAILABLE:
            try:
                return pytesseract.image_to_string(image_path)
            except:
                pass

        if self.ocr_reader is not None:
            try:
                result = self.ocr_reader.readtext(image_path)
                return " ".join([x[1] for x in result])
            except:
                pass

        return None

    def extract_images_and_handwriting(self, pdf_path):
        """Extract images and perform OCR on them"""
        doc = fitz.open(pdf_path)
        image_output = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Save image temporarily
                image = Image.open(io.BytesIO(image_bytes))
                image_path = f"temp_img_{page_num}_{img_index}.png"
                image.save(image_path)

                # Perform OCR
                ocr_text = self.perform_ocr(image_path)
                if ocr_text:
                    image_output.append(f"--- Page {page_num + 1} Image {img_index + 1} OCR Text ---")
                    image_output.append(ocr_text)
                else:
                    # Save images if OCR failed
                    output_image_path = os.path.join("output", f"page_{page_num}_img_{img_index}.png")
                    image.save(output_image_path)
                    image_output.append(f"Image saved to {output_image_path} (OCR not available)")

                # Remove temporary image
                try:
                    os.remove(image_path)
                except:
                    pass

        return "\n".join(image_output)

    def extract_charts_and_handwriting(self, pdf_path):
        """Convert PDF pages to images and extract text"""
        try:
            images = convert_from_path(pdf_path)
            chart_output = []

            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                open_cv_image = np.array(image)
                open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

                # Save temporary image for OCR
                temp_path = f"temp_page_{i}.png"
                cv2.imwrite(temp_path, open_cv_image)

                # Perform OCR
                ocr_text = self.perform_ocr(temp_path)
                if ocr_text:
                    chart_output.append(f"--- Page {i + 1} Full Page OCR (Charts/Handwriting) ---")
                    chart_output.append(ocr_text)
                else:
                    output_path = os.path.join("output", f"page_{i}_full.png")
                    cv2.imwrite(output_path, open_cv_image)
                    chart_output.append(f"Full page image saved to {output_path} (OCR not available)")

                # Clean up
                try:
                    os.remove(temp_path)
                except:
                    pass

            return "\n".join(chart_output)
        except Exception as e:
            return f"Failed to extract charts/handwriting: {str(e)}"

    def process_pdf(self, pdf_path):
        """Process PDF and extract all content types"""
        print("Extracting text and simple tables...")
        text_output, tables_output = self.extract_text_and_tables(pdf_path)

        print("Extracting advanced tables...")
        advanced_tables = self.extract_tables_with_tabula(pdf_path)

        print("Extracting images and OCR...")
        image_output = self.extract_images_and_handwriting(pdf_path)

        print("Extracting charts and handwriting...")
        chart_output = self.extract_charts_and_handwriting(pdf_path)

        # Combine all outputs
        return {
            "text": text_output,
            "simple_tables": tables_output,
            "advanced_tables": advanced_tables,
            "images": image_output,
            "charts_and_handwriting": chart_output
        }

    def save_output(self, final_output, output_dir="output"):
        """Save all extracted content to files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for key, content in final_output.items():
            with open(os.path.join(output_dir, f"{key}.txt"), "w", encoding="utf-8") as f:
                f.write(content)


def main():
    pdf_path = "./sample.pdf"  # Change to your PDF path
    extractor = PDFExtractor()

    print(f"Processing PDF: {pdf_path}")
    final_output = extractor.process_pdf(pdf_path)

    print("Saving results...")
    extractor.save_output(final_output)

    print("Extraction complete! Check the 'output' folder for results.")


if __name__ == "__main__":
    main()