import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

@client
class MusicalChairs extends StatelessComponent {
  const MusicalChairs({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'bg-[#0a0a0a] min-h-screen pt-32 pb-16 px-6 font-["Manrope"]',
      [
        div(
          classes: 'max-w-5xl mx-auto flex flex-col gap-8',
          [
            h1(classes: 'text-5xl md:text-7xl font-black font-["Space_Grotesk"] text-white tracking-tighter uppercase mb-4 text-center', [Component.text('MUSICAL CHAIRS')]),
            
            div(
              classes: 'w-full bg-[#0a0a0a] border border-[#262626] p-2 mt-8 shadow-[0_20px_40px_rgba(255,255,255,0.03)]',
              [ // Video Embed
                iframe(
                  src: 'https://www.youtube.com/embed/videoseries?si=tP57kGOI7jnbvDk3&list=PLjZmpfalyZbVRJ9pmVBmtXLYwW8WYDST1', 
                  attributes: {
                    'title': 'YouTube video player',
                    'frameborder': '0',
                    'allow': 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share',
                    'referrerpolicy': 'strict-origin-when-cross-origin',
                    'allowfullscreen': 'true',
                  }, 
                  classes: 'w-full aspect-video rounded-lg shadow-xl border border-[#1a1a1a]',
                  [],
                )
              ],
            ),
          ],
        )
      ],
    );
  }
}
