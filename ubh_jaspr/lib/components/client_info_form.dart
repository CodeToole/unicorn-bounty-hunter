import 'package:jaspr/jaspr.dart';
import 'package:jaspr/dom.dart';

class ClientInfoForm extends StatelessComponent {
  final String artistName;
  final ValueChanged<String> onArtistNameChanged;
  final String email;
  final ValueChanged<String> onEmailChanged;
  final String phoneNumber;
  final ValueChanged<String> onPhoneNumberChanged;
  final String requestedDate;
  final ValueChanged<String> onRequestedDateChanged;

  const ClientInfoForm({
    super.key,
    required this.artistName,
    required this.onArtistNameChanged,
    required this.email,
    required this.onEmailChanged,
    required this.phoneNumber,
    required this.onPhoneNumberChanged,
    required this.requestedDate,
    required this.onRequestedDateChanged,
  });

  String get _currentDatePart {
    if (requestedDate.contains('T')) {
      return requestedDate.split('T')[0];
    }
    return requestedDate;
  }

  String get _currentTimePart {
    if (requestedDate.contains('T')) {
      final parts = requestedDate.split('T');
      if (parts.length > 1 && parts[1].length >= 5) {
        return parts[1].substring(0, 5); // HH:mm
      }
    }
    return '';
  }

  void _updateDateTime(String newDate, String newTime) {
    if (newDate.isEmpty) {
      onRequestedDateChanged('');
    } else {
      final timeStr = newTime.isNotEmpty ? newTime : "12:00";
      onRequestedDateChanged('${newDate}T$timeStr');
    }
  }

  List<Map<String, String>> _generateDates() {
    final List<Map<String, String>> list = [];
    final now = DateTime.now();
    
    list.add({
      'value': '',
      'label': 'SELECT A BOOKING DATE',
    });

    final weekDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    for (int i = 0; i < 45; i++) {
      final date = now.add(Duration(days: i));
      
      final year = date.year;
      final monthStr = date.month.toString().padLeft(2, '0');
      final dayStr = date.day.toString().padLeft(2, '0');
      final isoValue = '$year-$monthStr-$dayStr';
      
      final dayName = weekDays[date.weekday % 7];
      final monthName = months[date.month - 1];
      
      String label = '$dayName, $monthName ${date.day}, $year';
      if (i == 0) {
        label += ' (TODAY)';
      } else if (i == 1) {
        label += ' (TOMORROW)';
      } else if (date.weekday == DateTime.saturday || date.weekday == DateTime.sunday) {
        label += ' (WEEKEND)';
      }
      
      list.add({
        'value': isoValue,
        'label': label.toUpperCase(),
      });
    }
    return list;
  }

  List<Map<String, String>> _generateTimes() {
    final List<Map<String, String>> list = [];
    list.add({
      'value': '',
      'label': 'SELECT A START TIME',
    });
    
    // Generate times from 8:00 AM to 10:00 PM
    for (int hour = 8; hour <= 22; hour++) {
      for (int min = 0; min < 60; min += 30) {
        final hourStr = hour.toString().padLeft(2, '0');
        final minStr = min.toString().padLeft(2, '0');
        final isoValue = '$hourStr:$minStr';
        
        final time12 = hour > 12 ? hour - 12 : (hour == 0 ? 12 : hour);
        final amPm = hour >= 12 ? 'PM' : 'AM';
        
        list.add({
          'value': isoValue,
          'label': '$time12:$minStr $amPm',
        });
      }
    }
    return list;
  }

  @override
  Component build(BuildContext context) {
    return div([
      input(
        type: InputType.text, 
        attributes: {'placeholder': 'ARTIST NAME', 'required': 'true'},
        value: artistName,
        onInput: (value) => onArtistNameChanged(value.toString()),
        classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] uppercase'
      ),
      input(
        type: InputType.email, 
        attributes: {'placeholder': 'EMAIL ADDRESS', 'required': 'true'},
        value: email,
        onInput: (value) => onEmailChanged(value.toString()),
        classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] uppercase'
      ),
      input(
        type: InputType.tel, 
        attributes: {'placeholder': 'PHONE NUMBER', 'required': 'true'},
        value: phoneNumber,
        onInput: (value) => onPhoneNumberChanged(value.toString()),
        classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] uppercase'
      ),
      div([
        label([text('REQUESTED DATE')], classes: 'block text-xs font-bold text-[#888] mb-2 font-["Space_Grotesk"] tracking-widest'),
        select(
          classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] cursor-pointer appearance-none',
          onChange: (value) {
            final newDate = value.isNotEmpty ? value.first : '';
            _updateDateTime(newDate, _currentTimePart);
          },
          [
            for (final d in _generateDates())
              option(
                value: d['value']!,
                selected: _currentDatePart == d['value'],
                [text(d['label']!)],
              ),
          ],
        ),
        
        label([text('START TIME')], classes: 'block text-xs font-bold text-[#888] mb-2 font-["Space_Grotesk"] tracking-widest'),
        select(
          classes: 'w-full bg-[#131313] border border-[#262626] text-white px-4 py-3 mb-4 focus:outline-none focus:border-[#D4AF37] font-["Manrope"] cursor-pointer appearance-none',
          onChange: (value) {
            final newTime = value.isNotEmpty ? value.first : '';
            _updateDateTime(_currentDatePart, newTime);
          },
          [
            for (final t in _generateTimes())
              option(
                value: t['value']!,
                selected: _currentTimePart == t['value'],
                [text(t['label']!)],
              ),
          ],
        ),
      ]),
    ]);
  }
}

