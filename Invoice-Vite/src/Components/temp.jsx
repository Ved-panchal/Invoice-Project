import axios from "axios";
import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { format, isValid } from "date-fns";

function Temp() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [error, setError] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: "application/pdf, image/jpeg, image/png",
  });

  const delay = () => {
    return new Promise((resolve) => {
      setTimeout(resolve, 5000);
    });
  };

  const upload_pdf = async (file) => {
    try {
      const formData = new FormData();
      formData.append("document", file);
      const response = await axios.post(
        "http://localhost:5500/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      await delay();
      return response;
    } catch (error) {
      console.error("Error uploading document:", error);
      throw error;
    }
  };

  const setInitialFilesState = (files) => {
    const newFiles = files.map((file) => ({
      pdfId: "Loading...",
      pdfName: file.name,
      pdfStatus: "Pending",
      createdAt: new Date(),
    }));
    setUploadedFiles((prevUploadedFiles) => [
      ...newFiles,
      ...prevUploadedFiles,
    ]);
    return [...newFiles, ...uploadedFiles];
  };

  const getApiResponse = async (file) => {
    try {
      const response = await upload_pdf(file);
      const fileId = response.data;
      return {
        pdfStatus: "Completed",
        pdfId: fileId,
        pdfName: file.name,
        createdAt: new Date(),
      };
    } catch (error) {
      return {
        pdfStatus: "Exception",
        pdfId: "cannot be extracted",
        pdfName: file.name,
        createdAt: new Date(),
      };
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length > 0) {
      setLoading(true);
      setError(null);
      const initialFilesState = setInitialFilesState(files);
      for (let index = 0; index < files.length; index++) {
        try {
          const updatedFile = await getApiResponse(files[index]);
          initialFilesState[index] = updatedFile;
          setUploadedFiles([...initialFilesState]);
        } catch (error) {
          console.error("Error uploading document:", error);
          setError("Error uploading document. Please try again.");
        }
      }
      setLoading(false);
      setFiles([]);
    } else {
      console.error("No files selected.");
      setError("No files selected. Please select files to upload.");
    }
  };

  const handleDelete = async (fileToDelete) => {
    try {
      // Only attempt to delete from the server if the file has been successfully uploaded
      if (fileToDelete.pdfId !== "cannot be extracted" && fileToDelete.pdfId !== "Loading...") {
        await axios.post("http://localhost:5500/delete", { fileId: fileToDelete.pdfId });
      }
      setUploadedFiles((prevUploadedFiles) =>
        prevUploadedFiles.filter((file) => file.pdfId !== fileToDelete.pdfId)
      );
    } catch (error) {
      console.error("Error deleting document:", error);
      setError("Error deleting document. Please try again.");
    }
  };

  useEffect(() => {
    const fetchUploadedFiles = async () => {
    localStorage.setItem('user_id', '2');
    const user_id = localStorage.getItem('user_id');
    try {
      let response = await axios.get(`http://localhost:5500/get_pdfs/${user_id}`);
      let data = response.data;
      setUploadedFiles(data);
    } catch (error) {
      console.error("Error fetching uploaded files:", error);
      setError("Error fetching uploaded files. Please try again.");
    }};

    fetchUploadedFiles();
  }, []);

  const formatDate = (date) => {
    if (!date || !isValid(new Date(date))) return "Invalid date";
    return format(new Date(date), "MMM dd, yyyy, hh:mm a");
  };

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
                Drag 'n' drop PDF, JPEG, or PNG files here, or click to select
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
          <button
            type="submit"
            disabled={files.length === 0 || loading}
            style={styles.button}
          >
            {loading ? "Uploading..." : "Upload"}
          </button>
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
                    <span
                      style={{
                        ...styles.status,
                        backgroundColor:
                          file.pdfStatus === "Completed"
                            ? "#28a745"
                            : file.pdfStatus === "Pending"
                            ? "#ffc107"
                            : "#dc3545",
                      }}
                    >
                      {file.pdfStatus}
                    </span>
                  </td>
                  <td style={styles.tableCell}>{file.pdfName}</td>
                  <td style={styles.tableCell}>{formatDate(file.createdAt)}</td>
                  <td style={styles.tableCell}>PENDING</td>
                  <td style={styles.tableCell}>
                    <div style={styles.actions}>
                      <button
                        style={styles.deleteButton}
                        onClick={() => handleDelete(file)}
                      >
                        Delete
                      </button>
                      {file.pdfStatus === "Completed" && (
                        <button
                          style={styles.viewButton}
                          onClick={() =>
                            window.open(`/my-documents/${file.pdfId}`, "_blank")
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
        </div>
      </div>
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
    fontSize: "36px",
    fontWeight: "bold",
  },
  container: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "80%",
  },
  form: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    width: "100%",
    maxWidth: "700px",
  },
  dropzone: {
    width: "100%",
    padding: "60px",
    borderWidth: "2px",
    borderColor: "#cccccc",
    borderStyle: "dashed",
    borderRadius: "5px",
    backgroundColor: "#ffffff",
    color: "#333333",
    textAlign: "center",
    cursor: "pointer",
    marginBottom: "20px",
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
    fontSize: "14px",
    backgroundColor: "#dc3545",
    color: "#ffffff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  button: {
    padding: "10px 20px",
    fontSize: "16px",
    backgroundColor: "#007bff",
    color: "#ffffff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
  error: {
    color: "#dc3545",
    marginBottom: "10px",
  },
  tableContainer: {
    marginTop: "20px",
    width: "100%",
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    backgroundColor: "#ffffff",
  },
  tableHeader: {
    padding: "10px",
    backgroundColor: "#007bff",
    color: "#ffffff",
    border: "1px solid #dddddd",
  },
  tableRow: {
    borderBottom: "1px solid #dddddd",
  },
  tableCell: {
    padding: "10px",
    textAlign: "center",
    border: "1px solid #dddddd",
  },
  status: {
    padding: "5px 10px",
    color: "#ffffff",
    borderRadius: "5px",
  },
  actions: {
    display: "flex",
    justifyContent: "center",
    gap: "10px",
  },
  viewButton: {
    padding: "5px 10px",
    fontSize: "14px",
    backgroundColor: "#28a745",
    color: "#ffffff",
    border: "none",
    borderRadius: "5px",
    cursor: "pointer",
  },
};

export default Temp;
