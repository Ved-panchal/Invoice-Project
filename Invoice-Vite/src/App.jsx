import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadInvoicePage from "./Components/UploadInvoicePage";
// import DisplayInvoiceDataPage from './Components/DisplayInvoiceDataPage';
import MyDocument from './Components/MyDocument';
import Loader from './Components/Loader';
import Temp from './Components/Temp';

function App() {
  return (
    <Router>
    <Routes>
        <Route path="/"  element={<UploadInvoicePage />} />
        <Route path="/temp"  element={<Temp />} />
        {/* <Route path="/invoice-details" element={<DisplayInvoiceDataPage />} /> */}
        <Route path="/my-documents/:fileCode" element={<MyDocument />} />
        <Route path="/loader" element={<div style={{
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  }}><Loader /></div>} />
    </Routes>
    </Router>
  )
}

export default App
