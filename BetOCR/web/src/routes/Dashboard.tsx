import { useEffect, useState } from "react";
import { setStats } from "@/api";
import { Card, CardTitle } from "@/components/Card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { useToast } from "@/components/Toast";

export default function Dashboard(){
  const [hours, setHours] = useState(72);
  const [data, setData] = useState<any[]>([]);
  const { push } = useToast();

  async function load(){
    try {
      const stats = await setStats(hours);
      setData(stats.map((s:any)=>({ name: s.set_name, profit: Number(s.net_profit || 0), wins: s.wins, bets: s.total_bets })));
    } catch (e:any) { push({ msg: e.message || "Failed to load stats", type:"err" }); }
  }

  useEffect(()=>{ load(); }, [hours]);

  const totals = {
    bets: data.reduce((s,x)=>s+x.bets,0),
    wins: data.reduce((s,x)=>s+x.wins,0),
    profit: data.reduce((s,x)=>s+x.profit,0).toFixed(2)
  };

  return (
    <div className="grid gap-6">
      <div className="grid md:grid-cols-3 gap-4">
        <Card><CardTitle>Total Bets</CardTitle><div className="text-3xl font-bold">{totals.bets}</div></Card>
        <Card><CardTitle>Wins</CardTitle><div className="text-3xl font-bold">{totals.wins}</div></Card>
        <Card><CardTitle>Net Profit (A$)</CardTitle><div className="text-3xl font-bold">{totals.profit}</div></Card>
      </div>

      <Card>
        <div className="flex items-center justify-between">
          <CardTitle>Profit by Set</CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-sm text-mut">Hours</span>
            <input className="w-24" type="number" value={hours} onChange={e=>setHours(Number(e.target.value||72))}/>
            <button className="btn px-3 py-2 rounded-xl" onClick={load}>Refresh</button>
          </div>
        </div>
        <div className="h-80 mt-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="profit" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </Card>
    </div>
  );
}