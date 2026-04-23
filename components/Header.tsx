"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <header className="fixed top-0 w-full z-50 bg-[#0e0e0e]/95 backdrop-blur-xl border-b border-[#262626]">
      <div className="flex justify-between items-center w-full px-6 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-4">
          {/* Mobile Menu Toggle Button */}
          <button 
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} 
            className="md:hidden text-[#00e3fd] active:scale-95 transition-transform z-[110] relative"
            aria-label="Toggle Menu"
          >
            {isMobileMenuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8"><path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
            )}
          </button>
          <Link 
            href="/" 
            onClick={() => setIsMobileMenuOpen(false)}
            className="text-2xl font-black text-[#00e3fd] tracking-tighter font-headline uppercase relative z-[110]"
          >
            PRESTIGE
          </Link>
        </div>
        
        {/* Desktop Navigation */}
        <nav className="hidden md:flex gap-8 items-center">
          <Link className="font-headline uppercase tracking-tighter font-bold text-zinc-400 hover:text-[#00e3fd] transition-all" href="/services">SERVICES & STUDIO</Link>
          <Link className="font-headline uppercase tracking-tighter font-bold text-zinc-400 hover:text-[#00e3fd] transition-all" href="/musical-chairs">MUSICAL CHAIRS</Link>
          <Link className="font-headline uppercase tracking-tighter font-bold text-zinc-400 hover:text-[#00e3fd] transition-all" href="/rap-funxtion">RAP FUNXTION</Link>
        </nav>
        
        <Link 
          href="/services"
          className="hidden md:block bg-[#00e3fd] text-black px-6 py-2 font-headline font-bold text-sm tracking-widest uppercase hover:bg-[#00c5dd] active:scale-95 transition-all text-center"
        >
          Join the Hunt
        </Link>
      </div>

      {/* Full-Screen Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="fixed inset-0 w-full h-[100dvh] bg-[#0e0e0e]/98 backdrop-blur-3xl z-[100] flex flex-col items-center justify-center">
          <nav className="flex flex-col items-center gap-12 w-full px-6">
            <Link onClick={() => setIsMobileMenuOpen(false)} className="font-headline uppercase tracking-tighter font-black text-3xl text-white hover:text-[#00e3fd] transition-all text-center" href="/services">SERVICES & STUDIO</Link>
            <Link onClick={() => setIsMobileMenuOpen(false)} className="font-headline uppercase tracking-tighter font-black text-3xl text-white hover:text-[#00e3fd] transition-all text-center" href="/musical-chairs">MUSICAL CHAIRS</Link>
            <Link onClick={() => setIsMobileMenuOpen(false)} className="font-headline uppercase tracking-tighter font-black text-3xl text-white hover:text-[#00e3fd] transition-all text-center" href="/rap-funxtion">RAP FUNXTION</Link>
            <Link onClick={() => setIsMobileMenuOpen(false)} href="/services" className="mt-8 bg-[#00e3fd] text-black px-10 py-4 font-headline font-bold text-lg tracking-widest uppercase active:scale-95 transition-all w-full max-w-xs text-center">Join the Hunt</Link>
          </nav>
        </div>
      )}
    </header>
  );
}
