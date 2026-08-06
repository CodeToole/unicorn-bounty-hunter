import 'dart:convert';

import 'package:firebase_functions/firebase_functions.dart';
import 'package:google_generative_ai/google_generative_ai.dart';
import 'package:http/http.dart' as http;

final STRIPE_SECRET_KEY = defineSecret('STRIPE_SECRET_KEY');
final GEMINI_API_KEY = defineSecret('GEMINI_API_KEY');

// ──────────────────────────────────────────────────────────
// Firestore REST API — Lead Capture
//
// Uses the GCE metadata server to obtain an OAuth2 access
// token (automatic on Cloud Run / Cloud Functions gen2),
// then writes a document to the `leads` collection via
// the Firestore REST API.
// ──────────────────────────────────────────────────────────
const _firestoreProjectId = 'ubh-production-2026';

const _allowedOrigins = {
  'https://unicornbountyhunters.com',
  'https://ubh-production-2026.web.app',
  'http://localhost:8080',
  'http://localhost:3000',
};

String _getAllowedOrigin(Map<String, String> headers) {
  final origin = headers['origin'] ?? headers['Origin'];
  if (origin != null && _allowedOrigins.contains(origin)) {
    return origin;
  }
  // Default to the first allowed origin if not matched or missing
  return 'https://unicornbountyhunters.com';
}

/// Fetches an OAuth2 access token from the GCE metadata server.
/// This is the standard way Cloud Run workloads authenticate to
/// Google APIs without a service account key file.
Future<String> _getAccessToken() async {
  final tokenResponse = await http.get(
    Uri.parse(
      'http://metadata.google.internal/computeMetadata/v1/instance/'
      'service-accounts/default/token',
    ),
    headers: {'Metadata-Flavor': 'Google'},
  );
  if (tokenResponse.statusCode != 200) {
    throw Exception(
      'Failed to retrieve access token from metadata server '
      '(status ${tokenResponse.statusCode}): ${tokenResponse.body}',
    );
  }
  final tokenData = jsonDecode(tokenResponse.body) as Map<String, dynamic>;
  return tokenData['access_token'] as String;
}

/// Writes a lead document to the Firestore `leads` collection.
/// Returns the created document name on success.
Future<String> _writeLeadToFirestore({
  required Map<String, dynamic> leadFields,
  required String source,
}) async {
  final accessToken = await _getAccessToken();

  // Convert the flat Dart map into Firestore Value objects.
  final firestoreFields = <String, dynamic>{};
  for (final entry in leadFields.entries) {
    if (entry.value == null) continue;
    if (entry.value is int) {
      firestoreFields[entry.key] = {'integerValue': entry.value.toString()};
    } else {
      firestoreFields[entry.key] = {'stringValue': entry.value.toString()};
    }
  }
  // Add metadata fields.
  firestoreFields['source'] = {'stringValue': source};
  firestoreFields['createdAt'] = {
    'timestampValue': DateTime.now().toUtc().toIso8601String(),
  };

  final url = Uri.parse(
    'https://firestore.googleapis.com/v1/projects/$_firestoreProjectId/'
    'databases/(default)/documents/leads',
  );

  final response = await http.post(
    url,
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'fields': firestoreFields}),
  );

  if (response.statusCode != 200 && response.statusCode != 201) {
    throw Exception(
      'Firestore write failed (status ${response.statusCode}): '
      '${response.body}',
    );
  }

  final doc = jsonDecode(response.body) as Map<String, dynamic>;
  return doc['name'] as String;
}

/// Writes a subscriber email to the Firestore `subscribers` collection.
Future<String> _writeSubscriberToFirestore({required String email}) async {
  final accessToken = await _getAccessToken();

  final firestoreFields = <String, dynamic>{
    'email': {'stringValue': email},
    'createdAt': {'timestampValue': DateTime.now().toUtc().toIso8601String()},
  };

  final url = Uri.parse(
    'https://firestore.googleapis.com/v1/projects/$_firestoreProjectId/'
    'databases/(default)/documents/subscribers',
  );

  final response = await http.post(
    url,
    headers: {
      'Authorization': 'Bearer $accessToken',
      'Content-Type': 'application/json',
    },
    body: jsonEncode({'fields': firestoreFields}),
  );

  if (response.statusCode != 200 && response.statusCode != 201) {
    throw Exception(
      'Firestore write to subscribers failed (status ${response.statusCode}): '
      '${response.body}',
    );
  }

  final doc = jsonDecode(response.body) as Map<String, dynamic>;
  return doc['name'] as String;
}

void main(List<String> args) async {
  await runFunctions((firebase) {
    // Basic HTTPS onRequest function
    firebase.https.onRequest(name: 'helloWorld', (request) async {
      return Response.ok('Hello from Dart Cloud Functions!');
    });

    // Basic callable function
    firebase.https.onCall(name: 'greet', (request, response) async {
      final data = request.data as Map<String, dynamic>?;
      final name = data?['name'] ?? 'World';
      return CallableResult({'message': 'Hello, $name!'});
    });

    // ──────────────────────────────────────────────────────────
    // Direct-to-Consumer Email Capture
    // ──────────────────────────────────────────────────────────
    firebase.https.onRequest(name: 'subscribe', (request) async {
      // Handle CORS preflight request
      if (request.method == 'OPTIONS') {
        return Response(
          204,
          headers: {
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
          },
        );
      }

      if (request.method != 'POST') {
        return Response(
          405,
          body: jsonEncode({'error': 'Method Not Allowed. Use POST.'}),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      }

      final String bodyString;
      try {
        bodyString = await request.readAsString();
      } on Exception catch (e) {
        logger.error('Failed to read request body', {
          'endpoint': 'subscribe',
          'error': e.toString(),
        });
        return Response(
          400,
          body: jsonEncode({'error': 'Unable to read request body.'}),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      }

      final Map<String, dynamic> payload;
      try {
        payload = jsonDecode(bodyString) as Map<String, dynamic>;
      } on FormatException {
        return Response(
          400,
          body: jsonEncode({'error': 'Invalid JSON payload.'}),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      }

      final email = payload['email'] as String?;
      if (email == null || email.isEmpty) {
        return Response(
          400,
          body: jsonEncode({'error': 'Missing required field: email.'}),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      }

      try {
        final docName = await _writeSubscriberToFirestore(email: email);
        logger.info('Subscriber captured to Firestore', {
          'endpoint': 'subscribe',
          'firestoreDoc': docName,
          'email': email,
        });

        try {
          final webhookUrl = Uri.parse(
            'https://script.google.com/macros/s/AKfycbyfqQ-JqgVpyq9jfx0ykcabSpegIEowHWirx60B7RwY3rVYk-u6-nvqAvwQAQnDgDWH8g/exec',
          );
          await http
              .post(
                webhookUrl,
                headers: {'Content-Type': 'application/json'},
                body: jsonEncode({'email': email}),
              )
              .timeout(const Duration(seconds: 10));
          logger.info('Subscriber forwarded to Google Workspace webhook', {
            'endpoint': 'subscribe',
            'email': email,
          });
        } on Exception catch (e) {
          logger.error('Google Workspace webhook failed', {
            'endpoint': 'subscribe',
            'email': email,
            'error': e.toString(),
          });
        }

        return Response.ok(
          jsonEncode({
            'status': 'success',
            'message': 'Subscribed successfully.',
          }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      } on Exception catch (e) {
        logger.error('Firestore subscriber capture failed', {
          'endpoint': 'subscribe',
          'email': email,
          'error': e.toString(),
        });
        return Response(
          500,
          body: jsonEncode({
            'error': 'Internal server error.',
            'details': e.toString(),
          }),
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
          },
        );
      }
    });

    // ──────────────────────────────────────────────────────────
    // Studio Booking Process
    //
    // Webhook stub for Stripe/Square checkout when an artist
    // books a $50/hr studio block. Accepts POST with JSON body:
    //   { "artistName", "requestedDate", "blockDuration" }
    // ──────────────────────────────────────────────────────────
    firebase.https.onRequest(name: 'studioBookingProcess', (request) async {
      if (request.method != 'POST') {
        return Response(
          405,
          body: jsonEncode({'error': 'Method Not Allowed. Use POST.'}),
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
    });

    // ──────────────────────────────────────────────────────────
    // Create Stripe Checkout Session
    // ──────────────────────────────────────────────────────────
    firebase.https.onRequest(
      name: 'createStripeCheckout',
      options: HttpsOptions(secrets: [STRIPE_SECRET_KEY]),
      (request) async {
        // Handle CORS preflight request
        if (request.method == 'OPTIONS') {
          return Response(
            204,
            headers: {
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
              'Access-Control-Allow-Methods': 'POST, OPTIONS',
              'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            },
          );
        }

        if (request.method != 'POST') {
          return Response(
            405,
            body: jsonEncode({'error': 'Method Not Allowed. Use POST.'}),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }

        final String bodyString;
        try {
          bodyString = await request.readAsString();
        } on Exception catch (e) {
          logger.error('Failed to read request body', {
            'endpoint': 'createStripeCheckout',
            'error': e.toString(),
          });
          return Response(
            400,
            body: jsonEncode({'error': 'Unable to read request body.'}),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }

        final Map<String, dynamic> payload;
        try {
          payload = jsonDecode(bodyString) as Map<String, dynamic>;
        } on FormatException {
          return Response(
            400,
            body: jsonEncode({'error': 'Invalid JSON payload.'}),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }

        final artistName = payload['artistName'] as String?;
        final blockDuration = payload['blockDuration'] as int?;
        final sessionName = payload['sessionName'] as String?;
        final email = payload['email'] as String?;

        if (artistName == null ||
            blockDuration == null ||
            sessionName == null) {
          return Response(
            400,
            body: jsonEncode({
              'error':
                  'Missing required fields: artistName, blockDuration, sessionName.',
            }),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }

        // ── LEAD CAPTURE: Write to Firestore BEFORE Stripe ──
        // This ensures we have the lead data even if the user
        // abandons the Stripe checkout page.
        try {
          final docName = await _writeLeadToFirestore(
            leadFields: {
              'artistName': artistName,
              'email': email,
              'sessionType': sessionName,
              'blockDuration': blockDuration,
            },
            source: 'stripe-checkout',
          );
          logger.info('Lead captured to Firestore', {
            'endpoint': 'createStripeCheckout',
            'firestoreDoc': docName,
            'artistName': artistName,
          });
        } on Exception catch (e) {
          // Log the failure but DO NOT block the checkout flow.
          // The lead write is critical but should not prevent
          // a paying customer from completing their purchase.
          logger.error('Firestore lead capture failed — continuing to Stripe', {
            'endpoint': 'createStripeCheckout',
            'artistName': artistName,
            'error': e.toString(),
          });
        }

        final stripeKey = STRIPE_SECRET_KEY.value().trim();
        if (stripeKey.isEmpty) {
          logger.error('STRIPE_SECRET_KEY secret parameter is empty', {
            'endpoint': 'createStripeCheckout',
          });
          return Response(
            500,
            body: jsonEncode({
              'error': 'Stripe payment integration configuration failure.',
            }),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }

        final totalCostInCents = blockDuration * 50 * 100;

        try {
          final stripeResponse = await http.post(
            Uri.parse('https://api.stripe.com/v1/checkout/sessions'),
            headers: {
              'Authorization': 'Bearer $stripeKey',
              'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: {
              'success_url': 'https://ubh-production-2026.web.app/success',
              'cancel_url': 'https://ubh-production-2026.web.app/services',
              'mode': 'payment',
              'line_items[0][price_data][currency]': 'usd',
              'line_items[0][price_data][product_data][name]':
                  '$sessionName - $artistName',
              'line_items[0][price_data][unit_amount]':
                  totalCostInCents.toString(),
              'line_items[0][quantity]': '1',
              if (email != null && email.isNotEmpty) 'customer_email': email,
            },
          );

          if (stripeResponse.statusCode == 200 ||
              stripeResponse.statusCode == 201) {
            final Map<String, dynamic> stripeData =
                jsonDecode(stripeResponse.body) as Map<String, dynamic>;
            final checkoutUrl = stripeData['url'] as String?;

            if (checkoutUrl == null) {
              logger.error('Stripe response missing session URL', {
                'endpoint': 'createStripeCheckout',
                'response': stripeResponse.body,
              });
              return Response(
                500,
                body: jsonEncode({'error': 'Failed to generate checkout URL.'}),
                headers: {
                  'Content-Type': 'application/json',
                  'Access-Control-Allow-Origin': _getAllowedOrigin(
                    request.headers,
                  ),
                },
              );
            }

            return Response.ok(
              jsonEncode({'checkoutUrl': checkoutUrl}),
              headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': _getAllowedOrigin(
                  request.headers,
                ),
              },
            );
          } else {
            logger.error('Stripe API error', {
              'endpoint': 'createStripeCheckout',
              'statusCode': stripeResponse.statusCode,
              'response': stripeResponse.body,
            });
            return Response(
              stripeResponse.statusCode,
              body: jsonEncode({
                'error': 'Stripe transaction failed to initiate.',
                'details': stripeResponse.body,
              }),
              headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': _getAllowedOrigin(
                  request.headers,
                ),
              },
            );
          }
        } on Exception catch (e) {
          logger.error('Stripe connection failed', {
            'endpoint': 'createStripeCheckout',
            'error': e.toString(),
          });
          return Response(
            500,
            body: jsonEncode({
              'error': 'Failed to connect to payment processor.',
              'details': e.toString(),
            }),
            headers: {
              'Content-Type': 'application/json',
              'Access-Control-Allow-Origin': _getAllowedOrigin(request.headers),
            },
          );
        }
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
      options: HttpsOptions(secrets: [GEMINI_API_KEY]),
      (request) async {
        if (request.method != 'POST') {
          return Response(
            405,
            body: jsonEncode({'error': 'Method Not Allowed. Use POST.'}),
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
        final email = payload['email'] as String?;
        final phoneNumber = payload['phoneNumber'] as String?;
        final requestedDate = payload['requestedDate'] as String?;

        if (artistName == null ||
            email == null ||
            phoneNumber == null ||
            requestedDate == null) {
          return Response(
            400,
            body: jsonEncode({
              'error':
                  'Missing required fields: artistName, email, phoneNumber, requestedDate.',
            }),
            headers: {'Content-Type': 'application/json'},
          );
        }

        // ── Secure API Key Retrieval ──────────────────────────
        // Exposed to Cloud Run via Google Cloud Secret Manager.
        // Set with: firebase functions:secrets:set GEMINI_API_KEY
        final apiKey = GEMINI_API_KEY.value().trim();
        if (apiKey.isEmpty) {
          logger.error('GEMINI_API_KEY secret parameter is empty', {
            'endpoint': 'musicalChairsIntake',
          });
          return Response(
            500,
            body: jsonEncode({
              'error': 'AI Evaluation infrastructure configuration failure.',
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
- Email: $email
- Phone: $phoneNumber
- Requested Slot: $requestedDate
- Track Link: [Will be delivered via AirDrop/Direct transfer]

Analyze this request against our strict brand parameters (High fidelity, authentic bars, raw independent hustle, rejecting mass market formula). Since the track will be delivered in-person, make a preliminary vibe check based on their booking details.

Return a strict, flat JSON response matching this model schema exactly:
{
  "vibeCheckPassed": true/false,
  "scoutingNotes": "A brief 2-sentence breakdown of why they fit or do not fit the underground aesthetic using our authoritative label voice.",
  "recommendedNextStep": "Assign Identity Code / Request alternative mixes / Deny entry"
}
''';

        // ── LEAD CAPTURE: Write to Firestore BEFORE Gemini ──
        try {
          final docName = await _writeLeadToFirestore(
            leadFields: {
              'artistName': artistName,
              'email': email,
              'phoneNumber': phoneNumber,
              'requestedDate': requestedDate,
            },
            source: 'musical-chairs-intake',
          );
          logger.info('Lead captured to Firestore', {
            'endpoint': 'musicalChairsIntake',
            'firestoreDoc': docName,
            'artistName': artistName,
          });
        } on Exception catch (e) {
          logger
              .error('Firestore lead capture failed — continuing to AI eval', {
                'endpoint': 'musicalChairsIntake',
                'artistName': artistName,
                'error': e.toString(),
              });
        }

        logger.info('Sending application to Gemini evaluation engine', {
          'endpoint': 'musicalChairsIntake',
          'artistName': artistName,
          'email': email,
          'requestedDate': requestedDate,
        });

        try {
          final response = await model.generateContent([Content.text(prompt)]);
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
