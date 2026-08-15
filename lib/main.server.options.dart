// dart format off
// ignore_for_file: type=lint

// GENERATED FILE, DO NOT MODIFY
// Generated with jaspr_builder

import 'package:jaspr/server.dart';
import 'package:ubh_jaspr/components/email_capture.dart' as _email_capture;
import 'package:ubh_jaspr/constants/theme.dart' as _theme;
import 'package:ubh_jaspr/pages/musical_chairs.dart' as _musical_chairs;
import 'package:ubh_jaspr/pages/podcast.dart' as _podcast;
import 'package:ubh_jaspr/pages/services.dart' as _services;

/// Default [ServerOptions] for use with your Jaspr project.
///
/// Use this to initialize Jaspr **before** calling [runApp].
///
/// Example:
/// ```dart
/// import 'main.server.options.dart';
///
/// void main() {
///   Jaspr.initializeApp(
///     options: defaultServerOptions,
///   );
///
///   runApp(...);
/// }
/// ```
ServerOptions get defaultServerOptions => ServerOptions(
  clientId: 'main.client.dart.js',
  clients: {
    _email_capture.EmailCapture: ClientTarget<_email_capture.EmailCapture>(
      'email_capture',
    ),
    _musical_chairs.MusicalChairs: ClientTarget<_musical_chairs.MusicalChairs>(
      'musical_chairs',
    ),
    _podcast.PodcastPage: ClientTarget<_podcast.PodcastPage>('podcast'),
    _services.Services: ClientTarget<_services.Services>('services'),
  },
  styles: () => [..._theme.styles],
);
