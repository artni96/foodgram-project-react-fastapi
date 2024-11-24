from fileinput import filename

from pypdf import PdfWriter

def create_items_list():
    writer = PdfWriter()
    page = writer.add_blank_page(210, 297)


    with open('test_123.pdf', 'wb') as f:
        writer.write(f)

if __name__ == '__main__':
    create_items_list()
