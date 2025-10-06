import { useEffect, useState } from "react";
import { Card, CardTitle } from "@/components/Card";
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from "recharts";

type RiskResp = {
  hours:number;
  summary:{ sharpe:number|null; max_drawdown:number|null; var95:number|null; n:number };
  daily_pl: { date:string; pl:number }[];
  exposure_by_set: { name:string; stake:number }[];
  exposure_by_bookmaker: { name:string; stake:number }[];
};

export default function Risk(){
  const [hours, setHours] = useState(720);
  const [data, setData] = useState<RiskResp | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function load(){
    setErr(null);
    try{
      const r = await fetch(`/stats/risk?hours=${hours}`, { headers: { Authorization: "Bearer "+localStorage.getItem("token") } });
      if(!r.ok) throw new Error(await r.text());
      setData(await r.json());
    }catch(e:any){ setErr(e.message || "Failed to load"); }
  }
  useEffect(()=>{ load(); }, [hours]);

  return (
    <div className="grid gap-6">
      <div className="card flex items-center justify-between">
        <div className="font-semibold">Risk Management</div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-mut">Hours</span>
          <input className="w-24" type="number" value={hours} onChange={e=>setHours(Number(e.target.value || 720))}/>
          <button className="btn rounded-xl" onClick={load}>Refresh</button>
        </div>
      </div>

      {err && <div className="card" style={{color:"#ff8e8e"}}>{err}</div>}

      {data && <>
        <div className="grid md:grid-cols-3 gap-4">
          <Card><CardTitle>Sharpe Ratio</CardTitle><div className="text-3xl font-bold">{data.summary.sharpe ?? "—"}</div><div className="text-sm text-mut">Per-bet Sharpe (RF=0)</div></Card>
          <Card><CardTitle>Max Drawdown</CardTitle><div className="text-3xl font-bold">{data.summary.max_drawdown ?? "—"}</div><div className="text-sm text-mut">Peak-to-trough of cumulative P/L</div></Card>
          <Card><CardTitle>VaR (95%)</CardTitle><div className="text-3xl font-bold">{data.summary.var95 ?? "—"}</div><div className="text-sm text-mut">Historical per-bet VaR</div></Card>
        </div>

        <Card>
          <CardTitle>P/L over Time</CardTitle>
          <div className="h-72 mt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.daily_pl}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="pl" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <div className="grid md:grid-cols-2 gap-4">
          <Card>
            <CardTitle>Exposure by Set</CardTitle>
            <div className="h-64 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.exposure_by_set}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="stake" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card>
            <CardTitle>Exposure by Bookmaker</CardTitle>
            <div className="h-64 mt-2">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.exposure_by_bookmaker}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="stake" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </>}
    </div>
  );
}