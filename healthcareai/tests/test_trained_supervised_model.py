import unittest
import numpy as np
import pandas as pd

import healthcareai.tests.helpers as helpers
from healthcareai.common.healthcareai_error import HealthcareAIError
from healthcareai.trainer import SupervisedModelTrainer


class TestTrainedSupervisedModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """ Load a dataframe, train a linear model and prepare a prediction dataframe for assertions """
        training_df = helpers.load_sample_dataframe()

        # Drop columns that won't help machine learning
        training_df.drop(['PatientID', 'InTestWindowFLG'], axis=1, inplace=True)

        hcai = SupervisedModelTrainer(
            training_df,
            'SystolicBPNBR',
            'regression',
            impute=True,
            grain_column='PatientEncounterID')

        # Train the linear regression model
        cls.trained_linear_model = hcai.linear_regression()

        # Load a new df for predicting
        cls.prediction_df = helpers.load_sample_dataframe()

        # Drop columns that won't help machine learning
        columns_to_remove = ['PatientID', 'InTestWindowFLG']
        cls.prediction_df.drop(columns_to_remove, axis=1, inplace=True)

        # Create various outputs
        cls.predictions = cls.trained_linear_model.make_predictions(cls.prediction_df)
        cls.factors = cls.trained_linear_model.make_factors(cls.prediction_df, number_top_features=3)
        cls.predictions_with_3_factors = cls.trained_linear_model.make_predictions_with_k_factors(
            cls.prediction_df,
            number_top_features=3)
        cls.original_with_predictions_3_factors = cls.trained_linear_model.make_original_with_predictions_and_features(
            cls.prediction_df,
            number_top_features=3)
        cls.catalyst_dataframe = cls.trained_linear_model.create_catalyst_dataframe(cls.prediction_df)

    def test_top_k_factors_raises_error_on_more_features_than_model_has(self):
        self.assertRaises(HealthcareAIError, self.trained_linear_model.make_factors, self.prediction_df, 10)

    def test_predictions_is_numpy_array(self):
        self.assertIsInstance(self.predictions, np.ndarray)

    def test_predictions_are_same_length_as_input(self):
        self.assertEqual(len(self.predictions), len(self.prediction_df))

    def test_factors_return_is_dataframe(self):
        self.assertIsInstance(self.factors, pd.DataFrame)

    def test_factors_are_same_length_as_input(self):
        self.assertEqual(len(self.factors), len(self.prediction_df))

    def test_factors_columns(self):
        expected = ['PatientEncounterID', 'Factor1TXT', 'Factor2TXT', 'Factor3TXT']
        results = self.factors.columns.values
        self.assertTrue(set(expected) == set(results))

    def test_predictions_with_factors_return_is_dataframe(self):
        self.assertIsInstance(self.predictions_with_3_factors, pd.DataFrame)

    def test_predictions_with_factors_are_same_length_as_input(self):
        self.assertEqual(len(self.predictions_with_3_factors), len(self.prediction_df))

    def test_predictions_with_factors_columns(self):
        expected = ['PatientEncounterID', 'SystolicBPNBR', 'Factor1TXT', 'Factor2TXT', 'Factor3TXT']
        results = self.predictions_with_3_factors.columns.values
        self.assertTrue(set(expected) == set(results))

    def test_original_with_predictions_factors_return_is_dataframe(self):
        self.assertIsInstance(self.original_with_predictions_3_factors, pd.DataFrame)

    def test_original_with_predictions_factors_are_same_length_as_input(self):
        self.assertEqual(len(self.original_with_predictions_3_factors), len(self.prediction_df))

    def test_original_with_predictions_factors_columns(self):
        expected = ['PatientEncounterID', 'SystolicBPNBR', 'LDLNBR', 'A1CNBR', 'GenderFLG', 'ThirtyDayReadmitFLG',
                    'Factor1TXT', 'Factor2TXT', 'Factor3TXT']
        results = self.original_with_predictions_3_factors.columns.values
        self.assertTrue(set(expected) == set(results))

    def test_catalyst_return_is_dataframe(self):
        self.assertIsInstance(self.catalyst_dataframe, pd.DataFrame)

    def test_catalyst_are_same_length_as_input(self):
        self.assertEqual(len(self.catalyst_dataframe), len(self.prediction_df))

    def test_catalyst_columns(self):
        expected = ['PatientEncounterID', 'Factor1TXT', 'Factor2TXT', 'Factor3TXT', 'SystolicBPNBR', 'BindingID',
                    'BindingNM', 'LastLoadDTS']
        results = self.catalyst_dataframe.columns.values
        self.assertTrue(set(expected) == set(results))

    def test_metrics_returns_object(self):
        self.assertIsInstance(self.trained_linear_model.metrics(), dict)

    def test_prepare_and_subset_returns_dataframe(self):
        self.assertIsInstance(self.trained_linear_model.prepare_and_subset(self.prediction_df), pd.DataFrame)


if __name__ == '__main__':
    unittest.main()
