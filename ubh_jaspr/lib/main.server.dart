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
      raw('''
        <script type="text/javascript">
        var _iub = _iub || [];
        _iub.csConfiguration = {"siteId":4536990,"cookiePolicyId":80575093,"lang":"en","storage":{"useSiteId":true}};
        </script>
        <script type="text/javascript" src="https://cs.iubenda.com/autoblocking/4536990.js"></script>
        <script type="text/javascript" src="//cdn.iubenda.com/cs/gpp/stub.js"></script>
        <script type="text/javascript" src="//cdn.iubenda.com/cs/iubenda_cs.js" charset="UTF-8" async></script>
      '''),
      raw('''
        <script type="text/javascript">
            (function(c,l,a,r,i,t,y){
                c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
                t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
                y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
            })(window, document, "clarity", "script", "wt9isjbqwk");
        </script>
      '''),
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
