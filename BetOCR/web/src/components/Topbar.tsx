import { logout, getRole, hasAuth } from "@/auth";

export default function Topbar(){
  const role = getRole();
  return (
    <header className="sticky top-0 z-10 bg-bg/70 backdrop-blur border-b border-line px-6 py-3 flex items-center justify-between">
      <div className="text-sm text-mut">Welcome {hasAuth() ? `(${role})` : ""}</div>
      <div className="flex items-center gap-2">
        {hasAuth() ? <button className="btn" onClick={logout}>Logout</button> : null}
      </div>
    </header>
  );
}