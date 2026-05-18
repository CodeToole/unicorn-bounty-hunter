import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../components/booking_button.dart';

class MusicalChairs extends StatefulComponent {
  const MusicalChairs({super.key});

  @override
  State<MusicalChairs> createState() => _MusicalChairsState();
}

class _MusicalChairsState extends State<MusicalChairs> {
  String artistName = '';
  String instagram = '';
  String trackLink = '';
  String errorMessage = '';
  bool isLoading = false;
  bool isSuccess = false;

  void handleApply(dynamic e) async {
    e.preventDefault();
    if (artistName.isEmpty || instagram.isEmpty || trackLink.isEmpty) return;
    
    setState(() {
      errorMessage = '';
      isLoading = true;
    });
    
    try {
      final response = await http.post(
        Uri.parse('https://musical-chairs-intake-loz23viwea-uc.a.run.app'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'artistName': artistName,
          'instagramUrl': instagram,
          'trackLink': trackLink,
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
    return div(
      classes: 'bg-[#0e0e0e] min-h-screen pt-32 pb-16 px-6 font-["Manrope"]',
      [
        div(
          classes: 'max-w-5xl mx-auto flex flex-col gap-8',
          [
            h1(classes: 'text-5xl md:text-7xl font-black font-["Space_Grotesk"] text-[#00e3fd] tracking-tighter uppercase mb-4 text-center', [Component.text('MUSICAL CHAIRS')]),
            
            div(
              classes: 'w-full bg-[#0e0e0e] border border-[#262626] p-2 mt-8 shadow-[0_20px_40px_rgba(0,227,253,0.05)]',
              [ // Video Embed
                iframe(
                  src: 'https://www.youtube.com/embed/ZBMJ8kroBaw?si=lQGRR_ZLn3APg7HK', 
                  attributes: {'frameBorder': '0', 'allowFullScreen': 'true'}, 
                  classes: 'w-full aspect-video',
                  []
                )
              ],
            ),

            div(
              classes: 'w-full max-w-2xl mx-auto bg-[#0e0e0e] border border-[#262626] p-8 mt-8',
              [ // Form
                h2(classes: 'text-2xl font-black text-white font-["Space_Grotesk"] text-center mb-6', [Component.text('SECURE YOUR SLOT')]),
                isSuccess ? div(classes: 'flex flex-col items-center justify-center', [
                  p(classes: 'text-center text-white mb-6 font-bold text-lg', [Component.text('Details saved! Please select your slot below:')]),
                  BookingButton('''
                    <script>
                    (function() {
                      var target = document.currentScript;
                      window.addEventListener('load', function() {
                        calendar.schedulingButton.load({
                          url: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ243z66IaSP_i8VyqQzEohv6AQr7S3USVAC4jB6n223LcB9f7HKVqAuHwQtHyQnEQUomYt9_7aq?gv=true',
                          color: '#039BE5',
                          label: 'Book Musical Chairs',
                          target,
                        });
                      });
                    })();
                    </script>
                  '''),
                ]) : form(
                  attributes: {'onsubmit': 'return false;'}, 
                  events: {'submit': handleApply},
                  [
                    input(
                      type: InputType.text, 
                      attributes: {'placeholder': 'ARTIST NAME', 'required': 'true'}, 
                      value: artistName, 
                      onInput: (value) => setState(() => artistName = value as String), 
                      classes: 'w-full bg-[#131313] border-b border-[#262626] text-white p-4 mb-4 focus:outline-none focus:border-[#00e3fd]'
                    ),
                    input(
                      type: InputType.url, 
                      attributes: {'placeholder': 'INSTAGRAM URL', 'required': 'true'}, 
                      value: instagram, 
                      onInput: (value) => setState(() => instagram = value as String), 
                      classes: 'w-full bg-[#131313] border-b border-[#262626] text-white p-4 mb-4 focus:outline-none focus:border-[#00e3fd]'
                    ),
                    input(
                      type: InputType.url, 
                      attributes: {'placeholder': 'TRACK LINK (DRIVE/DROPBOX/CLOUD)', 'required': 'true'}, 
                      value: trackLink, 
                      onInput: (value) => setState(() => trackLink = value as String), 
                      classes: 'w-full bg-[#131313] border-b border-[#262626] text-white p-4 mb-4 focus:outline-none focus:border-[#00e3fd]'
                    ),
                    button(
                      attributes: isLoading ? {'disabled': 'true'} : {},
                      classes: 'bg-[#00e3fd] text-black px-8 py-4 font-bold tracking-widest uppercase w-full mt-4 hover:bg-[#00c5dd] disabled:opacity-50 disabled:cursor-not-allowed', 
                      [Component.text(isLoading ? 'SAVING...' : 'SAVE DETAILS & CONTINUE TO CALENDAR')]
                    ),
                    if (errorMessage.isNotEmpty) p(classes: 'text-center text-red-500 text-xs tracking-widest uppercase mt-4 font-bold', [Component.text(errorMessage)])
                  ],
                )
              ],
            )
          ],
        )
      ],
    );
  }
}
