
from ui.common.audio_alarm import AudioAlarm
from ui.common.fullscreen_alert import FullscreenAlert
from ui.home.index import Home


class PublicControls:
    audio_alarm: AudioAlarm = None
    fullscreen_alert: FullscreenAlert = None

    home: Home = None

    @staticmethod
    def on_eexi_power_breach_occured():
        print("================on_eexi_power_breach_occured==========")
        print(PublicControls.audio_alarm)
        print(PublicControls.fullscreen_alert)
        print(PublicControls.home)
        if PublicControls.audio_alarm is not None:
            PublicControls.audio_alarm.play()
        if PublicControls.fullscreen_alert is not None:
            PublicControls.fullscreen_alert.start()
        if PublicControls.home is not None:
            PublicControls.home.update_event_badge()

    @staticmethod
    def on_eexi_power_breach_recovery():
        if PublicControls.audio_alarm is not None:
            PublicControls.audio_alarm.stop()
        if PublicControls.fullscreen_alert is not None:
            PublicControls.fullscreen_alert.stop()

    @staticmethod
    def on_power_overload_occured():
        if PublicControls.home is not None:
            PublicControls.home.update_alarm_badge()
            PublicControls.home.alarm_bgcolor_start_blink()

    @staticmethod
    def on_power_overload_recovery():
        if PublicControls.home is not None:
            PublicControls.home.alarm_bgcolor_stop_blink()
