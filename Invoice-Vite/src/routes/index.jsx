import { useRoutes } from "react-router-dom";
import Home from "../Components/Home/Home";
import HeaderLayout from "../Layouts/HeaderLayout";
import SideBarLayout from "../Layouts/SideBarLayout";
import UploadInvoicePage from "../pages/UploadInvoicePage";
import CustomPrompt from "../pages/CustomPrompt";
import MyDocument from "../pages/MyDocument";
import { ToastContainer } from "react-toastify";

export default function Router() {
  return useRoutes([
    {
      path: "/",
      element: <HeaderLayout />,
      children: [
        {
          path: "/",
          element: <Home />,
        },
      ],
    },
    {
      path: "profile",
      element: <SideBarLayout />,
      children: [
        {
          path: "uploadinvoice",
          element: <UploadInvoicePage />,
        },
        {
          path: "customprompt",
          element: <CustomPrompt />,
        },
      ],
    },
    {
      path: "/my-documents/:fileCode",
      element: <MyDocument />,
    },
    {
      path: "*",
      element: <ToastContainer />,
    },

    // Auth Routes

    // {
    //   path: 'auth',
    //   children: [
    //     {
    //       path: 'login',
    //       element: <Login />,
    //     },
    //     {
    //       path: 'register',
    //       element: <Register />,
    //     },
    //     { path: 'reset-password', element: <ResetPassword /> },
    //     { path: 'forgot-password', element: <ForgotPassword /> },
    //   ],
    // },

    // Dashboard Routes
    // {
    //   path: 'dashboard',
    //   element: (
    //         <DashboardLayout />
    //   ),
    //   children: [
    //     { element: <Navigate to={LANDING_ROUTE} replace />, index: true },
    //     {
    //       path: 'app',
    //       element: (
    //         <RoleBasedGuard accessibleRoles={[USER_ROLES.ADMIN, USER_ROLES.USER]}>
    //           <GeneralApp />
    //         </RoleBasedGuard>
    //       ),
    //     },
    //     {
    //       path: 'account',
    //       element: <UserProfile />,
    //     },
    //     {
    //       path: 'products',
    //       element: <Products />,
    //     },
    //     {
    //       path: 'product/:id',
    //       element: <Product />,
    //     },
    //     {
    //       path: 'checkout',
    //       element: <Checkout />,
    //     },
    //   ],
    // },

    // Main Routes
    // {
    //   path: '*',
    //   element: <LogoOnlyLayout />,
    //   children: [
    //     { path: 'maintenance', element: <Maintenance /> },
    //     { path: '404', element: <NotFound /> },
    //     { path: '*', element: <Navigate to="/404" replace /> },
    //   ],
    // },
    // {
    //   path: '/',
    //   element: <MainLayout />,
    //   children: [
    //     { path: 'about-us', element: <About /> },
    //     { path: 'contact-us', element: <Contact /> },
    //     { path: 'faqs', element: <Faqs /> },
    //   ],
    // },
    // {
    //   path: '/',
    //   element: <Outlet />,
    //   children: [{ element: <Navigate to={LANDING_ROUTE} replace />, index: true }],
    // },
    // { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
