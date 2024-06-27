import {
    FormControl,
    FormLabel,
    FormErrorMessage,
    Input,
    Button,
  } from "@chakra-ui/react";
  import { useState } from "react";
  
  const SignUpForm = () => {
    const [username, setUsername] = useState("");
    const [email, setEmail] = useState("");
    const [mobile, setMobile] = useState("");
    const [password, setPassword] = useState("");
  
    const [isUserError, setIsUserError] = useState(false);
    const [isEmailError, setIsEmailError] = useState(false);
    const [isMobileError, setIsMobileError] = useState(false);
    const [isPassError, setIsPassError] = useState(false);
  
    const handleUserChange = (e) => {
      const value = e.target.value;
      setUsername(value);
      setIsUserError(!value);
    };
  
    const handleEmailChange = (e) => {
      const value = e.target.value;
      setEmail(value);
      setIsEmailError(!value || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(value));
    };
  
    const handleMobileChange = (e) => {
      const value = e.target.value;
      setMobile(value);
      setIsMobileError(!value || !/^\d{10}$/.test(value));
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
      if (!email || !/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(email)) {
        setIsEmailError(true);
        valid = false;
      }
      if (!mobile || !/^\d{10}$/.test(mobile)) {
        setIsMobileError(true);
        valid = false;
      }
      if (!password || password.length < 6 || password.length > 20) {
        setIsPassError(true);
        valid = false;
      }
      return valid;
    };
  
    const handleSubmit = (e) => {
      e.preventDefault();
      if (validateForm()) {
        console.log("Form submitted", { username, email, mobile, password });
      }
    };
  
    return (
      <form onSubmit={handleSubmit}>
        <FormControl isInvalid={isUserError} mb={4}>
          <FormLabel>Username</FormLabel>
          <Input type="text" value={username} onChange={handleUserChange} />
          {isUserError && <FormErrorMessage>Username is required.</FormErrorMessage>}
        </FormControl>
        <FormControl isInvalid={isEmailError} mb={4}>
          <FormLabel>Email</FormLabel>
          <Input type="email" value={email} onChange={handleEmailChange} />
          {isEmailError && <FormErrorMessage>Enter a valid email.</FormErrorMessage>}
        </FormControl>
        <FormControl isInvalid={isMobileError} mb={4}>
          <FormLabel>Mobile</FormLabel>
          <Input type="text" value={mobile} onChange={handleMobileChange} />
          {isMobileError && <FormErrorMessage>Enter a valid 10-digit mobile number.</FormErrorMessage>}
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
        <Button type="submit" colorScheme="blue">Sign Up</Button>
      </form>
    );
  };
  
  export default SignUpForm;
  