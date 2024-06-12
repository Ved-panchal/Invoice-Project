/* eslint-disable react/prop-types */
import { useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import axios from 'axios';
import InvoiceForm from './InvoiceForm';
import './CSS/PdfViewer.css';

pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.js`;

const PdfViewer = ({ pdfUrl, fileName, fileCode }) => {
  const canvasContainerRef = useRef(null);
  const [numPages, setNumPages] = useState(0);
  const [data, setData] = useState([]);
  const [imgCondition, setImageCondition] = useState(false);
  const scale_val = 1.92;

  const handleBack = () => {
    window.location = '/';
  };

  useEffect(() => {
    const getData = async () => {
      if (fileCode.substring(fileCode.length - 1) === '1') {
        setImageCondition(true);
      }
      try {
        const response = await axios.get(`http://localhost:5500/invoice/get_data/${fileName}`, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        setData(response.data['data']);
      } catch (error) {
        console.log('Error getting data', error);
      }
    };

    if (data.length === 0) {
      getData();
    }

    if (!imgCondition) {
      const loadingTask = pdfjsLib.getDocument(pdfUrl);
      loadingTask.promise.then((pdf) => {
        setNumPages(pdf.numPages);

        for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
          pdf.getPage(pageNumber).then((page) => {
            const viewport = page.getViewport({ scale: scale_val });
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
              canvasContext: context,
              viewport: viewport,
            };

            canvasContainerRef.current.appendChild(canvas);

            page.render(renderContext);
          });
        }
      });
    }
  }, [pdfUrl, fileCode, imgCondition, data.length]);

  return (
    <div>
      <div className="navbar">
        <button onClick={handleBack}>Back</button>
        <h1>Pdf Viewer</h1>
      </div>
      <div className="container">
        <div className="content">
          {data.length > 0 ? <InvoiceForm invoiceData={data} scale={scale_val}/> : <div className="loader">Loading...</div>}
        </div>
        {imgCondition ? (
          <div className="pdf-view">
            <img src={`http://localhost:5500/static/1/${fileCode}.JPEG`} alt="" style={{ height: '100%', width: '100%' }} />
          </div>
        ) : (
          <div className="pdf-view" ref={canvasContainerRef}></div>
        )}
      </div>
    </div>
  );
};

export default PdfViewer;
