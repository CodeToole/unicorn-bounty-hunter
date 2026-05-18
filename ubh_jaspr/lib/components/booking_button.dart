import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class BookingButton extends StatelessComponent {
  final String htmlSnippet;

  const BookingButton(this.htmlSnippet, {super.key});

  @override
  Component build(BuildContext context) {
    return div([raw(htmlSnippet)]);
  }
}
