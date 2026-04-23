import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';
import 'dart:async';

class Services extends StatefulComponent {
  const Services({super.key});
  @override
  State<Services> createState() => _ServicesState();
}

class _ServicesState extends State<Services> {
  List<Map<String, String>> messages = [
    {'role': 'system', 'text': 'Connection established. What do you need to know about the studio?'}
  ];
  String currentInput = '';
  bool isTyping = false;

  void handleSend() {
    if (currentInput.trim().isEmpty) return;

    setState(() {
      messages.add({'role': 'user', 'text': currentInput});
      currentInput = '';
      isTyping = true;
    });

    // Agentic Processing Delay
    Timer(const Duration(milliseconds: 1500), () {
      setState(() {
        messages.add({'role': 'system', 'text': 'Inquiry logged. A UBH engineer will follow up shortly to confirm block rates and analog gear requirements.'});
        isTyping = false;
      });
    });
  }

  @override
  Component build(BuildContext context) {
    return div([
      div([
        h2([text('STUDIO CONCIERGE (AGENTIC ENGINE)')], classes: 'text-2xl font-black text-white font-["Space_Grotesk"] tracking-tighter uppercase mb-6'),
        div([
          // Message History
          for (var msg in messages)
            p([
              strong([text(msg['role'] == 'system' ? 'UBH System: ' : 'You: ')], classes: msg['role'] == 'system' ? 'text-[#00e3fd]' : 'text-zinc-400'),
              text(' ' + msg['text']!)
            ], classes: 'mb-3 font-["Manrope"] text-sm text-white'),
          
          if (isTyping) p([i([text('UBH System is typing...')])], classes: 'text-[#00e3fd] text-xs font-["Manrope"] animate-pulse')
        ], classes: 'bg-[#131313] border border-[#262626] h-[250px] p-4 mb-4 overflow-y-auto flex flex-col'),
        
        div([
          input(
            type: InputType.text, 
            placeholder: 'e.g., Do you mix vocals remotely?', 
            value: currentInput,
            onChange: (value) => setState(() => currentInput = value),
            classes: 'flex-1 bg-[#131313] border border-[#262626] text-white px-4 py-3 focus:outline-none focus:border-[#00e3fd] font-["Manrope"]'
          ),
          button([text('SEND')], onClick: handleSend, classes: 'bg-[#00e3fd] text-black px-6 py-3 font-bold tracking-widest uppercase ml-2 hover:bg-[#00c5dd]')
        ], classes: 'flex')
      ], classes: 'w-full max-w-4xl mx-auto mt-12 bg-[#0e0e0e] border border-[#262626] p-8'),
      
      div([
        iframe([], src: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ2uQJv23R2QyomV62yBxkrbf2eg1SuJtrHaWvo9ccbl3PNkByKS3M_wY93jcndjQ0JQhlGkp8k9?gv=true', classes: 'w-full min-h-[600px] bg-transparent', attributes: {'frameBorder': '0'})
      ], classes: 'w-full max-w-4xl mx-auto my-16 border border-[#262626]')
    ], classes: 'bg-[#0e0e0e] min-h-screen pt-24 pb-12 px-6');
  }
}
