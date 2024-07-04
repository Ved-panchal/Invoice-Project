import { Outlet } from "react-router-dom";
import Sidebar from "../Components/Sidebar/Sidebar";

const SideBarLayout = () => {
  return (
    <>
      <Sidebar />
      <Outlet />
    </>
  );
};

export default SideBarLayout;
