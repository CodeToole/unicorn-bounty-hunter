import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class Home extends StatelessComponent {
  const Home({super.key});

  @override
  Component build(BuildContext context) {
    return section(
      classes: 'relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-[#0e0e0e]',
      [
        // Hero Background
        div(
          classes: 'absolute inset-0 z-0',
          [
            img(
              src: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBvtBy7Ou8Mdz3nTMKa9d3jLsi1rKO1uWuZpF7nAY1bhSr__WZpiCoYJHUjyvYNRUK38L2jyLXrxh-SJznHIaBQ7KrJcD0ZxJ-Xv_hkpfOB5_Vfpwj9RF7ohGB9D7SrjnRJ9k9lteTdRs6Ty77jaLbdsRIZwVRHRzJxALNXG2rhm2nj7hnfvr-S66QnYLv4eUPvZ6ZWjDALAQHHQhZj1oc9hwQlmgzaXybqGQbl85Pji7_OCrAIjVD8GeEZg2dj8GrP-UbDLN3gKg', 
              alt: 'Candid high-contrast portrait of a hip-hop artist',
              classes: 'w-full h-full object-cover grayscale brightness-50',
            ),
            div(classes: 'absolute inset-0 bg-gradient-to-t from-[#0e0e0e] via-transparent to-[#0e0e0e]/40', []),
            div(classes: 'absolute inset-0 bg-gradient-to-r from-[#0e0e0e]/80 via-transparent to-[#0e0e0e]/20', []),
          ],
        ),
        
        // Hero Content
        div(
          classes: 'relative z-10 w-full px-6 md:px-12 flex flex-col items-start gap-0',
          [
            span(classes: 'font-["Manrope"] text-[#00e3fd] text-sm md:text-base tracking-[0.4em] uppercase mb-4 ml-1', [Component.text('ARTIST FOCAL POINT / ALI')]),
            h1(
              classes: 'text-[12vw] md:text-[10vw] leading-[0.85] font-black tracking-tighter uppercase font-["Space_Grotesk"] text-white',
              [
                Component.text('UNICORN'), br(), 
                span(classes: 'text-[#00e3fd] text-shadow-[0_0_20px_rgba(0,227,253,0.3)]', [Component.text('BOUNTY')]), br(), 
                Component.text('HUNTER')
              ],
            ),
            div(
              classes: 'mt-8 flex flex-col md:flex-row gap-6 items-start md:items-center',
              [
                button(classes: 'bg-[#00e3fd] text-black px-10 py-5 font-["Space_Grotesk"] font-bold text-lg tracking-tighter active:scale-95 transition-all hover:bg-[#00c5dd]', [Component.text('LISTEN NOW')]),
                div(
                  classes: 'flex items-center gap-4 text-zinc-500',
                  [
                    div(classes: 'w-12 h-[1px] bg-zinc-500', []),
                    p(classes: 'font-["Manrope"] text-xs tracking-widest uppercase', [Component.text('Latest Release: "Obsidian Dreams"')]),
                  ],
                ),
              ],
            ),

            // UBH Core Mission (Option 1)
            p(
              classes: 'font-["Manrope"] text-zinc-400 text-sm tracking-widest uppercase text-center mt-12 max-w-2xl mx-auto',
              [
                Component.text('Unicorn Bounty Hunters (UBH) is a premier independent music collective and multimedia label forged in Mobile, Alabama. We bridge the gap between raw, philosophical backpack hip-hop and high-frequency electronic production. UBH is not just a roster; it is a unified front of artists, producers, and designers dedicated to preserving the prestige of the underground while engineering the future of sound.')
              ],
            ),
          ],
        ),

        // Side Metadata (DAW Inspired)
        div(
          classes: 'absolute right-6 bottom-12 hidden lg:flex flex-col gap-8 text-right border-r border-[#00e3fd]/20 pr-6 text-white',
          [
            div(
              [
                p(classes: 'font-["Manrope"] text-[10px] text-[#00e3fd] tracking-widest uppercase mb-1', [Component.text('Status')]),
                p(classes: 'font-["Space_Grotesk"] text-lg font-bold', [Component.text('RECORDING')]),
              ],
            ),
            div(
              [
                p(classes: 'font-["Manrope"] text-[10px] text-[#00e3fd] tracking-widest uppercase mb-1', [Component.text('BPM')]),
                p(classes: 'font-["Space_Grotesk"] text-lg font-bold', [Component.text('128.00')]),
              ],
            ),
            div(
              [
                p(classes: 'font-["Manrope"] text-[10px] text-[#00e3fd] tracking-widest uppercase mb-1', [Component.text('Location')]),
                p(classes: 'font-["Space_Grotesk"] text-lg font-bold uppercase', [Component.text('London / Underground')]),
              ],
            ),
          ],
        ),
      ],
    );
  }
}
