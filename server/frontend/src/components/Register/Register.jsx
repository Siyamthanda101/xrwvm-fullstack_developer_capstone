import React, { useState } from "react";
import "./Register.css";
import userIcon from "../assets/person.png";
import emailIcon from "../assets/email.png";
import passwordIcon from "../assets/password.png";
import closeIcon from "../assets/close.png";

const Register = () => {
  const [userName, setUserName] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");

  const register = async (event) => {
    event.preventDefault();

    try {
      const response = await fetch(
        `${window.location.origin}/djangoapp/register`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            userName,
            password,
            firstName,
            lastName,
            email,
          }),
        }
      );
      const result = await response.json();

      if (response.ok && result.status === "Authenticated") {
        sessionStorage.setItem("username", result.userName);
        window.location.href = window.location.origin;
      } else {
        alert(result.error || "Registration could not be completed.");
      }
    } catch {
      alert("Registration could not be completed. Please try again.");
    }
  };

  return (
    <main className="register_container">
      <div
        className="header"
        style={{
          display: "flex",
          flexDirection: "row",
          justifyContent: "space-between",
        }}
      >
        <span className="text" style={{ flexGrow: "1" }}>
          Sign Up
        </span>
        <a href="/" aria-label="Return home">
          <img style={{ width: "1cm" }} src={closeIcon} alt="" />
        </a>
      </div>

      <form onSubmit={register}>
        <div className="inputs">
          <label className="input">
            <img src={userIcon} className="img_icon" alt="" />
            <input
              type="text"
              name="username"
              placeholder="Username"
              className="input_field"
              autoComplete="username"
              required
              value={userName}
              onChange={(event) => setUserName(event.target.value)}
            />
          </label>
          <label className="input">
            <img src={userIcon} className="img_icon" alt="" />
            <input
              type="text"
              name="firstName"
              placeholder="First name"
              className="input_field"
              autoComplete="given-name"
              required
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
            />
          </label>
          <label className="input">
            <img src={userIcon} className="img_icon" alt="" />
            <input
              type="text"
              name="lastName"
              placeholder="Last name"
              className="input_field"
              autoComplete="family-name"
              required
              value={lastName}
              onChange={(event) => setLastName(event.target.value)}
            />
          </label>
          <label className="input">
            <img src={emailIcon} className="img_icon" alt="" />
            <input
              type="email"
              name="email"
              placeholder="Email"
              className="input_field"
              autoComplete="email"
              required
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />
          </label>
          <label className="input">
            <img src={passwordIcon} className="img_icon" alt="" />
            <input
              type="password"
              name="password"
              placeholder="Password"
              className="input_field"
              autoComplete="new-password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </label>
        </div>
        <div className="submit_panel">
          <input className="submit" type="submit" value="Register" />
        </div>
      </form>
    </main>
  );
};

export default Register;
