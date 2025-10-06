import { useEffect, useState } from "react";
import { listUsers, createUser, updateUser, patchUserStatus, resetPassword } from "@/api";
import { Card, CardTitle } from "@/components/Card";
import { Table, Thead, Th, Tbody, Td } from "@/components/Table";
import { useToast } from "@/components/Toast";
import { getRole } from "@/auth";

type User = { id:number; username:string; role:"admin"|"employee"; is_active:boolean };

export default function Users(){
  const [users,setUsers]=useState<User[]>([]);
  const [u,setU]=useState(""); const [p,setP]=useState(""); const [r,setR]=useState<"admin"|"employee">("employee");
  const { push } = useToast();
  const role = getRole();

  const load=async()=>{ try{ setUsers(await listUsers()); }catch(e:any){ push({msg:e.message,type:"err"}); } };
  useEffect(()=>{ load(); },[]);

  const createU=async()=>{ try{ await createUser(u,p,r); setU(""); setP(""); await load(); push({msg:"User created",type:"ok"});}catch(e:any){ push({msg:e.message,type:"err"});} };
  const toggle=async(id:number, active:boolean)=>{ await patchUserStatus(id, active); await load(); };
  const makeAdmin=async(id:number)=>{ await updateUser(id,{role:"admin"}); await load(); };
  const makeEmployee=async(id:number)=>{ await updateUser(id,{role:"employee"}); await load(); };
  const reset=async(id:number)=>{ const pw=prompt("New password:"); if(!pw) return; await resetPassword(id,pw); push({msg:"Password updated",type:"ok"}); };

  if(role!=="admin") return <div className="card">You need admin access.</div>;

  return (
    <div className="grid gap-6">
      <Card>
        <CardTitle>Create user</CardTitle>
        <div className="grid md:grid-cols-[1fr_1fr_200px_120px] gap-3 mt-2">
          <input placeholder="username" value={u} onChange={e=>setU(e.target.value)}/>
          <input placeholder="password" value={p} onChange={e=>setP(e.target.value)}/>
          <select value={r} onChange={e=>setR(e.target.value as any)}>
            <option value="employee">employee</option>
            <option value="admin">admin</option>
          </select>
          <button className="btn rounded-xl" onClick={createU}>Add</button>
        </div>
      </Card>

      <Card>
        <CardTitle>All users</CardTitle>
        <div className="overflow-auto">
          <Table>
            <Thead>
              <Th>ID</Th><Th>Username</Th><Th>Role</Th><Th>Active</Th><Th>Actions</Th>
            </Thead>
            <Tbody>
              {users.map(u=>
                <tr key={u.id}>
                  <Td>{u.id}</Td>
                  <Td>{u.username}</Td>
                  <Td><span className="badge">{u.role}</span></Td>
                  <Td>{u.is_active?"Yes":"No"}</Td>
                  <Td>
                    <div className="flex gap-2">
                      {u.role==="admin"
                        ? <button className="px-3 py-2 rounded-xl border border-line" onClick={()=>makeEmployee(u.id)}>Make employee</button>
                        : <button className="px-3 py-2 rounded-xl border border-line" onClick={()=>makeAdmin(u.id)}>Make admin</button>}
                      <button className="px-3 py-2 rounded-xl border border-line" onClick={()=>toggle(u.id, !u.is_active)}>{u.is_active?"Disable":"Enable"}</button>
                      <button className="px-3 py-2 rounded-xl border border-line" onClick={()=>reset(u.id)}>Reset PW</button>
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