import { useEffect, useState } from "react";
import { fetchSets, createSet, renameSet, toggleSet } from "@/api";
import { Card, CardTitle } from "@/components/Card";
import { Table, Thead, Th, Tbody, Td } from "@/components/Table";
import { useToast } from "@/components/Toast";
import { getRole } from "@/auth";

type SetItem = { id:number; name:string; is_active:boolean };

export default function Sets(){
  const [sets,setSets]=useState<SetItem[]>([]);
  const [name,setName]=useState("");
  const { push } = useToast();
  const role = getRole();

  const load=async()=>{ try{ setSets(await fetchSets()); }catch(e:any){ push({msg:e.message,type:"err"});} };
  useEffect(()=>{ load(); },[]);

  if(role!=="admin") return <div className="card">You need admin access.</div>;

  return (
    <div className="grid gap-6">
      <Card>
        <CardTitle>Create set</CardTitle>
        <div className="flex gap-3 mt-2">
          <input placeholder="name (e.g., s)" value={name} onChange={e=>setName(e.target.value)}/>
          <button className="btn rounded-xl" onClick={async()=>{ if(!name) return; await createSet(name); setName(""); await load(); push({msg:"Set created",type:"ok"}); }}>Add</button>
        </div>
      </Card>

      <Card>
        <CardTitle>All sets</CardTitle>
        <div className="overflow-auto">
          <Table>
            <Thead>
              <Th>ID</Th><Th>Name</Th><Th>Active</Th><Th>Actions</Th>
            </Thead>
            <Tbody>
              {sets.map(s=>
                <tr key={s.id}>
                  <Td>{s.id}</Td>
                  <Td>{s.name}</Td>
                  <Td>{s.is_active?"Yes":"No"}</Td>
                  <Td>
                    <div className="flex gap-2">
                      <button className="px-3 py-2 rounded-xl border border-line" onClick={async()=>{ const n=prompt("New name", s.name); if(!n) return; await renameSet(s.id,n); await load(); }}>Rename</button>
                      <button className="px-3 py-2 rounded-xl border border-line" onClick={async()=>{ await toggleSet(s.id, !s.is_active); await load(); }}>{s.is_active?"Disable":"Enable"}</button>
                    </div>
                  </Td>
                </tr>
              )}
            </Tbody>
          </Table>
        </div>
      </Card>
    </div>
  );
}