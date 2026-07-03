import { useEffect, useState } from "react";
import api from "../services/api";

function Integrations() {

  const [status, setStatus] =
    useState({
      xero_connected: false,
      erpnext_connected: false,
    });

  const [erpUrl, setErpUrl] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [apiSecret, setApiSecret] = useState("");
  const readyForSync =
    status.xero_connected &&
    status.erpnext_connected;

  useEffect(() => {

    const fetchStatus = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/integrations/status",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setStatus(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchStatus();

  }, []);

  const connectERPNext = async () => {

    try {

      const token =
        localStorage.getItem("token");

      await api.post(
        "/erpnext/connect",
        null,
        {
          params: {
            erp_url: erpUrl,
            api_key: apiKey,
            api_secret: apiSecret
          },
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );

      const response =
        await api.get(
          "/integrations/status",
          {
            headers: {
              Authorization:
                `Bearer ${token}`
            }
          }
        );

      setStatus(
        response.data
      );

      setErpUrl("");
      setApiKey("");
      setApiSecret("");

      alert(
        "ERPNext Connected Successfully"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Failed to connect ERPNext"
      );

    }
  };

  const connectXero = () => {

    window.location.href =
      "http://localhost:8000/xero/login";

  };

  const syncXeroCustomers = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/xero/customers",
        {
        headers: {
            Authorization:
            `Bearer ${token}`
        }
        }
    );

    alert(
        "Xero customers synced"
    );
    };

    const syncXeroInvoices = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "sync/xero/invoices",
        {
            headers: {
                Authorization: `Bearer ${localStorage.getItem("token")}`
            }
        }
    );

    alert(
        "Xero invoices synced"
    );
    };

    const syncXeroItems = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/xero/items",
        {
        headers: {
            Authorization:
            `Bearer ${token}`
        }
        }
    );

    alert(
        "Xero items synced"
    );
    };

    const syncXeroSuppliers = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/xero/suppliers",
        {
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );

    alert(
        "Xero suppliers synced"
      );
    };

    const syncXeroBills = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/xero/bills",
        {
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );

      alert(
        "Xero bills synced"
      );
    };

    const syncXeroPurchaseOrders = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/xero/purchase-orders",
        {
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );

      alert(
        "Xero Purchase Orders synced"
      );
    };

  const syncXeroSalesOrders = async () => {

  const token =
      localStorage.getItem("token");

  await api.get(
      "/sync/xero/sales-orders",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "Xero Sales Orders synced"
    );
  };

  const syncXeroAccounts = async () => {

  const token =
      localStorage.getItem("token");

  await api.get(
      "/sync/xero/accounts",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "Xero Accounts synced"
    );
  };

  const syncERPCustomers = async () => {

    try {

        const token =
        localStorage.getItem("token");

        await api.get(
        "/sync/erpnext/customers",
        {
            headers: {
            Authorization:
                `Bearer ${token}`
            }
        }
        );

        alert(
        "ERPNext customers synced"
        );

    } catch (error) {

        console.error(error);

        alert(
        "Failed to sync ERPNext customers"
        );

    }

    };

    const syncERPInvoices = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/erpnext/invoices",
        {
        headers: {
            Authorization:
            `Bearer ${token}`
        }
        }
    );

    alert(
        "ERPNext invoices synced"
    );
    };

    const syncERPItems = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/erpnext/items",
        {
        headers: {
            Authorization:
            `Bearer ${token}`
        }
        }
    );

    alert(
        "ERPNext items synced"
    );
    };

    const syncERPSuppliers = async () => {

    const token =
        localStorage.getItem("token");

    await api.get(
        "/sync/erpnext/suppliers",
        {
          headers: {
            Authorization:
              `Bearer ${token}`
          }
        }
      );

    alert(
        "ERPNext suppliers synced"
      );
    };

    const syncERPBills = async () => {

    const token =
      localStorage.getItem("token");

    await api.get(
      "/sync/erpnext/bills",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "ERPNext bills synced"
    );
  };

  const syncERPPurchaseOrders = async () => {

    const token =
      localStorage.getItem("token");

    await api.get(
      "/sync/erpnext/purchase-orders",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "ERPNext Purchase Orders synced"
    );
  };

  const syncERPSalesOrders = async () => {

  const token =
      localStorage.getItem("token");

  await api.get(
      "/sync/erpnext/sales-orders",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "ERPNext Sales Orders synced"
    );
  };

  const syncERPAccounts = async () => {

  const token =
      localStorage.getItem("token");

  await api.get(
      "/sync/erpnext/accounts",
      {
        headers: {
          Authorization:
            `Bearer ${token}`
        }
      }
    );

    alert(
      "ERPNext Accounts synced"
    );
  };

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Integrations
      </h1>

      <div className="grid grid-cols-2 gap-6">

        <div className="bg-white p-6 rounded-xl shadow">

          <h2 className="text-2xl font-bold mb-4">
            ERPNext
          </h2>

          <p className="mb-4">

            {
              status.erpnext_connected
                ? "🟢 Connected"
                : "🔴 Not Connected"
            }

          </p>

          {
            !status.erpnext_connected && (

              <div className="mb-4">

                <input
                  type="text"
                  placeholder="ERP URL"
                  value={erpUrl}
                  onChange={(e) =>
                    setErpUrl(e.target.value)
                  }
                  className="w-full border p-2 rounded mb-2"
                />

                <input
                  type="text"
                  placeholder="API Key"
                  value={apiKey}
                  onChange={(e) =>
                    setApiKey(e.target.value)
                  }
                  className="w-full border p-2 rounded mb-2"
                />

                <input
                  type="text"
                  placeholder="API Secret"
                  value={apiSecret}
                  onChange={(e) =>
                    setApiSecret(e.target.value)
                  }
                  className="w-full border p-2 rounded mb-2"
                />

                <button
                  onClick={connectERPNext}
                  className="w-full bg-orange-600 text-white p-2 rounded mb-4"
                >
                  Connect ERPNext
                </button>

              </div>

            )
          }

          {
            readyForSync && (
              <>
                <button
                  onClick={syncERPCustomers}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Customers
                </button>

                <button
                  onClick={syncERPInvoices}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Invoices
                </button>

                <button
                  onClick={syncERPItems}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Items
                </button>

                <button
                  onClick={syncERPSuppliers}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Suppliers
                </button>

                <button
                  onClick={syncERPBills}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Bills
                </button>

                <button
                  onClick={syncERPPurchaseOrders}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Purchase Orders
                </button>

                <button
                  onClick={syncERPSalesOrders}
                  className="w-full bg-blue-600 text-white p-2 rounded mb-2"
                >
                  Sync Sales Orders
                </button>

                <button
                  onClick={syncERPAccounts}
                  className="w-full bg-blue-600 text-white p-2 rounded"
                >
                  Sync Accounts
                </button>
              </>
            )
          }

        </div>

        <div className="bg-white p-6 rounded-xl shadow">

          <h2 className="text-2xl font-bold mb-4">
            Xero
          </h2>

          <p className="mb-4">

            {
              status.xero_connected
                ? "🟢 Connected"
                : "🔴 Not Connected"
            }

          </p>

          {
            !status.xero_connected && (

              <button
                onClick={connectXero}
                className="w-full bg-blue-500 text-white p-2 rounded mb-4"
              >
                Connect Xero
              </button>

            )
          }

          {
            readyForSync && (
              <>
                <button
                  onClick={syncXeroCustomers}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Customers
                </button>

                <button
                  onClick={syncXeroInvoices}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Invoices
                </button>

                <button
                  onClick={syncXeroItems}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Items
                </button>

                <button
                  onClick={syncXeroSuppliers}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Suppliers
                </button>

                <button
                  onClick={syncXeroBills}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Bills
                </button>

                <button
                  onClick={syncXeroPurchaseOrders}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Purchase Orders
                </button>

                <button
                  onClick={syncXeroSalesOrders}
                  className="w-full bg-green-600 text-white p-2 rounded mb-2"
                >
                  Sync Sales Orders
                </button>

                <button
                  onClick={syncXeroAccounts}
                  className="w-full bg-green-600 text-white p-2 rounded"
                >
                  Sync Accounts
                </button>
              </>
            )
          }

        </div>

      </div>

    </div>
  );

  {
    !readyForSync && (
      <div className="col-span-2 bg-yellow-100 border border-yellow-300 p-4 rounded">

        Connect both Xero and ERPNext before syncing data.

      </div>
    )
  }
}

export default Integrations;