from ui.common.audio_alarm import AudioAlarm
from ui.common.fullscreen_alert import FullscreenAlert
from ui.home.event.event_button import EventButton
from ui.home.alarm.alarm_button import AlarmButton

class ControlManager:
    audio_alarm: AudioAlarm | None = None
    fullscreen_alert: FullscreenAlert | None = None
    event_button: EventButton | None = None
    alarm_button: AlarmButton | None = None