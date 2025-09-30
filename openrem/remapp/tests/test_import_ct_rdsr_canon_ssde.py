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
        self.assertEqual(study.patientmoduleattr_set.get().not_patient_indicator, None)

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
            .size_specific_dose_estimation,
            Decimal(26.3),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter,
            Decimal(66.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.get()
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[1]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
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
            .size_specific_dose_estimation,
            Decimal(1.4),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter,
            Decimal(67.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.get()
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[2]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
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
            .size_specific_dose_estimation,
            Decimal(34.8),
        )
        self.assertAlmostEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter,
            Decimal(67.0),
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.get()
            .measurement_method.code_meaning,
            "Arithmetic Average of SSDE(z)",
        )
        self.assertEqual(
            study.ctradiationdose_set.get()
            .ctirradiationeventdata_set.order_by("id")[3]
            .sizespecificdoseestimation_set.get()
            .water_equivalent_diameter_method.code_meaning,
            "Water Equivalent Diameter From Localizer",
        )
