from datetime import datetime, timezone

from db.models.io_conf import IOConf
from db.models.language import Language
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.ship_info import ShipInfo
from db.models.factor_conf import FactorConf
from db.models.breach_reason import BreachReason
from db.models.preference import Preference
from db.models.date_time_conf import DateTimeConf
from db.models.limitations import Limitations
from db.models.test_mode_conf import TestModeConf
from db.models.user import User


class DataInit:
    @staticmethod
    def init():
        DataInit.__init_system_settings()
        DataInit.__init_preference()
        DataInit.__init_ship_info()
        DataInit.__init_factor_conf()
        DataInit.__init_breach_reason()
        DataInit.__init_propeller_setting()
        DataInit.__init_language()
        DataInit.__init_io_conf()
        DataInit.__init_date_time_conf()
        DataInit.__init_limitations()
        DataInit.__init_test_mode_conf()
        DataInit.__init_user()

    def __init_limitations():
        if Limitations.select().count() == 0:
            Limitations.create(
                speed_max=2000,
                torque_max=2000,
                power_max=200000,
                speed_warning=1800,
                torque_warning=1800,
                power_warning=180000
            )

    def __init_system_settings():
        if SystemSettings.select().count() == 0:
            SystemSettings.create(
                display_thrust=False,
                amount_of_propeller=1,
                sha_po_li=True,
                eexi_limited_power=180000,
                eexi_breach_checking_duration=60
            )

    def __init_date_time_conf():
        standard_date_time_format = '%Y-%m-%d %H:%M:%S'
        if DateTimeConf.select().count() == 0:
            DateTimeConf.create(
                utc_date_time=datetime.now(timezone.utc).strftime(standard_date_time_format),
                system_date_time=datetime.now().strftime(standard_date_time_format),
                sync_with_gps=False,
                date_format="%Y-%m-%d",
            )

    def __init_ship_info():
        if ShipInfo.select().count() == 0:
            ShipInfo.create(
                ship_type="", ship_name="", imo_number="", ship_size=""
            )

    def __init_factor_conf():
        if FactorConf.select().count() == 0:
            FactorConf.create(
                bearing_outer_diameter_D=0,
                bearing_inner_diameter_d=0,
                sensitivity_factor_k=0,
                elastic_modulus_E=0,
                poisson_ratio_mu=0)

    def __init_breach_reason():
        if BreachReason.select().count() == 0:
            BreachReason.insert_many([
                {"reason": "operating in adverse weather"},
                {"reason": "opearting in ice-infested waters"},
                {"reason": "participation in search and rescue operations"},
                {"reason": "avoidance of porates"},
                {"reason": "engine maintenance"},
                {"reason": "description of other reasons"}
            ]).execute()

    def __init_propeller_setting():
        if PropellerSetting.select().count() == 0:
            PropellerSetting.create(
                rpm_of_mcr_operating_point=2000.0,
                shaft_power_of_mcr_operating_point=200000.0,

                rpm_left_of_normal_propeller_curve=79.5,
                bhp_left_of_normal_propeller_curve=50.0,
                rpm_right_of_normal_propeller_curve=100,
                bhp_right_of_normal_propeller_curve=100,
                # hex blue color
                line_color_of_normal_propeller_curve="#0000ff",

                value_of_light_propeller_curve=5.0,
                # hex blue color
                line_color_of_light_propeller_curve="#0000ff",

                value_of_speed_limit_curve=105.0,
                # hex red color
                line_color_of_speed_limit_curve="#ff0000",

                rpm_left_of_torque_load_limit_curve=70.9,
                bhp_left_of_torque_load_limit_curve=51.9,
                rpm_right_of_torque_load_limit_curve=97.0,
                bhp_right_of_torque_load_limit_curve=97.5,
                # hex green color
                line_color_of_torque_load_limit_curve="#00ff00",

                value_of_overload_curve=5.0,
                # hex red color
                line_color_of_overload_curve="#ff0000",

                alarm_enabled_of_overload_curve=False
            )

    def __init_preference():
        if Preference.select().count() == 0:
            Preference.create(
                theme=1,
                system_unit=0,
                language=0,
                data_refresh_interval=5
            )

    def __init_io_conf():
        if IOConf.select().count() == 0:
            IOConf.create(
                plc_ip='192.168.1.2',
                plc_port=502,
                gps_ip='192.168.1.3',
                gps_port=502,
                sps1_ip='192.168.1.4',
                sps1_port=502,
                sps2_ip='192.168.1.5',
                sps2_port=502
            )

    def __init_test_mode_conf():
        if TestModeConf.select().count() == 0:
            TestModeConf.create(
                min_torque=1000,
                max_torque=2000,
                min_speed=1001,
                max_speed=2002,
                min_thrust=1002,
                max_thrust=2002,
                min_revolution=1000,
                max_revolution=2000,
                time_interval=1
            )

    def __init_user():
        if User.select().count() == 0:
            User.create(
                user_name="root",
                user_pwd="root",
                user_role=0
            )

    def __init_language():
        if Language.select().count() == 0:
            Language.insert_many([
                {
                    "code": "lang.lang.app.name",
                    "chinese": "轴功率仪表",
                    "english": "Shaft Power Meter"
                },

                {
                    "code": "lang.toast.success",
                    "chinese": "操作成功",
                    "english": "Operation Success"
                },

                {
                    "code": "lang.toast.warning",
                    "chinese": "操作存在警告",
                    "english": "Operation Warning"
                },

                {
                    "code": "lang.toast.error",
                    "chinese": "操作发生错误",
                    "english": "Operation Error"
                },

                {
                    "code": "lang.button.save",
                    "chinese": "保存",
                    "english": "Save"
                },

                {
                    "code": "lang.button.start",
                    "chinese": "开始",
                    "english": "Start"
                },

                {
                    "code": "lang.button.stop",
                    "chinese": "停止",
                    "english": "Stop"
                },

                {
                    "code": "lang.button.cancel",
                    "chinese": "取消",
                    "english": "Cancel"
                },

                {
                    "code": "lang.button.reset",
                    "chinese": "重置",
                    "english": "Reset"
                },

                {
                    "code": "lang.button.search",
                    "chinese": "搜索",
                    "english": "Search"
                },

                {
                    "code": "lang.button.confirm",
                    "chinese": "确认",
                    "english": "Confirm"
                },
                {
                    "code": "lang.button.edit",
                    "chinese": "编辑",
                    "english": "Edit"
                },
                {
                    "code": "lang.button.delete",
                    "chinese": "删除",
                    "english": "Delete"
                },
                {
                    "code": "lang.common.app_name",
                    "chinese": "轴功率仪表",
                    "english": "Shaft Power Meter"
                },
                {
                    "code": "lang.common.operation",
                    "chinese": "操作",
                    "english": "Operation"
                },

                {
                    "code": "lang.common.power",
                    "chinese": "功率",
                    "english": "Power"
                },

                {
                    "code": "lang.common.is_overload",
                    "chinese": "是否过载",
                    "english": "Overload"
                },

                {
                    "code": "lang.common.speed",
                    "chinese": "转速",
                    "english": "Speed"
                },

                {
                    "code": "lang.common.torque",
                    "chinese": "扭矩",
                    "english": "Torque"
                },

                {
                    "code": "lang.common.thrust",
                    "chinese": "推力",
                    "english": "Thrust"
                },

                {
                    "code": "lang.common.revolution",
                    "chinese": "圈数",
                    "english": "Revolution"
                },

                {
                    "code": "lang.common.average_power",
                    "chinese": "平均功率",
                    "english": "Average Power"
                },

                {
                    "code": "lang.common.sum_power",
                    "chinese": "总功率",
                    "english": "Sum Power"
                },

                {
                    "code": "lang.common.sps1",
                    "chinese": "螺旋桨1",
                    "english": "sps1"
                },

                {
                    "code": "lang.common.sps2",
                    "chinese": "螺旋桨2",
                    "english": "sps2"
                },

                {
                    "code": "lang.common.total",
                    "chinese": "总计",
                    "english": "Total"
                },

                {
                    "code": "lang.common.limited_power",
                    "chinese": "限制功率",
                    "english": "Limited Power"
                },
                {
                    "code": "lang.common.unlimited_power",
                    "chinese": "最大功率",
                    "english": "Un-limited Power"
                },

                {
                    "code": "lang.common.eexi_limited_power",
                    "chinese": "EEXI 限制功率",
                    "english": "EEXI Limited Power"
                },
                {
                    "code": "lang.common.power_unlimited_mode",
                    "chinese": "功率无限制模式",
                    "english": "Power Un-limited Mode"
                },
                {
                    "code": "lang.common.start_date",
                    "chinese": "UTC 开始日期",
                    "english": "UTC Start Date"
                },

                {
                    "code": "lang.common.end_date",
                    "chinese": "UTC 结束日期",
                    "english": "UTC End Date"
                },

                {
                    "code": "lang.common.created_at",
                    "chinese": "创建时间",
                    "english": "Created At"
                },

                {
                    "code": "lang.common.updated_at",
                    "chinese": "更新时间",
                    "english": "Updated At"
                },

                {
                    "code": "lang.common.propeller_name",
                    "chinese": "螺旋桨名称",
                    "english": "Propeller Name"
                },

                {
                    "code": "lang.common.no",
                    "chinese": "序号",
                    "english": "No."
                },

                {
                    "code": "lang.common.utc_date_time",
                    "chinese": "UTC 日期时间",
                    "english": "UTC Date Time"
                },

                {
                    "code": "lang.common.location",
                    "chinese": "位置",
                    "english": "Location"
                },

                {
                    "code": "lang.common.breach_reason",
                    "chinese": "突破原因",
                    "english": "Breach Reason"
                },

                {
                    "code": "lang.common.start_position",
                    "chinese": "开始位置",
                    "english": "Start Position"
                },

                {
                    "code": "lang.common.end_position",
                    "chinese": "结束位置",
                    "english": "End Position"
                },

                {
                    "code": "lang.common.acknowledged_at",
                    "chinese": "确认时间",
                    "english": "Acknowledged At"
                },

                {
                    "code": "lang.common.note",
                    "chinese": "备注",
                    "english": "Note"
                },
                {
                    "code": "lang.common.event_name",
                    "chinese": "事件名称",
                    "english": "Event Name"
                },
                {
                    "code": "lang.common.acknowledge_time",
                    "chinese": "确认时间",
                    "english": "Acknowledge Time"
                },

                {
                    "code": "lang.common.view",
                    "chinese": "查看",
                    "english": "View"
                },

                {
                    "code": "lang.common.export",
                    "chinese": "导出",
                    "english": "Export"
                },
                {
                    "code": "lang.common.ip_address_format_error",
                    "chinese": "IP地址格式错误",
                    "english": "IP Address Format Error"
                },
                {
                    "code": "lang.header.home",
                    "chinese": "主页",
                    "english": "Home"
                },
                {
                    "code": "lang.header.report",
                    "chinese": "报告",
                    "english": "Report"
                },
                {
                    "code": "lang.header.setting",
                    "chinese": "设置",
                    "english": "Setting"
                },
                {
                    "code": "lang.header.shapoli",
                    "chinese": "ShaPoLi",
                    "english": "ShaPoLi"
                },

                {
                    "code": "lang.home.tab.dashboard",
                    "chinese": "仪表板",
                    "english": "Dashboard"
                },
                {
                    "code": "lang.home.tab.counter",
                    "chinese": "计数器",
                    "english": "Counter"
                },

                {
                    "code": "lang.home.tab.trendview",
                    "chinese": "趋势视图",
                    "english": "Trend View"
                },
                {
                    "code": "lang.home.tab.propeller_curve",
                    "chinese": "螺旋桨曲线",
                    "english": "Propeller Curve"
                },
                {
                    "code": "lang.home.tab.alarm",
                    "chinese": "报警",
                    "english": "Alarm"
                },
                {
                    "code": "lang.home.tab.logs",
                    "chinese": "日志",
                    "english": "Logs"
                },
                {
                    "code": "lang.home.tab.event",
                    "chinese": "事件",
                    "english": "Event"
                },

                {
                    "code": "lang.setting.system_conf.title",
                    "chinese": "系统配置",
                    "english": "System Conf."
                },

                {
                    "code": "lang.setting.general.title",
                    "chinese": "通用配置",
                    "english": "General"
                },

                {
                    "code": "lang.setting.propeller_setting.title",
                    "chinese": "螺旋桨配置",
                    "english": "Propeller Setting"
                },

                {
                    "code": "lang.setting.zero_cal.title",
                    "chinese": "零点校准",
                    "english": "Zero Cal."
                },

                {
                    "code": "lang.setting.zero_cal.submitted",
                    "chinese": "已提交",
                    "english": "Submitted"
                },

                {
                    "code": "lang.setting.zero_cal.started",
                    "chinese": "已开始",
                    "english": "Started"
                },

                {
                    "code": "lang.setting.zero_cal.aborted",
                    "chinese": "已中止",
                    "english": "Aborted"
                },
                {
                    "code": "lang.setting.zero_cal.accepted",
                    "chinese": "已接受",
                    "english": "Accepted"
                },
                {
                    "code": "lang.setting.io_conf.title",
                    "chinese": "IO 配置",
                    "english": "IO Conf."
                },

                {
                    "code": "lang.setting.language_conf.title",
                    "chinese": "语言配置",
                    "english": "Language Conf."
                },

                {
                    "code": "lang.setting.language_conf.code",
                    "chinese": "代码",
                    "english": "Code"
                },

                {
                    "code": "lang.setting.language_conf.chinese",
                    "chinese": "中文",
                    "english": "Chinese"
                },

                {
                    "code": "lang.setting.language_conf.english",
                    "chinese": "英文",
                    "english": "English"
                },

                {
                    "code": "lang.setting.self_test.title",
                    "chinese": "自检",
                    "english": "Self Test"
                },

                {
                    "code": "lang.setting.permission_conf.title",
                    "chinese": "权限配置",
                    "english": "Permission Conf."
                },

                {
                    "code": "lang.setting.test_mode.title",
                    "chinese": "测试模式",
                    "english": "Test Mode"
                },

                {
                    "code": "lang.setting.test_mode.customize_data_range",
                    "chinese": "自定义数据范围",
                    "english": "Customize Data Range"
                },

                {
                    "code": "lang.setting.test_mode.instant_mock_data",
                    "chinese": "瞬时模拟数据",
                    "english": "Instant Mock Data"
                },

                {
                    "code": "lang.setting.test_mode.min_torque",
                    "chinese": "最小扭矩",
                    "english": "Min Torque"
                },

                {
                    "code": "lang.setting.test_mode.max_torque",
                    "chinese": "最大扭矩",
                    "english": "Max Torque"
                },

                {
                    "code": "lang.setting.test_mode.min_speed",
                    "chinese": "最小转速",
                    "english": "Min Speed"
                },

                {
                    "code": "lang.setting.test_mode.max_speed",
                    "chinese": "最大转速",
                    "english": "Max Speed"
                },

                {
                    "code": "lang.setting.test_mode.min_thrust",
                    "chinese": "最小推力",
                    "english": "Min Thrust"
                },

                {
                    "code": "lang.setting.test_mode.max_thrust",
                    "chinese": "最大推力",
                    "english": "Max Thrust"
                },

                {
                    "code": "lang.setting.test_mode.min_revolution",
                    "chinese": "最小圈数",
                    "english": "Min Revolution"
                },

                {
                    "code": "lang.setting.test_mode.max_revolution",
                    "chinese": "最大圈数",
                    "english": "Max Revolution"
                },

                {
                    "code": "lang.setting.test_mode.please_confirm",
                    "chinese": "请确认",
                    "english": "Please Confirm"
                },

                {
                    "code": "lang.setting.test_mode.system_restart_after_change",
                    "chinese": "修改系统配置后,软件需要重启才能生效",
                    "english": "This software need to be restarted after you changed the system settings."
                },

                {
                    "code": "lang.setting.setting",
                    "chinese": "设置",
                    "english": "Setting"
                },

                {
                    "code": "lang.setting.display_thrust",
                    "chinese": "显示推力",
                    "english": "Display Thrust"
                },

                {
                    "code": "lang.setting.amount_of_propeller",
                    "chinese": "螺旋桨数量",
                    "english": "Amount of Propeller"
                },

                {
                    "code": "lang.setting.enable_sha_po_li",
                    "chinese": "启用ShaPoLi",
                    "english": "Enable ShaPoLi"
                },
                {
                    "code": "lang.setting.display_propeller_curve",
                    "chinese": "显示螺旋桨曲线",
                    "english": "Display Propeller Curve"
                },
                {
                    "code": "lang.setting.single_propeller",
                    "chinese": "单桨",
                    "english": "Single"
                },

                {
                    "code": "lang.setting.twins_propeller",
                    "chinese": "双桨",
                    "english": "Twins"
                },

                {
                    "code": "lang.setting.eexi_limited_power",
                    "chinese": "EEXI 限制功率",
                    "english": "EEXI Limited Power"
                },

                {
                    "code": "lang.setting.eexi_breach_checking_duration",
                    "chinese": "EEXI 超限检查周期",
                    "english": "EEXI Breach Checking Duration"
                },

                {
                    "code": "lang.setting.ship_info",
                    "chinese": "船体信息",
                    "english": "Ship Info"
                },

                {
                    "code": "lang.setting.ship_type",
                    "chinese": "船体类型",
                    "english": "Ship Type"
                },

                {
                    "code": "lang.setting.ship_name",
                    "chinese": "船体名称",
                    "english": "Ship Name"
                },

                {
                    "code": "lang.setting.imo_number",
                    "chinese": "IMO 号码",
                    "english": "IMO Number"
                },

                {
                    "code": "lang.setting.ship_size",
                    "chinese": "船体尺寸",
                    "english": "Ship Size"
                },

                {
                    "code": "lang.setting.factor_conf",
                    "chinese": "系数配置",
                    "english": "Factor Conf."
                },

                {
                    "code": "lang.setting.bearing_outer_diameter_D",
                    "chinese": "轴承外径",
                    "english": "Bearing Outer Diameter"
                },

                {
                    "code": "lang.setting.bearing_inner_diameter_d",
                    "chinese": "轴承内径",
                    "english": "Bearing Inner Diameter"
                },

                {
                    "code": "lang.setting.sensitivity_factor_k",
                    "chinese": "灵敏度系数",
                    "english": "Sensitivity Factor"
                },

                {
                    "code": "lang.setting.elastic_modulus_E",
                    "chinese": "弹性模量",
                    "english": "Elastic Modulus"
                },

                {
                    "code": "lang.setting.poisson_ratio_mu",
                    "chinese": "泊松比",
                    "english": "Poisson Ratio"
                },



                {
                    "code": "lang.setting.preference",
                    "chinese": "偏好设置",
                    "english": "Preference"
                },

                {
                    "code": "lang.setting.theme",
                    "chinese": "主题",
                    "english": "Theme"
                },
                {
                    "code": "lang.setting.theme.light",
                    "chinese": "浅色",
                    "english": "Light"
                },

                {
                    "code": "lang.setting.theme.dark",
                    "chinese": "深色",
                    "english": "Dark"
                },

                {
                    "code": "lang.setting.unit",
                    "chinese": "单位",
                    "english": "Unit"
                },

                {
                    "code": "lang.setting.unit.metric",
                    "chinese": "公制",
                    "english": "Metric"
                },

                {
                    "code": "lang.setting.unit.si",
                    "chinese": "国际单位制",
                    "english": "SI"
                },

                {
                    "code": "lang.setting.language",
                    "chinese": "语言",
                    "english": "Language"
                },

                {
                    "code": "lang.setting.data_refresh_interval",
                    "chinese": "界面数据刷新间隔",
                    "english": "Data Refresh Interval"
                },

                {
                    "code": "lang.setting.maximum_limitations",
                    "chinese": "最大限制",
                    "english": "Maximum Limitations"
                },

                {
                    "code": "lang.setting.warning_limitations",
                    "chinese": "警告限制",
                    "english": "Warning Limitations"
                },

                {
                    "code": "lang.setting.utc_date_time_conf",
                    "chinese": "UTC 日期时间配置",
                    "english": "UTC Date Time Conf."
                },

                {
                    "code": "lang.setting.current_utc_date_time",
                    "chinese": "当前UTC日期时间",
                    "english": "Current UTC Date Time"
                },

                {
                    "code": "lang.setting.date",
                    "chinese": "日期",
                    "english": "Date"
                },

                {
                    "code": "lang.setting.time",
                    "chinese": "时间",
                    "english": "Time"
                },

                {
                    "code": "lang.setting.date_format",
                    "chinese": "日期格式",
                    "english": "Date Format"
                },

                {
                    "code": "lang.setting.sync_with_gps",
                    "chinese": "与GPS同步",
                    "english": "Sync with GPS"
                },

                {
                    "code": "lang.setting.mcr_operating_point",
                    "chinese": "MCR 运行点",
                    "english": "MCR Operating Point"
                },

                {
                    "code": "lang.setting.normal_propeller_curve",
                    "chinese": "正常螺旋桨曲线 (1)",
                    "english": "Normal Propeller Curve (1)"
                },

                {
                    "code": "lang.setting.rpm_left",
                    "chinese": "左转速",
                    "english": "RPM Left"
                },

                {
                    "code": "lang.setting.rpm_right",
                    "chinese": "右转速",
                    "english": "RPM Right"
                },

                {
                    "code": "lang.setting.power_left",
                    "chinese": "左功率",
                    "english": "Power Left"
                },

                {
                    "code": "lang.setting.power_right",
                    "chinese": "右功率",
                    "english": "Power Right"
                },

                {
                    "code": "lang.setting.light_propeller_curve",
                    "chinese": "轻载螺旋桨曲线 (2)",
                    "english": "Light Propeller Curve (2)"
                },

                {
                    "code": "lang.setting.torque_load_limit_curve",
                    "chinese": "扭矩负载限制曲线 (4)",
                    "english": "Torque Load Limit Curve (4)"
                },

                {
                    "code": "lang.setting.overload_curve",
                    "chinese": "过载曲线 (5)",
                    "english": "Overload Curve (5)"
                },

                {
                    "code": "lang.setting.speed_limit_curve",
                    "chinese": "速度限制曲线 (3)",
                    "english": "Speed Limit Curve (3)"
                },

                {
                    "code": "lang.setting.enable_overload_alarm",
                    "chinese": "启用过载报警",
                    "english": "Enable Overload Alarm"
                },

                {
                    "code": "lang.setting.plc_conf",
                    "chinese": "PLC 配置",
                    "english": "PLC Conf."
                },

                {
                    "code": "lang.setting.save_limitations_to_plc_failed",
                    "chinese": "保存上下限到PLC失败",
                    "english": "Save Limitations to PLC Failed"
                },


                {
                    "code": "lang.setting.check_plc_connection",
                    "chinese": "检查PLC连接",
                    "english": "Check PLC Connection"
                },

                {
                    "code": "lang.setting.check_gps_connection",
                    "chinese": "检查GPS连接",
                    "english": "Check GPS Connection"
                },

                {
                    "code": "lang.setting.check_sps_connection",
                    "chinese": "检查SPS连接",
                    "english": "Check SPS Connection"
                },

                {
                    "code": "lang.setting.4_20_ma_power_min",
                    "chinese": "4-20mA 功率最小值",
                    "english": "4-20mA Power Min"
                },


                {
                    "code": "lang.setting.4_20_ma_power_max",
                    "chinese": "4-20mA 功率最大值",
                    "english": "4-20mA Power Max"
                },

                {
                    "code": "lang.setting.4_20_ma_power_offset",
                    "chinese": "4-20mA 功率偏移",
                    "english": "4-20mA Power Offset"
                },

                {
                    "code": "lang.setting.4_20_ma_torque_min",
                    "chinese": "4-20mA 扭矩最小值   ",
                    "english": "4-20mA Torque Min"
                },

                {
                    "code": "lang.setting.4_20_ma_torque_max",
                    "chinese": "4-20mA 扭矩最大值",
                    "english": "4-20mA Torque Max"
                },

                {
                    "code": "lang.setting.4_20_ma_torque_offset",
                    "chinese": "4-20mA 扭矩偏移",
                    "english": "4-20mA Torque Offset"
                },

                {
                    "code": "lang.setting.4_20_ma_thrust_min",
                    "chinese": "4-20mA 推力最小值",
                    "english": "4-20mA Thrust Min"
                },


                {
                    "code": "lang.setting.4_20_ma_thrust_max",
                    "chinese": "4-20mA 推力最大值",
                    "english": "4-20mA Thrust Max"
                },

                {
                    "code": "lang.setting.4_20_ma_thrust_offset",
                    "chinese": "4-20mA 推力偏移",
                    "english": "4-20mA Thrust Offset"
                },

                {
                    "code": "lang.setting.4_20_ma_speed_min",
                    "chinese": "4-20mA 速度最小值",
                    "english": "4-20mA Speed Min"
                },

                {
                    "code": "lang.setting.4_20_ma_speed_max",
                    "chinese": "4-20mA 速度最大值",
                    "english": "4-20mA Speed Max"
                },

                {
                    "code": "lang.setting.4_20_ma_speed_offset",
                    "chinese": "4-20mA 速度偏移",
                    "english": "4-20mA Speed Offset"
                },


                {
                    "code": "lang.setting.ip",
                    "chinese": "IP 地址",
                    "english": "IP Address"
                },

                {
                    "code": "lang.setting.port",
                    "chinese": "端口",
                    "english": "Port"
                },

                {
                    "code": "lang.setting.output_conf",
                    "chinese": "输出配置",
                    "english": "Output Conf."
                },

                {
                    "code": "lang.setting.gps_conf",
                    "chinese": "GPS 配置",
                    "english": "GPS Conf."
                },

                {
                    "code": "lang.setting.sps1_conf",
                    "chinese": "SPS1 配置",
                    "english": "SPS1 Conf."
                },

                {
                    "code": "lang.setting.sps2_conf",
                    "chinese": "SPS2 配置",
                    "english": "SPS2 Conf."
                },

                {
                    "code": "lang.log.event_log",
                    "chinese": "事件日志",
                    "english": "Event Log"
                },

                {
                    "code": "lang.log.data_log",
                    "chinese": "数据日志",
                    "english": "Data Log"
                },

                {
                    "code": "lang.log.gps_log",
                    "chinese": "GPS 日志",
                    "english": "GPS Log"
                },
                {
                    "code": "lang.log.operation_log",
                    "chinese": "操作日志",
                    "english": "Operation Log"
                },
                {
                    "code": "lang.operation_log.operation_type",
                    "chinese": "操作类型",
                    "english": "Operation Type"
                },
                {
                    "code": "lang.operation_log.operation_content",
                    "chinese": "操作内容",
                    "english": "Operation Content"
                },
                {
                    "code": "lang.report.report_name",
                    "chinese": "报告名称",
                    "english": "Report Name"
                },

                {
                    "code": "lang.report.export_success",
                    "chinese": "导出成功",
                    "english": "Export Success"
                },
                {
                    "code": "lang.counter.interval",
                    "chinese": "间隔",
                    "english": "Interval"
                },
                {
                    "code": "lang.counter.manually",
                    "chinese": "手动",
                    "english": "Manually"
                },
                {
                    "code": "lang.counter.total",
                    "chinese": "总计",
                    "english": "Total"
                },
                {
                    "code": "lang.counter.running",
                    "chinese": "运行中",
                    "english": "Running"
                },
                {
                    "code": "lang.counter.reset",
                    "chinese": "重置",
                    "english": "Reset"
                },
                {
                    "code": "lang.counter.stopped",
                    "chinese": "已停止",
                    "english": "Stopped"
                },
                {
                    "code": "lang.counter.start",
                    "chinese": "启动",
                    "english": "Start"
                },
                {
                    "code": "lang.counter.stop",
                    "chinese": "停止",
                    "english": "Stop"
                },
                {
                    "code": "lang.counter.resume",
                    "chinese": "恢复",
                    "english": "Resume"
                },
                {
                    "code": "lang.counter.total_energy",
                    "chinese": "总耗量",
                    "english": "Total Energy"
                },
                {
                    "code": "lang.counter.average_power",
                    "chinese": "平均功率",
                    "english": "Average Power"
                },
                {
                    "code": "lang.counter.average_speed",
                    "chinese": "转速",
                    "english": "Rotational Speed"
                },
                {
                    "code": "lang.counter.interval_setting",
                    "chinese": "间隔设置",
                    "english": "Interval Setting"
                },
                {
                    "code": "lang.counter.hours",
                    "chinese": "小时",
                    "english": "Hours"
                },
                {
                    "code": "lang.counter.started_at",
                    "chinese": "开始于",
                    "english": "Started At"
                },
                {
                    "code": "lang.counter.stopped_at",
                    "chinese": "停止于",
                    "english": "Stopped At"
                },
                {
                    "code": "lang.counter.measured",
                    "chinese": "已测量",
                    "english": "Measured"
                },
                {
                    "code": "lang.counter.please_confirm",
                    "chinese": "请确认",
                    "english": "Please Confirm"
                },
                {
                    "code": "lang.counter.do_you_really_want_to_reset_counter",
                    "chinese": "你确定要重置计数器吗？",
                    "english": "Do you really want to reset the counter?"
                },
                {
                    "code": "lang.counter.yes",
                    "chinese": "是",
                    "english": "Yes"
                },
                {
                    "code": "lang.counter.no",
                    "chinese": "否",
                    "english": "No"
                },
                {
                    "code": "lang.counter.interval_has_been_changed",
                    "chinese": "间隔已更改",
                    "english": "Interval has been changed"
                },
                {
                    "code": "lang.counter.interval_cannot_be_empty",
                    "chinese": "间隔不能为空",
                    "english": "Interval cannot be empty"
                },
                {
                    "code": "lang.counter.interval_must_be_greater_than_0",
                    "chinese": "间隔必须大于0",
                    "english": "Interval must be greater than 0"
                },
                {
                    "code": "lang.trendview.cannot_search_more_than_90_days",
                    "chinese": "不能搜索超过90天",
                    "english": "Cannot search more than 90 days"
                },
                {
                    "code": "lang.propeller_curve.mcr_operating_point",
                    "chinese": "MCR 操作点",
                    "english": "MCR Operating Point"
                },
                {
                    "code": "lang.propeller_curve.normal_propeller_curve",
                    "chinese": "正常螺旋桨曲线",
                    "english": "Normal Propeller Curve"
                },
                {
                    "code": "lang.propeller_curve.light_propeller_curve",
                    "chinese": "轻载螺旋桨曲线",
                    "english": "Light Propeller Curve"
                },
                {
                    "code": "lang.propeller_curve.speed_limit_curve",
                    "chinese": "速度限制曲线",
                    "english": "Speed Limit Curve"
                },
                {
                    "code": "lang.propeller_curve.torque_load_limit_curve",
                    "chinese": "扭矩负载限制曲线",
                    "english": "Torque Load Limit Curve"
                },
                {
                    "code": "lang.propeller_curve.overload_curve",
                    "chinese": "过载曲线",
                    "english": "Overload Curve"
                },
                {
                    "code": "lang.propeller_curve.engine_speed",
                    "chinese": "发动机转速, % of A",
                    "english": "Engine Speed, % of A"
                },
                {
                    "code": "lang.propeller_curve.engine_shaft_power",
                    "chinese": "发动机轴功率, % of A",
                    "english": "Engine Shaft Power, % of A"
                },
                {
                    "code": "lang.alarm.plc_disconnected",
                    "chinese": "PLC 断开",
                    "english": "PLC Disconnected"
                },
                {
                    "code": "lang.alarm.gps_disconnected",
                    "chinese": "GPS 断开",
                    "english": "GPS Disconnected"
                },
                {
                    "code": "lang.alarm.sps1_disconnected",
                    "chinese": "SPS1 断开",
                    "english": "SPS1 Disconnected"
                },
                {
                    "code": "lang.alarm.sps2_disconnected",
                    "chinese": "SPS2 断开",
                    "english": "SPS2 Disconnected"
                },
                {
                    "code": "lang.alarm.app_unexpected_exit",
                    "chinese": "应用意外退出",
                    "english": "App Unexpected Exit"
                },
                {
                    "code": "lang.alarm.power_overload",
                    "chinese": "功率过载",
                    "english": "Power Overload"
                },
                {
                    "code": "lang.alarm.unknown",
                    "chinese": "未知",
                    "english": "Unknown"
                },
                {
                    "code": "lang.alarm.acknowledge",
                    "chinese": "确认",
                    "english": "Acknowledge"
                },
                {
                    "code": "lang.alarm.please_select_at_least_one_alarm",
                    "chinese": "请至少选择一个告警",
                    "english": "Please select at least one alarm"
                },
                {
                    "code": "lang.event.reason_for_power_reserve_breach",
                    "chinese": "功率突破原因",
                    "english": "Reason for Power Reserve Breach"
                },
                {
                    "code": "lang.event.date_time_of_power_reserve_breach",
                    "chinese": "功率突破时间",
                    "english": "Date/Time of Power Reserve Breach"
                },
                {
                    "code": "lang.event.ship_position_of_power_reserve_breach",
                    "chinese": "功率突破时的位置",
                    "english": "Ship Position of Power Reserve Breach"
                },
                {
                    "code": "lang.event.date_time_when_returning_to_limited_power",
                    "chinese": "功率恢复时间",
                    "english": "Date/Time when Returning to Limited Power"
                },
                {
                    "code": "lang.event.ship_position_when_returning_to_limited_power",
                    "chinese": "功率恢复时的位置",
                    "english": "Ship Position when Returning to Limited Power"
                },
                {
                    "code": "lang.event.note",
                    "chinese": "备注",
                    "english": "Note"
                },
                {
                    "code": "lang.event.ice_condition",
                    "chinese": "冰况",
                    "english": "Ice Condition"
                },
                {
                    "code": "lang.event.wave_height",
                    "chinese": "浪高",
                    "english": "Wave Height"
                },
                {
                    "code": "lang.event.beaufort_number",
                    "chinese": "风级",
                    "english": "Beaufort Number"
                },
                {
                    "code": "lang.permission.user_name",
                    "chinese": "用户名",
                    "english": "User Name"
                },
                {
                    "code": "lang.permission.user_pwd",
                    "chinese": "密码",
                    "english": "Password"
                },
                {
                    "code": "lang.permission.user_role",
                    "chinese": "角色",
                    "english": "Role"
                },
                {
                    "code": "lang.permission.edit_user",
                    "chinese": "编辑用户",
                    "english": "Edit User"
                },
                {
                    "code": "lang.permission.delete_user",
                    "chinese": "删除用户",
                    "english": "Delete User"
                },
                {
                    "code": "lang.permission.role",
                    "chinese": "角色",
                    "english": "Role"
                },
                {
                    "code": "lang.permission.add_user",
                    "chinese": "添加用户",
                    "english": "Add User"
                },
                {
                    "code": "lang.permission.confirm_user_pwd",
                    "chinese": "确认密码",
                    "english": "Confirm Password"
                },
                {
                    "code": "lang.permission.user_name_exists",
                    "chinese": "用户名已存在",
                    "english": "User Name Exists"
                },
                {
                    "code": "lang.permission.password_not_match",
                    "chinese": "密码不匹配",
                    "english": "Password Not Match"
                },
                {
                    "code": "lang.permission.user_name_required",
                    "chinese": "用户名不能为空",
                    "english": "User Name Required"
                },
                {
                    "code": "lang.permission.user_pwd_required",
                    "chinese": "密码不能为空",
                    "english": "Password Required"
                },
                {
                    "code": "lang.permission.confirm_user_pwd_required",
                    "chinese": "确认密码不能为空",
                    "english": "Confirm Password Required"
                },
                {
                    "code": "lang.permission.user_role_required",
                    "chinese": "角色不能为空",
                    "english": "User Role Required"
                },
                {
                    "code": "lang.permission.all",
                    "chinese": "所有",
                    "english": "All"
                },
                {
                    "code": "lang.permission.admin",
                    "chinese": "管理员",
                    "english": "Admin"
                },
                {
                    "code": "lang.permission.master",
                    "chinese": "主控",
                    "english": "Master"
                },
                {
                    "code": "lang.permission.user",
                    "chinese": "用户",
                    "english": "User"
                },
                {
                    "code": "lang.permission.authentication",
                    "chinese": "认证",
                    "english": "Authentication"
                },
                {
                    "code": "lang.permission.user_name_and_pwd_are_required",
                    "chinese": "用户名和密码不能为空",
                    "english": "User Name and Password are required"
                },
                {
                    "code": "lang.permission.user_name_or_pwd_is_incorrect",
                    "chinese": "用户名或密码不正确",
                    "english": "User Name or Password is Incorrect"
                }
            ]).execute()
