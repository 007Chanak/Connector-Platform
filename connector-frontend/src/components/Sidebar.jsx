import { Link } from "react-router-dom";

function Sidebar() {

  const handleLogout = () => {

    localStorage.removeItem(
      "token"
    );

    window.location.href =
      "/login";
  };

  return (

    <div className="w-64 bg-slate-900 text-white min-h-screen p-5 flex flex-col">

      <div>

        <h1 className="text-2xl font-bold mb-10">
          Connector
        </h1>

        <nav className="flex flex-col gap-4">

          <Link to="/">
            Dashboard
          </Link>

          <Link to="/customers">
            Customers
          </Link>

          <Link to="/invoices">
            Invoices
          </Link>

          <Link to="/items">
            Items
          </Link>

          <Link to="/suppliers">
            Suppliers
          </Link>

          <Link to="/bills">
            Bills
          </Link>

          <Link to="/purchase-orders">
            Purchase Orders
          </Link>

          <Link to="/sales-orders">
            Sales Orders
          </Link>

          <Link to="/accounts">
            Accounts
          </Link>

          <Link to="/integrations">
            Integrations
          </Link>

          <Link to="/migration-center">
            Migration Center
          </Link>

        </nav>

      </div>

      <div className="mt-auto">

        <button
          onClick={handleLogout}
          className="w-full bg-red-600 hover:bg-red-700 rounded p-2"
        >
          Logout
        </button>

      </div>

    </div>

  );
}

export default Sidebar;