import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class Services extends StatefulComponent {
  const Services({super.key});
  @override
  State<Services> createState() => _ServicesState();
}

class _ServicesState extends State<Services> {
  String artistName = '';
  String requestedDate = '';
  String blockDuration = '';
  String statusMessage = '';
  String errorMessage = '';
  bool isLoading = false;

  void handleSend(dynamic e) async {
    e.preventDefault();
    if (artistName.trim().isEmpty || requestedDate.trim().isEmpty || blockDuration.trim().isEmpty) return;

    setState(() {
      isLoading = true;
      statusMessage = '';
      errorMessage = '';
    });

    try {
      final response = await http.post(
        Uri.parse('https://studio-booking-process-loz23viwea-uc.a.run.app'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'artistName': artistName,
          'requestedDate': requestedDate,
          'blockDuration': int.tryParse(blockDuration) ?? 1,
        }),
      );

      if (response.statusCode == 200) {
        setState(() {
          artistName = '';
          requestedDate = '';
          blockDuration = '';
          statusMessage = 'Submission Received';
          isLoading = false;
        });
      } else {
        setState(() {
          errorMessage = 'Error: ${response.statusCode}';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        errorMessage = 'Error connecting to server.';
        isLoading = false;
      });
    }
  }

  @override
  Component build(BuildContext context) {
    return div([
      div([
        h2([Component.text('STUDIO BOOKING')], classes: 'text-2xl font-black text-white font-["Space_Grotesk"] tracking-tighter uppercase mb-6'),
        form(
          attributes: {'onsubmit': 'return false;'}, 
          events: {'submit': handleSend},
          [
            input(
              type: InputType.text, 
              attributes: {'placeholder': 'ARTIST NAME', 'required': 'true'},
              value: artistName,
              onInput: (value) => setState(() => artistName = value as String),
              classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#00e3fd] font-["Manrope"]'
            ),
            input(
              type: InputType.date, 
              attributes: {'placeholder': 'REQUESTED DATE', 'required': 'true'},
              value: requestedDate,
              onInput: (value) => setState(() => requestedDate = value as String),
              classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#00e3fd] font-["Manrope"]'
            ),
            input(
              type: InputType.number, 
              attributes: {'placeholder': 'BLOCK DURATION (HOURS)', 'min': '1', 'required': 'true'},
              value: blockDuration,
              onInput: (value) => setState(() => blockDuration = value as String),
              classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#00e3fd] font-["Manrope"]'
            ),
            button([Component.text(isLoading ? 'SENDING...' : 'SEND')], 
              attributes: isLoading ? {'disabled': 'true'} : {},
              classes: 'w-full bg-[#00e3fd] text-black px-6 py-3 font-bold tracking-widest uppercase hover:bg-[#00c5dd] disabled:opacity-50 disabled:cursor-not-allowed'
            ),
            if (statusMessage.isNotEmpty)
              p([Component.text(statusMessage)], classes: 'text-[#00e3fd] mt-4 font-["Manrope"] text-center font-bold'),
            if (errorMessage.isNotEmpty)
              p([Component.text(errorMessage)], classes: 'text-red-500 mt-4 font-["Manrope"] text-center font-bold')
          ]
        )
      ], classes: 'w-full max-w-4xl mx-auto mt-12 bg-[#0e0e0e] border border-[#262626] p-8'),
      
      div([
        iframe([], 
          src: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true',
          attributes: {
            'width': '100%',
            'height': '600',
            'frameborder': '0',
            'style': 'border: 0'
          },
        )
      ], classes: 'w-full max-w-4xl mx-auto my-16 border border-[#262626]')
    ], classes: 'bg-[#0e0e0e] min-h-screen pt-24 pb-12 px-6');
  }
}
