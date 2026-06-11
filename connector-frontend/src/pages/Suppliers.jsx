import { useEffect, useState } from "react";
import api from "../services/api";

function Suppliers() {

  const [suppliers, setSuppliers] = useState([]);

  useEffect(() => {

    const fetchSuppliers = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/suppliers",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setSuppliers(response.data);

      } catch (error) {

        console.error(error);

      }

    };

    fetchSuppliers();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Suppliers
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Suppliers Name
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

            {suppliers.map(
              (supplier) => (

                <tr
                  key={supplier.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {supplier.supplier_name}
                  </td>

                  <td className="p-4">
                    {supplier.email}
                  </td>

                  <td className="p-4">
                    {supplier.phone}
                  </td>

                  <td className="p-4">
                    {supplier.source}
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

export default Suppliers;