import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-zinc-950 dark:bg-black w-full rounded-none border-t border-zinc-900">
      <div className="flex flex-col md:flex-row justify-between items-center px-10 py-16 gap-10">
        <div className="flex flex-col gap-4">
          <span className="text-xl font-black text-white font-headline uppercase tracking-tighter">
            UBH<span className="text-secondary">/</span>PRESTIGE
          </span>
          <p className="font-body text-[10px] tracking-[0.2em] uppercase text-zinc-600">
            © 2024 UNDERGROUND PRESTIGE. ALL RIGHTS RESERVED.
          </p>
        </div>
        <div className="flex flex-wrap justify-center gap-8">
          <Link
            className="font-body text-[10px] tracking-[0.2em] uppercase text-zinc-600 hover:text-white transition-colors"
            href="/services"
          >
            SERVICES & STUDIO
          </Link>
          <Link
            className="font-body text-[10px] tracking-[0.2em] uppercase text-zinc-600 hover:text-white transition-colors"
            href="/musical-chairs"
          >
            MUSICAL CHAIRS
          </Link>
          <Link
            className="font-body text-[10px] tracking-[0.2em] uppercase text-zinc-600 hover:text-white transition-colors"
            href="/rap-funxtion"
          >
            RAP FUNXTION
          </Link>
          <Link
            className="font-body text-[10px] tracking-[0.2em] uppercase text-zinc-600 hover:text-white transition-colors"
            href="#"
          >
            LEGAL
          </Link>
        </div>
        <div className="flex gap-4">
          <span
            className="material-symbols-outlined text-zinc-600 hover:text-secondary cursor-pointer transition-colors"
            data-icon="brand_awareness"
          >
            brand_awareness
          </span>
          <span
            className="material-symbols-outlined text-zinc-600 hover:text-secondary cursor-pointer transition-colors"
            data-icon="headphones"
          >
            headphones
          </span>
          <span
            className="material-symbols-outlined text-zinc-600 hover:text-secondary cursor-pointer transition-colors"
            data-icon="podcasts"
          >
            podcasts
          </span>
        </div>
      </div>
    </footer>
  );
}
