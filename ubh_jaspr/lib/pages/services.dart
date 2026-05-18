import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../components/booking_button.dart';

class Services extends StatefulComponent {
  const Services({super.key});
  @override
  State<Services> createState() => _ServicesState();
}

class _ServicesState extends State<Services> {
  String artistName = '';
  String requestedDate = '';
  String blockDuration = '';
  String errorMessage = '';
  bool isLoading = false;
  bool isSuccess = false;

  void handleSend(dynamic e) async {
    e.preventDefault();
    if (artistName.trim().isEmpty || requestedDate.trim().isEmpty || blockDuration.trim().isEmpty) return;

    setState(() {
      isLoading = true;
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
          isSuccess = true;
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
        isSuccess ? div([
          h2([Component.text('DETAILS SAVED')], classes: 'text-2xl font-black text-[#00e3fd] font-["Space_Grotesk"] tracking-tighter uppercase mb-2 text-center'),
          p([Component.text('Please select your preferred session below to finalize booking:')], classes: 'text-center text-white mb-8 font-["Manrope"]'),
          div([
            // 1. Shadow Talk Button
            BookingButton('''
              <link href="https://calendar.google.com/calendar/scheduling-button-script.css" rel="stylesheet">
              <script src="https://calendar.google.com/calendar/scheduling-button-script.js" async></script>
              <script>
              (function() {
                var target = document.currentScript;
                window.addEventListener('load', function() {
                  calendar.schedulingButton.load({
                    url: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ3lCKQxjodQnYnU25G0CN3Dlm53CcyOTHwH4feyUIH4NW7BUu3pcXTfX6o3dw03gMjZVBQuenLF?gv=true',
                    color: '#039BE5',
                    label: 'Book Shadow Talk',
                    target,
                  });
                });
              })();
              </script>
            '''),

            // 2. Studio Booking Button
            BookingButton('''
              <script>
              (function() {
                var target = document.currentScript;
                window.addEventListener('load', function() {
                  calendar.schedulingButton.load({
                    url: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true',
                    color: '#039BE5',
                    label: 'Book Studio Time',
                    target,
                  });
                });
              })();
              </script>
            '''),
          ], classes: 'flex flex-col md:flex-row gap-6 justify-center items-center'),
        ]) : div([
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
              button([Component.text(isLoading ? 'SAVING...' : 'SAVE DETAILS & CONTINUE TO CALENDAR')], 
                attributes: isLoading ? {'disabled': 'true'} : {},
                classes: 'w-full bg-[#00e3fd] text-black px-6 py-3 font-bold tracking-widest uppercase hover:bg-[#00c5dd] disabled:opacity-50 disabled:cursor-not-allowed'
              ),
              if (errorMessage.isNotEmpty)
                p([Component.text(errorMessage)], classes: 'text-red-500 mt-4 font-["Manrope"] text-center font-bold')
            ]
          )
        ])
      ], classes: 'w-full max-w-4xl mx-auto mt-12 bg-[#0e0e0e] border border-[#262626] p-8'),
    ], classes: 'bg-[#0e0e0e] min-h-screen pt-24 pb-12 px-6');
  }
}
