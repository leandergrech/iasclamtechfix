import os
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, NumberObject


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


if __name__ == '__main__':
    docs_dir = '../docs_ias'
    doc_paths = [os.path.join(docs_dir, item) for item in os.listdir(docs_dir)]
    for doc_path in doc_paths:
        replace_ias_logo(pdf_path=doc_path, save_dir='../docs_epejv', new_logo_path='../new_logo_small.jpg')
