import React, { useEffect } from 'react';
import PdfViewer from './PdfViewer'; // Importing PdfViewer component
import { useParams } from 'react-router-dom';

const MyDocument = () => {
    // Extracting the 'fileName' parameter from the URL using useParams hook
    const { fileCode } = useParams();
    console.log(fileCode)
    if(fileCode){
        var fileName = fileCode.substring(0, fileCode.length - 1);
        let extension_bit = fileCode.substring(fileCode.length - 1);
        var extension;
        if(extension_bit == '0'){
            extension = 'pdf'
        }else if(extension_bit == '1'){
            extension = 'JPEG'
        }
    }
    return (
        <div>
            {/* 
                Render PdfViewer component only if 'fileName' is available
                Pass the PDF URL and file name as props to PdfViewer component
            */}
            {fileName && <PdfViewer pdfUrl={`http://localhost:5500/static/${fileCode}.${extension}`} fileName={fileName} fileCode={fileCode}/>}
        </div>
    );
};

export default MyDocument;

