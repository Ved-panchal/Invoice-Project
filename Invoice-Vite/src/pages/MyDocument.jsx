import { apiurl } from '../utils/config';
import PdfViewer from './PdfViewer'; // Importing PdfViewer component
import { useParams } from 'react-router-dom';

const MyDocument = () => {
    // Extracting the 'fileName' parameter from the URL using useParams hook
    const { fileCode } = useParams();
    const userId = localStorage.getItem('userId');
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
            {fileName && <PdfViewer pdfUrl={`http://${apiurl}/static/${userId}/${fileCode}.${extension}`} fileName={fileName} fileCode={fileCode}/>}
        </div>
    );
};

export default MyDocument;

