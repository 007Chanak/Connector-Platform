import { useEffect, useState } from "react";
import api from "../services/api";

function SalesOrders() {

  const [salesOrders, setSalesOrders] =
    useState([]);

  useEffect(() => {

    const fetchSalesOrders =
      async () => {

        try {

          const token =
            localStorage.getItem(
              "token"
            );

          const response =
            await api.get(
              "/sales-orders",
              {
                headers: {
                  Authorization:
                    `Bearer ${token}`
                }
              }
            );

          setSalesOrders(
            response.data
          );

        } catch (error) {

          console.error(error);

        }

      };

    fetchSalesOrders();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Sales Orders
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                SO Number
              </th>

              <th className="text-left p-4">
                Customer
              </th>

              <th className="text-left p-4">
                Item
              </th>

              <th className="text-left p-4">
                Quantity
              </th>

              <th className="text-left p-4">
                Line Amount
              </th>

              <th className="text-left p-4">
                Amount
              </th>

              <th className="text-left p-4">
                Status
              </th>

              <th className="text-left p-4">
                Source
              </th>

            </tr>

          </thead>

          <tbody>

            {salesOrders.map(
              (so) => (

                <tr
                  key={so.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {so.so_number}
                  </td>

                  <td className="p-4">
                    {so.customer_name}
                  </td>

                  <td className="p-4">
                    {so.item_name}
                  </td>

                  <td className="p-4">
                    {so.quantity}
                  </td>

                  <td className="p-4">
                    ₹{so.line_amount}
                  </td>

                  <td className="p-4">
                    ₹{so.total_amount}
                  </td>

                  <td className="p-4">
                    {so.status}
                  </td>

                  <td className="p-4">
                    {so.source}
                  </td>

                </tr>

              )
            )}

          </tbody>

        </table>

      </div>

    </div>

  );
}

export default SalesOrders;