from datetime import date

HTML_ROW_TEMPLATE = """
    <tr>
      <td>{order_date}</td>
      <td>{barcode_number}</td>      
      <td><img src='{barcode_img_url}'></td>
      <td>{amount}</td>
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
        width: 100%;
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
            <tr>  <th>Order date</th>   <th>Barcode number</th>   <th>Barcode image</th>  <th>Amount</th>   </tr>
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
            output_table += HTML_ROW_TEMPLATE.format(order_date=coupon['Date'],
                                                     barcode_number=coupon['barcode'],
                                                     barcode_img_url=coupon['barcode_url'],
                                                     amount=coupon['amount'])
        return HTML_PAGE_TEMPLATE.format(output_table=output_table, restaurantName=restaurant_name)

    def write_to_files(self):
        for r in self.coupons.values():
            filename = f"output/{date.today().strftime('%y-%m-%d')}_{r['restaurantName']}.html"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(self.format_orders(r['orders'], r['restaurantName']))
