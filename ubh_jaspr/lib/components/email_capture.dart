import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

@client
class EmailCapture extends StatefulComponent {
  const EmailCapture({super.key});

  @override
  State<EmailCapture> createState() => _EmailCaptureState();
}

class _EmailCaptureState extends State<EmailCapture> {
  bool isPopupOpen = true;
  bool isWidgetOpen = false;
  String email = '';
  String statusMessage = '';
  bool isSuccess = false;
  bool isLoading = false;

  Future<void> _submitEmail() async {
    final trimmedEmail = email.trim();
    if (trimmedEmail.isEmpty) {
      setState(() {
        isSuccess = false;
        statusMessage = 'PLEASE ENTER A VALID EMAIL.';
      });
      return;
    }

    setState(() {
      isLoading = true;
      statusMessage = 'SUBMITTING...';
    });

    try {
      final response = await http.post(
        Uri.parse('https://subscribe-loz23viwea-uc.a.run.app'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': trimmedEmail}),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        setState(() {
          isSuccess = true;
          statusMessage = 'WELCOME TO THE ROSTER.';
          email = '';
        });

        // Auto-close popup after a short delay
        if (isPopupOpen) {
          Future.delayed(const Duration(seconds: 2), () {
            if (mounted) {
              setState(() {
                isPopupOpen = false;
                statusMessage = '';
              });
            }
          });
        }
      } else {
        setState(() {
          isSuccess = false;
          statusMessage = 'SUBMISSION FAILED. TRY AGAIN.';
        });
      }
    } catch (e) {
      setState(() {
        isSuccess = false;
        statusMessage = 'ERROR CONNECTING TO SERVER.';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }

  @override
  Component build(BuildContext context) {
    if (isPopupOpen) {
      return div(
        classes: 'fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-4',
        [
          div(
            classes: 'relative bg-[#0d0d0d] border border-[#d4af37]/30 rounded-xl max-w-md w-full p-8 text-center shadow-2xl',
            [
              // X Close Button
              button(
                classes: 'absolute top-4 right-4 text-zinc-400 hover:text-white transition-colors duration-200 cursor-pointer text-xl font-bold bg-transparent border-0',
                onClick: () {
                  setState(() {
                    isPopupOpen = false;
                    statusMessage = '';
                  });
                },
                [text('×')]
              ),
              
              h2(
                classes: 'text-3xl md:text-4xl font-extrabold font-["Space_Grotesk"] text-[#d4af37] tracking-wider mb-2 uppercase',
                [text('JOIN THE HUNT')]
              ),
              
              p(
                classes: 'text-zinc-400 text-sm mb-6 max-w-xs mx-auto font-["Manrope"]',
                [text('Subscribe for exclusive UBH updates, early drops, and priority studio booking.')]
              ),
              
              input(
                type: InputType.email,
                classes: 'w-full bg-[#141414] border border-[#262626] focus:border-[#d4af37] text-white px-4 py-3 rounded-lg outline-none mb-4 transition-colors font-["Manrope"] placeholder-zinc-600',
                attributes: {'placeholder': 'ENTER YOUR EMAIL', 'required': 'true'},
                value: email,
                onInput: (val) {
                  email = val.toString();
                }
              ),
              
              button(
                classes: 'w-full bg-[#d4af37] hover:bg-[#b8952b] text-black font-extrabold py-3 px-6 rounded-lg uppercase tracking-wider transition-colors font-["Space_Grotesk"] cursor-pointer disabled:opacity-55',
                attributes: isLoading ? {'disabled': 'true'} : {},
                onClick: _submitEmail,
                [text(isLoading ? 'SUBMITTING...' : 'JOIN THE HUNT')]
              ),
              
              if (statusMessage.isNotEmpty)
                p(
                  classes: 'text-sm mt-4 font-["Manrope"] ${isSuccess ? "text-green-500" : "text-red-500"}',
                  [text(statusMessage)]
                )
            ]
          )
        ]
      );
    } else {
      // Floating Widget bottom-6 right-6
      return div(
        classes: 'fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3',
        [
          if (isWidgetOpen)
            div(
              classes: 'bg-[#0d0d0d] border border-[#d4af37]/30 rounded-lg p-5 w-80 shadow-2xl text-left flex flex-col gap-3 font-["Manrope"]',
              [
                h3(
                  classes: 'text-sm font-bold text-[#d4af37] uppercase tracking-wider font-["Space_Grotesk"]',
                  [text('GET UBH EXCLUSIVES')]
                ),
                p(
                  classes: 'text-xs text-zinc-400',
                  [text('Enter your email for drop alerts:')]
                ),
                input(
                  type: InputType.email,
                  classes: 'w-full bg-[#141414] border border-[#262626] focus:border-[#d4af37] text-white text-sm px-3 py-2 rounded outline-none placeholder-zinc-600',
                  attributes: {'placeholder': 'YOUR EMAIL', 'required': 'true'},
                  value: email,
                  onInput: (val) {
                    email = val.toString();
                  }
                ),
                button(
                  classes: 'w-full bg-[#d4af37] hover:bg-[#b8952b] text-black text-xs font-bold py-2 rounded uppercase tracking-wider transition-colors cursor-pointer disabled:opacity-55',
                  attributes: isLoading ? {'disabled': 'true'} : {},
                  onClick: _submitEmail,
                  [text(isLoading ? 'SUBMITTING...' : 'SUBSCRIBE')]
                ),
                if (statusMessage.isNotEmpty)
                  p(
                    classes: 'text-xs font-medium ${isSuccess ? "text-green-500" : "text-red-500"}',
                    [text(statusMessage)]
                  )
              ]
            ),
          button(
            classes: 'w-14 h-14 bg-[#d4af37] hover:bg-[#b8952b] text-black rounded-full flex items-center justify-center shadow-lg transition-transform hover:scale-105 duration-200 cursor-pointer text-2xl border-0',
            onClick: () {
              setState(() {
                isWidgetOpen = !isWidgetOpen;
                statusMessage = ''; // Clear status message on toggle
              });
            },
            [text(isWidgetOpen ? '×' : '✉️')]
          )
        ]
      );
    }
  }
}
