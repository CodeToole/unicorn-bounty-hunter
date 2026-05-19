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
  String blockDuration = '1';
  String bookingType = 'studio'; // 'studio' or 'shadow'
  String errorMessage = '';
  bool isLoading = false;
  bool isSuccess = false;

  // Define Google Calendar booking URLs for each studio duration.
  // Paste your custom Google Calendar schedule links (configured with Stripe payments) here!
  final Map<String, String> studioCalendarUrls = {
    '1': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 1 Hour ($50)
    '2': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 2 Hours ($100) (Replace with your 2-hour link!)
    '3': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 3 Hours ($150) (Replace with your 3-hour link!)
    '4': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 4 Hours ($200) (Replace with your 4-hour link!)
    '5': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 5 Hours ($250) (Replace with your 5-hour link!)
    '6': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 6 Hours ($300) (Replace with your 6-hour link!)
    '7': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 7 Hours ($350) (Replace with your 7-hour link!)
    '8': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 8 Hours ($400) (Replace with your 8-hour link!)
  };

  void handleSend(dynamic e) async {
    e.preventDefault();
    if (artistName.trim().isEmpty || requestedDate.trim().isEmpty) return;

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
          'blockDuration': bookingType == 'studio' ? (int.tryParse(blockDuration) ?? 1) : 1,
          'bookingType': bookingType,
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
          p([Component.text(bookingType == 'studio' 
              ? 'Please finalize your $blockDuration-hour studio booking below:'
              : 'Please finalize your Shadow Talk booking below:')], 
            classes: 'text-center text-white mb-8 font-["Manrope"]'),
          div([
            if (bookingType == 'shadow')
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
              ''')
            else
              BookingButton('''
                <link href="https://calendar.google.com/calendar/scheduling-button-script.css" rel="stylesheet">
                <script src="https://calendar.google.com/calendar/scheduling-button-script.js" async></script>
                <script>
                (function() {
                  var target = document.currentScript;
                  window.addEventListener('load', function() {
                    calendar.schedulingButton.load({
                      url: '${studioCalendarUrls[blockDuration] ?? studioCalendarUrls['1']}',
                      color: '#00e3fd',
                      label: 'Book Studio Time (${blockDuration} ${int.parse(blockDuration) > 1 ? 'Hours' : 'Hour'})',
                      target,
                    });
                  });
                })();
                </script>
              '''),
          ], classes: 'flex flex-col gap-6 justify-center items-center'),
        ]) : div([
          // Sleek Cyberpunk Tab Selector
          div([
            button([Component.text('STUDIO SESSION (\$50/HR)')],
              events: {'click': (dynamic event) => setState(() => bookingType = 'studio')},
              classes: 'flex-1 py-4 text-center font-bold tracking-wider font-["Space_Grotesk"] uppercase border-b-2 transition-all duration-300 ' + 
                (bookingType == 'studio' 
                  ? 'text-[#00e3fd] border-[#00e3fd] bg-[#131313]' 
                  : 'text-[#888888] border-[#262626] hover:text-white hover:border-[#555555] bg-transparent')
            ),
            button([Component.text('SHADOW TALK (PODCAST)')],
              events: {'click': (dynamic event) => setState(() => bookingType = 'shadow')},
              classes: 'flex-1 py-4 text-center font-bold tracking-wider font-["Space_Grotesk"] uppercase border-b-2 transition-all duration-300 ' + 
                (bookingType == 'shadow' 
                  ? 'text-[#00e3fd] border-[#00e3fd] bg-[#131313]' 
                  : 'text-[#888888] border-[#262626] hover:text-white hover:border-[#555555] bg-transparent')
            ),
          ], classes: 'flex mb-8 border-b border-[#262626]'),

          h2([Component.text(bookingType == 'studio' ? 'STUDIO BOOKING' : 'SHADOW TALK PODCAST BOOKING')], 
            classes: 'text-2xl font-black text-white font-["Space_Grotesk"] tracking-tighter uppercase mb-6 text-center'),
          
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
              if (bookingType == 'studio')
                div([
                  label([Component.text('SESSION DURATION')], classes: 'block text-xs font-bold text-[#888] mb-2 font-["Space_Grotesk"] tracking-widest'),
                  select(
                    attributes: {'name': 'blockDuration'},
                    events: {
                      'change': (dynamic event) {
                        final value = event.target.value as String;
                        setState(() => blockDuration = value);
                      }
                    },
                    classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-6 focus:outline-none focus:border-[#00e3fd] font-["Manrope"] cursor-pointer appearance-none',
                    [
                      option(attributes: blockDuration == '1' ? {'value': '1', 'selected': 'true'} : {'value': '1'}, [Component.text('1 Hour (\$50)')]),
                      option(attributes: blockDuration == '2' ? {'value': '2', 'selected': 'true'} : {'value': '2'}, [Component.text('2 Hours (\$100)')]),
                      option(attributes: blockDuration == '3' ? {'value': '3', 'selected': 'true'} : {'value': '3'}, [Component.text('3 Hours (\$150)')]),
                      option(attributes: blockDuration == '4' ? {'value': '4', 'selected': 'true'} : {'value': '4'}, [Component.text('4 Hours (\$200)')]),
                      option(attributes: blockDuration == '5' ? {'value': '5', 'selected': 'true'} : {'value': '5'}, [Component.text('5 Hours (\$250)')]),
                      option(attributes: blockDuration == '6' ? {'value': '6', 'selected': 'true'} : {'value': '6'}, [Component.text('6 Hours (\$300)')]),
                      option(attributes: blockDuration == '7' ? {'value': '7', 'selected': 'true'} : {'value': '7'}, [Component.text('7 Hours (\$350)')]),
                      option(attributes: blockDuration == '8' ? {'value': '8', 'selected': 'true'} : {'value': '8'}, [Component.text('8 Hours (\$400)')]),
                    ]
                  ),
                ]),
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
