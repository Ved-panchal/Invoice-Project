/* eslint-disable react/prop-types */
import { useEffect, useRef, useState } from 'react';
import * as pdfjsLib from 'pdfjs-dist';
import 'pdfjs-dist/web/pdf_viewer.css';
import axios from 'axios';
import InvoiceForm from '../Components/InvoiceForm/InvoiceForm';
import '../CSS/PdfViewer.css';
import { useNavigate } from 'react-router-dom';

pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.js`;

const PdfViewer = ({ pdfUrl, fileName, fileCode }) => {
  const canvasContainerRef = useRef(null);
  const [numPages, setNumPages] = useState(0);
  const [data, setData] = useState([]);
  const [imgCondition, setImageCondition] = useState(false);
  const navigate = useNavigate();
  const scale_val = 1.9;

  const handleBack = () => {
    navigate('/')
  };

  const handleApprove = async () => {
    try {
      // Send the approval status to the server
      await axios.post('http://localhost:5500/invoice/approve', { fileName });
      alert('Invoice approved');
    } catch (error) {
      console.error('Error approving invoice', error);
    }
  };

  const handleReject = async () => {
    try {
      // Send the rejection status to the server
      await axios.post('http://localhost:5500/invoice/reject', { fileName });
      alert('Invoice rejected');
    } catch (error) {
      console.error('Error rejecting invoice', error);
    }
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
          <div className="action-buttons">
            <button className="approve-btn" onClick={handleApprove}>Approve</button>
            <button className="reject-btn" onClick={handleReject}>Reject</button>
          </div>
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
