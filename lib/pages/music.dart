import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class MusicPage extends StatelessComponent {
  const MusicPage({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'min-h-screen bg-black text-white px-6 py-12',
      [
        // Header Section
        div(classes: 'max-w-6xl mx-auto text-center mb-12', [
          h1(classes: 'text-4xl font-bold text-[#FFD700] tracking-wider uppercase mb-2', [
            text('THE VAULT'),
          ]),
          p(classes: 'text-gray-400 text-sm max-w-md mx-auto', [
            text('Support the roster directly. Stream and purchase official UBH catalog releases via Bandcamp.'),
          ]),
        ]),

        // Album Grid Section
        div(
          classes: 'max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-2 gap-8 justify-items-center',
          [
            // Album 1: Wilderness
            div(classes: 'w-full max-w-[380px] bg-[#111111] p-4 rounded-xl border border-[#1a1a1a] shadow-2xl', [
              h3(classes: 'text-lg font-bold text-[#FFD700] mb-3 text-center', [text('Wilderness')]),
              iframe(
                [],
                src: 'https://bandcamp.com/EmbeddedPlayer/album=2846109268/size=large/bgcol=333333/linkcol=FFD700/tracklist=false/transparent=true/',
                attributes: {
                  'seamless': '',
                  'style': 'border: 0; width: 100%; height: 470px;',
                },
              ),
            ]),

            // Album 2: Locals Only
            div(classes: 'w-full max-w-[380px] bg-[#111111] p-4 rounded-xl border border-[#1a1a1a] shadow-2xl', [
              h3(classes: 'text-lg font-bold text-[#FFD700] mb-3 text-center', [text('Locals Only')]),
              iframe(
                [],
                src: 'https://bandcamp.com/EmbeddedPlayer/album=3414750159/size=large/bgcol=333333/linkcol=FFD700/tracklist=false/transparent=true/',
                attributes: {
                  'seamless': '',
                  'style': 'border: 0; width: 100%; height: 470px;',
                },
              ),
            ]),
          ],
        ),
      ],
    );
  }
}
