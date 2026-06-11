import { useEffect, useState } from "react";
import api from "../services/api";

function Bills() {

  const [bills, setBills] = useState([]);

  useEffect(() => {

    const fetchBills = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/bills",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setBills(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchBills();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Bills
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Bill Number
              </th>

              <th className="text-left p-4">
                Supplier
              </th>

              <th className="text-left p-4">
                Item Name
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

            {bills.map(
              (bill) => (

                <tr
                  key={bill.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {bill.bill_number}
                  </td>

                  <td className="p-4">
                    {bill.supplier_name}
                  </td>

                  <td className="p-4">
                    {bill.item_name}
                  </td>

                  <td className="p-4">
                    ₹{bill.line_amount}
                  </td>

                  <td className="p-4">
                    ₹{bill.total_amount}
                  </td>

                  <td className="p-4">
                    {bill.status}
                  </td>

                  <td className="p-4">
                    {bill.source}
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

export default Bills;