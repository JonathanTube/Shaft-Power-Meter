from db.models.language import Language
from db.models.propeller_setting import PropellerSetting
from db.models.system_settings import SystemSettings
from db.models.ship_info import ShipInfo
from db.models.factor_conf import FactorConf
from db.models.breach_reason import BreachReason
from db.models.report_info import ReportInfo
from db.models.preference import Preference


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

    def __init_system_settings():
        if SystemSettings.select().count() == 0:
            SystemSettings.create(
                display_thrust=False,
                amount_of_propeller=1,
                eexi_limited_power=0,
                sha_po_li=False
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

    def init_report_info_for_test():
        if ReportInfo.select().count() == 0:
            ReportInfo.insert_many([
                {"report_name": "Test Report 1"},
                {"report_name": "Test Report 2"},
                {"report_name": "Test Report 3"},
                {"report_name": "Test Report 4"},
                {"report_name": "Test Report 5"},
                {"report_name": "Test Report 6"},
                {"report_name": "Test Report 7"},
                {"report_name": "Test Report 8"},
                {"report_name": "Test Report 9"},
                {"report_name": "Test Report 10"}
            ]).execute()

    def __init_propeller_setting():
        if PropellerSetting.select().count() == 0:
            PropellerSetting.create(
                rpm_of_mcr_operating_point=1000.0,
                shaft_power_of_mcr_operating_point=1000.0,

                rpm_left_of_normal_propeller_curve=79.5,
                bhp_left_of_normal_propeller_curve=50.0,
                rpm_right_of_normal_propeller_curve=100,
                bhp_right_of_normal_propeller_curve=100,
                line_color_of_normal_propeller_curve="blue",

                value_of_light_propeller_curve=5.0,
                line_color_of_light_propeller_curve="blue",

                value_of_speed_limit_curve=105.0,
                line_color_of_speed_limit_curve="red",

                rpm_left_of_torque_load_limit_curve=70.9,
                bhp_left_of_torque_load_limit_curve=51.9,
                rpm_right_of_torque_load_limit_curve=97.0,
                bhp_right_of_torque_load_limit_curve=97.5,
                line_color_of_torque_load_limit_curve="green",

                value_of_overload_curve=5.0,
                line_color_of_overload_curve="red",

                alarm_enabled_of_overload_curve=False
            )

    def __init_preference():
        if Preference.select().count() == 0:
            Preference.create(
                theme=0,
                system_unit=0,
                language=0,
                data_refresh_interval=5
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
                    "code": "lang.common.power",
                    "chinese": "功率",
                    "english": "Power"
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
                    "code": "lang.common.sps1",
                    "chinese": "螺旋桨1",
                    "english": "SPS1"
                },

                {
                    "code": "lang.common.sps2",
                    "chinese": "螺旋桨2",
                    "english": "SPS2"
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
                    "code": "lang.setting.io_conf.title",
                    "chinese": "IO 配置",
                    "english": "IO Conf."
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
                    "code": "lang.setting.data_backup.title",
                    "chinese": "数据备份",
                    "english": "Data Backup"
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
                }
            ]).execute()
