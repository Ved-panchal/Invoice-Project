import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast, { Toaster } from 'react-hot-toast';
// import api from '../utils/UserApi';
import api from '../utils/apiUtils';
import '../CSS/Signin.css'; // Import the CSS file

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
        // Create URLSearchParams object to encode data as application/x-www-form-urlencoded
        const params = new URLSearchParams();
        params.append('username', username);
        params.append('password', password);
  
        const response = await api.post('/auth/token', params.toString(), {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
  
        if (response) {
          localStorage.setItem('username', username);
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
      <div className="signin-container">
        <div className="signin-card">
          <h2 className="signin-title">Sign In</h2>
          <form onSubmit={handleSubmit} className="signin-form">
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={errors.username ? 'input-error' : ''}
              />
              {errors.username && <span className="error-message">{errors.username}</span>}
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={errors.password ? 'input-error' : ''}
              />
              {errors.password && <span className="error-message">{errors.password}</span>}
            </div>
            <button type="submit" className="signin-button">Sign In</button>
          </form>
        </div>
      </div>
    </>
  );
};

export default Signin;
