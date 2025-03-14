import pytest
from peewee import SqliteDatabase
from src.db.models.factor_conf import GeneralSetting, BaseModel


@pytest.fixture(scope='module')
def setup_database():
    # Bind model to test db
    db = SqliteDatabase(':memory:')
    BaseModel._meta.database = db
    db.connect()
    db.create_tables([GeneralSetting])
    yield
    # Drop tables and close connection
    db.drop_tables([GeneralSetting])
    db.close()


def test_create_general_setting(setup_database):
    # Create a GeneralSetting instance
    setting = GeneralSetting.create(
        bearing_outer_diameter_D=100.0,
        bearing_inner_diameter_d=50.0,
        shaft_outer_radius_R=25.0,
        shaft_inner_radius_r=10.0,
        elastic_modulus_E=210.0,
        poisson_ratio_mu=0.3,
        sensitivity_factor_k=1.5,
        torque_coefficient=0.8,
        tension_compression_coefficient=1.2
    )

    # Retrieve the instance from the db
    retrieved_setting = GeneralSetting.get_by_id(setting.id)

    # Assert that the retrieved values match the created values
    assert retrieved_setting.bearing_outer_diameter_D == 100.0
    assert retrieved_setting.bearing_inner_diameter_d == 50.0
    assert retrieved_setting.shaft_outer_radius_R == 25.0
    assert retrieved_setting.shaft_inner_radius_r == 10.0
    assert retrieved_setting.elastic_modulus_E == 210.0
    assert retrieved_setting.poisson_ratio_mu == 0.3
    assert retrieved_setting.sensitivity_factor_k == 1.5
    assert retrieved_setting.torque_coefficient == 0.8
    assert retrieved_setting.tension_compression_coefficient == 1.2


def test_update_general_setting(setup_database):
    # Create a GeneralSetting instance
    setting = GeneralSetting.create(
        bearing_outer_diameter_D=100.0,
        bearing_inner_diameter_d=50.0,
        shaft_outer_radius_R=25.0,
        shaft_inner_radius_r=10.0,
        elastic_modulus_E=210.0,
        poisson_ratio_mu=0.3,
        sensitivity_factor_k=1.5,
        torque_coefficient=0.8,
        tension_compression_coefficient=1.2
    )

    # Update the instance
    setting.bearing_outer_diameter_D = 110.0
    setting.save()

    # Retrieve the updated instance from the db
    updated_setting = GeneralSetting.get_by_id(setting.id)

    # Assert that the updated values match the new values
    assert updated_setting.bearing_outer_diameter_D == 110.0


def test_delete_general_setting(setup_database):
    # Create a GeneralSetting instance
    setting = GeneralSetting.create(
        bearing_outer_diameter_D=100.0,
        bearing_inner_diameter_d=50.0,
        shaft_outer_radius_R=25.0,
        shaft_inner_radius_r=10.0,
        elastic_modulus_E=210.0,
        poisson_ratio_mu=0.3,
        sensitivity_factor_k=1.5,
        torque_coefficient=0.8,
        tension_compression_coefficient=1.2
    )

    # Delete the instance
    setting_id = setting.id
    setting.delete_instance()

    # Assert that the instance no longer exists in the db
    with pytest.raises(GeneralSetting.DoesNotExist):
        GeneralSetting.get_by_id(setting_id)
