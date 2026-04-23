import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:jaspr_router/jaspr_router.dart';
import 'pages/home.dart';
import 'pages/services.dart';
import 'pages/musical_chairs.dart';
import 'pages/rap_funxtion.dart';
import 'components/header.dart';

class App extends StatelessComponent {
  const App({super.key});

  @override
  Component build(BuildContext context) {
    return Router(routes: [
      ShellRoute(
        builder: (context, state, child) => div([
          const Header(), // Global Navigation
          child,          // The active page
        ], classes: 'w-full min-h-screen'),
        routes: [
          Route(path: '/', title: 'UBH | Prestige', builder: (context, state) => const Home()),
          Route(path: '/services', title: 'UBH | Studio', builder: (context, state) => const Services()),
          Route(path: '/musical-chairs', title: 'UBH | Showcase', builder: (context, state) => const MusicalChairs()),
          Route(path: '/rap-funxtion', title: 'UBH | Rap Funxtion', builder: (context, state) => const RapFunxtion()),
        ],
      ),
    ]);
  }
}
