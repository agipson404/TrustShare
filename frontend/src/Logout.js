import React from "react";

function Logout({ setLoggedIn }) {
  const handleLogout = () => {
    localStorage.removeItem("token");
    setLoggedIn(false);
    window.location.href = "/"; // or use react-router navigate
  };

  return <button onClick={handleLogout}>Logout</button>;
}

export default Logout;
