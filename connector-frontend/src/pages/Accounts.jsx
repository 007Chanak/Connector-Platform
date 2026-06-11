import { useEffect, useState } from "react";
import api from "../services/api";

function Accounts() {

  const [accounts, setAccounts] = useState([]);

  useEffect(() => {

    const fetchAccounts = async () => {

      try {

        const token =
          localStorage.getItem("token");

        const response =
          await api.get(
            "/accounts",
            {
              headers: {
                Authorization:
                  `Bearer ${token}`
              }
            }
          );

        setAccounts(
          response.data
        );

      } catch (error) {

        console.error(error);

      }

    };

    fetchAccounts();

  }, []);

  return (

    <div>

      <h1 className="text-4xl font-bold mb-8">
        Accounts
      </h1>

      <div className="bg-white rounded-xl shadow overflow-hidden">

        <table className="w-full">

          <thead className="bg-slate-100">

            <tr>

              <th className="text-left p-4">
                Account Code
              </th>

              <th className="text-left p-4">
                Account Name
              </th>

              <th className="text-left p-4">
                Type
              </th>

              <th className="text-left p-4">
                Class
              </th>

              <th className="text-left p-4">
                Parent Account
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

            {accounts.map(
              (account) => (

                <tr
                  key={account.id}
                  className="border-t"
                >

                  <td className="p-4">
                    {account.account_code || "-"}
                  </td>

                  <td className="p-4">
                    {account.account_name}
                  </td>

                  <td className="p-4">
                    {account.account_type || "-"}
                  </td>

                  <td className="p-4">
                    {account.account_class || "-"}
                  </td>

                  <td className="p-4">
                    {account.parent_account || "-"}
                  </td>

                  <td className="p-4">
                    {account.status}
                  </td>

                  <td className="p-4">
                    {account.source}
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

export default Accounts;