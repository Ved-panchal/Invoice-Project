import React, { useEffect, useState } from 'react';
import './CSS/InvoiceForm.css';

const InvoiceForm = ({ invoiceData, scale }) => {
  var { CardCode, TaxDate, DocDate, DocDueDate, CardName, DiscountPercent, DocumentLines } = invoiceData[0];
  const data_arr = invoiceData.slice(1, invoiceData.length);
  const [cardCode, setCardCode] = useState(CardCode);
  const [taxDate, setTaxDate] = useState(TaxDate);
  const [docDueDate, setDocDueDate] = useState(DocDueDate);
  const [discountPercent, setDiscountPercent] = useState(DiscountPercent);
  const [cardName, setCardName] = useState(CardName);
  const [docDate, setDocDate] = useState(DocDate);
  const [documentLines, setDocumentLines] = useState(DocumentLines);
  const [selectedRows, setSelectedRows] = useState([]);
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
      if (document.querySelectorAll('canvas').length === 0) {
        return;
      }
      let id = event.target.id;
      if (image_canvas.length === 0) {
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
              ctx.rect((cord.x0 - 1.5) * scale, (cord.top - 1.5) * scale, ((cord.x1 - cord.x0) + 3) * scale, ((cord.bottom - cord.top) + 2) * scale);
              ctx.stroke();
              if (!flag) {
                let canvas_height = current_canvas.getBoundingClientRect().height;
                let document_height = current_canvas.height;
                let cord_document_top = ((document_height * cord.top) / canvas_height) * scale;

                document.querySelector('div.pdf-view').scrollTo({ top: (cord_document_top + canvas_height * index), behavior: "smooth" });
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
              ctx.rect((cord.x0 - 1.5) * scale, (cord.top - 1.5) * scale, ((cord.x1 - cord.x0) + 3) * scale, ((cord.bottom - cord.top) + 2) * scale);
              ctx.stroke();
              if (!flag) {
                let canvas_height = current_canvas.getBoundingClientRect().height;
                let document_height = current_canvas.height;
                let cord_document_top = ((document_height * cord.top) / canvas_height) * scale;
                document.querySelector('div.pdf-view').scrollTo({ top: (cord_document_top + canvas_height * index), behavior: "smooth" });
                flag = true;
              }
            });
          }
        });
      }
    };

    const handleBlur = () => {
      if (image_canvas.length === 0) {
        return;
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

  const handleAddRow = () => {
    setDocumentLines([...documentLines, { ItemCode: '', Quantity: '', UnitPrice: '', TaxCode: '', cords: [] }]);
  };

  const handleDeleteRows = () => {
    setDocumentLines(documentLines.filter((_, index) => !selectedRows.includes(index)));
    setSelectedRows([]);
  };

  const handleInputChange = (index, field, value) => {
    const newDocumentLines = [...documentLines];
    newDocumentLines[index][field] = value;
    setDocumentLines(newDocumentLines);
  };

  const handleSelectRow = (index) => {
    if (selectedRows.includes(index)) {
      setSelectedRows(selectedRows.filter(rowIndex => rowIndex !== index));
    } else {
      setSelectedRows([...selectedRows, index]);
    }
  };

  const validateInputs = () => {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
      if (!input.value) {
        input.classList.add('error');
      } else {
        input.classList.remove('error');
      }
    });
  };

  useEffect(() => {
    validateInputs();
  }, [cardCode,
    taxDate,
    docDueDate,
    discountPercent,
    cardName,
    docDate,documentLines]);

  return (
    <div className="form-section">
      <h2 className="form-heading">Invoice Details</h2>
      <header>
        <div className="invoice-header">
          <div className="form-group">
            <label htmlFor="CardCode">Vendor ID:</label>
            <input type="text" id="CardCode" value={cardCode || ""}  onChange={e => setCardCode(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="CardName">Vendor Name:</label>
            <input type="text" id="CardName" value={cardName || ""} onChange={e => setCardName(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="TaxDate">Tax Date:</label>
            <input type="text" id="TaxDate" value={taxDate || ""} onChange={e => setTaxDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="DocDate">Document Date:</label>
            <input type="text" id="DocDate" value={docDate || ""} onChange={e => setDocDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="DocDueDate">Due Date:</label>
            <input type="text" id="DocDueDate" value={docDueDate || ""} onChange={e => setDocDueDate(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="DiscountPercent">Discount %:</label>
            <input type="text" id="DiscountPercent" value={discountPercent || ""} onChange={e => setDiscountPercent(e.target.value)} />
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
                <th>Select</th>
              </tr>
            </thead>
            <tbody>
              {documentLines.map((line, index) => (
                <tr key={index}>
                  <td><input type="text" id={index.toString()} value={line.ItemCode} onChange={(e) => handleInputChange(index, 'ItemCode', e.target.value)} /></td>
                  <td><input type="text" value={line.Quantity} onChange={(e) => handleInputChange(index, 'Quantity', e.target.value)} /></td>
                  <td><input type="text" value={line.UnitPrice} onChange={(e) => handleInputChange(index, 'UnitPrice', e.target.value)} /></td>
                  <td><input type="text" value={line.TaxCode} onChange={(e) => handleInputChange(index, 'TaxCode', e.target.value)} /></td>
                  <td><input type="checkbox" checked={selectedRows.includes(index)} onChange={() => handleSelectRow(index)} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="table-buttons">
          <button className="Addrow-btn" onClick={handleAddRow}>Add Row</button>
          <button className="Delete-btn" onClick={handleDeleteRows} disabled={selectedRows.length === 0}>Delete Selected</button>
        </div>
      </main>
    </div>
  );
};

export default InvoiceForm;
