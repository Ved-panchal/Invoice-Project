import React, { useEffect, useState } from 'react';
import { Document, Page } from 'react-pdf';
import { pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import "./CSS/PdfViewer.css";
import InvoiceForm from './InvoiceForm';
import axios from 'axios';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.js`;

const PdfViewer = ({ pdfUrl, fileName , fileCode}) => {
    // State variables to manage PDF viewing
    const [numPages, setNumPages] = useState(null); // Total number of pages in the PDF
    const [data, setData] = useState([]); // Data fetched from the server
    const [img_condition, setImage_condition] = useState(false); // Condition to render an image instead of a PDF

    // Callback function triggered when the PDF document is loaded successfully
    const onDocumentLoadSuccess = ({ numPages }) => {
        setNumPages(numPages);
    };

    const handleBack = () => {
        window.location = '/'; 
    };

    useEffect(() => {
        
        // Function to fetch data from the server
        const getData = async () => {
            console.log('hello');
            // Checking if the extension bit is set 
            if (fileCode.substring(fileCode.length - 1) === '1') {
                setImage_condition(true); // If the file is an image, set the image condition to true
            }
            try {
                const response = await axios.get(`http://localhost:5500/invoice/get_data/${fileName}`, {
                    headers: {
                        "Content-Type": 'application/json'
                    }
                });
                setData(response.data["data"]);
                console.log('babu',response)
            } catch (error) {
                console.log("error getting data", error);
            }
        };
        if(data.length === 0){
             getData(); // Call the function to fetch data when the component mounts
        }
    }, []); // Empty dependency array ensures this runs only once

    // Render the component
    return (
        <div>
            {/* Navigation bar */}
            <div className="navbar">
                <button onClick={handleBack}>Back</button>
                <h1>Pdf Viewer</h1>
            </div>
            <div className="container">
                <div className="content">
                    {data.length > 0 ? <InvoiceForm invoiceData={data} /> : <div className="loader">Loading...</div>}
                </div>
                {img_condition ? (
                    <div className='pdf-view'>
                        <img src={`http://localhost:5500/static/${fileCode}.JPEG` } alt="" style={{ height: "100%", width: "100%" }} />{
                        }
                    </div>
                ) : (
                    <div className="pdf-view">
                        <Document className="InvoiceView" file={pdfUrl} onLoadSuccess={onDocumentLoadSuccess}>
                            {Array.from(new Array(numPages), (el, index) => (
                                <Page key={`page_${index + 1}`} pageNumber={index + 1} />
                            ))}
                        </Document>
                    </div>
                )}
            </div>
        </div>
    );
};

export default PdfViewer;

