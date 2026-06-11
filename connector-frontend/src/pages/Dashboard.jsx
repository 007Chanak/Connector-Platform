import { useEffect, useState } from "react";

import StatsCard from "../components/StatsCard";

import api from "../services/api";

function Dashboard() {

  const [stats, setStats] = useState({
    customers: 0,
    invoices: 0,
    items: 0,
    suppliers: 0,
    bills: 0,
    purchaseOrders: 0,
    salesOrders: 0,
    accounts: 0,
    xero_connected: false,
    erpnext_connected: false,
  });

  useEffect(() => {

    const fetchStats = async () => {

      try {

        const token = localStorage.getItem(
          "token"
        );

        const response = await api.get(
          "/dashboard/stats",
          {
            headers: {
              Authorization:
                `Bearer ${token}`,
            },
          }
        );

        setStats(response.data);

      } catch (error) {

        console.error(
          error
        );

      }
    };

    fetchStats();

  }, []);

  return (
    <div>

      <h1 className="text-4xl font-bold mb-8">
        Dashboard
      </h1>

      <div className="grid grid-cols-3 gap-6">

        <StatsCard
          title="Customers"
          value={stats.customers}
        />

        <StatsCard
          title="Invoices"
          value={stats.invoices}
        />

        <StatsCard
          title="Items"
          value={stats.items}
        />

        <StatsCard
          title="Suppliers"
          value={stats.suppliers}
        />

        <StatsCard
          title="Bills"
          value={stats.bills}
        />

        <StatsCard
          title="Purchase Order"
          value={stats.purchaseOrders}
        />

        <StatsCard
          title="Sales Order"
          value={stats.salesOrders}
        />

        <StatsCard
          title="Accounts"
          value={stats.accounts}
        />

      </div>

      <div className="mt-10 bg-white rounded-xl shadow p-6">

        <h2 className="text-xl font-bold mb-4">
          Integrations
        </h2>

        <div className="space-y-2">

          <p>
            {stats.erpnext_connected
              ? "🟢 ERPNext Connected"
              : "🔴 ERPNext Not Connected"}
          </p>

          <p>
            {stats.xero_connected
              ? "🟢 Xero Connected"
              : "🔴 Xero Not Connected"}
          </p>

        </div>

      </div>

    </div>
  );
}

export default Dashboard;