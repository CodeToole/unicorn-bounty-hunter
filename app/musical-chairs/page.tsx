"use client";

import { useState, useEffect } from "react";
import { collection, addDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function MusicalChairsPage() {
  const [mounted, setMounted] = useState(false);
  const [artistName, setArtistName] = useState("");
  const [instagram, setInstagram] = useState("");
  const [submitStatus, setSubmitStatus] = useState("");

  useEffect(() => { setMounted(true); }, []);

  const handleApply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!artistName || !instagram) return;
    
    setSubmitStatus("ENCRYPTING...");
    try {
      await addDoc(collection(db, "musical_chairs_leads"), {
        artistName: artistName,
        instagramUrl: instagram,
        submissionDate: new Date(),
        status: "pending",
        notified: false
      });
      setSubmitStatus("APPLICATION RECEIVED. STAND BY.");
      setArtistName("");
      setInstagram("");
    } catch (error) {
      setSubmitStatus("ERROR. COMM LINK SEVERED.");
    }
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen pt-32 pb-16 px-6">
      <div className="max-w-5xl mx-auto flex flex-col gap-12">
        <div className="text-center">
          <h1 className="text-5xl md:text-7xl font-black font-['Space_Grotesk'] text-[#00e3fd] tracking-tighter uppercase mb-4">Musical Chairs</h1>
          <p className="text-zinc-400 font-['Manrope'] text-lg tracking-widest uppercase">The Official UBH Cipher Showcase</p>
        </div>

        {/* Video Embed */}
        <div className="w-full bg-[#0e0e0e] border border-[#262626] p-2 md:p-4 shadow-[0_20px_40px_rgba(0,227,253,0.05)]">
          {mounted && (
            <div className="relative w-full aspect-video">
              <iframe 
                className="absolute top-0 left-0 w-full h-full"
                src="https://www.youtube.com/embed/ZBMJ8kroBaw?si=lQGRR_ZLn3APg7HK" 
                title="Musical Chairs Video Player" 
                frameBorder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                referrerPolicy="strict-origin-when-cross-origin" 
                allowFullScreen
              ></iframe>
            </div>
          )}
        </div>

        {/* Application Form */}
        <div className="w-full max-w-2xl mx-auto bg-[#0e0e0e] border border-[#262626] p-8 mt-8">
          <h2 className="text-2xl font-black text-white font-['Space_Grotesk'] tracking-tighter uppercase mb-6 text-center">Secure Your Slot</h2>
          <form onSubmit={handleApply} className="flex flex-col gap-6">
            <input type="text" required placeholder="ARTIST NAME" value={artistName} onChange={(e) => setArtistName(e.target.value)} className="w-full bg-[#131313] border-0 border-b border-[#262626] text-white px-4 py-4 font-['Manrope'] focus:outline-none focus:border-[#00e3fd] transition-colors" />
            <input type="url" required placeholder="INSTAGRAM URL" value={instagram} onChange={(e) => setInstagram(e.target.value)} className="w-full bg-[#131313] border-0 border-b border-[#262626] text-white px-4 py-4 font-['Manrope'] focus:outline-none focus:border-[#00e3fd] transition-colors" />
            <button type="submit" className="mt-4 bg-[#00e3fd] text-black px-8 py-4 font-['Space_Grotesk'] font-bold text-lg tracking-widest uppercase hover:bg-[#00c5dd] active:scale-95 transition-all w-full">APPLY NOW</button>
            {submitStatus && <p className="text-center font-['Manrope'] text-[#00e3fd] text-xs tracking-widest uppercase mt-4">{submitStatus}</p>}
          </form>
        </div>
      </div>
    </div>
  );
}
