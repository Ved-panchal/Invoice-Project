import axios from "axios";
import { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";

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

  useEffect(() => {
    localStorage.setItem('user_id', '2');
    const user_id = localStorage.getItem('user_id');
    const get_pdfs = async () => {
      let response = await axios.get(`http://localhost:5500/get_pdfs/${user_id}`);
      let data = response.data;
      setUploadedFiles(data);
    };
    get_pdfs();
  }, []);

  useEffect(() => {
    const user_id = localStorage.getItem('user_id');

    const socket = new WebSocket(`ws://localhost:5500/ws/${user_id}`);

    // Listen for messages from the WebSocket server
    socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      console.log("ws message",message)
      // Update the uploadedFiles state based on the received message
      // setUploadedFiles((prevFiles) => {
      //   const index = prevFiles.findIndex((file) => file.pdfName === message.pdfName);
      //   if (index !== -1) {
      //     return [
      //       ...prevFiles.slice(0, index),
      //       { ...prevFiles[index], ...message },
      //       ...prevFiles.slice(index + 1),
      //     ];
      //   } else {
      //     return prevFiles;
      //   }
      // });
    };

    // Cleanup function to close WebSocket connection when component unmounts
    return () => {
      socket.close();
    };
  }, []);

  const upload_pdf = async (files) => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('documents', file));
      const user_id = localStorage.getItem('user_id');
      const response = await axios.post(`http://localhost:5500/uploadFiles/${user_id}`, formData, { // 2 is for user id when login is created then it should be replaced
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      // console.log("response", response)
      return response.data.result;
    } catch (error) {
      console.log('error uploading', error);
      throw error;
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length > 0) {
      setLoading(true);


      // Add files to uploadedFiles with status "Pending"
      const newFiles = files.map((file) => ({
        pdfId: "Loading...",
        pdfName: file.name,
        pdfStatus: "Pending"
      }));
      setUploadedFiles((prevFiles) => [...newFiles, ...prevFiles]);

      try {
        const response = await upload_pdf(files);
        console.log("Files uploaded successfully:", response.data);
      } catch (error) {
        console.error("Error uploading documents:", error);
      } finally {
        setLoading(false);
      }
    } else {
      console.error("No files selected.");
    }
  };

  const handleDelete = (fileToDelete) => {
    setFiles(files.filter((file) => file !== fileToDelete));
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
              {uploadedFiles.map((uploadedFile, index) => (
                <tr
                  key={`pdf-${index}`}
                  onClick={() => {
                    window.open(`/my-documents/${uploadedFile.pdfId}`, '_blank');
                  }}
                >
                  <td>{uploadedFile.pdfStatus}</td>
                  <td>{uploadedFile.pdfName}</td>
                  <td>{uploadedFile.pdfId}</td>
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
};

export default UploadDocumentPage;
