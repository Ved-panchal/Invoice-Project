import axios from "axios";
import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { Writable } from 'stream';
import Loader from "./Loader";

function UploadDocumentPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ".pdf, .jpg, .jpeg, .png, .docx",
  });

  const upload_pdf = async (file) => {
    try {
      const formData = new FormData();
      formData.append('document', file);
      // const response = await axios.get('http://localhost:5500/stream');
      // const response = await axios.post('http://localhost:5500/upload', formData, {
      //   headers: {
      //     'Content-Type': 'multipart/form-data',
      //   },
      // });
      return response;
    } catch (error) {
      console.log('error uploading', error);
      throw error;
    }
  };

  const setInitialFilesState = (files) => {
    let prevUploadedFiles = uploadedFiles;
    let newFiles = files.map((file) => ({
      pdfId: "Loading...",
      pdfName: file.name,
      pdfStatus: 'Pending'
    }));
    setUploadedFiles([...newFiles, ...prevUploadedFiles]);
    return [...newFiles, ...prevUploadedFiles];
  };
  


  const getApiResponse = async (file) => {
    try {
      let response = await upload_pdf(file);
      // const fileId = response.data.file_id;
      const fileId = response.data;
      return {
        pdfStatus: 'Completed',
        pdfId: fileId,
        pdfName: file.name
      };
    } catch (error) {
      console.error('Error uploading document:', error);
      return {
        pdfStatus: 'Exception',
        pdfId: 'cannot be extracted',
        pdfName: file.name
      };
    }
  };
  

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length > 0) {
      setLoading(true);
      let currstate = setInitialFilesState(files);
      try {
        for (let index = 0; index < files.length; index++) {
          const updatedFile = await getApiResponse(files[index]);
          currstate[index] = updatedFile;
          setUploadedFiles([...currstate]);
        }
        setLoading(false);
      } catch (error) {
        console.error("Error uploading documents:", error);
        setLoading(false);
      }
    } else {
      console.error("No files selected.");
    }
  };

  const handleDelete = (fileToDelete) => {
    setFiles(files.filter((file) => file !== fileToDelete));
  };

  useEffect(() => {
    const get_pdfs = async () => {
      let response = await axios.post("http://localhost:5500/get_pdfs", {
        userId: 1,
      });
      let data = response.data;
      setUploadedFiles(data);
    };
    get_pdfs();
  }, []);

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Upload Document</h1>
      <div style={styles.container}>
        <form onSubmit={handleSubmit} style={styles.form}>
          <div {...getRootProps({ style: styles.dropzone })}>
            <input {...getInputProps()} />
            {isDragActive ? (
              <p>Drop the files here ...</p>
            ) : (
              <p>
                Drag 'n' drop PDF, DOCX, or JPG files here, or click to select
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
                    onClick={() => handleDelete(file)}
                    style={styles.deleteButton}
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
          <button
            type="submit"
            disabled={files.length === 0 || loading}
            style={styles.button}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
        </form>
        <div className="pdfList">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Name</th>
                <th>ID</th>
              </tr>
            </thead>
            <tbody>
              {uploadedFiles.map((file, index) => (
                <tr key={`pdf-${index}`} onClick={() => {
                  window.open(`/my-documents/${file.pdfId}`, '_blank');
                }}>
                  <td>{file.pdfStatus}</td>
                  <td>{file.pdfName}</td>
                  <td>{file.pdfId}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
      {/* {loading && (
        <div style={styles.overlay}>
          <Loader />
        </div>
      )} */}
    </div>
  );
}

const styles = {
  page: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f7f7f7",
    padding: "20px",
    textAlign: "center",
  },
  heading: {
    marginBottom: "20px",
    fontSize: "50px",
  },
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    flex: 1,
    width: "100%",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    maxWidth: "700px",
  },
  dropzone: {
    width: "70vw",
    padding: "160px",
    borderWidth: "2px",
    borderColor: "#cccccc",
    borderStyle: "dashed",
    borderRadius: "5px",
    backgroundColor: "#ffffff",
    color: "#333333",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "10px",
  },
  fileDetailsContainer: {
    width: "100%",
    maxHeight: "200px",
    overflowY: "auto",
    marginBottom: "10px",
  },
  fileDetails: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: "5px",
    padding: "5px 10px",
    backgroundColor: "#e9e9e9",
    borderRadius: "5px",
  },
  fileName: {
    fontSize: "14px",
    marginRight: "10px",
  },
  deleteButton: {
    padding: "5px 10px",
    fontSize: "12px",
    cursor: "pointer",
  },
  button: {
    marginTop: "10px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
  },
  cancelButton: {
    marginTop: "10px",
    padding: "10px 20px",
    fontSize: "16px",
    cursor: "pointer",
    backgroundColor: "#dc3545",
    color: "#fff",
  },
  progressContainer: {
    width: "100%",
    backgroundColor: "#e0e0e0",
    borderRadius: "5px",
    marginTop: "10px",
  },
  progressBar: {
    height: "10px",
    backgroundColor: "#76c7c0",
    borderRadius: "5px",
  },
  status: {
    marginTop: "10px",
    fontSize: "14px",
    fontWeight: "bold",
  },
  overlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(255, 255, 255, 0.8)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999,
  },
};

export default UploadDocumentPage;
