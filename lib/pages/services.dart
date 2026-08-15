import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:universal_web/web.dart' as web;
import '../components/booking_button.dart';
import '../components/client_info_form.dart';

@client
class Services extends StatefulComponent {
  const Services({super.key});
  @override
  State<Services> createState() => _ServicesState();
}

class _ServicesState extends State<Services> {
  String artistName = '';
  String email = '';
  String phoneNumber = '';
  String requestedDate = '';
  int blockDuration = 1;
  int shadowTalkDuration = 1;
  String activeTab = 'studio'; // 'studio' or 'shadow'
  String errorMessage = '';
  bool isLoading = false;

  // Define Google Calendar booking URLs for shadow talk / fallbacks
  final Map<String, String> studioCalendarUrls = {
    '1': 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ18Lc7xaYyOdDrF7p9awdh1SF3MYJhGgc_0B6sN2UH7wfIJRvxN-C2P6xztIHuWYMdXxskU4j1Z?gv=true', // 1 Hour ($50)
  };

  @override
  Component build(BuildContext context) {
    return div([
      div([
        div([
          // Sleek Cyberpunk Tab Selector
          div([
            button([text('STUDIO SESSION (\$50/HR)')],
              onClick: () => setState(() { activeTab = 'studio'; }),
              classes: 'flex-1 py-4 text-center font-bold tracking-wider font-["Space_Grotesk"] uppercase border-b-2 transition-all duration-300 ' + 
                (activeTab == 'studio' 
                  ? 'text-[#D4AF37] border-[#D4AF37] bg-[#0a0a0a]' 
                  : 'text-[#888888] border-[#262626] hover:text-white hover:border-[#555555] bg-transparent')
            ),
            button([text('SHADOW TALK (PODCAST)')],
              onClick: () => setState(() { 
                activeTab = 'shadow'; 
                blockDuration = shadowTalkDuration;
              }),
              classes: 'flex-1 py-4 text-center font-bold tracking-wider font-["Space_Grotesk"] uppercase border-b-2 transition-all duration-300 ' + 
                (activeTab == 'shadow' 
                  ? 'text-[#D4AF37] border-[#D4AF37] bg-[#0a0a0a]' 
                  : 'text-[#888888] border-[#262626] hover:text-white hover:border-[#555555] bg-transparent')
            ),
          ], classes: 'flex mb-8 border-b border-[#262626]'),

          h2([text(activeTab == 'studio' ? 'STUDIO BOOKING' : 'SHADOW TALK PODCAST BOOKING')], 
            classes: 'text-2xl font-black text-white font-["Space_Grotesk"] tracking-tighter uppercase mb-6 text-center'),
          
          form(
            attributes: {'onsubmit': 'return false;'}, 
            [
              ClientInfoForm(
                artistName: artistName,
                onArtistNameChanged: (value) => setState(() => artistName = value),
                email: email,
                onEmailChanged: (value) => setState(() => email = value),
                phoneNumber: phoneNumber,
                onPhoneNumberChanged: (value) => setState(() => phoneNumber = value),
                requestedDate: requestedDate,
                onRequestedDateChanged: (value) => setState(() => requestedDate = value),
              ),
              if (activeTab == 'studio')
                div([
                  label([text('SESSION DURATION')], classes: 'block text-xs font-bold text-[#888] mb-2 font-["Space_Grotesk"] tracking-widest'),
                  select(
                    classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-6 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] cursor-pointer appearance-none',
                    onChange: (value) {
                      final selectedString = value.isNotEmpty ? value.first : '1';
                      setState(() => blockDuration = int.tryParse(selectedString) ?? 1);
                    },
                    [
                      option(value: '1', selected: blockDuration == 1, [text('1 Hour (\$50)')]),
                      option(value: '2', selected: blockDuration == 2, [text('2 Hours (\$100)')]),
                      option(value: '3', selected: blockDuration == 3, [text('3 Hours (\$150)')]),
                      option(value: '4', selected: blockDuration == 4, [text('4 Hours (\$200)')]),
                      option(value: '5', selected: blockDuration == 5, [text('5 Hours (\$250)')]),
                      option(value: '6', selected: blockDuration == 6, [text('6 Hours (\$300)')]),
                      option(value: '7', selected: blockDuration == 7, [text('7 Hours (\$350)')]),
                      option(value: '8', selected: blockDuration == 8, [text('8 Hours (\$400)')]),
                    ]
                  ),
                ]),
              if (activeTab == 'shadow')
                div([
                  label([text('PACKAGE SELECT')], classes: 'block text-xs font-bold text-[#888] mb-2 font-["Space_Grotesk"] tracking-widest'),
                  select(
                    classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-6 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] cursor-pointer appearance-none',
                    onChange: (value) {
                      final selectedString = value.isNotEmpty ? value.first : '1';
                      final val = int.tryParse(selectedString) ?? 1;
                      setState(() {
                        shadowTalkDuration = val;
                        blockDuration = val;
                      });
                    },
                    [
                      option(value: '1', selected: shadowTalkDuration == 1, [text('Shadow Talk Podcast Only (\$50)')]),
                      option(value: '2', selected: shadowTalkDuration == 2, [text('Shadow Talk + Musical Chairs Bundle (\$100)')]),
                    ]
                  ),
                ]),
              button([
                text(isLoading ? 'PREPARING CHECKOUT...' : 'CONTINUE TO SECURE CHECKOUT')
              ], 
                attributes: isLoading ? {'disabled': 'true'} : {},
                events: {
                  'click': (e) async {
                    e.preventDefault();
                    if (artistName.trim().isEmpty || email.trim().isEmpty || phoneNumber.trim().isEmpty || requestedDate.trim().isEmpty) return;
                    
                    web.window.alert('Connecting to Stripe Gateway...');
                    
                    setState(() {
                      isLoading = true;
                      errorMessage = '';
                    });

                    try {
                      final sessionName = activeTab == 'studio' ? 'Studio Session' : (shadowTalkDuration == 2 ? 'Shadow Talk + Musical Chairs Bundle' : 'Shadow Talk Podcast Only');

                      final response = await http.post(
                        Uri.parse('https://create-stripe-checkout-loz23viwea-uc.a.run.app'),
                        headers: {'Content-Type': 'application/json'},
                        body: jsonEncode({
                          'artistName': artistName,
                          'email': email,
                          'phoneNumber': phoneNumber,
                          'requestedDate': requestedDate,
                          'blockDuration': blockDuration, // Active blockDuration state variable
                          'sessionName': sessionName,
                        }),
                      );

                      if (response.statusCode == 200) {
                        final checkoutUrl = jsonDecode(response.body)['checkoutUrl'];
                        web.window.location.href = checkoutUrl;
                      } else {
                        web.window.alert('Server Error: ${response.statusCode} - ${response.body}');
                        setState(() {
                          errorMessage = 'Stripe payment integration failure.';
                          isLoading = false;
                        });
                      }
                    } catch (error) {
                      web.window.alert('Client/Network Error: $error');
                      setState(() {
                        errorMessage = 'Error connecting to server: $error';
                        isLoading = false;
                      });
                    }
                  }
                },
                classes: 'w-full bg-[#0a0a0a] border border-[#D4AF37] text-[#D4AF37] px-6 py-3 font-bold tracking-widest uppercase hover:bg-[#D4AF37] hover:text-[#0a0a0a] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed font-["Space_Grotesk"]'
              ),
              if (errorMessage.isNotEmpty)
                p([text(errorMessage)], classes: 'text-red-500 mt-4 font-["Manrope"] text-center font-bold')
            ]
          )
        ])
      ], classes: 'w-full max-w-4xl mx-auto mt-12 bg-[#0a0a0a] border border-[#262626] p-8'),
    ], classes: 'bg-[#0a0a0a] min-h-screen pt-24 pb-12 px-6');
  }
}
