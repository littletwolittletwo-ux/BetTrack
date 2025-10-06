export default function Modal({ open, onClose, title, children, onConfirm, confirmLabel="Confirm" }:{
  open: boolean; onClose: ()=>void; title: string; children: React.ReactNode; onConfirm?: ()=>void; confirmLabel?: string;
}){
  if(!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/60" onClick={onClose}></div>
      <div className="relative card w-full max-w-md">
        <div className="text-lg font-semibold mb-2">{title}</div>
        <div className="text-sm text-mut mb-4">{children}</div>
        <div className="flex gap-2 justify-end">
          <button className="px-3 py-2 rounded-xl border border-line" onClick={onClose}>Cancel</button>
          {onConfirm && <button className="btn px-3 py-2 rounded-xl" onClick={onConfirm}>{confirmLabel}</button>}
        </div>
      </div>
    </div>
  );
}