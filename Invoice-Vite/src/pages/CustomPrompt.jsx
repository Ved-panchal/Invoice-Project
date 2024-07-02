import React, { useState, useEffect } from "react";
import api from "../utils/apiUtils";

function CustomPrompt() {
  const [directFields, setDirectFields] = useState([]);
  const [tableFields, setTableFields] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFields = async () => {
      try {
        const response = await api.get(`/get_fields`);
        console.log("response", response);
        const data = response.data.fields;
        const { direct, table } = formatFields(data);
        setDirectFields(direct);
        setTableFields(table);
      } catch (error) {
        console.error("Error fetching fields:", error);
        setError("Error fetching fields. Please try again.");
      }
    };

    fetchFields();
  }, []);

  useEffect(() => {
    if (error != null) {
      alert(error);
      setError(null);
    }
  }, [error]);

  const formatFields = (fieldsData) => {
    const directFields = Object.entries(fieldsData)
      .filter(([key, value]) => typeof value === "string")
      .map(([key, value]) => ({ name: key, description: value }));

    const tableFields = Object.entries(fieldsData.DocumentLines || {}).map(
      ([key, value]) => ({ name: key, description: value })
    );

    return { direct: directFields, table: tableFields };
  };

  const handleAddDirectField = () => {
    const newField = { name: "", description: "" };
    setDirectFields([...directFields, newField]);
  };

  const handleAddTableField = () => {
    const newField = { name: "", description: "" };
    setTableFields([...tableFields, newField]);
  };

  const handleFieldChange = (index, key, value, isTableField) => {
    const updatedFields = isTableField ? [...tableFields] : [...directFields];
    updatedFields[index][key] = value;
    isTableField ? setTableFields(updatedFields) : setDirectFields(updatedFields);
  };

  const handleDeleteField = (index, isTableField) => {
    const updatedFields = isTableField ? [...tableFields] : [...directFields];
    updatedFields.splice(index, 1);
    isTableField ? setTableFields(updatedFields) : setDirectFields(updatedFields);
  };

  const handleSave = async () => {
    const allFields = [...directFields, ...tableFields];
    for (let field of allFields) {
      if (!field.name || field.name.length > 15 || !field.description || field.description.length > 100) {
        setError("Field name must not exceed 15 characters and description must not exceed 100 characters.");
        return;
      }
    }

    try {
      const formattedData = formatDataForApi();
      console.log("formattedData", formattedData);
      await api.post(`/update_fields`, { fields: formattedData });
      setError(null);
      alert("Fields updated successfully!");
    } catch (error) {
      console.error("Error saving fields:", error);
      setError("Error saving fields. Please try again.");
    }
  };

  const formatDataForApi = () => {
    const direct = directFields.reduce((acc, field) => {
      acc[field.name] = field.description;
      return acc;
    }, {});

    const table = tableFields.reduce((acc, field) => {
      acc[field.name] = field.description;
      return acc;
    }, {});

    return { ...direct, DocumentLines: table };
  };

  return (
    <div style={styles.page}>
      <h1 style={styles.heading}>Manage Fields</h1>
      <div style={styles.container}>
        <div style={styles.fieldList}>
          <h2 style={styles.subHeading}>Direct Fields</h2>
          {directFields.map((field, index) => (
            <div key={index} style={styles.fieldItem}>
              <input
                type="text"
                value={field.name}
                onChange={(e) => handleFieldChange(index, "name", e.target.value, false)}
                style={styles.input}
              />
              <input
                type="text"
                value={field.description}
                onChange={(e) => handleFieldChange(index, "description", e.target.value, false)}
                style={styles.input}
              />
              <button onClick={() => handleDeleteField(index, false)} style={styles.deleteButton}>
                Delete
              </button>
            </div>
          ))}
        </div>

        <div style={styles.fieldForm}>
          <button onClick={handleAddDirectField} style={styles.button}>
            Add Direct Field
          </button>
        </div>

        <div style={styles.fieldList}>
          <h2 style={styles.subHeading}>Table Fields</h2>
          {tableFields.map((field, index) => (
            <div key={index} style={styles.fieldItem}>
              <input
                type="text"
                value={field.name}
                onChange={(e) => handleFieldChange(index, "name", e.target.value, true)}
                style={styles.input}
              />
              <input
                type="text"
                value={field.description}
                onChange={(e) => handleFieldChange(index, "description", e.target.value, true)}
                style={styles.input}
              />
              <button onClick={() => handleDeleteField(index, true)} style={styles.deleteButton}>
                Delete
              </button>
            </div>
          ))}
        </div>

        <div style={styles.fieldForm}>
          <button onClick={handleAddTableField} style={styles.button}>
            Add Table Field
          </button>
        </div>

        <button onClick={handleSave} style={styles.saveButton}>
          Save
        </button>
      </div>
    </div>
  );
}

const styles = {
  page: {
    width: "100vw",
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#2c3e50',
    padding: '20px',
    textAlign: 'center',
    letterSpacing: '1px',
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
  subHeading: {
    marginBottom: '10px',
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#ecf0f1',
    fontFamily: "'Poppins', sans-serif",
  },
  fieldForm: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    width: '100%',
    maxWidth: '700px',
    fontFamily: "'Poppins', sans-serif",
    marginBottom: '20px',
  },
  input: {
    padding: '10px',
    marginBottom: '10px',
    width: '80%',
    maxWidth: '400px',
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
    margin: '10px',
  },
  saveButton: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#27ae60',
    color: '#ecf0f1',
    border: 'none',
    borderRadius: '5px',
    cursor: 'pointer',
    fontFamily: "'Poppins', sans-serif",
    margin: '10px',
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
  error: {
    color: '#e74c3c',
    marginBottom: '10px',
    fontFamily: "'Poppins', sans-serif",
  },
  fieldList: {
    width: '100%',
    fontFamily: "'Poppins', sans-serif",
  },
  fieldItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px',
    marginBottom: '10px',
    backgroundColor: '#34495e',
    borderRadius: '5px',
    color: '#ecf0f1',
    fontFamily: "'Poppins', sans-serif",
  },
};

export default CustomPrompt
