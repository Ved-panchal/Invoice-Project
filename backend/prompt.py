def prepare_prompt(text=""):
    """
    Prepare the prompt for the OpenAI API to extract invoice data.

    Args:
    - text (str): The text extracted from the PDF.

    Returns:
    - str: The prepared prompt with the given text and instructions for data extraction.
    """
    invoiceData = {
        "CardCode": "V10000",
        "TaxDate": "2024-05-20",
        "DocDate": "2024-05-21",
        "DocDueDate": "2024-06-25",
        "CardName": "Acme Associates",
        "DiscountPercent": "10.00",
        "DocumentLines": [
            {
                "ItemCode": "A00001",
                "Quantity": "100",
                "TaxCode": "TAXON",
                "UnitPrice": "50"
            }
        ]
    }
    prompt = (
        f"{text}\n"
        """Extract the Details from this invoice in json format.
        if data is not available in invoice then give me blank please now give me json data.
        Please don't give me any other text and explanantion only give me json data.
        I have a sample of json and the explataion of each term
        "CardCode": "V10000",
            "TaxDate": "2024-05-20",
            "DocDate": "2024-05-21",
            "DocDueDate": "2024-06-25",
            "CardName": "Acme Associates",
            "DiscountPercent": "10.00",
            "DocumentLines": [
                {
                    "ItemCode": "A00001",
                    "Quantity": "100",
                    "TaxCode": "TAXON",
                    "UnitPrice": "50"
                }
            ]
        CardCode :- It means Vendor ID which can always start with "V", it is different from Customer and if it is empty give me empty string,
        TaxDate :- Tax date on an invoice refers to the date on which a delivery is recorded for VAT purposes1. If an invoice is issued within 14 days of the supply date, the invoice date is used as the tax point for VAT purposes.Format For TaxDate should be same that was written in the input text.
        DocDate :- It is a date on which the Doc is created.
        DocDueDate :- It is a date on which the Invoice should be paid or the doc will expire sometimes it is written in invoice but sometimes it will not written also there can be some text that can hint towards the due date calculation.
        Card Name :- It is the name of invoice or company name from which the invoice is generated or it can written as heading as well.
        Discount Price :- A trade discount is a percentage or dollar amount taken off of the item price or the invoice total. For example, the standard price of a product is $20, and the discounted price is $15, or a 10% \\discount is taken off of the invoice total due to a summer sale.
        DocumentLines :- It is the items list that are in the invoice and it should be the total number of items that are present in invoice.
        Item Code :- An item code is a numeric representation of a product or service provided by a department to a customer. Each product needs to have a unique item code to ensure appropriate classification, and item codes are essential for proper invoicing.
        Quantity :- the amount of items that are bought in the invoice each items can have different or same quantity.
        Tax code :- Tax codes are sequenced collections of one or more tax components that define the tax rates applied on line items and how to calculate the tax amount. Only one tax code can be applied on a line item.
        Tax codes are used in the enhanced tax engine configuration and also in third-party tax calculation systems. Tax codes in the basic tax configuration simply define the name, description, and the country/region.
        For line items that are exempted from tax, instead of not applying a tax code, apply a tax code that has a tax component with zero tax rate. The description of this tax code should clearly indicate that the item is exempted from tax.
        In India Tax code can include IGST,SGST,CGST with the percentage value.
        UnitPrice :- It is the price of the single unit of an item. it is not total amount.
        Special instruction for the date format as it is provided in text PLEASE Don.t reformat to any other format.
        """
    )
    return prompt