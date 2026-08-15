import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

/// Data model for a Rap Funxtion lineup artist.
class _LineupArtist {
  final String name;
  final String tag;

  const _LineupArtist({required this.name, required this.tag});
}

/// The official RF16 lineup.
const List<_LineupArtist> _rf16Lineup = [
  _LineupArtist(name: 'Ali Kazem', tag: 'Headliner'),
  _LineupArtist(name: 'Tayo-Sei', tag: 'Featured'),
  _LineupArtist(name: 'Whoistidez', tag: 'Featured'),
  _LineupArtist(name: 'Lowkee (G.O.M)', tag: 'Featured'),
  _LineupArtist(name: 'Unknown', tag: 'Featured'),
  _LineupArtist(name: 'Yung Illie', tag: 'Featured'),
  _LineupArtist(name: 'Ongopeppo', tag: 'Featured'),
  _LineupArtist(name: 'Merro', tag: 'Featured'),
];

class RapFunxtion extends StatelessComponent {
  const RapFunxtion({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'bg-[#0a0a0a] min-h-screen pt-32 pb-20 px-6',
      [
        div(
          classes: 'max-w-5xl mx-auto flex flex-col gap-16',
          [
            // ──────────────────────────────────────────────
            //  PAGE TITLE
            // ──────────────────────────────────────────────
            div(
              classes: 'text-center',
              [
                h1(
                  [Component.text('RAP FUNXTION — RESCHEDULING IN PROGRESS')],
                  classes:
                      'text-5xl md:text-7xl font-black tracking-tighter text-white leading-none font-["Space_Grotesk"] uppercase',
                ),
                p(
                  [Component.text('The July 19th showcase has been postponed. New dates, venue details, and line-up configurations are currently being finalized. Join the Hunt via our email list to receive immediate confirmation when the new date drops.')],
                  classes:
                      'text-zinc-400 font-["Manrope"] text-base md:text-lg tracking-wide mt-6 max-w-2xl mx-auto',
                ),
              ],
            ),

            // ──────────────────────────────────────────────
            //  EVENT FLYER
            // ──────────────────────────────────────────────
            div(
              classes: 'flex justify-center',
              [
                img(
                  src: '/images/rf16_flyer_new.jpg',
                  alt: 'Rap Funxtion 16 Official Flyer',
                  classes:
                      'max-w-md w-full rounded-lg shadow-lg shadow-[#D4AF37]/20',
                ),
              ],
            ),

            // (── EVENT DETAILS CARD REMOVED — RF16 cancelled, rescheduling in progress ──)

            // ──────────────────────────────────────────────
            //  THE LINEUP
            // ──────────────────────────────────────────────
            div(
              classes: 'pt-8',
              [
                // Section header
                div(
                  classes: 'text-center mb-12',
                  [
                    div(
                      classes: 'flex items-center justify-center gap-4 mb-6',
                      [
                        div(
                          classes:
                              'w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60',
                          [],
                        ),
                        span(
                          classes:
                              'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.5em] uppercase',
                          [Component.text('PERFORMING LIVE')],
                        ),
                        div(
                          classes:
                              'w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60',
                          [],
                        ),
                      ],
                    ),
                    h2(
                      [Component.text('THE LINEUP')],
                      classes:
                          'font-["Space_Grotesk"] text-4xl md:text-5xl lg:text-6xl font-black tracking-tight uppercase text-white',
                    ),
                  ],
                ),

                // Artist Grid
                div(
                  classes:
                      'grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6',
                  [
                    for (final artist in _rf16Lineup)
                      _buildLineupCard(artist),
                  ],
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  /// Builds a single lineup artist card with Black & Gold styling.
  Component _buildLineupCard(_LineupArtist artist) {
    return div(
      classes:
          'group relative bg-[#0d0d0d] border border-[#1a1a1a] '
          'hover:border-[#D4AF37] transition-all duration-300 transform hover:-translate-y-1 '
          'p-6 flex flex-col items-center text-center',
      [
        // Monogram circle
        div(
          classes:
              'w-16 h-16 rounded-full bg-[#111111] border border-[#222222] '
              'group-hover:border-[#D4AF37]/50 transition-colors duration-300 '
              'flex items-center justify-center mb-4',
          [
            span(
              classes:
                  'font-["Space_Grotesk"] text-xl font-bold text-zinc-400 '
                  'group-hover:text-[#D4AF37] transition-colors duration-300',
              [Component.text(artist.name[0].toUpperCase())],
            ),
          ],
        ),

        // Artist name
        h3(
          [Component.text(artist.name)],
          classes:
              'font-["Space_Grotesk"] text-base md:text-lg font-bold tracking-tight text-[#D4AF37] uppercase mb-1',
        ),

        // Tag
        span(
          classes:
              'font-["Manrope"] text-zinc-500 text-xs tracking-widest uppercase',
          [Component.text(artist.tag)],
        ),
      ],
    );
  }
}
