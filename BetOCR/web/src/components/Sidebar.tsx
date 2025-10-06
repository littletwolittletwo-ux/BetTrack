import { Link, useLocation } from "react-router-dom";
import { getRole, hasAuth, logout } from "@/auth";
import { Shield, Upload, Users, Settings2, LayoutDashboard, LogOut, FileText, Database, Activity } from "lucide-react";

export default function Sidebar(){
  const loc = useLocation();
  const role = getRole();
  const active = (p:string) => loc.pathname.includes(p) ? "bg-[#0f1721] border border-line" : "";
  
  return (
    <aside className="h-screen bg-card border-r border-line p-4 flex flex-col gap-3">
      <div className="flex items-center gap-2 mb-2">
        <img 
          src="/static/bet-tracker-logo.png" 
          alt="Bet Tracker" 
          className="w-full h-auto"
        />
      </div>
      {hasAuth() ? (
        <>
          <Link className={`card py-3 flex items-center gap-3 ${active("dashboard")}`} to="dashboard"><LayoutDashboard size={18}/> Dashboard</Link>
          <Link className={`card py-3 flex items-center gap-3 ${active("risk")}`} to="risk"><Activity size={18}/> Risk</Link>
          <Link className={`card py-3 flex items-center gap-3 ${active("upload")}`} to="upload"><Upload size={18}/> Upload</Link>
          <Link className={`card py-3 flex items-center gap-3 ${active("uploads")}`} to="uploads"><FileText size={18}/> All Uploads</Link>
          {role==="admin" && <>
            <Link className={`card py-3 flex items-center gap-3 ${active("users")}`} to="users"><Users size={18}/> Users</Link>
            <Link className={`card py-3 flex items-center gap-3 ${active("sets")}`} to="sets"><Settings2 size={18}/> Sets</Link>
            <Link className={`card py-3 flex items-center gap-3 ${active("csv-management")}`} to="csv-management"><Database size={18}/> CSV Files</Link>
          </>}
          <button className="card py-3 flex items-center gap-3 text-red-400 hover:bg-red-900/20 mt-4" onClick={logout}>
            <LogOut size={18}/> Logout
          </button>
        </>
      ) : (
        <Link className={`card py-3 flex items-center gap-3 ${active("login")}`} to="login"><Shield size={18}/> Login</Link>
      )}
      <div className="mt-auto text-xs text-mut">v0.2.0</div>
    </aside>
  );
}