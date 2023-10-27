import base64
from datetime import date
import requests

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
        <head>
        <style>
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
        </style>
        </head>
        <body>
            <h1> {restaurantName} </h1>
            <table id="barcodes">
            <tr> 
  				<th width="70px">Order date</th>
				<th width="30px">Amount</th>
				<th width="50px">Barcode number</th> 
				<th width="300px">Barcode image</th>
             </tr>
            {output_table}
            </table>
        </body>
        </html>
    """


class CouponFormatter:
    def __init__(self, coupons):
        self.coupons = coupons

    def format_orders(self, orders, restaurant_name):
        output_table = ""
        for coupon in orders:
            # URL of the image you want to embed
            image_url = coupon['barcode_url']

            # Fetch the image from the URL
            response = requests.get(image_url)

            if response.status_code == 200:
                # Get the image content and encode it in base64
                image_data = base64.b64encode(response.content).decode("utf-8")
            else:
                print(f'fail to get image:{image_url}')

            output_table += HTML_ROW_TEMPLATE.format(order_date=coupon['Date'],
                                                     barcode_number=coupon['barcode'],
                                                     image_data=image_data,
                                                     amount=coupon['amount'])
        return HTML_PAGE_TEMPLATE.format(output_table=output_table, restaurantName=restaurant_name)

    def write_to_files(self):
        for r in self.coupons.values():
            filename = f"output/{date.today().strftime('%y-%m-%d')}_{r['vendorName']}.html"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.format_orders(r['orders'], r['restaurantName']))
            HTML(string=open(filename, 'rb').read()).write_pdf(filename + ".pdf")
