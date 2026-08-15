import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import '../components/email_capture.dart';

/// Data model for a UBH Roster artist.
class _ArtistData {
  final String name;
  final String handle;
  final String role;
  final String imageUrl;

  const _ArtistData({
    required this.name,
    required this.handle,
    required this.role,
    required this.imageUrl,
  });
}

/// The core UBH artist roster.
const List<_ArtistData> _councilRoster = [
  _ArtistData(
    name: 'Ali Kazem',
    handle: '@shadowurameshi',
    role: 'Founder / Executive Producer',
    imageUrl: '/images/ali.jpg',
  ),
  _ArtistData(
    name: 'Malik Rose',
    handle: '@gentlemanrosayy',
    role: 'Vocalist / A&R',
    imageUrl: '/images/malik.jpg',
  ),
  _ArtistData(
    name: 'Unkn0wn Da Rapper',
    handle: '@unkn0wndaproducer',
    role: 'Producer / Engineer',
    imageUrl: '/images/unknown.jpg',
  ),
  _ArtistData(
    name: 'Yung Illie',
    handle: '@illieaking',
    role: 'Lyricist / Creative Director',
    imageUrl: '/images/illie.png',
  ),
];

class Home extends StatelessComponent {
  const Home({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'w-full',
      [
        // LAYER 1: The Video
        video(
          [source(src: '/videos/webfunxion.mp4', type: 'video/mp4')],
          autoplay: true,
          loop: true,
          muted: true,
          classes: 'fixed inset-0 w-full h-full object-cover z-0',
          attributes: {'playsinline': ''},
        ),

        // LAYER 2: The Dark Overlay
        div(
          classes: 'fixed inset-0 w-full h-full bg-[#050505]/85 z-10',
          [],
        ),

        // FLOATING CTA — REMOVED (RF16 cancelled, rescheduling in progress)

        // LAYER 3: The Scrolling Content
        div(
          classes: 'relative z-20 w-full min-h-screen flex flex-col items-center',
          [
            // ──────────────────────────────────────────────
            //  HERO SECTION
            // ──────────────────────────────────────────────
            section(
              classes: 'relative h-[70vh] w-full flex items-center justify-center',
              [
                // Brand Logo — floating
                div(
                  classes: 'relative z-20 flex flex-col items-center',
                  [
                    img(
                      src: '/images/ubh_logo.jpg',
                      alt: 'Unicorn Bounty Hunters Logo',
                      classes: 'w-64 md:w-96 object-contain shadow-2xl filter drop-shadow-[0_0_40px_rgba(255,255,255,0.2)]',
                    ),
                  ],
                ),
              ],
            ),

            // ──────────────────────────────────────────────
            //  THE UBH ROSTER — Artist Roster
            // ──────────────────────────────────────────────
            section(
              classes: 'relative w-full py-20 md:py-28',
              [
                // Section Header
                div(
                  classes: 'max-w-7xl mx-auto px-6 mb-16 text-center',
                  [
                    // Decorative line + label
                    div(
                      classes: 'flex items-center justify-center gap-4 mb-6',
                      [
                        div(classes: 'w-16 h-[1px] bg-gradient-to-r from-transparent to-[#D4AF37]/60', []),
                        span(
                          classes: 'font-["Manrope"] text-[#D4AF37] text-xs tracking-[0.5em] uppercase',
                          [Component.text('ARTIST ROSTER')],
                        ),
                        div(classes: 'w-16 h-[1px] bg-gradient-to-l from-transparent to-[#D4AF37]/60', []),
                      ],
                    ),
                    h2(
                      classes: 'font-["Space_Grotesk"] text-4xl md:text-5xl lg:text-6xl font-black tracking-tight uppercase text-white',
                      [Component.text('THE UBH ROSTER')],
                    ),
                  ],
                ),

                // Artist Grid — wider container, larger cards
                div(
                  classes: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 px-6 max-w-7xl mx-auto',
                  [
                    for (final artist in _councilRoster)
                      _buildArtistCard(artist),
                  ],
                ),
              ],
            ),
          ],
        ),
        const EmailCapture(),
      ],
    );
  }

  /// Builds a single artist card with brand-consistent styling.
  Component _buildArtistCard(_ArtistData artist) {
    // Strip the @ to build the Instagram profile URL
    final handleWithoutAt = artist.handle.startsWith('@')
        ? artist.handle.substring(1)
        : artist.handle;

    return div(
      classes: 'group relative bg-[#0d0d0d] border border-[#1a1a1a] '
          'hover:border-[#D4AF37] transition-all duration-300 transform hover:-translate-y-1 '
          'p-10 flex flex-col items-center text-center',
      [
        // Artist Image
        img(
          src: artist.imageUrl,
          alt: '${artist.name} photo',
          classes: 'w-20 h-20 md:w-24 md:h-24 rounded-full object-cover border-2 border-[#1a1a1a] group-hover:border-[#D4AF37] transition-colors duration-300 mx-auto mb-4 shadow-lg',
        ),

        // Artist name
        h3(
          classes: 'font-["Space_Grotesk"] text-xl font-bold tracking-tight text-white uppercase mb-1',
          [Component.text(artist.name)],
        ),

        // Role
        span(
          classes: 'font-["Manrope"] text-zinc-500 text-xs tracking-widest uppercase mb-3',
          [Component.text(artist.role)],
        ),

        // Divider
        div(
          classes: 'w-8 h-[1px] bg-[#1a1a1a] group-hover:bg-[#D4AF37]/40 '
              'transition-colors duration-300 mb-3',
          [],
        ),

        // Handle — clickable gold link to Instagram
        a(
          [Component.text(artist.handle)],
          href: 'https://instagram.com/$handleWithoutAt',
          target: Target.blank,
          classes: 'font-["Manrope"] text-sm tracking-wide text-[#D4AF37] hover:text-[#f0d060] transition-colors duration-200',
        ),
      ],
    );
  }
}
