import { createContext, useContext, useState } from "react";

type Toast = { id:number; msg:string; type?: "ok"|"err" };
const Ctx = createContext<{ toasts:Toast[]; push:(t:Omit<Toast,"id">)=>void; remove:(id:number)=>void } | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const push = (t:Omit<Toast,"id">) => {
    const id = Date.now()+Math.random();
    setToasts(x=>[...x,{...t,id}]);
    setTimeout(()=>remove(id), 3500);
  };
  const remove = (id:number) => setToasts(x=>x.filter(t=>t.id!==id));
  return <Ctx.Provider value={{toasts,push,remove}}>{children}<ToastList toasts={toasts} remove={remove}/></Ctx.Provider>;
}
export function useToast(){ const v = useContext(Ctx); if(!v) throw new Error("Toast ctx"); return v; }

function ToastList({ toasts, remove }:{ toasts:Toast[]; remove:(id:number)=>void }) {
  return <div className="fixed top-4 right-4 space-y-2 z-50">
    {toasts.map(t=>
      <div key={t.id} className={`px-4 py-2 rounded-xl border ${t.type==="err"?"border-danger bg-[#2a1212]":"border-ok bg-[#0d2a21]"}`}>
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${t.type==="err"?"bg-danger":"bg-ok"}`}></div>
          <div>{t.msg}</div>
          <button className="ml-2 text-mut" onClick={()=>remove(t.id)}>×</button>
        </div>
      </div>
    )}
  </div>;
}