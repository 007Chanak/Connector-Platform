import { useEffect, useState } from "react";
import api from "../services/api";

function Customers() {

  const [customers, setCustomers] = useState([]);

  useEffect(() => {

    const fetchCustomers = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/customers",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setCustomers(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchCustomers();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Customers
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Name
              </th>

              <th className="text-left p-4">
                Email
              </th>

              <th className="text-left p-4">
                Phone
              </th>

              <th className="text-left p-4">
                Source
              </th>

            </tr>

          </thead>

          <tbody>

            {customers.map(
              (customer) => (

                <tr
                  key={customer.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {customer.customer_name}
                  </td>

                  <td className="p-4">
                    {customer.email}
                  </td>

                  <td className="p-4">
                    {customer.phone}
                  </td>

                  <td className="p-4">
                    {customer.source}
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

export default Customers;