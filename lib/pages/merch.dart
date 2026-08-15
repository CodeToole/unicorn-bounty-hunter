import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class MerchPage extends StatelessComponent {
  const MerchPage({super.key});

  @override
  Component build(BuildContext context) {
    return div(
      classes: 'min-h-[80vh] flex flex-col items-center justify-center bg-black text-white px-6',
      [
        h1(
          classes: 'text-5xl md:text-7xl font-bold text-[#FFD700] tracking-widest uppercase mb-6 text-center',
          [text('UBH APPAREL')],
        ),
        div(
          classes: 'border border-[#1a1a1a] bg-[#0a0a0a] px-12 py-16 rounded-xl shadow-2xl text-center max-w-2xl',
          [
            h2(
              classes: 'text-3xl font-bold text-white tracking-widest uppercase mb-4',
              [text('COMING SOON')],
            ),
            p(
              classes: 'text-gray-400 text-lg',
              [
                text('The official Unicorn Bounty Hunters collective uniform. Gray and Beige colorways are currently in production. Join the Hunt via the email list to be notified of the first drop.'),
              ],
            ),
          ],
        ),
      ],
    );
  }
}
