"use client";

import { useState, useEffect } from "react";

const rf16Lineup = [
  { name: "Ali Kazem", tag: "Headliner" },
  { name: "Tayo-Sei", tag: "Featured" },
  { name: "Whoistidez", tag: "Featured" },
  { name: "Lowkee (G.O.M)", tag: "Featured" },
  { name: "Unknown", tag: "Featured" },
  { name: "Yung Illie", tag: "Featured" },
  { name: "Ongopeppo", tag: "Featured" },
  { name: "Merro", tag: "Featured" },
];

export default function RapFunxtionPage() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  return (
    <div className="bg-[#0a0a0a] text-on-surface min-h-screen pt-32 pb-16 px-6">
      <div className="max-w-5xl mx-auto flex flex-col gap-16">
        {/* Title */}
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-black font-['Space_Grotesk'] text-white tracking-tighter uppercase mb-4">RAP FUNXTION 16</h1>
          <p className="text-zinc-400 font-['Manrope'] text-lg tracking-widest uppercase">Live Energy. Underground Prestige.</p>
        </div>

        {/* Video Embed */}
        <div className="w-full bg-[#0e0e0e] border border-[#262626] p-2 md:p-4 shadow-[0_20px_40px_rgba(255,255,255,0.03)]">
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

        {/* Event Flyer */}
        <div className="flex justify-center">
          <img
            src="/images/rf16_flyer.png"
            alt="Rap Funxtion 16 Official Flyer"
            className="max-w-md w-full rounded-lg shadow-lg shadow-[#D4AF37]/20"
          />
        </div>

        {/* Event Details — Black & Gold */}
        <div className="bg-[#0d0d0d] border border-[#D4AF37]/30 rounded-2xl p-8 md:p-12 text-center space-y-6">
          {/* Section label */}
          <div className="flex items-center justify-center gap-4 mb-2">
            <div className="w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"></div>
            <span className="font-['Manrope'] text-[#D4AF37] text-xs tracking-[0.5em] uppercase">EVENT DETAILS</span>
            <div className="w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"></div>
          </div>

          {/* Location */}
          <div className="space-y-1">
            <span className="font-['Manrope'] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block">LOCATION</span>
            <p className="text-white font-['Space_Grotesk'] text-lg md:text-xl font-bold tracking-wide">Rat Trap · 3500 W Cervantes, Pensacola, FL</p>
          </div>

          <div className="w-20 h-[1px] bg-[#D4AF37]/30 mx-auto"></div>

          {/* Time */}
          <div className="space-y-1">
            <span className="font-['Manrope'] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block">TIME</span>
            <p className="text-white font-['Space_Grotesk'] text-lg md:text-xl font-bold tracking-wide">Doors open at 7:00 PM &nbsp;|&nbsp; Show starts at 8:30 PM</p>
          </div>

          <div className="w-20 h-[1px] bg-[#D4AF37]/30 mx-auto"></div>

          {/* Admission */}
          <div className="space-y-1">
            <span className="font-['Manrope'] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block">ADMISSION</span>
            <p className="text-white font-['Space_Grotesk'] text-2xl md:text-3xl font-black tracking-wide">$10 at the door</p>
          </div>
        </div>

        {/* THE LINEUP */}
        <div className="pt-8">
          {/* Section header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-4 mb-6">
              <div className="w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60"></div>
              <span className="font-['Manrope'] text-[#D4AF37] text-xs tracking-[0.5em] uppercase">PERFORMING LIVE</span>
              <div className="w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60"></div>
            </div>
            <h2 className="font-['Space_Grotesk'] text-4xl md:text-5xl lg:text-6xl font-black tracking-tight uppercase text-white">THE LINEUP</h2>
          </div>

          {/* Artist Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {rf16Lineup.map((artist) => (
              <div
                key={artist.name}
                className="group relative bg-[#0d0d0d] border border-[#1a1a1a] hover:border-[#D4AF37] transition-all duration-300 transform hover:-translate-y-1 p-6 flex flex-col items-center text-center"
              >
                {/* Monogram circle */}
                <div className="w-16 h-16 rounded-full bg-[#111111] border border-[#222222] group-hover:border-[#D4AF37]/50 transition-colors duration-300 flex items-center justify-center mb-4">
                  <span className="font-['Space_Grotesk'] text-xl font-bold text-zinc-400 group-hover:text-[#D4AF37] transition-colors duration-300">
                    {artist.name[0].toUpperCase()}
                  </span>
                </div>

                {/* Artist name */}
                <h3 className="font-['Space_Grotesk'] text-base md:text-lg font-bold tracking-tight text-[#D4AF37] uppercase mb-1">
                  {artist.name}
                </h3>

                {/* Tag */}
                <span className="font-['Manrope'] text-zinc-500 text-xs tracking-widest uppercase">
                  {artist.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
