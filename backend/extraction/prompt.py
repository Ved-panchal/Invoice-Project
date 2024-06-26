def prepare_prompt(text):
    """
    Prepare the prompt for the OpenAI API to extract invoice data.

    Args:
    - text (str): The text extracted from the PDF.

    Returns:
    - str: The prepared prompt with the given text and instructions for data extraction.
    """

    invoiceData = {
        "CardCode": "",
        "TaxDate": "",
        "DocDate": "",
        "DocDueDate": "",
        "CardName": "",
        "DiscountPercent": "",
        "DocumentLines": [
            {
                "ItemCode": "",
                "Quantity": "",
                "TaxCode": "",
                "UnitPrice": ""
            }
        ]
    }
    prompt1 = (
        f"{text}\n"
        """Extract the details from this invoice in JSON format. If data is not available, provide an empty string.
        don't give me any other text and explanantion only give me json data.
        I have a sample of json and the explataion of each term
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
        Special instruction for the date format as it is provided in text, Don't reformat to any other format.
        DONT GIVE ME ANY COMMENTS.
        """
        f"{invoiceData}"
        """
        STRICTLY WARNING :- DO NOT CALCULATE ANYTHING BY YOUR ONLY GIVE THAT DATA THAT YOU GET FROM INVOICE.

        DO NOT ADD ANY COMMENTS IN JSON DATA. GIVE ME DATA THAT IS PURLY IN JSON FORMAT. PROVIDE VALUE IN JSON IN STRING FORMAT.

        unit price and quantity should be in number only from the data and give me in string in json format.

        Extract the Details from this invoice in json format.

if data is not available in invoice then give me blank please now give me json data.

explanation of each term

CardCode :- CardCode is vendor id most of time it will not available in invoice and if present then it will written like this "V0001" or like this if you found vendor id like this then only give me that otherwise give me blank STRICTLY follow this.,

TaxDate :- Tax date on an invoice refers to the date on which a delivery is recorded for VAT purposes1. If an invoice is issued within 14 days of the supply date, the invoice date is used as the tax point for VAT purposes.Format For TaxDate should be same that was written in the input.

DocDate :- It is a date on which the Doc is created.

DocDueDate :- It is a date on which the Invoice should be paid or the doc will expire sometimes it is written in invoice but sometimes it will not written also there can be some text that can hint towards the due date calculation.

Card Name :- It is the name of invoice or company name from which the invoice is generated or it can written as heading as well.

Discount Price :- A trade discount is a percentage or dollar amount taken off of the item price or the invoice total. For example, the standard price of a product is 
20,and the discounted price is
20,and the discounted price is 15, or a 10% discount is taken off of the invoice total due to a summer sale.

DocumentLines :- It is the items list that are in the invoice and it should be the total number of items that are present in invoice.

Item Code :- HSN or SAC can also be called as item code. An item code is a numeric representation of a product or service provided by a department to a customer. Each product needs to have a unique item code to ensure appropriate classification, and item codes are essential for proper invoicing. you give item code among these two don't give me both just one HSA and SAC or among the description that written.For item code priority should be like this
Item code > HSN/SAC > Item code in description

Quantity :- the amount of items that are bought in the invoice each items can have different or same quantity.

Tax code :- Tax codes are sequenced collections of one or more tax components that define the tax rates applied on line items and how to calculate the tax amount. Only one tax code can be applied on a line item.
In tax code you should include Tax code with % value
like IGST, CGST, SGST and there %

Tax codes are used in the enhanced tax engine configuration and also in third-party tax calculation systems. Tax codes in the basic tax configuration simply define the name, description, and the country/region.

For line items that are exempted from tax, instead of not applying a tax code, apply a tax code that has a tax component with zero tax rate. The description of this tax code should clearly indicate that the item is exempted from tax.

In India Tax code can include IGST,SGST,CGST with the percentage value.

UnitPrice :- It is the price of the single unit of an item. it is not total amount, In this above output Amount is the unit price not the annual charges

this are the fields that you need to extract from this invoice text, please provide all the data exactly given in invoice and yes you can calculate some terms but don't cut any data from invoice and reply me with every data.

I have a sample of json and the explataion of each term



        """
    f'{invoiceData}'
    )

    prompt2 = (
        f"{text}\n"
        """Extract the details from this invoice in JSON format. If data is not available, provide an empty string.
            {
                "CardCode": "",
                "TaxDate": "",
                "DocDate": "",
                "DocDueDate": "",
                "CardName": "",
                "DiscountPrice": "",
                "DocumentLines": [
                    "ItemCode": "",
                    "Quantity": "",
                    "TaxCode": "",
                    "UnitPrice": ""
                ]
            }
            Descriptions:
            - CardCode: Vendor ID, starts with "V".
            - TaxDate: Date for VAT purposes.
            - DocDate: Creation date of the document.
            - DocDueDate: Payment due date.
            - CardName: Invoice or company name.
            - DiscountPrice: Discount on item or invoice total.
            - DocumentLines: List of items in the invoice.
                - ItemCode: Unique numeric representation of a product/service.
                - Quantity: Number of items bought.
                - TaxCode: Defines tax rates and calculations.
                - UnitPrice: Price per unit of an item.
            Keep date format as in input text. NO COMMENTS.
            Unit price and quantity should be in number only from the data and give me in string in json format.
            STRICTLY WARNING :- DO NOT CALCULATE ANYTHING BY YOURSELF.
            DO NOT ADD ANY COMMENTS AND EXTRA FEILDS IN JSON DATA. GIVE ME DATA THAT IS PURLY IN JSON FORMAT PROVIDED ABOVE. PROVIDE VALUE IN JSON IN STRING FORMAT.
        """
    )

    return prompt2


def generate_dynamic_prompt(text, fields_with_descriptions: dict):
    # Construct the JSON template
    json_template = "{\n"
    for field, description in fields_with_descriptions.items():
        if field == "DocumentLines":
            json_template += f'    "{field}": [\n        {{"\n'
            for subfield, subdescription in description.items():
                json_template += f'            "{subfield}": "",\n'
            json_template = json_template.rstrip(",\n") + "\n        }}\n    ],\n"
        else:
            json_template += f'    "{field}": "",\n'
    json_template = json_template.rstrip(",\n") + "\n}"

    # Construct the descriptions
    descriptions = "Descriptions:\n"
    for field, description in fields_with_descriptions.items():
        if field == "DocumentLines":
            descriptions += f"- {field}: List of items in the invoice.\n"
            for subfield, subdescription in description.items():
                descriptions += f"    - {subfield}: {subdescription}\n"
        else:
            descriptions += f"- {field}: {description}\n"

    # Combine everything to form the final prompt
    prompt = (
        f"{text}\n"
        f"Extract the details from this invoice in JSON format. If data is not available, provide an empty string.\n"
        f"{json_template}\n"
        f"{descriptions}"
        f"Keep date format as in input text. NO COMMENTS.\n"
        f"Unit price and quantity should be in number only from the data and give me in string in json format.\n"
        f"STRICTLY WARNING : DO NOT CALCULATE ANYTHING BY YOUR ONLY GIVE THAT DATA THAT YOU GET FROM INVOICE.\n"
        f"STRICTLY WARNING: DO NOT ADD ANY COMMENTS AND EXTRA FEILDS IN JSON DATA. GIVE ME DATA THAT IS PURLY IN JSON FORMAT PROVIDED ABOVE. PROVIDE VALUE IN JSON IN STRING FORMAT."
        f"This are the fields that you need to extract from this invoice text, please provide all the data exactly given in invoice and yes you can calculate some terms but don't cut any data from invoice and reply me with every data."
    )

    return prompt

# When we create register, we add default fields to the db along with it
_default_fields = {
    "CardCode": "CardCode is vendor id most of time it will not available in invoice and if present then it will written like this V0001 or like this if you found vendor id like this then only give me that otherwise give me blank STRICTLY follow this.",
    "TaxDate": "Tax date on an invoice refers to the date on which a delivery is recorded for VAT purposes1. If an invoice is issued within 14 days of the supply date, the invoice date is used as the tax point for VAT purposes.Format For TaxDate should be same that was written in the input.",
    "DocDate": "Creation date of the document.",
    "DocDueDate": "Payment due date.",
    "CardName": "Invoice or company name.",
    "DiscountPercentage": "Discount on item or invoice total.",
    "DocumentLines": {
        "ItemCode": "HSN or SAC can also be called as item code. An item code is a numeric representation of a product or service provided by a department to a customer. Each product needs to have a unique item code to ensure appropriate classification, and item codes are essential for proper invoicing. you give item code among these two don't give me both just one HSA and SAC or among the description that written.For item code priority should be like this, Item code > HSN/SAC > Item code in description",
        "Quantity": "the amount of items that are bought in the invoice each items can have different or same quantity.",
        "TaxCode": "Tax codes are sequenced collections of one or more tax components that define the tax rates applied on line items and how to calculate the tax amount. Only one tax code can be applied on a line item. In tax code you should include Tax code with % value like IGST, CGST, SGST and there % Tax codes are used in the enhanced tax engine configuration and also in third-party tax calculation systems. Tax codes in the basic tax configuration simply define the name, description, and the country/region. For line items that are exempted from tax, instead of not applying a tax code, apply a tax code that has a tax component with zero tax rate. The description of this tax code should clearly indicate that the item is exempted from tax. In India Tax code can include IGST,SGST,CGST with the percentage value..",
        "UnitPrice": "It is the price of the single unit of an item. it is not total amount, In this above output Amount is the unit price not the annual charges this are the fields that you need to extract from this invoice text, please provide all the data exactly given in invoice and yes you can calculate some terms but don't cut any data from invoice and reply me with every data. I have a sample of json and the explataion of each term.",
    }
}