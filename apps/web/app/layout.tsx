import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "Marketplace Agents",
  description: "Manage Facebook Marketplace monitoring agents",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <div style={{position:"fixed",top:14,right:18,zIndex:1000,display:"flex",gap:8,padding:6,background:"rgba(255,255,255,.92)",border:"1px solid #e5e7eb",borderRadius:10,boxShadow:"0 6px 24px rgba(15,23,42,.08)"}}>
          <Link href="/" style={{padding:"6px 10px",textDecoration:"none",fontSize:13,color:"#334155"}}>Manage</Link>
          <Link href="/agents" style={{padding:"6px 10px",textDecoration:"none",fontSize:13,color:"#334155"}}>Operations</Link>
        </div>
        {children}
      </body>
    </html>
  );
}
