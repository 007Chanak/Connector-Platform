import { useEffect, useState } from "react";
import api from "../services/api";

function Items() {

  const [items, setItems] = useState([]);

  useEffect(() => {

    const fetchItems = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/items",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setItems(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchItems();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Items
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Item Code
              </th>

              <th className="text-left p-4">
                Item Name
              </th>

              <th className="text-left p-4">
                Price
              </th>

              <th className="text-left p-4">
                Source
              </th>

            </tr>

          </thead>

          <tbody>

            {items.map(
              (item) => (

                <tr
                  key={item.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {item.item_code}
                  </td>

                  <td className="p-4">
                    {item.item_name}
                  </td>

                  <td className="p-4">
                    ₹{item.unit_price}
                  </td>

                  <td className="p-4">
                    {item.source}
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

export default Items;