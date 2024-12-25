
import jinja2
import pdfkit
from datetime import datetime


def create_shopping_list(data, username):
    today_date = datetime.now().strftime("%d.%m.%Y %H:%M")

    context = {
               'username': username,
               'item_dict': data,
               'today_date': today_date
            }

    template_loader = jinja2.FileSystemLoader('src/media')
    template_env = jinja2.Environment(loader=template_loader)

    html_template = './base_shopping_list_template.html'
    template = template_env.get_template(html_template)
    output_text = template.render(context)

    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')
    filename = f'{datetime.now().strftime("%d.%m.%Y_%H:%M:%S")}_{username}_shopping_list.pdf'
    output_pdf = f'src/media/shopping_lists/{filename}'
    pdfkit.from_string(output_text, output_pdf, configuration=config)
    return output_pdf
