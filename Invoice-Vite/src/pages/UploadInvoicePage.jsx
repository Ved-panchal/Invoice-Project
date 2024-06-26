import { useState, useCallback, useEffect, useRef } from "react";
import { useDropzone } from "react-dropzone";
import { format, isValid } from "date-fns";
import Loader from "../Components/Loader/Loader";
import "../CSS/UploadInvocie.css";
import { useNavigate } from "react-router-dom";
import AnimatedButton from "../Components/AnimatedBtn/AnimatedButton";
import api from "../../utils/apiUtils";

const allowedFileTypes = ["application/pdf", "image/jpeg", "image/png"];

function UploadInvoicePage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);

  const onDrop = useCallback((acceptedFiles) => {
    const validFiles = acceptedFiles.filter(file => allowedFileTypes.includes(file.type));
    if (validFiles.length !== acceptedFiles.length) {
      setError("Please upload only PDF, JPEG, or PNG files.");
      return;
    }
    setFiles((prevFiles) => [...prevFiles, ...validFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: allowedFileTypes.join(","),
  });

  const uploadPdf = async () => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('documents', file));
      const userId = localStorage.getItem('userId');
      const response = await api.post(`/uploadFiles/${userId}`, formData, { // 2 is for user id when login is created then it should be replaced
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data.result;
    } catch (error) {
      console.log('error uploading', error);
      throw error;
    }
  };


  const fetchUploadedFiles = async () => {
    const userId = localStorage.getItem('userId');
    try {
      let response = await api.post(`/get_pdfs/${userId}`, { page: currentPage, count: 5 });
      let data = response.data;
      setUploadedFiles(data)
    } catch (error) {
      console.error("Error fetching uploaded files:", error);
      setError("Error fetching uploaded files. Please try again.");
    }
  };

  useEffect(() => {
    localStorage.setItem('userId',"2")
    const userId = localStorage.getItem('userId');

    const socket = new WebSocket(`ws://localhost:5500/ws/${userId}`);

    // Listen for messages from the WebSocket server
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("ws message",message)
      // Update the uploadedFiles state based on the received message
      setUploadedFiles((prevFiles) => {
        const index = prevFiles.findIndex((file) => file.id === message.id);
        if (index !== -1) {
          return [
            ...prevFiles.slice(0, index),
            { ...prevFiles[index], ...message },
            ...prevFiles.slice(index + 1),
          ];
        } else {
          return prevFiles;
        }
      });
    };

    return () => {
      socket.close();
    };
  }, []);

  useEffect(() => {
    fetchTotalPages();
    fetchUploadedFiles();
  }, [currentPage]);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };
  
  const renderPagination = () => {
    const pages = [];

    const createPageButton = (pageNumber) => (
      <button
        key={pageNumber}
        onClick={() => handlePageChange(pageNumber)}
        style={currentPage === pageNumber ? styles.activePageButton : styles.pageButton}
      >
        {pageNumber}
      </button>
    );

    const addEllipsis = (key) => (
      <span key={key} style={styles.ellipsis}>...</span>
    );

    if (currentPage >= 4) {
      pages.push(createPageButton(1));
      if(currentPage != 4){
        pages.push(addEllipsis("start-ellipsis"));
      }
    }

    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
      pages.push(createPageButton(i));
    }

    // Add last page and ellipsis if necessary
    if (currentPage <= totalPages - 3) {
      if (currentPage != totalPages - 3) {
        pages.push(addEllipsis("end-ellipsis"));
      }
      pages.push(createPageButton(totalPages));
    }

    if(pages.length === 0){
      return <h1 style={{color:"white"}}>Please Upload Pdfs!!</h1>
    }

    return pages;
  };

  const handleSubmit = async () => {
    // event.preventDefault();
    if (files.length > 0) {
      setError(null);
      try {
        setLoading(true);
        let newFiles =  await uploadPdf();
        setLoading(false);
        // setUploadedFiles((prevFiles) => [...newFiles, ...prevFiles]);
        fetchTotalPages();
        setCurrentPage(1);
        fetchUploadedFiles();
      } catch (error) {
        console.error("Error uploading document:", error);
        setError("Error uploading document. Please reload and try again.");
      }
      setFiles([]);
    } else {
      console.error("No files selected.");
      setError("No files selected. Please select files to upload.");
    }
  };

  const handleDelete = async (fileToDelete) => {
    try {
      // Only attempt to delete from the server if the file has been successfully uploaded
      if (fileToDelete.pdfId !== "cannot be extracted" && fileToDelete.pdfId !== "Loading..." && fileToDelete.id !== "") {
        await api.post("/delete_pdf", { fileId: fileToDelete.id });
      }
      setUploadedFiles((prevUploadedFiles) =>
        prevUploadedFiles.filter((file) => file.id !== fileToDelete.id)
      );
      if(uploadedFiles.length === 1){
        setCurrentPage(currentPage - 1);
        return;
      }
      fetchTotalPages();
      fetchUploadedFiles();
    } catch (error) {
      console.error("Error deleting document:", error);
      setError("Error deleting document. Please try again.");
    }
  };


  const formatDate = (date) => {
    if (!date || !isValid(new Date(date))) return "Invalid date";
    return format(new Date(date), "MMM dd, yyyy, hh:mm a");
  };


  const fetchTotalPages = async () => {
    const userId = localStorage.getItem('userId');
    try {
      const response = await api.get(`/get_total_pages/${userId}`);
      const totalPdfCount = response.data;
      setTotalPages(Math.ceil(totalPdfCount / 5)); // Assuming 5 PDFs per page
    } catch (error) {
      console.error("Error fetching total pages:", error);
      setError("Error fetching total pages. Please try again.");
    }
  };
  
  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Upload Document</h1>
      <div style={styles.container}>
        <form style={styles.form}>
          <div {...getRootProps({ style: styles.dropzone })}>
            <input {...getInputProps()} />
            {isDragActive ? (
              <p style={styles.whitefont}>Drop the files here ...</p>
            ) : (
              <p style={styles.whitefont}>
                Drag 'n' drop PDF, DOC or DOCX files here, or click to select
                them
              </p>
            )}
          </div>
          {files.length > 0 && (
            <div style={styles.fileDetailsContainer}>
              {files.map((file, index) => (
                <div key={index} style={styles.fileDetails}>
                  <p style={styles.fileName}>Selected File: {file.name}</p>
                  <button
                    type="button"
                    onClick={() => {
                      setFiles((prevFiles) =>
                        prevFiles.filter((f, i) => i !== index)
                      );
                    }}
                    style={styles.deleteButton}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
          {error && <p style={styles.error}>{error}</p>}
            <AnimatedButton submit={handleSubmit} isDisabled={(files.length === 0 || loading) ? true : false}/>
        </form>
        <div style={styles.tableContainer}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.tableHeader}>STATUS</th>
                <th style={styles.tableHeader}>FILE NAME</th>
                <th style={styles.tableHeader}>CREATED</th>
                <th style={styles.tableHeader}>APPROVALS</th>
                <th style={styles.tableHeader}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {uploadedFiles.map((file, index) => (
                <tr key={`pdf-${index}`} style={styles.tableRow}>
                  <td style={styles.tableCell}>
                    {file.pdfStatus === 'Pending' && <div style={styles.pendingStatus}><span>{file.pdfStatus}  </span><Loader /></div>}
                    {file.pdfStatus === 'Completed' && <div style={styles.completeStatus}>{file.pdfStatus}</div>}
                    {file.pdfStatus === 'Exception' && <div style={styles.exceptionStatus}>{file.pdfStatus}</div>}
                  </td>
                  <td style={styles.tableCell}>{file.pdfName}</td>
                  <td style={styles.tableCell}>{formatDate(file.createdAt)}</td>
                  <td style={styles.tableCell}>PENDING</td>
                  <td style={styles.tableCell}>
                    <div style={styles.actions}>
                    {/* {file.pdfStatus !== 'Pending' && ( */}
                      <button
                        style={styles.deleteButton}
                        onClick={() => handleDelete(file)}
                      >
                        Delete
                      </button>
                      {/* )} */}
                      {file.pdfStatus === 'Completed' && (
                        <button
                          style={styles.viewButton}
                          onClick={() =>
                            navigate(`/my-documents/${file.pdfId}`)
                          }
                        >
                          View
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div style={styles.paginationContainer}>
            {renderPagination()}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#2c3e50',
    padding: '20px',
    textAlign: 'center',
    // letter-spacing: 1px;
    letterSpacing:'1px',
    fontFamily: "'Poppins', sans-serif",
  },
  heading: {
    marginBottom: '20px',
    fontSize: '36px',
    fontWeight: 'bold',
    color: '#ecf0f1',
    fontFamily: "'Poppins', sans-serif",
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '80%',
    fontFamily: "'Poppins', sans-serif",
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%',
    maxWidth: '700px',
    fontFamily: "'Poppins', sans-serif",
  },
  dropzone: {
    width: '100%',
    padding: '60px',
    borderWidth: '2px',
    borderColor: '#7f8c8d',
    borderStyle: 'dashed',
    borderRadius: '5px',
    backgroundColor: '#34495e',
    color: '#fff',
    textAlign: 'center',
    cursor: 'pointer',
    marginBottom: '20px',
    fontFamily: "'Poppins', sans-serif",
  },
  whitefont: {
    color: '#ffffffaf',
    fontWeight: '600',
    fontFamily: "'Poppins', sans-serif",
  },
  fileDetailsContainer: {
    width: '100%',
    maxHeight: '200px',
    overflowY: 'auto',
    marginBottom: '10px',
    fontFamily: "'Poppins', sans-serif",
  },
  fileDetails: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '5px',
    padding: '5px 10px',
    backgroundColor: '#95a5a6',
    borderRadius: '5px',
    fontFamily: "'Poppins', sans-serif",
  },
  fileName: {
    fontSize: '14px',
    marginRight: '10px',
    color: '#2c3e50',
    fontFamily: "'Poppins', sans-serif",
  },
  deleteButton: {
    padding: '5px 10px',
    fontSize: '14px',
    backgroundColor: '#e74c3c',
    color: '#ecf0f1',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontFamily: "'Poppins', sans-serif",
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#028391',
    color: '#ecf0f1',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontFamily: "'Poppins', sans-serif",
  },
  error: {
    color: '#e74c3c',
    marginBottom: '10px',
    fontFamily: "'Poppins', sans-serif",
  },
  tableContainer: {
    marginTop: '20px',
    width: '100%',
    overflowX: 'auto',
    fontFamily: "'Poppins', sans-serif",
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    backgroundColor: '#34495e',
    fontFamily: "'Poppins', sans-serif",
  },
  tableHeader: {
    padding: '15px',
    // backgroundColor: '#028391',
    color: '#ecf0f1',
    fontFamily: "'Poppins', sans-serif",
    // border: '1px solid #16a085',
  },
  tableRow: {
    // borderBottom: '1px solid #16a085',
    fontFamily: "'Poppins', sans-serif",
  },
  tableCell: {
    padding: '15px',
    textAlign: 'center',
    color: '#ecf0f1',
    fontFamily: "'Poppins', sans-serif",
    // border: '1px solid #16a085',
  },
  completeStatus: {
    width:'100%',
    padding: '5px 10px',
    color: '#004208',
    borderRadius: '5px',
    fontWeight: '600',
    fontFamily: "'Poppins', sans-serif",
    backgroundColor: "#03C988"
  },
  pendingStatus: {
    width:'100%',
    padding: '5px 10px',
    color: '#004208',
    borderRadius: '5px',
    fontWeight: '600',
    fontFamily: "'Poppins', sans-serif",
    backgroundColor: '#FFC700'
  },
  exceptionStatus: {
    width:'100%',
    padding: '5px 10px',
    color: '#4E150C',
    borderRadius: '5px',
    fontWeight: '600',
    fontFamily: "'Poppins', sans-serif",
    backgroundColor: '#F05941'
  },
  actions: {
    display: 'flex',
    justifyContent: 'center',
    gap: '10px',
    fontFamily: "'Poppins', sans-serif",
  },
  viewButton: {
    padding: '5px 10px',
    fontSize: '14px',
    backgroundColor: '#27ae60',
    color: '#ecf0f1',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontFamily: "'Poppins', sans-serif",
  },
  paginationContainer: {
    display: 'flex',
    justifyContent: 'center',
    margin: '20px 0 15px 0',
  },
  pageButton: {
    padding: '5px 10px',
    margin: '0 5px',
    cursor: 'pointer',
    backgroundColor: '#34495e',
    color: '#ecf0f1',
    border: 'none',
    borderRadius: '5px',
  },
  activePageButton: {
    padding: '5px 10px',
    margin: '0 5px',
    cursor: 'pointer',
    backgroundColor: '#ecf0f1',
    color: '#34495e',
    border: 'none',
    borderRadius: '5px',
  },
  ellipsis: {
    padding: '5px 10px',
    margin: '0 5px',
    color: '#ecf0f1',
  },

};

export default UploadInvoicePage;
