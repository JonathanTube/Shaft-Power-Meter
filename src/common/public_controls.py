from ui.common.audio_alarm import AudioAlarm
from ui.common.fullscreen_alert import FullscreenAlert
from ui.home.dashboard.sps_single.on.index import SingleShaPoLiOn
from ui.home.dashboard.sps_single.off.index import SingleShaPoLiOff
from ui.home.dashboard.sps_dual.on.index import DualShaPoLiOn
from ui.home.dashboard.sps_dual.off.index import DualShaPoLiOff
from utils.data_save import DataSave
from common.global_data import gdata
from ui.home.alarm.alarm_button import AlarmButton
from ui.home.event.event_button import EventButton


class PublicControls:
    audio_alarm: AudioAlarm = None
    fullscreen_alert: FullscreenAlert = None

    alarm_button: AlarmButton = None
    event_button: EventButton = None

    sps_single_on: SingleShaPoLiOn = None
    sps_single_off: SingleShaPoLiOff = None
    sps_dual_on: DualShaPoLiOn = None
    sps_dual_off: DualShaPoLiOff = None

    @staticmethod
    def on_eexi_power_breach_occured():
        if PublicControls.audio_alarm is not None:
            PublicControls.audio_alarm.play()
        if PublicControls.fullscreen_alert is not None:
            PublicControls.fullscreen_alert.start()
        if PublicControls.event_button is not None:
            PublicControls.event_button.update_badge()

    @staticmethod
    def on_eexi_power_breach_recovery():
        if PublicControls.audio_alarm is not None:
            PublicControls.audio_alarm.stop()
        if PublicControls.fullscreen_alert is not None:
            PublicControls.fullscreen_alert.stop()

    @staticmethod
    def on_power_overload_occured():
        if PublicControls.alarm_button is not None:
            PublicControls.alarm_button.update_badge()
            PublicControls.alarm_button.start_blink()

    @staticmethod
    def on_power_overload_recovery():
        if PublicControls.alarm_button is not None:
            PublicControls.alarm_button.stop_blink()

    @staticmethod
    def on_instant_data_refresh():
        DataSave.save('sps1')
        if gdata.amount_of_propeller == 2:
            DataSave.save('sps2')

        if PublicControls.sps_single_on is not None:
            PublicControls.sps_single_on.load_data()
        if PublicControls.sps_single_off is not None:
            PublicControls.sps_single_off.load_data()
        if PublicControls.sps_dual_on is not None:
            PublicControls.sps_dual_on.load_data()
        if PublicControls.sps_dual_off is not None:
            PublicControls.sps_dual_off.load_data()
