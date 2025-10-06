import Sidebar from "./Sidebar";
import Topbar from "./Topbar";
import { motion } from "framer-motion";

export default function AppShell({ children }:{ children: React.ReactNode }){
  return (
    <div className="min-h-screen grid" style={{gridTemplateColumns:"280px 1fr"}}>
      <Sidebar />
      <div className="min-h-screen flex flex-col">
        <Topbar />
        <motion.main
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.25 }}
          className="p-6 space-y-6"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}