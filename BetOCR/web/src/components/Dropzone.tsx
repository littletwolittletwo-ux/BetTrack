import { useState, DragEvent } from "react";

export default function Dropzone({ onFile }:{ onFile:(f:File)=>void }){
  const [highlight, setH] = useState(false);
  const onDrop = (e:DragEvent<HTMLDivElement>) => {
    e.preventDefault(); setH(false);
    const f = e.dataTransfer.files?.[0]; if (f) onFile(f);
  };
  return (
    <div
      onDragOver={e=>{e.preventDefault(); setH(true);}}
      onDragLeave={()=>setH(false)}
      onDrop={onDrop}
      className={`border-2 border-dashed rounded-2xl p-6 text-center ${highlight ? "border-acc bg-[#0f1721]" : "border-line"}`}
    >
      <div className="text-mut">Drag & drop screenshot here or click below</div>
    </div>
  );
}