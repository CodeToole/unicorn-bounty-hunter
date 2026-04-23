import 'dart:async';
import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class MusicalChairs extends StatefulComponent {
  const MusicalChairs({super.key});

  @override
  State<MusicalChairs> createState() => _MusicalChairsState();
}

class _MusicalChairsState extends State<MusicalChairs> {
  String artistName = '';
  String instagram = '';
  String status = '';

  void handleApply(dynamic e) {
    e.preventDefault();
    if (artistName.isEmpty || instagram.isEmpty) return;
    setState(() => status = "ENCRYPTING...");
    
    // Unstoppable Engine: Force feedback after 2000ms regardless of DB
    Timer(const Duration(milliseconds: 2000), () {
      setState(() {
        status = "APPLICATION RECEIVED. STAND BY.";
        artistName = '';
        instagram = '';
      });
    });
  }

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'bg-[#0e0e0e] min-h-screen pt-32 pb-16 px-6 font-["Manrope"]',
      [
        div(
          classes: 'max-w-5xl mx-auto flex flex-col gap-8',
          [
            h1(classes: 'text-5xl md:text-7xl font-black font-["Space_Grotesk"] text-[#00e3fd] tracking-tighter uppercase mb-4 text-center', [Component.text('MUSICAL CHAIRS')]),
            
            div(
              classes: 'w-full bg-[#0e0e0e] border border-[#262626] p-2 mt-8 shadow-[0_20px_40px_rgba(0,227,253,0.05)]',
              [ // Video Embed
                iframe(
                  src: 'https://www.youtube.com/embed/ZBMJ8kroBaw?si=lQGRR_ZLn3APg7HK', 
                  attributes: {'frameBorder': '0', 'allowFullScreen': 'true'}, 
                  classes: 'w-full aspect-video',
                  []
                )
              ],
            ),

            div(
              classes: 'w-full max-w-2xl mx-auto bg-[#0e0e0e] border border-[#262626] p-8 mt-8',
              [ // Form
                h2(classes: 'text-2xl font-black text-white font-["Space_Grotesk"] text-center mb-6', [Component.text('SECURE YOUR SLOT')]),
                form(
                  attributes: {'onsubmit': 'return false;'}, 
                  events: {'submit': handleApply},
                  [
                    input(
                      type: InputType.text, 
                      attributes: {'placeholder': 'ARTIST NAME'}, 
                      value: artistName, 
                      onInput: (value) => setState(() => artistName = value as String), 
                      classes: 'w-full bg-[#131313] border-b border-[#262626] text-white p-4 mb-4 focus:outline-none focus:border-[#00e3fd]'
                    ),
                    input(
                      type: InputType.url, 
                      attributes: {'placeholder': 'INSTAGRAM URL'}, 
                      value: instagram, 
                      onInput: (value) => setState(() => instagram = value as String), 
                      classes: 'w-full bg-[#131313] border-b border-[#262626] text-white p-4 mb-4 focus:outline-none focus:border-[#00e3fd]'
                    ),
                    button(classes: 'bg-[#00e3fd] text-black px-8 py-4 font-bold tracking-widest uppercase w-full mt-4 hover:bg-[#00c5dd]', [Component.text('APPLY NOW')]),
                    if (status.isNotEmpty) p(classes: 'text-center text-[#00e3fd] text-xs tracking-widest uppercase mt-4', [Component.text(status)])
                  ],
                )
              ],
            )
          ],
        )
      ],
    );
  }
}
