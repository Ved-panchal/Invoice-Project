import { useState } from "react";
import Header from "../Components/Header/Header";
import { Outlet } from "react-router-dom";
import LoginSignUpModal from "../Components/AuthModal/LoginSignUpModal";

const HeaderLayout = () => {
  const [isOpen, setIsOpen] = useState(false);
  const openModal = () => setIsOpen(true);
  const closeModal = () => setIsOpen(false);

  return (
    <>
      <Header isOpen={isOpen} openModal={openModal} closeModal={closeModal} />
      <Outlet />
      <LoginSignUpModal
        isOpen={isOpen}
        openModal={openModal}
        closeModal={closeModal}
      />
    </>
  );
};

export default HeaderLayout;
