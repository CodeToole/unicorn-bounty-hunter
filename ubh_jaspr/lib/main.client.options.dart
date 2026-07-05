// dart format off
// ignore_for_file: type=lint

// GENERATED FILE, DO NOT MODIFY
// Generated with jaspr_builder

import 'package:jaspr/client.dart';

import 'package:ubh_jaspr/components/email_capture.dart'
    deferred as _email_capture;
import 'package:ubh_jaspr/pages/musical_chairs.dart'
    deferred as _musical_chairs;
import 'package:ubh_jaspr/pages/podcast.dart' deferred as _podcast;
import 'package:ubh_jaspr/pages/services.dart' deferred as _services;

/// Default [ClientOptions] for use with your Jaspr project.
///
/// Use this to initialize Jaspr **before** calling [runApp].
///
/// Example:
/// ```dart
/// import 'main.client.options.dart';
///
/// void main() {
///   Jaspr.initializeApp(
///     options: defaultClientOptions,
///   );
///
///   runApp(...);
/// }
/// ```
ClientOptions get defaultClientOptions => ClientOptions(
  clients: {
    'email_capture': ClientLoader(
      (p) => _email_capture.EmailCapture(),
      loader: _email_capture.loadLibrary,
    ),
    'musical_chairs': ClientLoader(
      (p) => _musical_chairs.MusicalChairs(),
      loader: _musical_chairs.loadLibrary,
    ),
    'podcast': ClientLoader(
      (p) => _podcast.PodcastPage(),
      loader: _podcast.loadLibrary,
    ),
    'services': ClientLoader(
      (p) => _services.Services(),
      loader: _services.loadLibrary,
    ),
  },
);
