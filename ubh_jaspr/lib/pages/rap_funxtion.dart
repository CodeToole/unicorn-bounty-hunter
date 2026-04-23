import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class RapFunxtion extends StatelessComponent {
  const RapFunxtion({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'bg-[#0e0e0e] min-h-screen pt-32 pb-20 px-6',
      [
        div(
          classes: 'max-w-5xl mx-auto space-y-12',
          [
            // Title
            h1(
              [Component.text('RAP FUNXTION // LIVE ENERGY. UNDERGROUND PRESTIGE.')],
              classes: 'text-4xl md:text-7xl font-black tracking-tighter text-white leading-none',
            ),

            // YouTube Video Placeholder (using div since iframe helper is missing)
            div(
              classes: 'w-full aspect-video border border-[#262626] rounded-2xl overflow-hidden shadow-2xl bg-zinc-900 flex items-center justify-center',
              [
                p(
                  [Component.text('YOUTUBE PREMIERE: SCORPIO SZN')],
                  classes: 'text-zinc-500 font-bold tracking-widest',
                ),
              ],
            ),

            // Teaser
            div(
              classes: 'pt-20 border-t border-[#262626] text-center',
              [
                p(
                  [Component.text('NEXT CITY LOADING...')],
                  classes: 'text-2xl md:text-4xl font-black tracking-[0.5em] text-[#00e3fd] animate-pulse',
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }
}
