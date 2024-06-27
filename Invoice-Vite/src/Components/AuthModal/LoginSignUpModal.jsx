import {
  CButton,
  CModal,
  CModalBody,
} from "@coreui/react";
import "@coreui/coreui/dist/css/coreui.min.css";

import { useState } from "react";
import LoginForm from "./LoginForm/LoginForm";
import "../../CSS/LoginSignUpModal.css";

const LoginSignUpModal = () => {
    const [visible, setVisible] = useState(false)
    return (
      <>
        <CButton color="primary" onClick={() => setVisible(!visible)}>Login</CButton>
        <CModal
          visible={visible}
          onClose={() => setVisible(false)}
        >
          <CModalBody style={{padding:"0"}}>
            <LoginForm/>
          </CModalBody>
        </CModal>
      </>
    )
};

export default LoginSignUpModal;
