import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:jaspr_router/jaspr_router.dart';

class Header extends StatelessComponent {
  const Header({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'fixed top-0 w-full z-50 bg-[#0a0a0a]/95 backdrop-blur-xl border-b border-[#262626]',
      [
        div(
          classes: 'max-w-7xl mx-auto px-4 sm:px-6 h-16 md:h-20 flex items-center justify-between',
          [
            // Logo — text only, clean
            Link(
              to: '/',
              children: [
                span(
                  [Component.text('UBH')],
                  classes: 'text-xl md:text-2xl font-black tracking-tighter text-white font-["Space_Grotesk"]',
                ),
              ],
            ),

            // Desktop Navigation (md and up)
            div(
              classes: 'hidden md:flex items-center gap-8',
              [
                _navLink('/services', 'SERVICES & STUDIO'),
                _navLink('/musical-chairs', 'SHOWCASE'),
                _navLink('/rap-funxtion', 'RAP FUNXTION'),
                _navLink('/music', 'MUSIC'),
                _navLink('/merch', 'MERCH'),
              ],
            ),

            // Mobile Navigation — direct inline links (below md)
            // No toggle/overlay needed. High-contrast gold text links
            // with explicit pointer-events and z-index for iOS safety.
            div(
              classes: 'flex md:hidden items-center gap-3 relative z-50 pointer-events-auto',
              [
                _mobileNavLink('/services', 'SERVICES'),
                _mobileNavLink('/musical-chairs', 'SHOWCASE'),
                _mobileNavLink('/rap-funxtion', 'RAP FX'),
                _mobileNavLink('/music', 'MUSIC'),
                _mobileNavLink('/merch', 'MERCH'),
              ],
            ),
          ],
        ),
      ],
    );
  }

  Component _navLink(String to, String label) {
    return div(
      classes: 'text-[10px] font-bold tracking-[0.3em] text-[#a1a1a1] hover:text-white transition-colors duration-300',
      [
        Link(
          to: to,
          children: [Component.text(label)],
        ),
      ],
    );
  }

  Component _mobileNavLink(String to, String label) {
    return Link(
      to: to,
      children: [
        span(
          [Component.text(label)],
          classes:
              'text-[10px] font-bold tracking-[0.15em] text-[#D4AF37] '
              'active:text-white transition-colors duration-200 '
              'py-2 px-1 inline-block',
        ),
      ],
    );
  }
}
