import { useState } from "react";
import { login } from "@/api";
import { saveAuth } from "@/auth";
import { useToast } from "@/components/Toast";

export default function Login(){
  const [u,setU]=useState("");
  const [p,setP]=useState("");
  const { push } = useToast();

  const submit = async (e:React.FormEvent) => {
    e.preventDefault();
    try {
      const tok = await login(u,p);
      saveAuth(tok.access_token, tok.role);
      location.href = "/admin/";
    } catch (err:any){
      push({ msg: err.message || "Login failed", type: "err" });
    }
  };

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <div className="card w-full max-w-md">
        <div className="h1 mb-1">Welcome back</div>
        <div className="h2 mb-4">Sign in to continue</div>
        <form onSubmit={submit} className="grid gap-3">
          <label className="grid gap-1">
            <span className="text-sm text-mut">Username</span>
            <input value={u} onChange={e=>setU(e.target.value)} placeholder="admin"/>
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-mut">Password</span>
            <input type="password" value={p} onChange={e=>setP(e.target.value)} placeholder="••••••••"/>
          </label>
          <button className="btn py-2 rounded-xl">Sign in</button>
        </form>
      </div>
    </div>
  );
}