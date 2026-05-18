import 'dart:convert';
import 'dart:io' show Platform;

import 'package:firebase_functions/firebase_functions.dart';
import 'package:google_generative_ai/google_generative_ai.dart';

void main(List<String> args) async {
  await runFunctions((firebase) {
    // Basic HTTPS onRequest function
    firebase.https.onRequest(
      name: 'helloWorld',
      (request) async {
        return Response.ok('Hello from Dart Cloud Functions!');
      },
    );

    // Basic callable function
    firebase.https.onCall(name: 'greet', (request, response) async {
      final data = request.data as Map<String, dynamic>?;
      final name = data?['name'] ?? 'World';
      return CallableResult({'message': 'Hello, $name!'});
    });

    // ──────────────────────────────────────────────────────────
    // Studio Booking Process
    //
    // Webhook stub for Stripe/Square checkout when an artist
    // books a $50/hr studio block. Accepts POST with JSON body:
    //   { "artistName", "requestedDate", "blockDuration" }
    // ──────────────────────────────────────────────────────────
    firebase.https.onRequest(
      name: 'studioBookingProcess',
      (request) async {
        if (request.method != 'POST') {
          return Response(
            405,
            body: jsonEncode({
              'error': 'Method Not Allowed. Use POST.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final String bodyString;
        try {
          bodyString = await request.readAsString();
        } on Exception catch (e) {
          logger.error('Failed to read request body', {
            'endpoint': 'studioBookingProcess',
            'error': e.toString(),
          });
          return Response(
            400,
            body: jsonEncode({'error': 'Unable to read request body.'}),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final Map<String, dynamic> payload;
        try {
          payload = jsonDecode(bodyString) as Map<String, dynamic>;
        } on FormatException {
          return Response(
            400,
            body: jsonEncode({'error': 'Invalid JSON payload.'}),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final artistName = payload['artistName'] as String?;
        final requestedDate = payload['requestedDate'] as String?;
        final blockDuration = payload['blockDuration'] as int?;

        if (artistName == null ||
            requestedDate == null ||
            blockDuration == null) {
          return Response(
            400,
            body: jsonEncode({
              'error':
                  'Missing required fields: artistName, requestedDate, '
                  'blockDuration.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        logger.info('Studio booking received', {
          'endpoint': 'studioBookingProcess',
          'artistName': artistName,
          'requestedDate': requestedDate,
          'blockDuration': blockDuration,
          'ratePerHour': 50,
          'estimatedTotal': blockDuration * 50,
        });

        return Response.ok(
          jsonEncode({
            'status': 'received',
            'message':
                'Booking request for $artistName on $requestedDate '
                '($blockDuration hr) logged successfully.',
          }),
          headers: {'Content-Type': 'application/json'},
        );
      },
    );

    // ──────────────────────────────────────────────────────────
    // Musical Chairs Intake — AI-Powered A&R Scouting Engine
    //
    // Accepts POST with JSON body:
    //   { "artistName", "instagramUrl", "trackLink" }
    //
    // Passes the application to Gemini for an inline
    // "Underground Prestige" vibe check evaluation and returns
    // the structured AI verdict to the caller.
    // ──────────────────────────────────────────────────────────
    firebase.https.onRequest(
      name: 'musicalChairsIntake',
      (request) async {
        if (request.method != 'POST') {
          return Response(
            405,
            body: jsonEncode({
              'error': 'Method Not Allowed. Use POST.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final String bodyString;
        try {
          bodyString = await request.readAsString();
        } on Exception catch (e) {
          logger.error('Failed to read request body', {
            'endpoint': 'musicalChairsIntake',
            'error': e.toString(),
          });
          return Response(
            400,
            body: jsonEncode({'error': 'Unable to read request body.'}),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final Map<String, dynamic> payload;
        try {
          payload = jsonDecode(bodyString) as Map<String, dynamic>;
        } on FormatException {
          return Response(
            400,
            body: jsonEncode({'error': 'Invalid JSON payload.'}),
            headers: {'Content-Type': 'application/json'},
          );
        }

        final artistName = payload['artistName'] as String?;
        final instagramUrl = payload['instagramUrl'] as String?;
        final trackLink = payload['trackLink'] as String?;

        if (artistName == null ||
            instagramUrl == null ||
            trackLink == null) {
          return Response(
            400,
            body: jsonEncode({
              'error':
                  'Missing required fields: artistName, instagramUrl, '
                  'trackLink.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        // ── Secure API Key Retrieval ──────────────────────────
        // Exposed to Cloud Run via Google Cloud Secret Manager.
        // Set with: firebase functions:secrets:set GEMINI_API_KEY
        final apiKey = Platform.environment['GEMINI_API_KEY'];
        if (apiKey == null || apiKey.isEmpty) {
          logger.error('GEMINI_API_KEY environment variable is unassigned', {
            'endpoint': 'musicalChairsIntake',
          });
          return Response(
            500,
            body: jsonEncode({
              'error':
                  'AI Evaluation infrastructure configuration failure.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        // ── Initialize the Gemini Model Inline ────────────────
        final model = GenerativeModel(
          model: 'gemini-1.5-flash',
          apiKey: apiKey,
          generationConfig: GenerationConfig(
            responseMimeType: 'application/json',
          ),
        );

        // ── Construct the A&R Evaluation Prompt ───────────────
        final prompt = '''
You are the automated A&R Scouting Engine for Unicorn Bounty Hunters (UBH), an independent music label matching the "Underground Prestige" identity.

Evaluate the following applicant profile for entry into the collective:
- Artist Name: $artistName
- Instagram URL: $instagramUrl
- Prototyped Track Link: $trackLink

Analyze this request against our strict brand parameters (High fidelity, authentic bars, raw independent hustle, rejecting mass market formula).

Return a strict, flat JSON response matching this model schema exactly:
{
  "vibeCheckPassed": true/false,
  "scoutingNotes": "A brief 2-sentence breakdown of why they fit or do not fit the underground aesthetic using our authoritative label voice.",
  "recommendedNextStep": "Assign Identity Code / Request alternative mixes / Deny entry"
}
''';

        logger.info('Sending application to Gemini evaluation engine', {
          'endpoint': 'musicalChairsIntake',
          'artistName': artistName,
          'instagramUrl': instagramUrl,
          'trackLink': trackLink,
        });

        try {
          final response = await model.generateContent([
            Content.text(prompt),
          ]);
          final aiResult = response.text ?? '{}';

          return Response.ok(
            aiResult,
            headers: {'Content-Type': 'application/json'},
          );
        } on Exception catch (e) {
          logger.error('Gemini evaluation failed', {
            'endpoint': 'musicalChairsIntake',
            'artistName': artistName,
            'error': e.toString(),
          });
          return Response(
            500,
            body: jsonEncode({
              'error': 'A&R evaluation operation interrupted.',
              'details': e.toString(),
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }
      },
    );
  });
}
