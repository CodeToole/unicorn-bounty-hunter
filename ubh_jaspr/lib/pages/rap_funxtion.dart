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
                  [Component.text('RAP FUNXTION 16')],
                  classes:
                      'text-5xl md:text-7xl font-black tracking-tighter text-white leading-none font-["Space_Grotesk"] uppercase',
                ),
                p(
                  [Component.text('Live Energy. Underground Prestige.')],
                  classes:
                      'text-zinc-400 font-["Manrope"] text-lg tracking-widest uppercase mt-4',
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

            // ──────────────────────────────────────────────
            //  EVENT DETAILS — Black & Gold
            // ──────────────────────────────────────────────
            div(
              classes:
                  'bg-[#0d0d0d] border border-[#D4AF37]/30 rounded-2xl p-8 md:p-12 text-center space-y-6',
              [
                // Section label
                div(
                  classes: 'flex items-center justify-center gap-4 mb-2',
                  [
                    div(
                      classes:
                          'w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60',
                      [],
                    ),
                    span(
                      classes:
                          'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.5em] uppercase',
                      [Component.text('EVENT DETAILS')],
                    ),
                    div(
                      classes:
                          'w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60',
                      [],
                    ),
                  ],
                ),

                // Date
                div(
                  classes: 'space-y-1',
                  [
                    span(
                      classes:
                          'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block',
                      [Component.text('DATE')],
                    ),
                    p(
                      [
                        Component.text(
                            'Sunday, July 19, 2026')
                      ],
                      classes:
                          'text-white font-["Space_Grotesk"] text-lg md:text-xl font-bold tracking-wide',
                    ),
                  ],
                ),

                // Divider
                div(
                  classes: 'w-20 h-[1px] bg-[#D4AF37]/30 mx-auto',
                  [],
                ),

                // Location
                div(
                  classes: 'space-y-1',
                  [
                    span(
                      classes:
                          'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block',
                      [Component.text('LOCATION')],
                    ),
                    p(
                      [
                        Component.text(
                            'Rat Trap · 3500 W Cervantes, Pensacola, FL')
                      ],
                      classes:
                          'text-white font-["Space_Grotesk"] text-lg md:text-xl font-bold tracking-wide',
                    ),
                  ],
                ),

                // Divider
                div(
                  classes: 'w-20 h-[1px] bg-[#D4AF37]/30 mx-auto',
                  [],
                ),

                // Time
                div(
                  classes: 'space-y-1',
                  [
                    span(
                      classes:
                          'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block',
                      [Component.text('TIME')],
                    ),
                    p(
                      [
                        Component.text(
                            'Doors open at 6:00 PM | Show starts at 7:30 PM')
                      ],
                      classes:
                          'text-white font-["Space_Grotesk"] text-lg md:text-xl font-bold tracking-wide',
                    ),
                  ],
                ),

                // Divider
                div(
                  classes: 'w-20 h-[1px] bg-[#D4AF37]/30 mx-auto',
                  [],
                ),

                // Admission
                div(
                  classes: 'space-y-1',
                  [
                    span(
                      classes:
                          'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.3em] uppercase block',
                      [Component.text('ADMISSION')],
                    ),
                    p(
                      [Component.text('\$10 at the door')],
                      classes:
                          'text-white font-["Space_Grotesk"] text-2xl md:text-3xl font-black tracking-wide',
                    ),
                  ],
                ),
              ],
            ),

            // ──────────────────────────────────────────────
            //  TICKETS BUTTON
            // ──────────────────────────────────────────────
            div(
              classes: 'flex justify-center',
              [
                a(
                  [Component.text('BUY TICKETS')],
                  href: 'https://buytickets.at/ubh/2275875',
                  target: Target.blank,
                  classes:
                      'bg-black border border-[#D4AF37] text-[#D4AF37] font-bold py-4 px-8 mt-6 uppercase tracking-widest hover:bg-[#D4AF37] hover:text-black transition-colors duration-300 block text-center',
                ),
              ],
            ),

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
