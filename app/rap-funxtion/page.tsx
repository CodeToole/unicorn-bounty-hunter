"use client";

import { useState, useEffect } from "react";

export default function RapFunxtionPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  return (
    <div className="bg-surface text-on-surface min-h-screen pt-32 pb-16 px-6">
      <div className="max-w-5xl mx-auto flex flex-col gap-12">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-black font-['Space_Grotesk'] text-[#00e3fd] tracking-tighter uppercase mb-4">RAP FUNXTION</h1>
          <p className="text-zinc-400 font-['Manrope'] text-lg tracking-widest uppercase">Live Energy. Underground Prestige.</p>
        </div>

        {/* Video Embed */}
        <div className="w-full bg-[#0e0e0e] border border-[#262626] p-2 md:p-4 shadow-[0_20px_40px_rgba(0,227,253,0.05)]">
          {mounted && (
            <div className="relative w-full aspect-video">
              <iframe 
                className="absolute top-0 left-0 w-full h-full"
                src="https://www.youtube.com/embed/JD74UuKKSgU?si=dJOb9PU5wGIzv21F" 
                title="Rap Funxtion Video Player" 
                frameBorder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                referrerPolicy="strict-origin-when-cross-origin" 
                allowFullScreen
              ></iframe>
            </div>
          )}
        </div>

        {/* Teaser Block */}
        <div className="text-center mt-12">
          <h2 className="text-3xl font-black text-white font-['Space_Grotesk'] tracking-widest uppercase mb-6">NEXT CITY LOADING...</h2>
          <p className="text-zinc-400 font-['Manrope'] max-w-xl mx-auto mb-8">Make sure you are on the Tribe email list to receive the secure location coordinates for the next Rap FunXtion event.</p>
          <a href="/" className="inline-block bg-[#00e3fd] text-black px-10 py-4 font-['Space_Grotesk'] font-bold text-sm tracking-widest uppercase hover:bg-[#00c5dd] active:scale-95 transition-all">JOIN THE TRIBE</a>
        </div>
      </div>
    </div>
  );
}
