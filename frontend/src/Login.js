import React, { useState } from "react";
import axios from "axios";
import './App.css';

function Login({ setLoggedIn }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post("http://localhost:8000/login", {
        username,
        password,
      });

      localStorage.setItem("token", response.data.access_token);

      setMessage("Login successful!");
      setLoggedIn(true);
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Login failed. Check your credentials."
      );
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <h2>Login</h2>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={e => setUsername(e.target.value)}
        required
      /><br />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      /><br />
      <button type="submit">Login</button>
      <div>{message}</div>
    </form>
  );
}

export default Login;
