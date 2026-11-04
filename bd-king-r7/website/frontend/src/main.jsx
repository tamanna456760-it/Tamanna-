import React from "react";
import ReactDOM from "react-dom/client";
import App from "./apps.jsx";
import "./index.css";

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error('Missing "#root" element in the frontend HTML entry point.');
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
