import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
import api from '../utils/apiUtils';

const Signin = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    const isRedirected = localStorage.getItem('Failed');
    if (isRedirected) {
      toast.error("Not authorized without signing in.");
      localStorage.removeItem('Failed');
    }
  }, []);

  const validate = () => {
    const errors = {};
    if (!username || username.length < 6 || username.length > 12 || /\s/.test(username)) {
      errors.username = "Username must be 6-12 characters long and contain no spaces.";
    }
    if (!password || password.length < 6 || password.length > 12 || /\s/.test(password)) {
      errors.password = "Password must be 6-12 characters long and contain no spaces.";
    }
    return errors;
  };



  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      try {
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
  
        const response = await api.post('/auth/token', params.toString(), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
  
        if (response) {
          localStorage.setItem('userId', response.data['userId']);
          toast.success("Login successful!");
          setTimeout(() => {
            navigate('/');
          }, 2000);
        } else {
          toast.error("Login failed. Please check your credentials.");
        }
      } catch (error) {
        toast.error("Login failed. Please check your credentials.");
      }
    }
  };
  

  return (
    <>
      <Toaster />
      <div style={styles.signinContainer}>
        <div style={styles.signinCard}>
          <h2 style={styles.signinTitle}>Sign In</h2>
          <form onSubmit={handleSubmit} style={styles.signinForm}>
            <div style={styles.formGroup}>
              <label htmlFor="username" style={styles.formGroupLabel}>Username</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={errors.username ? { ...styles.formGroupInput, ...styles.formGroupInputError } : styles.formGroupInput}
              />
              {errors.username && <span style={styles.errorMessage}>{errors.username}</span>}
            </div>
            <div style={styles.formGroup}>
              <label htmlFor="password" style={styles.formGroupLabel}>Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={errors.password ? { ...styles.formGroupInput, ...styles.formGroupInputError } : styles.formGroupInput}
              />
              {errors.password && <span style={styles.errorMessage}>{errors.password}</span>}
            </div>
            <button type="submit" style={styles.signinButton}>Sign In</button>
          </form>
        </div>
      </div>
    </>
  );
};


const styles = {
  signinContainer: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100vh',
    backgroundColor: '#242424',
  },
  signinCard: {
    backgroundColor: '#333',
    padding: '2rem',
    borderRadius: '8px',
    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
    width: '100%',
    maxWidth: '400px',
    textAlign: 'center',
  },
  signinTitle: {
    color: 'rgba(255, 255, 255, 0.87)',
    fontSize: '1.5rem',
    marginBottom: '1rem',
  },
  signinForm: {
    display: 'flex',
    flexDirection: 'column',
  },
  formGroup: {
    marginBottom: '1rem',
    textAlign: 'left',
  },
  formGroupLabel: {
    color: 'rgba(255, 255, 255, 0.87)',
    display: 'block',
    marginBottom: '0.5rem',
  },
  formGroupInput: {
    width: '98%',
    padding: '0.5rem',
    border: '1px solid #555',
    borderRadius: '4px',
    backgroundColor: '#444',
    color: 'rgba(255, 255, 255, 0.87)',
  },
  formGroupInputError: {
    borderColor: 'red',
  },
  errorMessage: {
    color: 'red',
    fontSize: '0.875rem',
  },
  signinButton: {
    marginTop: '1rem',
    padding: '0.75rem',
    backgroundColor: '#1e90ff',
    color: 'rgba(255, 255, 255, 0.87)',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  signinButtonHover: {
    backgroundColor: '#1c7ed6',
  },
};



export default Signin;
