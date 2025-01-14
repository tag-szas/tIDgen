#!/usr/bin/python3

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.lib.units import mm,cm
from reportlab.graphics.shapes import Drawing 
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from math import ceil
from tID import n_to_tID
import os


class LabelGen(object):

    """Ein LabelGen kann sich selbst auf einem Canvas zeichnen.
    Es ist für eine bestimmte Größe entworfen. 
    Es wird in einem Rechteck zentriert und passend skaliert gezeichnet.

    """

    def __init__(self):
        self.width = 4*cm
        self.height = 2*cm

    def create(self, c):
        # Load SVG icon once and define it as a form
        svg_icon_path = "TAG-Logo.svg"  # Path to the SVG file
        svg_icon = svg2rlg(svg_icon_path)

        # Scale the SVG icon to the size of the label
        scale = min(self.width / svg_icon.width, self.height / svg_icon.height) * 0.45

        # Define the SVG icon as a form
        c.beginForm("TAG-LOGO")
        c.saveState()
        c.scale(scale,scale)
        renderPDF.draw(svg_icon, c, 0, 0)
        c.restoreState()
        c.endForm()
        return self

    def page_init(self,c):
        c.setFont("Courier-Bold", 18)

    def draw(self, c, serial_number):
        # Generate QR code
        
        qr_code = qr.QrCodeWidget(f"https://7ek.de/{serial_number}")
        bounds = qr_code.getBounds()
        qr_size = self.height  # Size of QR code

        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        d = Drawing(qr_size, qr_size, transform=[
            qr_size / width, 0, 0,
            qr_size / height, 0, 0
        ])
        d.add(qr_code)

        render_x = 0  # + (label_width - qr_size) / 2
        render_y = 0 + (self.height - qr_size) / 2

        d.drawOn(c, render_x, render_y)

        # Add serial number
        text_x = self.width / 2
        text_y = 2 * mm
        c.drawString(text_x, text_y, f"{serial_number}")

        # Add SVG icon using the form
        icon_x = self.width/2 + 0 * mm
        icon_y = self.height - 10 * mm

        c.saveState()

        c.translate(icon_x, icon_y)
        c.doForm("TAG-LOGO")
        c.restoreState()



class GridGen(object):
    def __init__(self, num_serials, layout = 40):
        self.num_serials = num_serials

        if layout == 1:
            self.page_width = 4*cm
            self.page_height = 2.5*cm
            layout = (1,1)
        else:
            self.page_width, self.page_height = A4
            if layout == 65:
                layout = (5,13)
            elif layout in [36,40]:
                layout = (4,layout//4)
            elif layout in [24,21,18,12]:
                layout = (3,layout//3)
            elif layout in [4,6,8,10,14,16]:
                layout = (2,layout//2)    
            else:
                raise ValueError("Ungültige Anzahl an Labels")
        
        self.layout = layout
        self.serials_per_page = layout[0] * layout[1]
        self.page_count = ceil(num_serials / self.serials_per_page)
        self.num_serials = self.page_count * self.serials_per_page
  
    def write_pdf(self, output_file, serials):
        
        nx,ny = self.layout
        page_width, page_height = self.page_width, self.page_height

        border = 0.1 * mm

        label_width = page_width / nx
        label_height = page_height / ny

        c = canvas.Canvas(output_file, pagesize=(page_width, page_height))

        labelgen = LabelGen().create(c)
        
        serials_per_page = nx * ny
        num_serials = self.num_serials

        for page in range(self.page_count):
            
            labelgen.page_init(c)
    
            for row in range(ny):
                for col in range(nx):
                    try:
                        serial_number = next(serials)
                    except StopIteration:
                        break

                    c.saveState()

                    x = col * label_width
                    y = page_height - (row + 1) * label_height

                    c.translate(x, y)

                    # Draw label border (optional, for alignment/debugging)
                    if False:
                        c.setStrokeColorRGB(0, 0, 0)
                        c.rect(0, 0, label_width, label_height, stroke=1, fill=0)

                    scale = min((label_width -2*border)/ labelgen.width, (label_height-2*border) / labelgen.height)
                    shift_x = (label_width - labelgen.width * scale) / 2
                    shift_y = (label_height - labelgen.height * scale) / 2
                    c.translate(shift_x, shift_y)
                    c.scale(scale, scale)   

                    if False:
                        c.setStrokeColorRGB(1, 0, 0)
                        c.rect(0, 0, labelgen.width, labelgen.height, stroke=1, fill=0)

                    labelgen.draw(c, serial_number)
            
                    c.restoreState()

            c.showPage()
            print(f"Seite {page+1} von {self.page_count} erstellt")

        c.save()
        return serial_number


def generate_serials(start):
    serial = start
    while True:
        yield n_to_tID(serial)
        serial += 1 


def get_start_serial():

    config_file = "~/.config/tIDgen-start.txt"
    config_file = os.path.expanduser(config_file)

    # Read the start value from the config file
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            start = int(f.read().strip())
    else:
        start = 1  # Default start value if the file does not exist
    return start



def write_next_start_serial(next_start_serial):
    config_file = "~/.config/tIDgen-start.txt"
    config_file = os.path.expanduser(config_file)

    # Save the new start value back to the config file
    with open(config_file, "w") as f:
        f.write(str(next_start_serial)) 


start = None

if start is None:
    start = get_start_serial()

count = 25

grid_gen = GridGen(count,layout=40)
print(grid_gen.num_serials)
nx,ny = grid_gen.layout
output_file = f"TAG labels {start}-{start+grid_gen.num_serials} ({nx}x{ny}).pdf"

grid_gen.write_pdf(output_file, generate_serials(start))

print(f"PDF mit Labels wurde erfolgreich erstellt: {output_file}")

write_next_start_serial(start + grid_gen.num_serials)



