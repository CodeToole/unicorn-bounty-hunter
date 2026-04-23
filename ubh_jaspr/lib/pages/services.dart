import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class Services extends StatefulComponent {
  const Services({super.key});
  @override
  State<Services> createState() => _ServicesState();
}

class _ServicesState extends State<Services> {
  @override
  Component build(BuildContext context) {
    return div(
      classes: 'bg-[#0e0e0e] min-h-screen pt-24 pb-12 px-6',
      [
        div(
          classes: 'w-full max-w-4xl mx-auto mt-12 bg-[#0e0e0e] border border-[#262626] p-8',
          [
            h2(classes: 'text-2xl font-black text-white font-["Space_Grotesk"] tracking-tighter uppercase mb-6', [Component.text('STUDIO CONCIERGE (AGENTIC ENGINE)')]),
            div(
              classes: 'bg-[#131313] border border-[#262626] h-[200px] p-4 mb-4 overflow-y-auto font-["Manrope"] text-sm',
              [
                p(classes: 'text-zinc-300', [strong([Component.text('UBH System: ')]), Component.text('Connection established. What do you need to know about the studio?')])
              ],
            ),
            div(
              classes: 'flex',
              [
                input(
                  type: InputType.text, 
                  attributes: {'placeholder': 'e.g., Do you mix vocals remotely?'}, 
                  classes: 'flex-1 bg-[#131313] border border-[#262626] text-white px-4 py-3 focus:outline-none focus:border-[#00e3fd]'
                ),
                button(classes: 'bg-[#00e3fd] text-black px-6 py-3 font-bold tracking-widest uppercase ml-2', [Component.text('SEND')])
              ],
            )
          ],
        ),
        
        div(
          classes: 'w-full max-w-4xl mx-auto my-16 border border-[#262626]',
          [
            iframe(
              src: 'https://calendar.google.com/calendar/appointments/schedules/AcZssZ2uQJv23R2QyomV62yBxkrbf2eg1SuJtrHaWvo9ccbl3PNkByKS3M_wY93jcndjQ0JQhlGkp8k9?gv=true', 
              classes: 'w-full min-h-[600px] bg-transparent', 
              attributes: {'frameBorder': '0'},
              []
            )
          ],
        )
      ],
    );
  }
}
