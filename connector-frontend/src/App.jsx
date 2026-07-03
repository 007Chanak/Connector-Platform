import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import Customers from "./pages/Customers";
import Invoices from "./pages/Invoices";
import Items from "./pages/Items";
import Suppliers from "./pages/Suppliers";
import Bills from "./pages/Bills";
import PurchaseOrders from "./pages/PurchaseOrders";
import SalesOrders from "./pages/SalesOrders";
import Accounts from "./pages/Accounts";
import Integrations from "./pages/Integrations";
import MigrationCenter from "./pages/MigrationCenter";
import WorkflowDesigner from "./pages/WorkflowDesigner";
import Login from "./pages/Login";
import Signup from "./pages/Signup";

function ProtectedLayout({ children }) {

  const token =
    localStorage.getItem("token");

  if (!token) {

    return (
      <Navigate
        to="/login"
        replace
      />
    );

  }

  return (

    <div className="flex">

      <Sidebar />

      <div className="flex-1 p-8">
        {children}
      </div>

    </div>

  );

}

function App() {

  const token =
    localStorage.getItem("token");

  return (

    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={
            token
              ? (
                <Navigate
                  to="/dashboard"
                  replace
                />
              )
              : (
                <Navigate
                  to="/login"
                  replace
                />
              )
          }
        />

        <Route
          path="/login"
          element={
            token
              ? (
                <Navigate
                  to="/dashboard"
                  replace
                />
              )
              : (
                <Login />
              )
          }
        />

        <Route
          path="/signup"
          element={<Signup />}
        />

        <Route
          path="/dashboard"
          element={
            <ProtectedLayout>
              <Dashboard />
            </ProtectedLayout>
          }
        />

        <Route
          path="/customers"
          element={
            <ProtectedLayout>
              <Customers />
            </ProtectedLayout>
          }
        />

        <Route
          path="/invoices"
          element={
            <ProtectedLayout>
              <Invoices />
            </ProtectedLayout>
          }
        />

        <Route
          path="/items"
          element={
            <ProtectedLayout>
              <Items />
            </ProtectedLayout>
          }
        />

        <Route
          path="/suppliers"
          element={
            <ProtectedLayout>
              <Suppliers />
            </ProtectedLayout>
          }
        />

        <Route
          path="/bills"
          element={
            <ProtectedLayout>
              <Bills />
            </ProtectedLayout>
          }
        />

        <Route
          path="/purchase-orders"
          element={
            <ProtectedLayout>
              <PurchaseOrders />
            </ProtectedLayout>
          }
        />

        <Route
          path="/sales-orders"
          element={
            <ProtectedLayout>
              <SalesOrders />
            </ProtectedLayout>
          }
        />

        <Route
          path="/accounts"
          element={
            <ProtectedLayout>
              <Accounts />
            </ProtectedLayout>
          }
        />

        <Route
          path="/integrations"
          element={
            <ProtectedLayout>
              <Integrations />
            </ProtectedLayout>
          }
        />

        <Route
          path="/migration-center"
          element={
            <ProtectedLayout>
              <MigrationCenter />
            </ProtectedLayout>
          }
        />

        <Route
          path="/workflow-designer"
          element={
            <ProtectedLayout>
              <WorkflowDesigner />
            </ProtectedLayout>
          }
        />

      </Routes>

    </BrowserRouter>

  );

}

export default App;