export function Card({children, className=""}:{children:React.ReactNode; className?:string}){
  return <div className={`card ${className}`}>{children}</div>;
}
export function CardTitle({children}:{children:React.ReactNode}){ return <div className="h1 mb-2">{children}</div>; }
export function CardSub({children}:{children:React.ReactNode}){ return <div className="h2">{children}</div>; }