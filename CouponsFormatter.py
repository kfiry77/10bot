import base64
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

            image_data = ''
            if response.status_code == 200:
                # Get the image content and encode it in base64
                image_data = base64.b64encode(response.content).decode("utf-8")
            else:
                print(f'fail to get image:{image_url}')

            output_table += HTML_ROW_TEMPLATE.format(order_date=coupon['Date'],
                                                     barcode_number=coupon['barcode'].replace("-", "-<br>"),
                                                     image_data=image_data,
                                                     amount=coupon['amount'])
        return HTML_PAGE_TEMPLATE.format(output_table=output_table, restaurantName=restaurant_name)
