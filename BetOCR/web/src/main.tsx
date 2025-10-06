import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./styles.css";
import App from "./App";
import Dashboard from "./routes/Dashboard";
import Login from "./routes/Login";
import Upload from "./routes/Upload";
import AllUploads from "./routes/AllUploads";
import Users from "./routes/Users";
import Sets from "./routes/Sets";
import CsvManagement from "./routes/CsvManagement";
import Risk from "./routes/Risk";
import { ToastProvider } from "./components/Toast";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ToastProvider>
      <BrowserRouter basename="/admin">
        <Routes>
          <Route path="/login" element={<Login/>} />
          <Route path="/" element={<App/>}>
            <Route index element={<Navigate to="dashboard" />} />
            <Route path="dashboard" element={<Dashboard/>} />
            <Route path="risk" element={<Risk/>} />
            <Route path="upload" element={<Upload/>} />
            <Route path="uploads" element={<AllUploads/>} />
            <Route path="users" element={<Users/>} />
            <Route path="sets" element={<Sets/>} />
            <Route path="csv-management" element={<CsvManagement/>} />
            <Route path="*" element={<Navigate to="dashboard" />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ToastProvider>
  </React.StrictMode>
);