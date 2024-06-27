import { useState } from "react";
import { Tabs, TabList, TabPanels, Tab, TabPanel } from "@chakra-ui/react";
import LoginForm from "../LoginForm/LoginForm";
import SignUpForm from "../SignUpForm/SignUpForm";

const LoginSignupTab = () => {
  const [tabIndex, setTabIndex] = useState(0);

  const handleTabsChange = (index) => {
    setTabIndex(index);
  };

  return (
    <Tabs 
      variant="soft-rounded" 
      colorScheme="green" 
      index={tabIndex} 
      onChange={handleTabsChange}
    >
      <TabList>
        <Tab>Login</Tab>
        <Tab>Sign Up</Tab>
      </TabList>
      <TabPanels>
        <TabPanel key={tabIndex === 0 ? 'login' : 'reset'}>
          <LoginForm />
        </TabPanel>
        <TabPanel key={tabIndex === 1 ? 'signup' : 'reset'}>
          <SignUpForm />
        </TabPanel>
      </TabPanels>
    </Tabs>
  );
}

export default LoginSignupTab;
