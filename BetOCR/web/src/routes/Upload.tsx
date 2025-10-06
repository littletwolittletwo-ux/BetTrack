import { useEffect, useState } from "react";
import { fetchSets, uploadBet, importCSV } from "@/api";
import Dropzone from "@/components/Dropzone";
import { Card, CardTitle } from "@/components/Card";
import { useToast } from "@/components/Toast";
import Modal from "@/components/Modal";

type SetItem = { id:number; name:string; is_active:boolean };

export default function Upload(){
  const [sets,setSets]=useState<SetItem[]>([]);
  const [setId,setSetId]=useState<number|undefined>();
  const [bookmaker,setBk]=useState("Sportsbet");
  const [stake,setStake]=useState("");
  const [file,setFile]=useState<File|null>(null);
  const [preview,setPreview]=useState<string|undefined>();
  const [out,setOut]=useState<any>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [csvFile, setCsvFile] = useState<File|null>(null);
  const [csvResult, setCsvResult] = useState<any>(null);
  const [csvSetId, setCsvSetId] = useState<number|undefined>();
  const { push } = useToast();

  useEffect(()=>{ (async()=>{
    try{
      const s = await fetchSets(true) as SetItem[];
      setSets(s); 
      if(s.length) {
        setSetId(s[0].id);
        setCsvSetId(s[0].id); // Also set default for CSV
      }
    }catch(e:any){ push({ msg: e.message, type:"err"}); }
  })(); }, []);

  const submit = async(e:React.FormEvent) => {
    e.preventDefault();
    if(!file || !setId || !stake){ push({ msg:"All fields required", type:"err"}); return; }
    // Show confirmation modal before upload
    setShowConfirmModal(true);
  };

  const confirmUpload = async() => {
    if(!file || !setId || !stake) return;
    const fd = new FormData();
    fd.append("set_id", String(setId));
    fd.append("bookmaker_name", bookmaker);
    fd.append("stake_manual", stake);
    fd.append("image", file);
    try{
      const resp = await uploadBet(fd);
      setOut(resp);
      setShowConfirmModal(false);
      push({ msg: "Bet uploaded successfully!", type: "ok" });
    }catch(err:any){ 
      setShowConfirmModal(false);
      push({ msg: err.message || "Upload failed", type:"err"}); 
    }
  };

  const handleCSVUpload = async (dryRun: boolean = false) => {
    if (!csvFile) {
      push({ msg: "Please select a CSV file", type: "err" });
      return;
    }
    if (!csvSetId) {
      push({ msg: "Please select a set for the CSV import", type: "err" });
      return;
    }
    
    try {
      const selectedSet = sets.find(s => s.id === csvSetId);
      const defaultSet = selectedSet ? selectedSet.name : String(csvSetId);
      const result = await importCSV(csvFile, dryRun, defaultSet);
      setCsvResult(result);
      if (dryRun) {
        push({ msg: `Dry run complete: ${(result as any).total_rows} rows validated`, type: "ok" });
      } else {
        push({ msg: `CSV imported: ${(result as any).inserted} rows added, ${(result as any).skipped} skipped`, type: "ok" });
      }
    } catch (err: any) {
      push({ msg: err.message || "CSV import failed", type: "err" });
    }
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardTitle>Upload betslip</CardTitle>
        <form className="grid md:grid-cols-2 gap-4 mt-2" onSubmit={submit}>
          <label className="grid gap-1">
            <span className="text-sm text-mut">Set</span>
            <select value={setId} onChange={e=>setSetId(Number(e.target.value))}>
              {sets.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-mut">Bookmaker</span>
            <input value={bookmaker} onChange={e=>setBk(e.target.value)} />
          </label>
          <label className="grid gap-1">
            <span className="text-sm text-mut">Stake (manual)</span>
            <input type="number" step="0.01" value={stake} onChange={e=>setStake(e.target.value)} />
          </label>
          <div className="grid gap-2">
            <span className="text-sm text-mut">Screenshot</span>
            <Dropzone onFile={(f)=>{ setFile(f); setPreview(URL.createObjectURL(f)); }} />
            <input type="file" accept="image/*" onChange={e=>{ const f=e.target.files?.[0]; if(f){ setFile(f); setPreview(URL.createObjectURL(f)); }}}/>
          </div>
          <div className="md:col-span-2">
            <button className="btn px-4 py-2 rounded-xl">Upload</button>
          </div>
        </form>
      </Card>

      {preview && <Card><CardTitle>Preview</CardTitle><img src={preview} className="rounded-xl border border-line mt-2 max-h-[360px] object-contain"/></Card>}
      
      {/* CSV Import Card */}
      <Card>
        <CardTitle>Import CSV</CardTitle>
        <div className="mt-2 space-y-4">
          <div>
            <span className="text-sm text-mut block mb-2">
              Upload a CSV with columns: <code>set,profit</code> or <code>stake,odds,profit</code>
            </span>
            <input 
              type="file" 
              accept=".csv" 
              onChange={(e) => setCsvFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-gray-400
                         file:mr-4 file:py-2 file:px-4
                         file:rounded file:border-0
                         file:text-sm file:font-medium
                         file:bg-blue-600 file:text-white
                         hover:file:bg-blue-700"
            />
          </div>
          
          <div>
            <label className="grid gap-1">
              <span className="text-sm text-mut">Set (for CSV without set column)</span>
              <select value={csvSetId} onChange={e=>setCsvSetId(Number(e.target.value))}>
                {sets.map(s=><option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </label>
          </div>
          
          <div className="flex gap-2">
            <button 
              type="button"
              onClick={() => handleCSVUpload(true)}
              className="btn px-4 py-2 rounded-xl bg-gray-600 hover:bg-gray-700"
              disabled={!csvFile || !csvSetId}
            >
              Preview (Dry Run)
            </button>
            <button 
              type="button"
              onClick={() => handleCSVUpload(false)}
              className="btn px-4 py-2 rounded-xl bg-green-600 hover:bg-green-700"
              disabled={!csvFile || !csvSetId}
            >
              Import CSV
            </button>
          </div>
          
          {csvResult && (
            <div className="mt-4 p-4 bg-[#0f1721] rounded border">
              <h4 className="font-medium mb-2">Import Result</h4>
              <div className="text-sm space-y-1">
                <div>File: <span className="text-blue-400">{csvResult.filename}</span></div>
                <div>Total rows: <span className="text-yellow-400">{csvResult.total_rows}</span></div>
                <div>Inserted: <span className="text-green-400">{csvResult.inserted}</span></div>
                <div>Skipped: <span className="text-red-400">{csvResult.skipped}</span></div>
                {csvResult.errors && csvResult.errors.length > 0 && (
                  <div>
                    <div className="text-red-400 mt-2">Errors:</div>
                    <ul className="list-disc list-inside text-xs text-red-300 ml-2">
                      {csvResult.errors.map((error: any, idx: number) => (
                        <li key={idx}>Row {error.row}: {error.error}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </Card>

      {out && <Card><CardTitle>Parsed result</CardTitle><pre className="mt-2 text-sm overflow-auto">{JSON.stringify(out,null,2)}</pre></Card>}
      
      {/* Pre-upload Confirmation Modal */}
      <Modal 
        open={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        title="Confirm Upload"
        onConfirm={confirmUpload}
        confirmLabel="Upload Bet"
      >
        <div className="space-y-2">
          <div><strong>Set:</strong> {sets.find(s => s.id === setId)?.name}</div>
          <div><strong>Bookmaker:</strong> {bookmaker}</div>
          <div><strong>Stake:</strong> ${stake}</div>
          <div><strong>File:</strong> {file?.name}</div>
        </div>
        <p className="mt-3 text-sm">Are you sure you want to upload this betting slip?</p>
      </Modal>
    </div>
  );
}

