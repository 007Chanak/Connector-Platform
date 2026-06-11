import api from "../services/api";

function MigrationCenter() {

  const getToken = () => {
    return localStorage.getItem("token");
  };

  const migrateCustomersToERPNext = async () => {
    try {

      await api.get(
        "/erpnext/push-customers",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Customers migrated to ERPNext");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateInvoicesToERPNext = async () => {
    try {

      await api.get(
        "/sync/invoices/erpnext",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Invoices migrated to ERPNext");

    } catch (error) {

    console.error(error);

    alert(
        JSON.stringify(
        error.response?.data
        )
    );

    }
  };

  const migrateItemsToERPNext = async () => {
    try {

      await api.get(
        "/sync/items/erpnext",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Items migrated to ERPNext");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateSuppliersToERPNext = async () => {
    try {

      await api.get(
        "/push/suppliers/erpnext",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Suppliers migrated to ERPNext");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateBillsToERPNext = async () => {
    try {

      await api.post(
        "/push/bills/erpnext",
        {},
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Bills migrated to ERPNext");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migratePurchaseOrdersToERPNext = async () => {

    try {

      await api.post(
        "/push/purchase-orders/erpnext",
        {},
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Purchase Orders migrated to ERPNext");

    } catch (error) {

      console.error(error);

      alert("Migration failed");

    }
  };

  const migrateSalesOrdersToERPNext = async () => {

    try {

      await api.post(
        "/push/sales-orders/erpnext",
        {},
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Sales Orders migrated to ERPNext");

    } catch (error) {

      console.error(error);

      alert("Migration failed");

    }
  };

  const migrateCustomersToXero = async () => {
    try {

      await api.get(
        "/sync/customers/xero",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Customers migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateInvoicesToXero = async () => {
    try {

      await api.get(
        "/sync/invoices/xero",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Invoices migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateItemsToXero = async () => {
    try {

      await api.get(
        "/sync/items/xero",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Items migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateSuppliersToXero = async () => {
    try {

      await api.get(
        "/push/suppliers/xero",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Suppliers migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateBillsToXero = async () => {
    try {

      await api.get(
        "/push/bills/xero",
        {
          headers: {
            Authorization: `Bearer ${getToken()}`
          }
        }
      );

      alert("Bills migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migratePurchaseOrdersToXero = async () => {

    try {

      await api.get(
        "/push/purchase-orders/xero",
        {
          headers: {
            Authorization:  `Bearer ${getToken()}`
          }
        }
      );

      alert("Purchase Orders migrated to Xero");

    } catch (error) {

      console.error(error);
      alert("Migration failed");

    }
  };

  const migrateSalesOrdersToXero = async () => {

    try {

      await api.get(
        "/push/sales-orders/xero",
        {
          headers: {
            Authorization:
              `Bearer ${getToken()}`
          }
        }
      );

      alert(
        "Sales Orders migrated to Xero"
      );

    } catch (error) {

      console.error(error);

      alert(
        "Migration failed"
      );

    }
  };

  return (
    <div>

      <h1 className="text-4xl font-bold mb-8">
        Migration Center
      </h1>

      <div className="grid grid-cols-2 gap-6">

        {/* ERPNext Card */}
        <div className="bg-white p-6 rounded-xl shadow">

          <h2 className="text-2xl font-bold mb-6">
            ERPNext
          </h2>

          <button
            onClick={migrateCustomersToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Customers
          </button>

          <button
            onClick={migrateInvoicesToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Invoices
          </button>

          <button
            onClick={migrateItemsToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Items
          </button>

          <button
            onClick={migrateSuppliersToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Suppliers
          </button>

          <button
            onClick={migrateBillsToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Bills
          </button>

          <button
            onClick={migratePurchaseOrdersToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded mb-3"
          >
            Push Purchase Orders
          </button>

          <button
            onClick={migrateSalesOrdersToERPNext}
            className="w-full bg-blue-600 text-white p-3 rounded"
          >
            Push Sales Orders
          </button>

        </div>

        {/* Xero Card */}
        <div className="bg-white p-6 rounded-xl shadow">

          <h2 className="text-2xl font-bold mb-6">
            Xero
          </h2>

          <button
            onClick={migrateCustomersToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Customers
          </button>

          <button
            onClick={migrateInvoicesToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Invoices
          </button>

          <button
            onClick={migrateItemsToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Items
          </button>

          <button
            onClick={migrateSuppliersToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Suppliers
          </button>

          <button
            onClick={migrateBillsToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Bills
          </button>

          <button
            onClick={migratePurchaseOrdersToXero}
            className="w-full bg-green-600 text-white p-3 rounded mb-3"
          >
            Push Purchase Orders
          </button>

          <button
            onClick={migrateSalesOrdersToXero}
            className="w-full bg-green-600 text-white p-3 rounded"
          >
            Push Sales Orders
          </button>

        </div>

      </div>

    </div>
  );
}

export default MigrationCenter;