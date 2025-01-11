import os
import io
import pymupdf
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, NumberObject
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4


def replace_ias_logo(pdf_path, save_dir, new_logo_path):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    xobject_name = '/I0'

    # Load the new image
    with open(new_logo_path, "rb") as img_file:
        new_image_data = img_file.read()

    # Access PDF, locate image and replace
    for page_number, page in enumerate(reader.pages):
        resources = page.get("/Resources").get_object()  # Resolve the indirect object
        xobjects = resources.get("/XObject", {})
        print(xobjects)

        if xobject_name in xobjects:
            xobject = xobjects[xobject_name].get_object()  # Resolve the indirect object
            if xobject.get("/Subtype") == "/Image":
                print(f"Replacing {xobject_name} on page {page_number + 1}")

                # Update the XObject with new image data
                xobject.update({
                    # NameObject("/Length"): NumberObject(len(new_image_data)),
                    NameObject("/Filter"): NameObject("/DCTDecode"),  # Assuming JPEG
                    NameObject("/Width"): NumberObject(287),  # Set appropriate width
                    NameObject("/Height"): NumberObject(230),  # Set appropriate height
                    NameObject("/ColorSpace"): NameObject("/DeviceRGB"),  # Assuming RGB
                })

                # Replace the image stream
                xobject._data = new_image_data

        # Add page to the writer
        writer.add_page(page)

    # Write the modified PDF to output
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, os.path.basename(pdf_path))
    with open(save_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Image replaced and saved to {save_path}")


def replace_ias_logo_and_text(pdf_path, save_dir, new_logo_path, text_replacements):
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    xobject_name = '/I0'

    # Load the new image
    with open(new_logo_path, "rb") as img_file:
        new_image_data = img_file.read()

    # Use PyMuPDF to find text positions
    pdf_doc = pymupdf.open(pdf_path)

    # Access PDF, locate image and replace
    for page_number, page in enumerate(reader.pages):
        # Replace image
        resources = page.get("/Resources").get_object()
        xobjects = resources.get("/XObject", {})

        if xobject_name in xobjects:
            xobject = xobjects[xobject_name].get_object()
            if xobject.get("/Subtype") == "/Image":
                print(f"Replacing {xobject_name} on page {page_number + 1}")
                xobject.update({
                    NameObject("/Filter"): NameObject("/DCTDecode"),
                    NameObject("/Width"): NumberObject(287),  # Update width
                    NameObject("/Height"): NumberObject(230),  # Update height
                    NameObject("/ColorSpace"): NameObject("/DeviceRGB"),
                })
                xobject._data = new_image_data

        # Replace text
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        pdf_page = pdf_doc[page_number]

        # debug_text_positions(pdf_page)

        target_text = [item['target'] for item in text_replacements]
        if len(target_text) > 0:
            text_positions = find_text_positions(pdf_page, target_text=target_text)
            print(text_positions)

            if len(text_positions) > 0:
                for ttext, bbox in text_positions.items():
                    x, y = bbox[0], pdf_page.rect.height - bbox[1]

                    new_text = ''
                    font_size = None
                    wspace = None
                    bold = False
                    italic = False
                    for entry in text_replacements:
                        if entry['target'] == ttext:
                            new_text = entry['new']
                            font_size = entry['size']
                            wspace = entry['wspace']
                            bold = entry['bold']
                            italic = entry['italic']
                            break

                    font_style_suffix = '-'
                    if bold:
                        font_style_suffix += 'Bold'
                    if italic:
                        font_style_suffix += 'Oblique'

                    # font_size = text_replacements[ttext]["size"]
                    text_height = font_size * wspace

                    font = "Helvetica" + font_style_suffix
                    can.setFont(font, font_size)

                    text_width = can.stringWidth(ttext, font, font_size)

                    # Draw a white rectangle behind the text
                    can.setFillColorRGB(1, 1, 1)  # White background
                    can.rect(x, y - text_height, text_width, text_height, fill=1, stroke=0)

                    # Draw the replacement text
                    can.setFillColorRGB(0, 0, 0)  # Black text
                    can.drawString(x, y - text_height + (text_height - font_size) / 2, new_text)

                can.save()
                packet.seek(0)
                overlay_pdf = PdfReader(packet)
                print(len(overlay_pdf.pages))
                page.merge_page(overlay_pdf.pages[0])

        # Add page to writer
        writer.add_page(page)

    # Save the modified PDF
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, os.path.basename(pdf_path))
    with open(save_path, "wb") as output_file:
        writer.write(output_file)

    print(f"Logo and text replaced. Saved to {save_path}")


def find_text_positions(pdf_page, target_text:list):
    """
    Debug function to extract all text and coordinates from a page.
    """
    results = {}
    for block in pdf_page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                text = span["text"]
                for ttext in target_text:
                    if ttext==text:
                        results[ttext] = tuple(span['bbox'])
                        print(f"Text: {span['text']}, Coords: ({span['bbox'][0]}, {span['bbox'][1]})")
    return results


# def find_text_positions(pdf_page, target_text):
#     """
#     Finds the positions (coordinates) of the target text on a given PDF page.
#
#     Args:
#         pdf_page (fitz.Page): The PDF page object from PyMuPDF.
#         target_text (str): The text to search for.
#
#     Returns:
#         list: A list of tuples containing (x, y) coordinates for each match.
#     """
#     text_instances = []
#     for match in pdf_page.search_for(target_text):
#         x, y = match.x0, match.y0  # Top-left corner of the found text
#         text_instances.append((x, y))
#     return text_instances


def test_logo_replacement():
    docs_dir = '../docs_ias'
    doc_paths = [os.path.join(docs_dir, item) for item in os.listdir(docs_dir)]
    for doc_path in doc_paths:
        replace_ias_logo(pdf_path=doc_path, save_dir='../docs_epejv', new_logo_path='../new_logo_small.jpg')


if __name__ == '__main__':
    par_dir = '/home/leander/code/iasClamTechFix'
    docs_dir = os.path.join(par_dir, 'docs_ias')
    new_logo_path = os.path.join(par_dir, 'new_logo_small.jpg')
    save_dir = os.path.join(par_dir, 'docs_text_fix')

    doc_paths = [os.path.join(docs_dir, item) for item in os.listdir(docs_dir)]
    text_replacements = {
        "Matthew Camilleri": {"text": "Mark Anthony Muscat",
                              "size": 10,
                              "bold": True,
                              "italic": False},
        "iAS Project Manager": {"text": "Project Team Lead",
                                "size": 9,
                                "bold": False,
                                "italic": True},
        "Michael Cutajar (iAS)": {"text": "David Micallef &/or Peter Zammit",
                                  "size": 10,
                                  "bold": True,
                                  "italic": False},
        "Date Iss3ued": {"text": "Date Issued",
                         "size": 9,
                         "bold": False,
                         "italic": True}
    }
    for doc_path in doc_paths:
        replace_ias_logo_and_text(pdf_path=doc_path, save_dir=save_dir, new_logo_path=new_logo_path, text_replacements=text_replacements)
        # exit(23)

