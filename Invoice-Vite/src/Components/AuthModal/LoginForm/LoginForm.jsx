import {
  FormControl,
  FormLabel,
  FormErrorMessage,
  Input,
  Button,
} from "@chakra-ui/react";
import { useState } from "react";
import api from "../../../utils/apiUtils";
import { showToast } from "../../../services/toasts";
import { useNavigate } from "react-router-dom";

const LoginForm = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isUserError, setIsUserError] = useState(false);
  const [isPassError, setIsPassError] = useState(false);
  const navigate = useNavigate();

  const handleUserChange = (e) => {
    const value = e.target.value;
    setUsername(value);
    setIsUserError(!value);
  };

  const handlePassChange = (e) => {
    const value = e.target.value;
    setPassword(value);
    setIsPassError(!value || value.length < 6 || value.length > 20);
  };

  const validateForm = () => {
    let valid = true;
    if (!username) {
      setIsUserError(true);
      valid = false;
    }
    if (!password || password.length < 6 || password.length > 20) {
      setIsPassError(true);
      valid = false;
    }
    return valid;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        const params = new URLSearchParams();
        params.append("username", username);
        params.append("password", password);

        const response = await api.post("/auth/token", params.toString(), {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        });

        if (response) {
          localStorage.setItem("userId", response.data["userId"]);
          showToast("Login Successfull!", "success");
          setTimeout(() => {
            navigate("/uploadinvoice");
          }, 2000);
        } else {
          showToast("Login failed. Please check your credentials.","error")
        }
      } catch (error) {
        showToast("Login failed. Please check your credentials.","error")
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <FormControl isInvalid={isUserError} mb={4}>
        <FormLabel>Username</FormLabel>
        <Input type="text" value={username} onChange={handleUserChange} />
        {isUserError && (
          <FormErrorMessage>Username is required.</FormErrorMessage>
        )}
      </FormControl>
      <FormControl isInvalid={isPassError} mb={4}>
        <FormLabel>Password</FormLabel>
        <Input type="password" value={password} onChange={handlePassChange} />
        {isPassError && (
          <FormErrorMessage>
            Password is required and must be between 6 and 20 characters.
          </FormErrorMessage>
        )}
      </FormControl>
      <Button type="submit" colorScheme="blue">
        Login
      </Button>
    </form>
  );
};

export default LoginForm;
