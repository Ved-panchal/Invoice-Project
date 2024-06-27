// src/components/Toast.js

import React from "react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const Toast = ({
  position = "top-right",
  autoClose = 5000,
  hideProgressBar = false,
  closeOnClick = true,
  pauseOnHover = true,
  draggable = true,
  progress = undefined,
}) => {
  return (
    <ToastContainer
      position={position}
      autoClose={autoClose}
      hideProgressBar={hideProgressBar}
      closeOnClick={closeOnClick}
      pauseOnHover={pauseOnHover}
      draggable={draggable}
      progress={progress}
      className="toast-container"
    />
  );
};

export const showToast = (message, type = "info") => {
  toast.dismiss();
  switch (type) {
    case "success":
      toast.success(message);
      break;
    case "error":
      toast.error(message);
      break;
    case "warn":
      toast.warn(message);
      break;
    case "info":
    default:
      toast.info(message);
      break;
  }
};

export default Toast;
