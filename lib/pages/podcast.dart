import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

@client
class PodcastPage extends StatelessComponent {
  @override
  Component build(BuildContext context) {
    return div([
      h1([Component.text('Podcast Booking')], classes: 'text-4xl font-bold mb-4'),
      p([Component.text('Book your 1-hour session. Cost: \$50.')], classes: 'mb-8'),
      iframe([],
        src: 'YOUR_NEW_PODCAST_CALENDAR_LINK_HERE', // Ali replaces this
        attributes: {
          'width': '100%',
          'height': '600',
          'frameborder': '0',
          'style': 'border: 0'
        },
      ),
    ], classes: 'min-h-screen bg-black text-white p-8');
  }
}
