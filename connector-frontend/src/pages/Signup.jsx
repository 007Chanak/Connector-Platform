import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Signup() {

  const navigate = useNavigate();

  const [companyName, setCompanyName] =
    useState("");

  const [email, setEmail] =
    useState("");

  const [password, setPassword] =
    useState("");

  const handleSignup = async (e) => {

    e.preventDefault();

    try {

      await api.post(
        "/signup",
        {
          company_name: companyName,
          email,
          password
        }
      );

      alert(
        "Signup Successful"
      );

      navigate("/login");

    } catch (error) {

      console.error(error);

      alert(
        "Signup Failed"
      );

    }

  };

  return (

    <div className="min-h-screen flex items-center justify-center">

      <form
        onSubmit={handleSignup}
        className="bg-white p-8 rounded-xl shadow w-96"
      >

        <h1 className="text-3xl font-bold mb-6">
          Signup
        </h1>

        <input
          type="text"
          placeholder="Company Name"
          className="w-full border p-3 mb-4 rounded"
          value={companyName}
          onChange={(e) =>
            setCompanyName(
              e.target.value
            )
          }
        />

        <input
          type="email"
          placeholder="Email"
          className="w-full border p-3 mb-4 rounded"
          value={email}
          onChange={(e) =>
            setEmail(
              e.target.value
            )
          }
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border p-3 mb-4 rounded"
          value={password}
          onChange={(e) =>
            setPassword(
              e.target.value
            )
          }
        />

        <button
          className="w-full bg-green-600 text-white p-3 rounded"
        >
          Signup
        </button>

      </form>

    </div>

  );

}

export default Signup;