import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {

    e.preventDefault();

    try {

      const formData = new FormData();

      formData.append(
        "username",
        email
      );

      formData.append(
        "password",
        password
      );

      const response = await api.post(
        "/login",
        formData
      );

      localStorage.setItem(
        "token",
        response.data.access_token
      );

      window.location.href = "/dashboard";

    } catch (error) {

      console.error(error);

      alert(
        error.response?.data?.detail ||
        "Login Failed"
      );

    }

  };

  return (

    <div className="min-h-screen flex items-center justify-center bg-slate-100">

      <form
        onSubmit={handleLogin}
        className="bg-white p-8 rounded-xl shadow w-96"
      >

        <h1 className="text-3xl font-bold mb-2">
          Connector Platform
        </h1>

        <p className="text-slate-500 mb-6">
          Login to continue
        </p>

        <input
          type="email"
          placeholder="Email"
          className="w-full border p-3 mb-4 rounded"
          value={email}
          onChange={(e) =>
            setEmail(e.target.value)
          }
        />

        <input
          type="password"
          placeholder="Password"
          className="w-full border p-3 mb-6 rounded"
          value={password}
          onChange={(e) =>
            setPassword(e.target.value)
          }
        />

        <button
          type="submit"
          className="w-full bg-blue-600 text-white p-3 rounded hover:bg-blue-700"
        >
          Login
        </button>

        <button
          type="button"
          onClick={() => navigate("/signup")}
          className="w-full mt-3 border border-slate-300 p-3 rounded"
        >
          Create Account
        </button>

      </form>

    </div>

  );

}

export default Login;