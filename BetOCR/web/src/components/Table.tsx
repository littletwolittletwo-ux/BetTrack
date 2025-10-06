export function Table({ children }:{ children: React.ReactNode }) {
  return <table className="w-full text-sm">
    {children}
  </table>;
}
export function Thead({ children }:{ children: React.ReactNode }) {
  return <thead className="text-mut"><tr className="border-b border-line">{children}</tr></thead>;
}
export function Th({ children }:{ children: React.ReactNode }) {
  return <th className="text-left p-3">{children}</th>;
}
export function Tbody({ children }:{ children: React.ReactNode }) {
  return <tbody className="divide-y divide-line">{children}</tbody>;
}
export function Td({ children }:{ children: React.ReactNode }) {
  return <td className="p-3 align-top">{children}</td>;
}