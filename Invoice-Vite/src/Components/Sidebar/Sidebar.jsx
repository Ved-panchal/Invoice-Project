import {
  CSidebar,
  CSidebarHeader,
  CSidebarBrand,
  CSidebarNav,
  CNavItem,
  CBadge,
  CSidebarFooter,
} from "@coreui/react";
import "@coreui/coreui/dist/css/coreui.min.css";
import CIcon from "@coreui/icons-react";
import { cilSettings } from "@coreui/icons";
import styles from "../../CSS/sidebar.module.css";
import logo from "../../assets/Logo.png";
import Upload from "../../assets/Upload-logo.png";
import Prompt from "../../assets/Prompt.png";

const Sidebar = () => {
  return (
    <CSidebar size="lg" unfoldable={true} className={styles.sidebar}>
      <CSidebarHeader className="border-bottom">
        <CSidebarBrand>
          <img className={styles.imgmainlogo} src={logo} alt="Logo" />
        </CSidebarBrand>
      </CSidebarHeader>
      <CSidebarNav>
        <CNavItem  href="/Uploadinvoice" style={{ fontWeight: "600" }}>
          <div style={{ marginRight: "2rem" }}>
            <img className={styles.navicons} src={Upload} alt="Upload" />
          </div>
          Upload Invoice
        </CNavItem>
        <CNavItem
          href="/customprompt"
          style={{ fontWeight: "600" }}
        >
          <div style={{ marginRight: "2rem" }}>
            <img className={styles.navicons} src={Prompt} alt="Prompt" />
          </div>
          Custom Prompt <CBadge color="warning ms-auto">Upcoming</CBadge>
        </CNavItem>
      </CSidebarNav>
    </CSidebar>
  );
};

export default Sidebar;