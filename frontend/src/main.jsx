import React from "react";
import ReactDOM from "react-dom/client";

import AppRouter from "./routes/AppRouter";
import SmoothScroll from "./components/common/SmoothScroll";
import ScrollProgress from "./components/common/ScrollProgress";

import "./styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <SmoothScroll />
    <ScrollProgress />
    <AppRouter />
  </React.StrictMode>
);