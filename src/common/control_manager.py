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


class ControlManager:
    audio_alarm: AudioAlarm | None = None
    fullscreen_alert: FullscreenAlert | None = None

    alarm_button: AlarmButton | None = None
    event_button: EventButton | None = None

    sps_single_on: SingleShaPoLiOn | None = None
    sps_single_off: SingleShaPoLiOff | None = None
    sps_dual_on: DualShaPoLiOn | None = None
    sps_dual_off: DualShaPoLiOff | None = None

    @staticmethod
    def on_eexi_power_breach_occured():
        ControlManager.audio_alarm.play()
        ControlManager.fullscreen_alert.start()
        if ControlManager.event_button is not None:
            ControlManager.event_button.update_badge()

    @staticmethod
    def on_eexi_power_breach_recovery():
        ControlManager.audio_alarm.stop()
        ControlManager.fullscreen_alert.stop()

    @staticmethod
    def on_power_overload_occured():
        if ControlManager.alarm_button is not None:
            ControlManager.alarm_button.update_badge()
            ControlManager.alarm_button.start_blink()

    @staticmethod
    def on_power_overload_recovery():
        if ControlManager.alarm_button is not None:
            ControlManager.alarm_button.stop_blink()

    @staticmethod
    def on_instant_data_refresh():
        DataSave.save('sps1')
        if gdata.amount_of_propeller == 2:
            DataSave.save('sps2')

        if ControlManager.sps_single_on is not None:
            ControlManager.sps_single_on.load_data()
        if ControlManager.sps_single_off is not None:
            ControlManager.sps_single_off.load_data()
        if ControlManager.sps_dual_on is not None:
            ControlManager.sps_dual_on.load_data()
        if ControlManager.sps_dual_off is not None:
            ControlManager.sps_dual_off.load_data()
