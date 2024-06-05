import React, { useEffect, useState } from 'react';
import './CSS/InvoiceForm.css';

const InvoiceForm = ({ invoiceData }) => {
  const { CardCode, TaxDate, DocDate, DocDueDate, CardName, DiscountPercent, DocumentLines } = invoiceData[0];
  const data_arr = invoiceData.slice(1, invoiceData.length);
  const [image_canvas, setImage_canvas] = useState([]);



  useEffect(() => {
      const loadCanvas = () => {
        const canvases = document.querySelectorAll('canvas');
        let arr = [];
        canvases.forEach(canvas => {
            arr.push(canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height))
        })
        setImage_canvas(arr);
    }


    const handleFocus = (event) => {

      if(document.querySelectorAll('canvas').length == 0){
        return
      }
      let id = event.target.id;
      if(image_canvas.length == 0){
        loadCanvas();
      }
      if (isNaN(id) && id !== 'DiscountPercent') {
        let flag = false;
        data_arr.forEach((data, index) => {
          const current_canvas = document.querySelectorAll('canvas')[index];
          const ctx = current_canvas.getContext("2d");
          if (data[id]['cords'].length > 0) {
            data[id]['cords'].forEach((cord) => {
              ctx.beginPath();
              ctx.strokeStyle = "red";
              ctx.rect(cord.x0 - 1.5, cord.top - 1.5, (cord.x1 - cord.x0) + 2, (cord.bottom - cord.top) + 2);
              ctx.stroke();
              if (!flag) {
                let canvas_height = current_canvas.getBoundingClientRect().height;
                let document_height = current_canvas.height;
                let cord_document_top = (document_height * cord.top) / canvas_height;

                document.querySelector('div.react-pdf__Document.InvoiceView').scrollTo({ top: (cord_document_top + canvas_height * index), behavior: "smooth" });
                flag = true;
              }
            });
          }
        });
      } else if (!isNaN(id)) {
        id = +id; // converting string to number
        let flag = false;
        data_arr.forEach((data, index) => {
          const current_canvas = document.querySelectorAll('canvas')[index];
          const ctx = current_canvas.getContext("2d");
          if (data['DocumentLines'][id]['cords'].length > 0) {
            data['DocumentLines'][id]['cords'].forEach((cord) => {
              ctx.beginPath();
              ctx.strokeStyle = "red";
              ctx.rect(cord.x0 - 1.5, cord.top - 1.5, (cord.x1 - cord.x0) + 2, (cord.bottom - cord.top) + 2);
              ctx.stroke();
              if (!flag) {
                let canvas_height = current_canvas.getBoundingClientRect().height;
                let document_height = current_canvas.height;
                let cord_document_top = (document_height * cord.top) / canvas_height;

                document.querySelector('div.react-pdf__Document.InvoiceView').scrollTo({ top: (cord_document_top + canvas_height * index), behavior: "smooth" });
                flag = true;
              }
            });
          }
        });
      }
    };

    const handleBlur = () => {
      if(image_canvas.length == 0){
        return
      }
      const canvases = document.querySelectorAll('canvas');
      canvases.forEach((canvas, index) => {
        canvas.getContext('2d').putImageData(image_canvas[index], 0, 0);
      });
    };

    const inputs = document.querySelectorAll('input[id]');
    inputs.forEach(input => {
      input.addEventListener('focus', handleFocus);
      input.addEventListener('blur', handleBlur);
    });

    return () => {
      inputs.forEach(input => {
        input.removeEventListener('focus', handleFocus);
        input.removeEventListener('blur', handleBlur);
      });
    };
  }, [data_arr, image_canvas]);

  return (
    <div className="form-section">
      <h2 className="form-heading">Invoice Details</h2>
      <header>
        <div className="invoice-header">
          <div className="form-group">
            <label htmlFor="CardCode">Vendor ID:</label>
            <input type="text" id="CardCode" value={CardCode} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="CardName">Vendor Name:</label>
            <input type="text" id="CardName" value={CardName} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="TaxDate">Tax Date:</label>
            <input type="text" id="TaxDate" value={TaxDate} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="DocDate">Document Date:</label>
            <input type="text" id="DocDate" value={DocDate} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="DocDueDate">Due Date:</label>
            <input type="text" id="DocDueDate" value={DocDueDate} readOnly />
          </div>
          <div className="form-group">
            <label htmlFor="DiscountPercent">Discount %:</label>
            <input type="text" id="DiscountPercent" value={DiscountPercent} readOnly />
          </div>
        </div>
      </header>
      <main>
        <div className="table-container">
          <table className="invoice-table">
            <thead>
              <tr>
                <th>Item Code</th>
                <th>Quantity</th>
                <th>Unit Price</th>
                <th>Tax</th>
              </tr>
            </thead>
            <tbody>
              {DocumentLines.map((line, index) => (
                <tr key={index}>
                  <td><input type="text" id={index} value={line.ItemCode} readOnly /></td>
                  <td><input type="text" value={line.Quantity} readOnly /></td>
                  <td><input type="text" value={line.UnitPrice} readOnly /></td>
                  <td><input type="text" value={line.TaxCode} readOnly /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
};

export default InvoiceForm;
