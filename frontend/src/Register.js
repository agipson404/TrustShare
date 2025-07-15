import React, { useState } from "react";
import axios from "axios";
import './App.css';

function Register() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post("http://localhost:8000/register", {
        username,
        password,
      });
      setMessage("Registration successful! You can now log in.");
    } catch (error) {
      setMessage(
        error.response?.data?.detail || "Registration failed. Try a different username."
      );
    }
  };

  return (
    <form onSubmit={handleRegister}>
      <h2>Register</h2>
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
      <button type="submit">Register</button>
      <div>{message}</div>
    </form>
  );
}

export default Register;
