import { Outlet, Navigate } from "react-router-dom";
import AppShell from "./components/AppShell";
import { hasAuth } from "./auth";

export default function App(){
  if (!hasAuth()) return <Navigate to="login" replace />;
  return <AppShell><Outlet/></AppShell>;
}