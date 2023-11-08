import base64
import requests
from PIL import Image
import io

from Processor import Processor

HTML_ROW_TEMPLATE = """
    <tr>
      <td>{order_date}</td>
      <td>{amount}</td>
      <td>{barcode_number}</td>
      <td><img src="data:image/png;base64,{image_data}"></td>      
    </tr>
    """
HTML_PAGE_TEMPLATE = """
        <!DOCTYPE html>
        <html> 
        <head> <style>
            @page {{ margin:0 }}	
            #barcodes {{
            font-family: Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            }}
            img {{
            opacity: 1
            }}
            #barcodes td, #barcodes th {{
            border: 1px solid #ddd;
            padding: 8px;
            }}
            #barcodes tr:nth-child(even){{
            background-color: #f2f2f2;}}
            #barcodes tr:hover {{background-color: #ddd;}}
            #barcodes th {{
            padding-top: 12px;
            padding-bottom: 12px;
            vertical-align: top;
            text-align: center;
            background-color: #04AA6D;
            color: white;
            }}
        </style> </head>
        <body>
            <h1> {restaurantName} </h1>
            <table id="barcodes">
            <tr> 
                <th width="10%">Order date</th>
                <th width="10%">$$$</th>
                <th width="10%">Barcode</th> 
                <th width="70%">Barcode image</th>
            </tr>
            {output_table}
            </table>
        </body>
        </html>
"""


class CouponFormatter(Processor):
    def __init__(self):
        super().__init__()

    @staticmethod
    def download_crop_encode(url):
        try:
            response = requests.get(url)
            response.raise_for_status()

            # Read the image into memory
            image = Image.open(io.BytesIO(response.content))

            # Crop the image (0.25 from top and bottom)
            width, height = image.size
            top_crop = int(0.20 * height)
            bottom_crop = height - top_crop
            cropped_image = image.crop((0, top_crop, width, bottom_crop))

            # Convert the cropped image to bytes
            image_bytes = io.BytesIO()
            cropped_image.save(image_bytes, format='PNG')
            image_bytes.seek(0)

            # Print the base64 encoded image
            return base64.b64encode(image_bytes.read()).decode('utf-8')

        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return ''

    def process_impl(self, data):
        orders = data['orders']
        restaurant_name = data['restaurantName']
        output_table = ""
        for coupon in orders:
            image_data = self.download_crop_encode(coupon['barcode_url'])

            output_table += HTML_ROW_TEMPLATE.format(order_date=coupon['Date'],
                                                     barcode_number=coupon['barcode'].replace("-", "-<br>"),
                                                     image_data=image_data,
                                                     amount=coupon['amount'])
        return {'vendorName': data['vendorName'],
                'buffer': HTML_PAGE_TEMPLATE.format(output_table=output_table, restaurantName=restaurant_name)}
