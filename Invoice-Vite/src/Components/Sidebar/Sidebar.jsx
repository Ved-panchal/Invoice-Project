import React from "react";
import {
  IconButton,
  Typography,
  List,
  ListItem,
  ListItemPrefix,
  ListItemSuffix,
  Alert,
  Drawer,
  Card,
} from "@material-tailwind/react";
import {
  Cog6ToothIcon,
  PowerIcon,
} from "@heroicons/react/24/solid";
import {
  CubeTransparentIcon,
  Bars3Icon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import "./Sidebar.css"
import Logo from "../../assets/Logo.png"
import Uploadlogo from "../../assets/Upload-logo.png"
import Promptlogo from "../../assets/Prompt.png"
import { useNavigate } from "react-router-dom";
import api from "../../utils/apiUtils";
import showToast from "../../services/toast";

const Sidebar = () => {
  const [open, setOpen] = React.useState(0);
  const [openAlert, setOpenAlert] = React.useState(true);
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(false);
  const navigate = useNavigate();

  // const handleOpen = (value) => {
  //   setOpen(open === value ? 0 : value);
  // };

  const handlelogout = async() => {
    const res = await api.post("/auth/logout")
    if(res.data){
      showToast({message:res.data.message,type:"success"})
    }
    setTimeout(() => {
      navigate("/")
    }, 1500);
  }

  const openDrawer = () => setIsDrawerOpen(true);
  const closeDrawer = () => setIsDrawerOpen(false);

  return (
    <>
      <IconButton className="burgerbtn" variant="text" size="lg" onClick={openDrawer}>
        {isDrawerOpen ? (
          <XMarkIcon className="h-8 w-8 stroke-2" />
        ) : (
          <Bars3Icon className="h-8 w-8 stroke-2" />
        )}
      </IconButton>
      <Drawer open={isDrawerOpen} onClose={closeDrawer}>
        <Card
          color="transparent"
          shadow={false}
          className="h-[calc(100vh-2rem)] w-full p-4"
        >
          <div className="mb-2 flex items-center gap-4 p-4">
            <img
              src={Logo}
              alt="brand"
              className="h-8 w-8"
            />
            <Typography variant="h5" color="blue-gray">
              Invoice Extractor
            </Typography>
          </div>
          <List>  
            <ListItem onClick={() => navigate("/profile/uploadinvoice")}>
              <ListItemPrefix>
                <img src={Uploadlogo} className="h-5 w-5"/>
              </ListItemPrefix>
              Upload Invoice
              <ListItemSuffix>
              </ListItemSuffix>
            </ListItem>
            <ListItem onClick={() => navigate("/profile/customprompt")}>
              <ListItemPrefix>
              <img src={Promptlogo} className="h-5 w-5"/>
              </ListItemPrefix>
              Custom Prompt
            </ListItem>
            <ListItem>
              <ListItemPrefix>
                <Cog6ToothIcon className="h-5 w-5" />
              </ListItemPrefix>
              Settings
            </ListItem>
            <ListItem onClick={() => handlelogout()}>
              <ListItemPrefix>
                <PowerIcon className="h-5 w-5" />
              </ListItemPrefix>
              Log Out
            </ListItem>
          </List>
          <Alert
            open={openAlert}
            className="mt-auto"
            onClose={() => setOpenAlert(false)}
          >
            <CubeTransparentIcon className="mb-4 h-12 w-12" />
            <Typography variant="h6" className="mb-1">
              Upgrade to PRO
            </Typography>
            <Typography variant="small" className="font-normal opacity-80">
              Upgrade to Material Tailwind PRO and get even more components,
              plugins, advanced features and premium.
            </Typography>
            <div className="mt-4 flex gap-3">
              <Typography
                as="a"
                href="#"
                variant="small"
                className="font-medium opacity-80"
                onClick={() => setOpenAlert(false)}
              >
                Dismiss
              </Typography>
              <Typography
                as="a"
                href="#"
                variant="small"
                className="font-medium"
              >
                Upgrade Now
              </Typography>
            </div>
          </Alert>
        </Card>
      </Drawer>
    </>
  );
};

export default Sidebar;
