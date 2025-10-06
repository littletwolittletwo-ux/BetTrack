export function Field({label, children}:{label:string; children:React.ReactNode}){
  return <label className="grid gap-1">
    <span className="text-sm text-mut">{label}</span>
    {children}
  </label>;
}