import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from "./Components/Sidebar/Sidebar";
import UploadInvoicePage from "./pages/UploadInvoicePage";
import MyDocument from './pages/MyDocument';
import Loader from './Components/Loader/Loader';
import Header from './Components/Header/Header';
import Home from './pages/Home';  
import './App.css';
import CustomPrompt from './pages/CustomPrompt';

const App = () => {
  return (
    <Router>
      <div className="app-container">
        <ConditionalSidebar />
        <div className="main-content">
          <ConditionalHeader />
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/uploadinvoice" element={<UploadInvoicePage />} />
            <Route path="/customprompt" element={<CustomPrompt />} />
            <Route path="/my-documents/:fileCode" element={<MyDocument />} />
            <Route path="/loader" element={
              <div style={{
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
              }}>
                <Loader />
              </div>
            } />
          </Routes>
        </div>
      </div>
    </Router>
  );
};

const ConditionalSidebar = () => {
  const location = useLocation();
  return (location.pathname !== "/") && (location.pathname !== "/Docs") && (location.pathname !== "/AboutUs") && (location.pathname !== "/Contact") && (!location.pathname.includes("my-documents")) ? <Sidebar /> : null;
};

const ConditionalHeader = () => {
  const location = useLocation();
  return location.pathname === "/" ? <Header /> : null;
};

export default App;
