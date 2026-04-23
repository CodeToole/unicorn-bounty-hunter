"use client";

import { useState, useEffect } from "react";
import { collection, addDoc } from "firebase/firestore";
import { db } from "@/lib/firebase";

export default function Page() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleJoinHunt = async (e: React.FormEvent) => {
    e.preventDefault();
    if (email) {
      await addDoc(collection(db, "ubh_subscribers"), { email: email, timestamp: new Date() });
      setStatus("ACCESS GRANTED. WELCOME TO THE TRIBE.");
      setEmail("");
    }
  };

  return (
    <div className="bg-surface text-on-surface selection:bg-secondary selection:text-on-secondary min-h-screen">
      <main className="pt-24">
        {/* Hero Section */}
        {/* ... (rest of the sections) */}
        <section className="relative min-h-screen w-full flex items-center justify-center overflow-hidden">
          {/* Hero Background */}
          <div className="absolute inset-0 z-0">
            <img
              className="w-full h-full object-cover grayscale brightness-50"
              data-alt="Candid high-contrast portrait of a hip-hop artist with cinematic blue and yellow studio lighting, moody atmosphere and architectural depth"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBvtBy7Ou8Mdz3nTMKa9d3jLsi1rKO1uWuZpF7nAY1bhSr__WZpiCoYJHUjyvYNRUK38L2jyLXrxh-SJznHIaBQ7KrJcD0ZxJ-Xv_hkpfOB5_Vfpwj9RF7ohGB9D7SrjnRJ9k9lteTdRs6Ty77jaLbdsRIZwVRHRzJxALNXG2rhm2nj7hnfvr-S66QnYLv4eUPvZ6ZWjDALAQHHQhZj1oc9hwQlmgzaXybqGQbl85Pji7_OCrAIjVD8GeEZg2dj8GrP-UbDLN3gKg"
              alt="Candid high-contrast portrait of a hip-hop artist"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-surface via-transparent to-surface/40"></div>
            <div className="absolute inset-0 bg-gradient-to-r from-surface/80 via-transparent to-surface/20"></div>
          </div>
          {/* Hero Content */}
          <div className="relative z-10 w-full px-6 md:px-12 flex flex-col items-start gap-0">
            <h1 className="font-headline text-[12vw] md:text-[10vw] leading-[0.85] font-black tracking-tighter uppercase">
              UNICORN
              <br />
              <span className="text-secondary text-glow-secondary">BOUNTY</span>
              <br />
              HUNTER
            </h1>
            <div className="mt-8 flex flex-col md:flex-row gap-6 items-start md:items-center">
              <button className="bg-secondary text-on-secondary px-10 py-5 font-headline font-bold text-lg tracking-tighter active:scale-95 transition-all hover:bg-secondary-fixed">
                LISTEN NOW
              </button>
              <div className="flex items-center gap-4 text-outline">
                <div className="w-12 h-[1px] bg-outline"></div>
                <p className="font-body text-xs tracking-widest uppercase">
                  Latest Release: "Obsidian Dreams"
                </p>
              </div>
            </div>
          </div>
          {/* Side Metadata (DAW Inspired) */}
          <div className="absolute right-6 bottom-12 hidden lg:flex flex-col gap-8 text-right border-r border-secondary/20 pr-6">
            <div>
              <p className="font-label text-[10px] text-secondary tracking-widest uppercase mb-1">
                Status
              </p>
              <p className="font-headline text-lg font-bold">RECORDING</p>
            </div>
            <div>
              <p className="font-label text-[10px] text-secondary tracking-widest uppercase mb-1">
                BPM
              </p>
              <p className="font-headline text-lg font-bold">128.00</p>
            </div>
            <div>
              <p className="font-label text-[10px] text-secondary tracking-widest uppercase mb-1">
                Location
              </p>
              <p className="font-headline text-lg font-bold uppercase">
                London / Underground
              </p>
            </div>
          </div>
        </section>

        {/* Music Section: Bento Grid Hybrid */}
        <section className="py-32 px-6 md:px-12 bg-surface">
          <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Artist Statement */}
            <div className="lg:col-span-4 flex flex-col justify-end p-8 bg-surface-container-low border-l-4 border-secondary">
              <h2 className="font-headline text-4xl font-bold mb-6 tracking-tighter uppercase">
                THE
                <br />
                ARCHITECT
              </h2>
              <p className="font-body text-on-surface-variant leading-relaxed">
                ALI is the sonic disruptor behind UBH. Merging high-frequency
                electronics with raw street narrative, redefining the prestige
                of underground soundscapes.
              </p>
            </div>
            {/* Bandcamp Player */}
            <div className="lg:col-span-8 glass-panel p-1 relative">
              <div className="absolute -top-4 -right-4 w-24 h-24 bg-primary/10 -z-10 blur-2xl"></div>
              <div className="w-full h-full min-h-[450px] bg-black flex items-center justify-center">
                <div className="w-full max-w-2xl px-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    <span className="font-label text-[10px] tracking-widest text-outline">
                      STREAMING DIRECT
                    </span>
                  </div>
                  {/* Bandcamp Player */}
                  {mounted && (
                    <div className="flex justify-center w-full my-8">
                      <iframe 
                        style={{ border: 0, width: "350px", height: "621px" }} 
                        src="https://bandcamp.com/EmbeddedPlayer/album=2846109268/size=large/bgcol=333333/linkcol=0f91ff/transparent=true/" 
                        seamless 
                        title="Wilderness by Ali Kazem"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Visual Teaser */}
        <section className="h-[530px] relative">
          <img
            className="w-full h-full object-cover"
            data-alt="Extreme close-up of high-end analog audio mixer with glowing yellow LEDs and intricate knobs in a dark studio setting"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuAIhm8pwfwK-hRLTBKT3kqRTe1JoChg_9b4xs7b997AQRzgdPLm14HSQa6shadLhGUb2GS3dx5I7Jnq0aQyGWWWTf5IruZrZCUhDtmjkp7W2iLdd_JTIL0XjN6W1_XP8Y3hAexgZrNlAJISX0VTl00ZAqoZEmfPcSLUmrghDiHch-pUgB8klb9vJZcMNiZ6u4xskO7Xf2mCz0IOBNuK8a9jdzvz_VbDc5Z_PUi63NaIa4vR9H_yBpF8btXaWmA3RmzSsbtTVBqiLQ"
            alt="Extreme close-up of high-end analog audio mixer"
          />
          <div className="absolute inset-0 bg-surface/60 backdrop-grayscale"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <h3 className="font-headline text-5xl md:text-7xl font-black tracking-[0.2em] uppercase text-white/20 select-none">
                PRESTIGE ONLY
              </h3>
            </div>
          </div>
        </section>

        {/* Lead Capture ('The Tribe') */}
        <section className="py-40 px-6 md:px-12 bg-surface-container-lowest relative overflow-hidden">
          <div className="absolute left-0 top-0 w-full h-[1px] bg-gradient-to-r from-transparent via-secondary/20 to-transparent"></div>
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="font-headline text-5xl md:text-7xl font-bold mb-6 tracking-tighter uppercase">
              THE TRIBE
            </h2>
            <p className="font-body text-xl text-on-surface-variant mb-12 max-w-xl mx-auto">
              Join the Tribe for secret drops, unreleased demos, and VIP access
              to underground sessions.
            </p>
            <form onSubmit={handleJoinHunt} className="flex flex-col md:flex-row gap-0 max-w-2xl mx-auto w-full">
              <input
                className="flex-grow bg-surface-container-highest border-0 border-b border-outline/30 focus:border-secondary focus:ring-0 text-white font-label p-6 placeholder:text-zinc-600 transition-all"
                placeholder="EMAIL_ADDRESS"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <button type="submit" className="bg-secondary text-on-secondary px-12 py-6 font-headline font-black text-sm tracking-[0.2em] hover:bg-secondary-fixed active:scale-95 transition-all">
                JOIN
              </button>
            </form>
            {status && <p className="mt-4 font-label text-secondary text-xs tracking-widest uppercase">{status}</p>}
            <p className="mt-8 font-label text-[10px] text-outline tracking-widest uppercase opacity-40">
              SECURE CONNECTION ESTABLISHED // DATA ENCRYPTED
            </p>
          </div>
        </section>
      </main>
    </div>
  );
}
