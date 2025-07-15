import React from "react";
import { Link } from "react-router-dom";
import './App.css';

function Intro() {
  return (
    <div className="intro-container">
      <h1>Welcome to TrustShare</h1>
      <p>
        <b>TrustShare</b> is a secure platform for sharing encrypted files and notes.<br />
        Register or log in to get started!
      </p>
      <div className="intro-links">
        <Link to="/register" className="intro-btn">Register</Link>
        <Link to="/login" className="intro-btn">Login</Link>
      </div>
    </div>
  );
}

export default Intro;
