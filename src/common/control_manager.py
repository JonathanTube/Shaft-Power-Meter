from ui.common.audio_alarm import AudioAlarm
from ui.common.fullscreen_alert import FullscreenAlert
from ui.header.logo import HeaderLogo
from ui.home.event.event_button import EventButton
from ui.home.alarm.alarm_button import AlarmButton
from ui.home.propeller_curve.diagram import PropellerCurveDiagram
from ui.home.trendview.diagram import TrendViewDiagram


class ControlManager:
    audio_alarm: AudioAlarm | None = None
    fullscreen_alert: FullscreenAlert | None = None
    event_button: EventButton | None = None
    alarm_button: AlarmButton | None = None

    header_logo: HeaderLogo | None = None
    propeller_curve_diagram: PropellerCurveDiagram | None = None

    trend_view_sps1: TrendViewDiagram | None = None
    trend_view_sps2: TrendViewDiagram | None = None

    @staticmethod
    def on_theme_change():
        if ControlManager.header_logo is not None:
            ControlManager.header_logo.update_style()

        if ControlManager.propeller_curve_diagram is not None:
            ControlManager.propeller_curve_diagram.update_style()

        if ControlManager.trend_view_sps1 is not None:
            ControlManager.trend_view_sps1.update_style()

        if ControlManager.trend_view_sps2 is not None:
            ControlManager.trend_view_sps2.update_style()
