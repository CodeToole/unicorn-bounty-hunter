"use client";

import { useState, useEffect } from "react";

export default function ServicesPage() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{role: string, text: string}[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userText = input;
    setMessages((prev) => [...prev, { role: "user", text: userText }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userText }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "system", text: data.message || data.error }]);
    } catch (error) {
      setMessages((prev) => [...prev, { role: "system", text: "Connection error." }]);
    }
    setIsLoading(false);
  };

  return (
    <div className="bg-surface text-on-surface min-h-screen pt-24 pb-12 px-6">
      {mounted && (
        <div className="w-full max-w-4xl mx-auto mt-12 mb-16 bg-[#0e0e0e] border border-[#262626] p-8">
          <div className="flex items-center gap-3 mb-6">
            <span className="material-symbols-outlined text-secondary text-2xl">smart_toy</span>
            <h2 className="text-2xl font-black text-white font-['Space_Grotesk'] tracking-tighter uppercase">Studio Concierge</h2>
          </div>
          <p className="text-zinc-400 font-['Manrope'] mb-6">Ask the UBH AI about mixing rates, available analog gear, or booking policies before reserving your block.</p>
          
          <div className="bg-[#131313] border border-[#262626] h-[300px] p-4 mb-4 font-['Manrope'] text-sm flex flex-col gap-4 overflow-y-auto">
            <div className="flex gap-3 items-start text-zinc-300">
              <span className="material-symbols-outlined text-secondary">bolt</span>
              <p><strong className="text-white">UBH System:</strong> Connection established. What do you need to know about the studio?</p>
            </div>
            {messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 items-start ${msg.role === 'user' ? 'text-zinc-400' : 'text-secondary'}`}>
                <span className="material-symbols-outlined">{msg.role === 'user' ? 'person' : 'bolt'}</span>
                <p><strong className="text-white">{msg.role === 'user' ? 'You' : 'UBH System'}:</strong> {msg.text}</p>
              </div>
            ))}
            {isLoading && <div className="text-zinc-500 text-xs tracking-widest uppercase animate-pulse">Processing...</div>}
          </div>

          <form onSubmit={handleSend} className="flex gap-2">
            <input type="text" value={input} onChange={(e) => setInput(e.target.value)} placeholder="e.g., Do you mix vocals remotely?" className="flex-1 bg-[#131313] border border-[#262626] text-white px-4 py-3 font-['Manrope'] text-sm focus:outline-none focus:border-[#00e3fd] transition-colors" />
            <button type="submit" disabled={isLoading} className="bg-secondary text-black px-6 py-3 font-headline font-bold text-sm tracking-widest uppercase hover:bg-secondary-dim active:scale-95 transition-all disabled:opacity-50">SEND</button>
          </form>
        </div>
      )}

      {mounted && (
        <div className="w-full max-w-4xl mx-auto my-16 bg-surface-container-highest p-4 rounded-none border border-outline/20 shadow-[0_20px_40px_rgba(0,227,253,0.05)]">
          <iframe src="https://calendar.google.com/calendar/appointments/schedules/AcZssZ2uQJv23R2QyomV62yBxkrbf2eg1SuJtrHaWvo9ccbl3PNkByKS3M_wY93jcndjQ0JQhlGkp8k9?gv=true" style={{ border: 0 }} className="w-full min-h-[600px] bg-transparent" frameBorder="0"></iframe>
        </div>
      )}
    </div>
  );
}
