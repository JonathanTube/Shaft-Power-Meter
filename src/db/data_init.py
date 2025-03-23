from db.models.system_settings import SystemSettings
from db.models.ship_info import ShipInfo
from db.models.factor_conf import FactorConf
from db.models.breach_reason import BreachReason
from db.models.report_info import ReportInfo


class DataInit:
    @staticmethod
    def init():
        DataInit.__init_system_settings()
        DataInit.__init_ship_info()
        DataInit.__init_factor_conf()
        DataInit.__init_breach_reason()

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
