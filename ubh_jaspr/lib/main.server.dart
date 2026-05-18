/// The entrypoint for the **server** environment.
///
/// The [main] method will only be executed on the server during pre-rendering.
/// To run code on the client, check the `main.client.dart` file.
library;

import 'package:jaspr/dom.dart';
// Server-specific Jaspr import.
import 'package:jaspr/server.dart';

// Imports the [App] component.
import 'app.dart';

// This file is generated automatically by Jaspr, do not remove or edit.
import 'main.server.options.dart';

void main() {
  // Initializes the server environment with the generated default options.
  Jaspr.initializeApp(
    options: defaultServerOptions,
  );

  // Starts the app.
  //
  // [Document] renders the root document structure (<html>, <head> and <body>)
  // with the provided parameters and components.
  runApp(Document(
    title: 'UNICORN BOUNTY HUNTER',
    head: [
      link(
        href: 'https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..900&family=Manrope:wght@200..800&display=swap',
        rel: 'stylesheet',
      ),
      script(src: 'https://cdn.tailwindcss.com'),
      raw('<script async src="https://www.googletagmanager.com/gtag/js?id=G-K90Z33WLLD"></script>'),
      raw('''
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'G-K90Z33WLLD');
        </script>
      '''),
    ],
    styles: [
      css('html, body').styles(
        padding: .zero,
        margin: .zero,
        backgroundColor: const Color.rgb(14, 14, 14),
      ),
    ],
    body: const App(),
  ));
}
