import React, { useState, useCallback, useRef } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';

function UploadDocumentPage() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle');
  const xhrRef = useRef(null);
  const navigate = useNavigate();

  const onDrop = useCallback((acceptedFiles) => {
    setFiles((prevFiles) => [...prevFiles, ...acceptedFiles]);
    setStatus('idle');
    setProgress(0);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg'],
    multiple: true,
  });

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (files.length > 0) {
      setLoading(true);
      setStatus('uploading');
      try {
        const formData = new FormData();
        files.forEach((file, index) => {
          formData.append(`document${index + 1}`, file);
        });

        const xhr = new XMLHttpRequest();
        xhrRef.current = xhr;
        xhr.open('POST', 'http://localhost:5500/api/extract', true);

        xhr.upload.onprogress = (event) => {
          if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            setProgress(percentComplete);
          }
        };

        xhr.onload = () => {
          if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            navigate('/invoice-details', { state: { invoiceData: response } });
            setStatus('completed');
          } else {
            console.error('Failed to upload documents.');
            setStatus('failed');
          }
          setLoading(false);
        };

        xhr.onerror = () => {
          console.error('Error uploading documents.');
          setLoading(false);
          setStatus('failed');
        };

        xhr.send(formData);
      } catch (error) {
        console.error('Error uploading documents:', error);
        setLoading(false);
        setStatus('failed');
      }
    } else {
      console.error('No files selected.');
    }
  };

  const handleCancel = () => {
    if (xhrRef.current) {
      xhrRef.current.abort();
      setLoading(false);
      setStatus('failed');
    }
  };

  const handleDelete = (fileToDelete) => {
    setFiles(files.filter((file) => file !== fileToDelete));
    setStatus('idle');
    setProgress(0);
  };

  const getStatusStyle = () => {
    switch (status) {
      case 'uploading':
        return styles.uploading;
      case 'processing':
        return styles.processing;
      case 'completed':
        return styles.completed;
      case 'failed':
        return styles.failed;
      default:
        return {};
    }
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
              <p>Drag 'n' drop PDF, DOCX, or JPG files here, or click to select them</p>
            )}
          </div>
          {files.length > 0 && (
            <div style={styles.fileDetailsContainer}>
              {files.map((file, index) => (
                <div key={index} style={styles.fileDetails}>
                  <p style={styles.fileName}>Selected File: {file.name}</p>
                  <button type="button" onClick={() => handleDelete(file)} style={styles.deleteButton}>
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
          <button type="submit" disabled={files.length === 0 || loading} style={styles.button}>
            {loading ? 'Uploading...' : 'Upload'}
          </button>
          {loading && (
            <button type="button" onClick={handleCancel} style={styles.cancelButton}>
              Cancel
            </button>
          )}
          <div style={{ ...styles.status, ...getStatusStyle() }}>
            {status === 'uploading' && 'Uploading...'}
            {status === 'processing' && 'Processing...'}
            {status === 'completed' && 'Completed'}
            {status === 'failed' && 'Failed'}
          </div>
          {loading && (
            <div style={styles.progressContainer}>
              <div style={{ ...styles.progressBar, width: `${progress}%` }} />
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

const styles = {
  page: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#f7f7f7',
    padding: '20px',
    textAlign: 'center',
  },
  heading: {
    marginBottom: '20px',
    fontSize: '2em',
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
    width: '100%',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%',
    maxWidth: '400px',
    padding: '10px',
  },
  dropzone: {
    width: '100%',
    height: '200px',
    padding: '40px',
    borderWidth: '2px',
    borderColor: '#cccccc',
    borderStyle: 'dashed',
    borderRadius: '5px',
    backgroundColor: '#ffffff',
    color: '#333333',
    textAlign: 'center',
    cursor: 'pointer',
    marginBottom: '10px',
    transition: 'all 0.2s ease-in-out',
  },
  fileDetailsContainer: {
    width: '100%',
    maxHeight: '200px',
    overflowY: 'auto',
    marginBottom: '10px',
  },
  fileDetails: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '5px',
    padding: '5px 10px',
    backgroundColor: '#e9e9e9',
    borderRadius: '5px',
  },
  fileName: {
    fontSize: '14px',
    marginRight: '10px',
  },
  deleteButton: {
    padding: '5px 10px',
    fontSize: '12px',
    cursor: 'pointer',
  },
  button: {
    marginTop: '10px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s ease',
  },
  cancelButton: {
    marginTop: '10px',
    padding: '10px 20px',
    fontSize: '16px',
    cursor: 'pointer',
    backgroundColor: '#dc3545',
    color: '#fff',
    transition: 'background-color 0.3s ease',
  },
  progressContainer: {
    width: '100%',
    backgroundColor: '#e0e0e0',
    borderRadius: '5px',
    marginTop: '10px',
  },
  progressBar: {
    height: '10px',
    backgroundColor: '#76c7c0',
    borderRadius: '5px',
  },
  status: {
    marginTop: '10px',
    fontSize: '14px',
    fontWeight: 'bold',
  },
  uploading: {
    color: '#ffa500',
  },
  processing: {
    color: '#007bff',
  },
  completed: {
    color: '#28a745',
  },
  failed: {
    color: '#dc3545',
  },
};

export default UploadDocumentPage;
