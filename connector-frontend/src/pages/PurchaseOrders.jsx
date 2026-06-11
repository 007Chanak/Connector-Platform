import { useEffect, useState } from "react";
import api from "../services/api";

function PurchaseOrders() {

  const [purchaseOrders, setPurchaseOrders] =
    useState([]);

  useEffect(() => {

    const fetchPurchaseOrders =
      async () => {

        try {

          const token =
            localStorage.getItem(
              "token"
            );

          const response =
            await api.get(
              "/purchase-orders",
              {
                headers: {
                  Authorization:
                    `Bearer ${token}`
                }
              }
            );

          setPurchaseOrders(
            response.data
          );

        } catch (error) {

          console.error(error);

        }

      };

    fetchPurchaseOrders();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Purchase Orders
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                PO Number
              </th>

              <th className="text-left p-4">
                Supplier
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

            {purchaseOrders.map(
              (po) => (

                <tr
                  key={po.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {po.po_number}
                  </td>

                  <td className="p-4">
                    {po.supplier_name}
                  </td>

                  <td className="p-4">
                    {po.item_name}
                  </td>

                  <td className="p-4">
                    {po.quantity}
                  </td>

                  <td className="p-4">
                    ₹{po.line_amount}
                  </td>

                  <td className="p-4">
                    ₹{po.total_amount}
                  </td>

                  <td className="p-4">
                    {po.status}
                  </td>

                  <td className="p-4">
                    {po.source}
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

export default PurchaseOrders;