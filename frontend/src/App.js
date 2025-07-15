import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from "react-router-dom";
import Register from "./Register";
import Login from "./Login";
import Intro from "./Intro";
import Dashboard from "./Dashboard";
import './App.css';

function AppContent({ loggedIn, setLoggedIn }) {
  const location = useLocation();

  const showNav = location.pathname !== "/";

  const handleLogout = () => {
    localStorage.removeItem("token");
    setLoggedIn(false);
  };

  return (
    <>
      {showNav && (
        <nav>
          <Link to="/">Home</Link> |{" "}
          <Link to="/register">Register</Link> |{" "}
          <Link to="/login">Login</Link>
          {loggedIn && (
            <>
              {" | "}
              <Link to="/dashboard">Dashboard</Link>
              {" | "}
              <button
                className="logout-btn"
                onClick={handleLogout}
                style={{
                  cursor: "pointer",
                  background: "none",
                  border: "none",
                  color: "blue",
                  textDecoration: "underline",
                  padding: 0,
                  fontSize: "inherit",
                  fontFamily: "inherit",
                }}
              >
                Logout
              </button>
            </>
          )}
        </nav>
      )}
      <Routes>
        <Route path="/" element={<Intro />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login setLoggedIn={setLoggedIn} />} />
        <Route
          path="/dashboard"
          element={
            loggedIn ? (
              <Dashboard setLoggedIn={setLoggedIn} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
      {loggedIn && location.pathname !== "/dashboard" && (
        <div>
          You're logged in! <Link to="/dashboard">Go to Dashboard</Link>
        </div>
      )}
    </>
  );
}

function App() {
  const [loggedIn, setLoggedIn] = useState(() => {
    return Boolean(localStorage.getItem("token"));
  });

  return (
    <BrowserRouter>
      <AppContent loggedIn={loggedIn} setLoggedIn={setLoggedIn} />
    </BrowserRouter>
  );
}

export default App;
