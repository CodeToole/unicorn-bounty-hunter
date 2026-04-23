import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:jaspr_router/jaspr_router.dart';

class Header extends StatefulComponent {
  const Header({super.key});

  @override
  State<Header> createState() => _HeaderState();
}

class _HeaderState extends State<Header> {
  bool isMobileMenuOpen = false;

  void toggleMenu() {
    setState(() {
      isMobileMenuOpen = !isMobileMenuOpen;
    });
  }

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'fixed top-0 w-full z-50 bg-[#0e0e0e]/95 backdrop-blur-xl border-b border-[#262626]',
      [
        div(
          classes: 'max-w-7xl mx-auto px-6 h-20 flex items-center justify-between',
          [
            // Logo
            Link(
              to: '/',
              children: [
                span([Component.text('UBH')], classes: 'text-2xl font-black tracking-tighter text-white'),
              ],
            ),

            // Desktop Navigation
            div(
              classes: 'hidden md:flex items-center gap-8',
              [
                _navLink('/services', 'SERVICES & STUDIO'),
                _navLink('/musical-chairs', 'SHOWCASE'),
                _navLink('/rap-funxtion', 'RAP FUNXTION'),
              ],
            ),

            // Mobile Toggle
            button(
              onClick: toggleMenu,
              classes: 'md:hidden text-white p-2 flex items-center gap-2',
              [
                span(
                  [Component.text(isMobileMenuOpen ? 'CLOSE' : 'MENU')],
                  classes: 'text-xs font-bold tracking-[0.2em]',
                ),
              ],
            ),
          ],
        ),

        // Mobile Menu Overlay
        if (isMobileMenuOpen)
          div(
            classes: 'fixed inset-0 w-full h-[100dvh] bg-[#0e0e0e]/98 backdrop-blur-3xl z-[100] flex flex-col items-center justify-center gap-12',
            [
              // Close button inside overlay
              button(
                onClick: toggleMenu,
                classes: 'absolute top-8 right-8 text-white text-sm font-bold tracking-[0.3em]',
                [Component.text('CLOSE')],
              ),
              
              _mobileNavLink('/', 'HOME'),
              _mobileNavLink('/services', 'SERVICES & STUDIO'),
              _mobileNavLink('/musical-chairs', 'SHOWCASE'),
              _mobileNavLink('/rap-funxtion', 'RAP FUNXTION'),
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
    return div(
      classes: 'text-4xl md:text-6xl font-black tracking-tighter text-white hover:text-[#00e3fd] transition-all duration-500',
      [
        button(
          onClick: toggleMenu,
          classes: 'bg-transparent border-none p-0',
          [
            Link(
              to: to,
              children: [Component.text(label)],
            ),
          ],
        ),
      ],
    );
  }
}
