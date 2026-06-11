import { useEffect, useState } from "react";
import api from "../services/api";

function Invoices() {

  const [invoices, setInvoices] = useState([]);

  useEffect(() => {

    const fetchInvoices = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/invoices",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setInvoices(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchInvoices();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Invoices
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Invoice Number
              </th>

              <th className="text-left p-4">
                Customer
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

            {invoices.map(
              (invoice) => (

                <tr
                  key={invoice.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {invoice.invoice_number}
                  </td>

                  <td className="p-4">
                    {invoice.customer_name}
                  </td>

                  <td className="p-4">
                    ₹{invoice.total_amount}
                  </td>

                  <td className="p-4">
                    {invoice.status}
                  </td>

                  <td className="p-4">
                    {invoice.source}
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

export default Invoices;