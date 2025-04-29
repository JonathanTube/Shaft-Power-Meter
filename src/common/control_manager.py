from db.models.propeller_setting import PropellerSetting
from ui.common.audio_alarm import AudioAlarm
from ui.common.fullscreen_alert import FullscreenAlert
from ui.home.dashboard.sps_single.on.index import SingleShaPoLiOn
from ui.home.dashboard.sps_single.off.index import SingleShaPoLiOff
from ui.home.dashboard.sps_dual.on.index import DualShaPoLiOn
from ui.home.dashboard.sps_dual.off.index import DualShaPoLiOff
from ui.home.event.event_button import EventButton
from ui.home.propeller_curve.diagram import PropellerCurveDiagram
from ui.home.trendview.diagram import TrendViewDiagram


class ControlManager:
    audio_alarm: AudioAlarm | None = None
    fullscreen_alert: FullscreenAlert | None = None
    event_button: EventButton | None = None

    sps_single_on: SingleShaPoLiOn | None = None
    sps_single_off: SingleShaPoLiOff | None = None
    sps_dual_on: DualShaPoLiOn | None = None
    sps_dual_off: DualShaPoLiOff | None = None

    propeller_conf: PropellerSetting | None = None
    propeller_curve_diagram: PropellerCurveDiagram | None = None

    trend_view_sps1: TrendViewDiagram | None = None
    trend_view_sps2: TrendViewDiagram | None = None

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
    def on_instant_data_refresh():
        if ControlManager.sps_single_on is not None:
            ControlManager.sps_single_on.load_data()

        if ControlManager.sps_single_off is not None:
            ControlManager.sps_single_off.load_data()

        if ControlManager.sps_dual_on is not None:
            ControlManager.sps_dual_on.load_data()

        if ControlManager.sps_dual_off is not None:
            ControlManager.sps_dual_off.load_data()

        if ControlManager.propeller_curve_diagram is not None:
            ControlManager.propeller_curve_diagram.update_sps_points()

    @staticmethod
    def on_theme_change():
        if ControlManager.propeller_curve_diagram is not None:
            ControlManager.propeller_curve_diagram.update_style()

        if ControlManager.trend_view_sps1 is not None:
            ControlManager.trend_view_sps1.update_style()

        if ControlManager.trend_view_sps2 is not None:
            ControlManager.trend_view_sps2.update_style()
