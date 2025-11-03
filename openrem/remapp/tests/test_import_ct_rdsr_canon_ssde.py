# This Python file uses the following encoding: utf-8
# test_import_ct_rdsr_canon_ssde.py

import datetime
import os
from decimal import Decimal
from django.test import TestCase
from remapp.extractors import rdsr
from remapp.models import (
    GeneralStudyModuleAttr,
    PatientIDSettings,
    NotPatientIndicatorsID,
    NotPatientIndicatorsName,
)


class ImportCTRDSR(TestCase):
    def setUp(self):
        """Adds the not-patient patterns to match against - set to be the same as in release 0.7.4"""
        NotPatientIndicatorsID(not_patient_id="*qa*").save()
        NotPatientIndicatorsID(not_patient_id="*phy*").save()
        NotPatientIndicatorsID(not_patient_id="*test*").save()
        NotPatientIndicatorsName(not_patient_name="*phys*").save()
        NotPatientIndicatorsName(not_patient_name="*test*").save()
        NotPatientIndicatorsName(not_patient_name="*qa*").save()

    def test_import_ct_rdsr_canon_ssde(self):
        """
        Imports a known RDSR file derived from a Canon Aquilion Serve SP, and tests all the values
        imported against those expected.
        """
        PatientIDSettings.objects.create()

        dicom_file = r"test_files/CT-RDSR-Canon_PRISM-SSDE.dcm"
        root_tests = os.path.dirname(os.path.abspath(__file__))
        dicom_path = os.path.join(root_tests, dicom_file)

        rdsr.rdsr(dicom_path)
        study = GeneralStudyModuleAttr.objects.order_by("id")[0]

        # Test that patient identifiable data is not stored
        self.assertEqual(study.patientmoduleattr_set.get().patient_name, None)
        self.assertEqual(study.patientmoduleattr_set.get().not_patient_indicator, 'IDs: *test* | Names: *test*')

        # Test that study level data is recorded correctly
        self.assertEqual(study.study_date, datetime.date(2025, 9, 30))
        self.assertEqual(study.study_time, datetime.time(12, 53, 28))
        self.assertEqual(study.accession_number, "0001.0002")
        self.assertEqual(study.study_description, "CT THORAX ABDOMEN")
        self.assertEqual(study.modality_type, "CT")

        self.assertEqual(
            study.generalequipmentmoduleattr_set.get().institution_name,
            "Radboudumc",
        )
        self.assertEqual(
            study.generalequipmentmoduleattr_set.get().manufacturer, "CANON_MEC"
        )
        self.assertEqual(
            study.generalequipmentmoduleattr_set.get().manufacturer_model_name,
            "Aquilion Serve SP",
        )
        self.assertEqual(
            study.generalequipmentmoduleattr_set.get().station_name, "rdctcan61"
        )

        # Test that patient study level data is recorded correctly
        self.assertEqual(study.patientstudymoduleattr_set.get().patient_age, "035Y")
        self.assertAlmostEqual(
            study.patientstudymoduleattr_set.get().patient_age_decimal, Decimal(35.7)
        )

        # Test that irradiation time data is stored correctly
        self.assertEqual(
            study.ctradiationdose_set.get().start_of_xray_irradiation,
            datetime.datetime(2025, 9, 30, 12, 53, 58),
        )
        self.assertEqual(
            study.ctradiationdose_set.get().end_of_xray_irradiation,
            datetime.datetime(2025, 9, 30, 12, 57, 9),
        )
        self.assertEqual(
            study.ctradiationdose_set.get().procedure_reported.code_meaning,
            "Computed Tomography X-Ray",
        )
        self.assertEqual(
            study.ctradiationdose_set.get().has_intent.code_meaning, "Diagnostic Intent"
        )
        self.assertEqual(
            study.ctradiationdose_set.get().source_of_dose_information.code_meaning,
            "Automated Data Collection",
        )

        # Test that device observer data is stored correctly
        self.assertEqual(
            study.ctradiationdose_set.get()
            .observercontext_set.get()
            .device_observer_uid,
            "1.2.392.200036.9116.2.6.1.41014.3167466974",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .observercontext_set.get()
            .observer_type.code_meaning,
            "Device",
        )
        self.assertEqual(
            study.ctradiationdose_set.get().scope_of_accumulation.code_meaning, "Study"
        )

        # Test that exposure data is recorded correctly
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctaccumulateddosedata_set.get()
            .total_number_of_irradiation_events,
            4,
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctaccumulateddosedata_set.get()
            .ct_dose_length_product_total,
            Decimal(327.3),
        )

        # Test that CT event data is recorded correctly
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .exposure_time,
            Decimal(7.26),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .nominal_single_collimation_width,
            Decimal(1.0),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .nominal_total_collimation_width,
            Decimal(40.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .acquisition_protocol,
            "CT Thorax Abdomen met i.v.",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .target_region.code_meaning,
            "Chest, Abdomen and Pelvis",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .exposure_time,
            Decimal(2.92),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .nominal_single_collimation_width,
            Decimal(0.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .nominal_total_collimation_width,
            Decimal(4),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .acquisition_protocol,
            "CT Thorax Abdomen met i.v.",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .exposure_time,
            Decimal(3.47),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .nominal_single_collimation_width,
            Decimal(0.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .nominal_total_collimation_width,
            Decimal(40),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .acquisition_protocol,
            "CT Thorax Abdomen met i.v.",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .exposure_time,
            Decimal(4.88),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .nominal_single_collimation_width,
            Decimal(0.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .nominal_total_collimation_width,
            Decimal(40),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .acquisition_protocol,
            "CT Thorax Abdomen met i.v.",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ct_acquisition_type.code_meaning,
            "Spiral Acquisition",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ct_acquisition_type.code_meaning,
            "Stationary Acquisition",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ct_acquisition_type.code_meaning,
            "Spiral Acquisition",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ct_acquisition_type.code_meaning,
            "Spiral Acquisition",
        )

        # Test that CT xraysource data is recorded correctly
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ctxraysourceparameters_set.get()
            .kvp,
            Decimal(120),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ctxraysourceparameters_set.get()
            .maximum_xray_tube_current,
            Decimal(50),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ctxraysourceparameters_set.get()
            .xray_tube_current,
            Decimal(50),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ctxraysourceparameters_set.get()
            .exposure_time_per_rotation,
            Decimal(0.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ctxraysourceparameters_set.get()
            .kvp,
            Decimal(100),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ctxraysourceparameters_set.get()
            .maximum_xray_tube_current,
            Decimal(50),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ctxraysourceparameters_set.get()
            .xray_tube_current,
            Decimal(50),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ctxraysourceparameters_set.get()
            .exposure_time_per_rotation,
            Decimal(0.35),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ctxraysourceparameters_set.get()
            .kvp,
            Decimal(100),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ctxraysourceparameters_set.get()
            .maximum_xray_tube_current,
            Decimal(40),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ctxraysourceparameters_set.get()
            .xray_tube_current,
            Decimal(40),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ctxraysourceparameters_set.get()
            .exposure_time_per_rotation,
            Decimal(0.35),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ctxraysourceparameters_set.get()
            .kvp,
            Decimal(120),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ctxraysourceparameters_set.get()
            .maximum_xray_tube_current,
            Decimal(300),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ctxraysourceparameters_set.get()
            .xray_tube_current,
            Decimal(300),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ctxraysourceparameters_set.get()
            .exposure_time_per_rotation,
            Decimal(0.5),
        )

        # Test that scanning length data is recorded correctly
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .scanninglength_set.get()
            .scanning_length,
            Decimal(856),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .scanninglength_set.get()
            .scanning_length,
            Decimal(4),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .scanninglength_set.get()
            .scanning_length,
            Decimal(322),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .scanninglength_set.get()
            .scanning_length,
            Decimal(249),
        )

        # Test that CT Dose data is recorded correctly
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .mean_ctdivol,
            Decimal(0.2),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .dlp,
            Decimal(17.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .ctdiw_phantom_type.code_meaning,
            "IEC Body Dosimetry Phantom",
        )
        # check SSDE/WED per z-location
        self.assertFalse(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[0]
            .sizespecificdoseestimation_set.exists()
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .mean_ctdivol,
            Decimal(9.1),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .dlp,
            Decimal(3.6),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .ctdiw_phantom_type.code_meaning,
            "IEC Body Dosimetry Phantom",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.all()[0]
            .size_specific_dose_estimation,
            Decimal(26.3),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter,
            Decimal(66.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.all()[0]
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
        # check SSDE/WED per z-location
        ssde_expected = [
                            {
                                "ssde_at_longitudinal_z": Decimal("26.35700000"),
                                "longitudinal_position_z": Decimal("-1259.00000000"),
                                "wed_at_longitudional_z": Decimal("66.33000000"),
                            },
                            {
                                "ssde_at_longitudinal_z": Decimal("26.33200000"),
                                "longitudinal_position_z": Decimal("-1258.00000000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "ssde_at_longitudinal_z": Decimal("26.28300000"),
                                "longitudinal_position_z": Decimal("-1257.00000000"),
                                "wed_at_longitudional_z": Decimal("67.11000000"),
                            },
                            {
                                "ssde_at_longitudinal_z": Decimal("26.31800000"),
                                "longitudinal_position_z": Decimal("-1256.00000000"),
                                "wed_at_longitudional_z": Decimal("66.74000000"),
                            },
                            {
                                "ssde_at_longitudinal_z": Decimal("26.38600000"),
                                "longitudinal_position_z": Decimal("-1255.00000000"),
                                "wed_at_longitudional_z": Decimal("66.04000000"),
                            },
                        ]
        set_ssde_expected = {frozenset(d.items()) for d in ssde_expected}
        set_ssde_found = {frozenset(d.items()) for d in
                          study.ctradiationdose_set.get()
                          .ctirradiationeventdata_set.order_by("id")[1]
                          .sizespecificdoseestimation_set.all()[0]
                          .ssdelongitudinalpositiondetail_set.values("ssde_at_longitudinal_z",
                                                                     "longitudinal_position_z",
                                                                     "wed_at_longitudional_z")
                         }
        self.assertEqual(set_ssde_expected, set_ssde_found)

        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .mean_ctdivol,
            Decimal(0.5),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .dlp,
            Decimal(15.4),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .ctdiw_phantom_type.code_meaning,
            "IEC Body Dosimetry Phantom",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.all()[0]
            .size_specific_dose_estimation,
            Decimal(1.4),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter,
            Decimal(67.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.all()[0]
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
        ssde_expected = [
                            {
                                "longitudinal_position_z": Decimal("-1452.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.77000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1451.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.93000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1450.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40800000"),
                                "wed_at_longitudional_z": Decimal("67.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1449.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.16000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1448.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1447.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.47000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1446.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1445.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1444.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1443.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1442.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1441.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1440.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.12000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1439.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.87000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1438.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1437.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1436.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1435.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1434.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1433.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1432.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1431.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1430.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.47000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1429.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1428.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1427.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1426.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1425.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.13000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1424.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1423.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("65.99000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1422.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1421.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1420.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1419.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.29000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1418.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1417.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1416.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1415.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1414.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.86000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1413.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.95000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1412.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.37000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1411.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.49000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1410.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1409.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.92000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1408.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.93000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1407.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1406.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1405.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1404.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1403.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1402.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1401.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.76000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1400.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1399.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1398.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.95000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1397.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("66.99000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1396.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1395.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1394.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.03000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1393.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.98000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1392.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.07000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1391.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1390.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1389.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.82000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1388.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1387.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.96000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1386.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1385.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1384.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1383.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.42000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1382.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1381.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.25000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1380.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.85000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1379.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1378.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.62000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1377.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1376.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1375.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1374.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.46000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1373.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1372.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1371.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1370.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1369.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("65.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1368.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.07000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1367.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.39000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1366.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("66.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1365.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41700000"),
                                "wed_at_longitudional_z": Decimal("65.76000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1364.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41700000"),
                                "wed_at_longitudional_z": Decimal("65.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1363.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1362.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1361.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1360.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1359.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.06000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1358.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.69000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1357.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1356.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.49000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1355.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1354.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1353.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1352.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1351.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1350.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1349.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1348.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1347.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.95000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1346.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1345.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1344.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1343.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1342.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1341.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.52000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1340.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.57000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1339.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1338.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1337.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.86000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1336.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.67000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1335.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.98000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1334.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40800000"),
                                "wed_at_longitudional_z": Decimal("67.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1333.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1332.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.16000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1331.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1330.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1329.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1328.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.64000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1327.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1326.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1325.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1324.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1323.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1322.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.12000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1321.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.32000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1320.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1319.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1318.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1317.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1316.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.52000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1315.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1314.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.62000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1313.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1312.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.45000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1311.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1310.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("65.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1309.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("65.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1308.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1307.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1306.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1305.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1304.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.65000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1303.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.32000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1302.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41700000"),
                                "wed_at_longitudional_z": Decimal("65.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1301.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.16000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1300.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.29000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1299.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.52000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1298.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.82000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1297.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.45000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1296.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1295.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1294.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.93000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1293.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1292.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1291.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("66.99000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1290.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1289.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.64000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1288.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1287.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1286.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.68000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1285.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.22000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1284.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1283.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1282.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1281.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.62000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1280.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1279.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1278.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1277.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1276.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1275.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1274.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1273.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40800000"),
                                "wed_at_longitudional_z": Decimal("67.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1272.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1271.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1270.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1269.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1268.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.35000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1267.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.89000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1266.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1265.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1264.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1263.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1262.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1261.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.69000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1260.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.54000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1259.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.33000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1258.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1257.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1256.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.74000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1255.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1254.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1253.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1252.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.39000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1251.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1250.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1249.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1248.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1247.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1246.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1245.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1244.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1243.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41600000"),
                                "wed_at_longitudional_z": Decimal("65.99000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1242.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.15000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1241.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1240.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1239.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1238.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.77000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1237.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1236.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1235.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1234.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1233.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1232.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.86000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1231.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1230.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1229.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1228.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1227.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.87000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1226.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.12000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1225.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.45000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1224.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1223.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1222.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1221.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1220.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1219.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.12000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1218.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.96000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1217.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.92000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1216.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.27000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1215.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.30000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1214.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1213.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1212.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1211.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1210.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.85000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1209.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1208.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1207.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.72000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1206.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.79000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1205.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1204.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1203.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.92000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1202.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1201.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1200.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1199.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1198.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1197.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1196.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1195.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1194.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.13000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1193.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.07000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1192.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1191.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1190.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1189.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1188.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1187.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1186.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.19000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1185.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.06000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1184.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1183.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1182.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1181.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1180.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1179.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1178.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1177.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1176.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1175.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.79000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1174.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.86000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1173.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1172.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1171.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1170.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.54000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1169.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1168.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1167.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.45000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1166.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1165.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1164.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1163.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1162.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1161.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("66.99000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1160.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1159.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1158.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41000000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1157.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40800000"),
                                "wed_at_longitudional_z": Decimal("67.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1156.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.22000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1155.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1154.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.94000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1153.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40900000"),
                                "wed_at_longitudional_z": Decimal("67.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1152.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.40700000"),
                                "wed_at_longitudional_z": Decimal("67.57000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1151.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.85000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1150.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.69000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1149.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.68000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1148.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1147.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1146.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1145.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1144.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1143.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1142.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1141.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41100000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1140.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.71000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1139.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1138.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1137.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1136.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41200000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1135.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1134.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.33000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1133.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41300000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1132.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.35000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1131.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41500000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1130.00000000"),
                                "ssde_at_longitudinal_z": Decimal("1.41400000"),
                                "wed_at_longitudional_z": Decimal("66.36000000"),
                            },
                        ]
        set_ssde_expected = {frozenset(d.items()) for d in ssde_expected}
        set_ssde_found = {frozenset(d.items()) for d in
                          study.ctradiationdose_set.get()
                          .ctirradiationeventdata_set.order_by("id")[2]
                          .sizespecificdoseestimation_set.all()[0]
                          .ssdelongitudinalpositiondetail_set.values("ssde_at_longitudinal_z",
                                                                     "longitudinal_position_z",
                                                                     "wed_at_longitudional_z")
                         }
        self.assertEqual(set_ssde_expected, set_ssde_found)

        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .mean_ctdivol,
            Decimal(12.0),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .dlp,
            Decimal(290.8),
        )
        # check SSDE/WED per z-location
        ssde_expected = [
                            {
                                "longitudinal_position_z": Decimal("-1451.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84200000"),
                                "wed_at_longitudional_z": Decimal("66.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1450.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73200000"),
                                "wed_at_longitudional_z": Decimal("67.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1449.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71600000"),
                                "wed_at_longitudional_z": Decimal("67.49000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1448.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79900000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1447.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1446.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.92500000"),
                                "wed_at_longitudional_z": Decimal("65.85000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1445.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78900000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1444.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83800000"),
                                "wed_at_longitudional_z": Decimal("66.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1443.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82600000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1442.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88200000"),
                                "wed_at_longitudional_z": Decimal("66.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1441.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85100000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1440.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93200000"),
                                "wed_at_longitudional_z": Decimal("65.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1439.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1438.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73900000"),
                                "wed_at_longitudional_z": Decimal("67.31000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1437.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91700000"),
                                "wed_at_longitudional_z": Decimal("65.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1436.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82400000"),
                                "wed_at_longitudional_z": Decimal("66.64000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1435.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91000000"),
                                "wed_at_longitudional_z": Decimal("65.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1434.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83500000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1433.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77100000"),
                                "wed_at_longitudional_z": Decimal("67.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1432.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88600000"),
                                "wed_at_longitudional_z": Decimal("66.16000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1431.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87700000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1430.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86400000"),
                                "wed_at_longitudional_z": Decimal("66.33000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1429.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82800000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1428.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87300000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1427.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93400000"),
                                "wed_at_longitudional_z": Decimal("65.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1426.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81700000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1425.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.94500000"),
                                "wed_at_longitudional_z": Decimal("65.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1424.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83300000"),
                                "wed_at_longitudional_z": Decimal("66.57000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1423.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.92100000"),
                                "wed_at_longitudional_z": Decimal("65.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1422.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89300000"),
                                "wed_at_longitudional_z": Decimal("66.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1421.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81500000"),
                                "wed_at_longitudional_z": Decimal("66.71000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1420.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91900000"),
                                "wed_at_longitudional_z": Decimal("65.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1419.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88100000"),
                                "wed_at_longitudional_z": Decimal("66.20000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1418.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85700000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1417.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86200000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1416.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93800000"),
                                "wed_at_longitudional_z": Decimal("65.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1415.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1414.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80900000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1413.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78200000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1412.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78800000"),
                                "wed_at_longitudional_z": Decimal("66.93000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1411.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93000000"),
                                "wed_at_longitudional_z": Decimal("65.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1410.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75700000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1409.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75500000"),
                                "wed_at_longitudional_z": Decimal("67.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1408.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1407.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75200000"),
                                "wed_at_longitudional_z": Decimal("67.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1406.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79900000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1405.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80200000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1404.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1403.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81800000"),
                                "wed_at_longitudional_z": Decimal("66.68000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1402.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84400000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1401.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85700000"),
                                "wed_at_longitudional_z": Decimal("66.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1400.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76100000"),
                                "wed_at_longitudional_z": Decimal("67.14000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1399.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84400000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1398.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81300000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1397.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75700000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1396.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80200000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1395.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80600000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1394.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.74400000"),
                                "wed_at_longitudional_z": Decimal("67.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1393.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80400000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1392.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75700000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1391.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78200000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1390.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71600000"),
                                "wed_at_longitudional_z": Decimal("67.49000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1389.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83700000"),
                                "wed_at_longitudional_z": Decimal("66.54000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1388.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1387.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73000000"),
                                "wed_at_longitudional_z": Decimal("67.38000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1386.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83700000"),
                                "wed_at_longitudional_z": Decimal("66.54000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1385.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77700000"),
                                "wed_at_longitudional_z": Decimal("67.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1384.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87300000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1383.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85900000"),
                                "wed_at_longitudional_z": Decimal("66.37000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1382.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84600000"),
                                "wed_at_longitudional_z": Decimal("66.47000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1381.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91900000"),
                                "wed_at_longitudional_z": Decimal("65.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1380.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82900000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1379.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1378.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77900000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1377.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87500000"),
                                "wed_at_longitudional_z": Decimal("66.24000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1376.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89300000"),
                                "wed_at_longitudional_z": Decimal("66.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1375.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82800000"),
                                "wed_at_longitudional_z": Decimal("66.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1374.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86200000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1373.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83300000"),
                                "wed_at_longitudional_z": Decimal("66.57000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1372.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89200000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1371.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84200000"),
                                "wed_at_longitudional_z": Decimal("66.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1370.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88200000"),
                                "wed_at_longitudional_z": Decimal("66.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1369.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87900000"),
                                "wed_at_longitudional_z": Decimal("66.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1368.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.96000000"),
                                "wed_at_longitudional_z": Decimal("65.58000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1367.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83500000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1366.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87700000"),
                                "wed_at_longitudional_z": Decimal("66.23000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1365.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93600000"),
                                "wed_at_longitudional_z": Decimal("65.77000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1364.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93800000"),
                                "wed_at_longitudional_z": Decimal("65.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1363.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.96200000"),
                                "wed_at_longitudional_z": Decimal("65.57000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1362.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78900000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1361.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.95600000"),
                                "wed_at_longitudional_z": Decimal("65.61000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1360.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83500000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1359.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87100000"),
                                "wed_at_longitudional_z": Decimal("66.27000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1358.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.92500000"),
                                "wed_at_longitudional_z": Decimal("65.85000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1357.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71000000"),
                                "wed_at_longitudional_z": Decimal("67.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1356.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1355.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86400000"),
                                "wed_at_longitudional_z": Decimal("66.33000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1354.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79900000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1353.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82900000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1352.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77100000"),
                                "wed_at_longitudional_z": Decimal("67.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1351.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1350.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77000000"),
                                "wed_at_longitudional_z": Decimal("67.07000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1349.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78000000"),
                                "wed_at_longitudional_z": Decimal("66.98000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1348.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84400000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1347.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1346.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71400000"),
                                "wed_at_longitudional_z": Decimal("67.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1345.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89300000"),
                                "wed_at_longitudional_z": Decimal("66.10000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1344.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84600000"),
                                "wed_at_longitudional_z": Decimal("66.47000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1343.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81800000"),
                                "wed_at_longitudional_z": Decimal("66.68000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1342.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80600000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1341.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86200000"),
                                "wed_at_longitudional_z": Decimal("66.34000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1340.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81700000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1339.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1338.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75500000"),
                                "wed_at_longitudional_z": Decimal("67.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1337.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77500000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1336.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81700000"),
                                "wed_at_longitudional_z": Decimal("66.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1335.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82400000"),
                                "wed_at_longitudional_z": Decimal("66.64000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1334.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73700000"),
                                "wed_at_longitudional_z": Decimal("67.32000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1333.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71400000"),
                                "wed_at_longitudional_z": Decimal("67.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1332.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75000000"),
                                "wed_at_longitudional_z": Decimal("67.22000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1331.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1330.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.74300000"),
                                "wed_at_longitudional_z": Decimal("67.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1329.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78600000"),
                                "wed_at_longitudional_z": Decimal("66.94000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1328.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82600000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1327.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1326.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75900000"),
                                "wed_at_longitudional_z": Decimal("67.15000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1325.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90100000"),
                                "wed_at_longitudional_z": Decimal("66.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1324.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81300000"),
                                "wed_at_longitudional_z": Decimal("66.73000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1323.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87000000"),
                                "wed_at_longitudional_z": Decimal("66.29000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1322.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82900000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1321.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.95200000"),
                                "wed_at_longitudional_z": Decimal("65.64000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1320.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77900000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1319.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1318.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77700000"),
                                "wed_at_longitudional_z": Decimal("67.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1317.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84400000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1316.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84000000"),
                                "wed_at_longitudional_z": Decimal("66.51000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1315.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83800000"),
                                "wed_at_longitudional_z": Decimal("66.53000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1314.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80400000"),
                                "wed_at_longitudional_z": Decimal("66.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1313.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1312.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91000000"),
                                "wed_at_longitudional_z": Decimal("65.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1311.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78800000"),
                                "wed_at_longitudional_z": Decimal("66.93000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1310.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91400000"),
                                "wed_at_longitudional_z": Decimal("65.94000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1309.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93000000"),
                                "wed_at_longitudional_z": Decimal("65.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1308.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90400000"),
                                "wed_at_longitudional_z": Decimal("66.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1307.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85900000"),
                                "wed_at_longitudional_z": Decimal("66.37000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1306.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88800000"),
                                "wed_at_longitudional_z": Decimal("66.14000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1305.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89900000"),
                                "wed_at_longitudional_z": Decimal("66.06000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1304.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88600000"),
                                "wed_at_longitudional_z": Decimal("66.16000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1303.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76100000"),
                                "wed_at_longitudional_z": Decimal("67.14000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1302.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.97100000"),
                                "wed_at_longitudional_z": Decimal("65.49000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1301.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91200000"),
                                "wed_at_longitudional_z": Decimal("65.96000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1300.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85900000"),
                                "wed_at_longitudional_z": Decimal("66.37000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1299.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87900000"),
                                "wed_at_longitudional_z": Decimal("66.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1298.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80000000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1297.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80200000"),
                                "wed_at_longitudional_z": Decimal("66.81000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1296.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1295.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78000000"),
                                "wed_at_longitudional_z": Decimal("66.98000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1294.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77500000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1293.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79900000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1292.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90100000"),
                                "wed_at_longitudional_z": Decimal("66.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1291.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86000000"),
                                "wed_at_longitudional_z": Decimal("66.36000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1290.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.69800000"),
                                "wed_at_longitudional_z": Decimal("67.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1289.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1288.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79300000"),
                                "wed_at_longitudional_z": Decimal("66.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1287.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85100000"),
                                "wed_at_longitudional_z": Decimal("66.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1286.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88800000"),
                                "wed_at_longitudional_z": Decimal("66.14000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1285.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75000000"),
                                "wed_at_longitudional_z": Decimal("67.22000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1284.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75000000"),
                                "wed_at_longitudional_z": Decimal("67.22000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1283.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91000000"),
                                "wed_at_longitudional_z": Decimal("65.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1282.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77100000"),
                                "wed_at_longitudional_z": Decimal("67.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1281.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1280.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79900000"),
                                "wed_at_longitudional_z": Decimal("66.84000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1279.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82200000"),
                                "wed_at_longitudional_z": Decimal("66.66000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1278.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78200000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1277.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.72300000"),
                                "wed_at_longitudional_z": Decimal("67.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1276.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80900000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1275.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77300000"),
                                "wed_at_longitudional_z": Decimal("67.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1274.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77700000"),
                                "wed_at_longitudional_z": Decimal("67.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1273.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.69300000"),
                                "wed_at_longitudional_z": Decimal("67.67000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1272.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1271.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78900000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1270.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.70100000"),
                                "wed_at_longitudional_z": Decimal("67.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1269.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78400000"),
                                "wed_at_longitudional_z": Decimal("66.95000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1268.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77900000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1267.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.68900000"),
                                "wed_at_longitudional_z": Decimal("67.70000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1266.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1265.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.70100000"),
                                "wed_at_longitudional_z": Decimal("67.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1264.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93200000"),
                                "wed_at_longitudional_z": Decimal("65.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1263.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82900000"),
                                "wed_at_longitudional_z": Decimal("66.60000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1262.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79100000"),
                                "wed_at_longitudional_z": Decimal("66.90000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1261.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.83500000"),
                                "wed_at_longitudional_z": Decimal("66.56000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1260.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80000000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1259.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87300000"),
                                "wed_at_longitudional_z": Decimal("66.26000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1258.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85300000"),
                                "wed_at_longitudional_z": Decimal("66.41000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1257.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80600000"),
                                "wed_at_longitudional_z": Decimal("66.78000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1256.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.72300000"),
                                "wed_at_longitudional_z": Decimal("67.43000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1255.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89900000"),
                                "wed_at_longitudional_z": Decimal("66.06000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1254.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90300000"),
                                "wed_at_longitudional_z": Decimal("66.03000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1253.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80000000"),
                                "wed_at_longitudional_z": Decimal("66.83000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1252.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.86800000"),
                                "wed_at_longitudional_z": Decimal("66.30000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1251.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84400000"),
                                "wed_at_longitudional_z": Decimal("66.48000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1250.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89500000"),
                                "wed_at_longitudional_z": Decimal("66.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1249.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1248.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84800000"),
                                "wed_at_longitudional_z": Decimal("66.46000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1247.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90600000"),
                                "wed_at_longitudional_z": Decimal("66.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1246.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.87900000"),
                                "wed_at_longitudional_z": Decimal("66.21000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1245.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90400000"),
                                "wed_at_longitudional_z": Decimal("66.01000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1244.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84900000"),
                                "wed_at_longitudional_z": Decimal("66.44000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1243.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.88200000"),
                                "wed_at_longitudional_z": Decimal("66.18000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1242.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93200000"),
                                "wed_at_longitudional_z": Decimal("65.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1241.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84200000"),
                                "wed_at_longitudional_z": Decimal("66.50000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1240.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78200000"),
                                "wed_at_longitudional_z": Decimal("66.97000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1239.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.93200000"),
                                "wed_at_longitudional_z": Decimal("65.80000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1238.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82600000"),
                                "wed_at_longitudional_z": Decimal("66.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1237.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78900000"),
                                "wed_at_longitudional_z": Decimal("66.91000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1236.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76200000"),
                                "wed_at_longitudional_z": Decimal("67.12000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1235.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89000000"),
                                "wed_at_longitudional_z": Decimal("66.13000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1234.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.74300000"),
                                "wed_at_longitudional_z": Decimal("67.28000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1233.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.82000000"),
                                "wed_at_longitudional_z": Decimal("66.67000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1232.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73700000"),
                                "wed_at_longitudional_z": Decimal("67.32000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1231.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1230.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77300000"),
                                "wed_at_longitudional_z": Decimal("67.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1229.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89000000"),
                                "wed_at_longitudional_z": Decimal("66.13000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1228.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77900000"),
                                "wed_at_longitudional_z": Decimal("67.00000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1227.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.85500000"),
                                "wed_at_longitudional_z": Decimal("66.40000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1226.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73400000"),
                                "wed_at_longitudional_z": Decimal("67.35000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1225.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.79300000"),
                                "wed_at_longitudional_z": Decimal("66.88000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1224.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.90300000"),
                                "wed_at_longitudional_z": Decimal("66.03000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1223.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77500000"),
                                "wed_at_longitudional_z": Decimal("67.02000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1222.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80800000"),
                                "wed_at_longitudional_z": Decimal("66.77000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1221.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77100000"),
                                "wed_at_longitudional_z": Decimal("67.05000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1220.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.74100000"),
                                "wed_at_longitudional_z": Decimal("67.29000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1219.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76800000"),
                                "wed_at_longitudional_z": Decimal("67.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1218.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.75700000"),
                                "wed_at_longitudional_z": Decimal("67.17000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1217.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.80900000"),
                                "wed_at_longitudional_z": Decimal("66.75000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1216.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76800000"),
                                "wed_at_longitudional_z": Decimal("67.08000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1215.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71900000"),
                                "wed_at_longitudional_z": Decimal("67.46000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1214.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76100000"),
                                "wed_at_longitudional_z": Decimal("67.14000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1213.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73500000"),
                                "wed_at_longitudional_z": Decimal("67.33000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1212.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.76600000"),
                                "wed_at_longitudional_z": Decimal("67.09000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1211.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.69800000"),
                                "wed_at_longitudional_z": Decimal("67.63000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1210.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.78000000"),
                                "wed_at_longitudional_z": Decimal("66.98000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1209.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.81500000"),
                                "wed_at_longitudional_z": Decimal("66.71000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1208.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.77300000"),
                                "wed_at_longitudional_z": Decimal("67.04000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1207.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.91200000"),
                                "wed_at_longitudional_z": Decimal("65.96000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1206.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.71800000"),
                                "wed_at_longitudional_z": Decimal("67.47000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1205.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89200000"),
                                "wed_at_longitudional_z": Decimal("66.11000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1204.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.89900000"),
                                "wed_at_longitudional_z": Decimal("66.06000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1203.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.84800000"),
                                "wed_at_longitudional_z": Decimal("66.46000000"),
                            },
                            {
                                "longitudinal_position_z": Decimal("-1202.50000000"),
                                "ssde_at_longitudinal_z": Decimal("34.73000000"),
                                "wed_at_longitudional_z": Decimal("67.38000000"),
                            },
                        ]
        set_ssde_expected = {frozenset(d.items()) for d in ssde_expected}
        set_ssde_found = {frozenset(d.items()) for d in
                          study.ctradiationdose_set.get()
                          .ctirradiationeventdata_set.order_by("id")[3]
                          .sizespecificdoseestimation_set.all()[0]
                          .ssdelongitudinalpositiondetail_set.values("ssde_at_longitudinal_z",
                                                                     "longitudinal_position_z",
                                                                     "wed_at_longitudional_z")
                         }
        self.assertEqual(set_ssde_expected, set_ssde_found)


        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .procedure_context.code_meaning,
            "Diagnostic radiography with contrast media",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .number_of_xray_sources,
            Decimal(1),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .ctdiw_phantom_type.code_meaning,
            "IEC Body Dosimetry Phantom",
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.all()[0]
            .size_specific_dose_estimation,
            Decimal(34.8),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter,
            Decimal(67.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.all()[0]
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.all()[0]
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
