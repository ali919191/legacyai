import os
import sys
import unittest

# Ensure tests import from the correct package path without pulling in backend/app.py
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_PACKAGE_DIR = os.path.join(ROOT_DIR, "app")
if APP_PACKAGE_DIR not in sys.path:
    sys.path.insert(0, APP_PACKAGE_DIR)

from services.security.response_moderation_service import (
    ResponseModerationService,
    ContentSensitivity,
)
from utils.test_logger import test_logger


class TestResponseModerationService(unittest.TestCase):
    def setUp(self):
        self.moderation_service = ResponseModerationService()

    def test_safe_response_passes_moderation(self):
        safe_response = "I remember our family vacation to the beach. It was wonderful spending time together."

        try:
            result = self.moderation_service.review_response(safe_response)

            self.assertTrue(result['is_safe'])
            self.assertEqual(result['sensitivity_level'], ContentSensitivity.SAFE)
            self.assertEqual(len(result['issues_found']), 0)

            test_logger.log_test_result(
                test_name="ResponseModerationService.safe_response_passes_moderation",
                input_params={"response": safe_response},
                expected_result={"is_safe": True, "sensitivity_level": "SAFE", "issues_count": 0},
                actual_result={"is_safe": result['is_safe'], "sensitivity_level": str(result['sensitivity_level']), "issues_count": len(result['issues_found'])},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.safe_response_passes_moderation",
                input_params={"response": safe_response},
                expected_result={"is_safe": True, "sensitivity_level": "SAFE", "issues_count": 0},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_violence_content_detected(self):
        violent_response = "I was involved in a violent fight that almost killed someone."

        try:
            result = self.moderation_service.review_response(violent_response)

            self.assertFalse(result['is_safe'])
            self.assertIn('violence', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.violence_content_detected",
                input_params={"response": violent_response},
                expected_result={"is_safe": False, "contains_violence": True},
                actual_result={"is_safe": result['is_safe'], "categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.violence_content_detected",
                input_params={"response": violent_response},
                expected_result={"is_safe": False, "contains_violence": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_illegal_activity_detected(self):
        illegal_response = "I used to deal drugs and make illegal money."

        try:
            result = self.moderation_service.review_response(illegal_response)

            self.assertFalse(result['is_safe'])
            self.assertIn('illegal_activity', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.illegal_activity_detected",
                input_params={"response": illegal_response},
                expected_result={"is_safe": False, "contains_illegal": True},
                actual_result={"is_safe": result['is_safe'], "categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.illegal_activity_detected",
                input_params={"response": illegal_response},
                expected_result={"is_safe": False, "contains_illegal": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_self_harm_content_detected(self):
        self_harm_response = "I was feeling so hopeless that I wanted to end my life."

        try:
            result = self.moderation_service.review_response(self_harm_response)

            self.assertFalse(result['is_safe'])
            self.assertIn('self_harm', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.self_harm_content_detected",
                input_params={"response": self_harm_response},
                expected_result={"is_safe": False, "contains_self_harm": True},
                actual_result={"is_safe": result['is_safe'], "categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.self_harm_content_detected",
                input_params={"response": self_harm_response},
                expected_result={"is_safe": False, "contains_self_harm": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_explicit_content_detected(self):
        explicit_response = "That intimate night we shared was very passionate and sexual."

        try:
            result = self.moderation_service.review_response(explicit_response)

            # Should detect explicit content issues
            self.assertIn('explicit_content', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.explicit_content_detected",
                input_params={"response": explicit_response},
                expected_result={"contains_explicit": True},
                actual_result={"categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.explicit_content_detected",
                input_params={"response": explicit_response},
                expected_result={"contains_explicit": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_hate_speech_detected(self):
        hate_response = "I can't stand those people, they're all bigots and racists."

        try:
            result = self.moderation_service.review_response(hate_response)

            self.assertFalse(result['is_safe'])
            self.assertIn('hate_speech', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.hate_speech_detected",
                input_params={"response": hate_response},
                expected_result={"is_safe": False, "contains_hate_speech": True},
                actual_result={"is_safe": result['is_safe'], "categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.hate_speech_detected",
                input_params={"response": hate_response},
                expected_result={"is_safe": False, "contains_hate_speech": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_medical_sensitive_content_detected(self):
        medical_response = "I was diagnosed with cancer and it was terminal."

        try:
            result = self.moderation_service.review_response(medical_response)

            # Should detect medical sensitive content issues
            self.assertIn('medical_sensitive', [issue['category'] for issue in result['issues_found']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.medical_sensitive_content_detected",
                input_params={"response": medical_response},
                expected_result={"contains_medical_sensitive": True},
                actual_result={"categories": [issue['category'] for issue in result['issues_found']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.medical_sensitive_content_detected",
                input_params={"response": medical_response},
                expected_result={"contains_medical_sensitive": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_adjust_response_if_needed_safe_response(self):
        safe_response = "I love spending time with my family and friends."

        try:
            adjusted = self.moderation_service.adjust_response_if_needed(safe_response)

            self.assertEqual(adjusted, safe_response)  # Should remain unchanged

            test_logger.log_test_result(
                test_name="ResponseModerationService.adjust_response_if_needed_safe",
                input_params={"response": safe_response},
                expected_result={"adjusted": safe_response},
                actual_result={"adjusted": adjusted},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.adjust_response_if_needed_safe",
                input_params={"response": safe_response},
                expected_result={"adjusted": safe_response},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_adjust_response_if_needed_inappropriate_response(self):
        inappropriate_response = "I was involved in violent crimes and illegal activities."

        try:
            adjusted = self.moderation_service.adjust_response_if_needed(inappropriate_response)

            self.assertNotEqual(adjusted, inappropriate_response)  # Should be replaced
            # Check for common safe response patterns
            safe_patterns = ["I'm not able to discuss", "That topic isn't appropriate", "I can't discuss"]
            self.assertTrue(any(pattern in adjusted for pattern in safe_patterns))

            test_logger.log_test_result(
                test_name="ResponseModerationService.adjust_response_if_needed_inappropriate",
                input_params={"response": inappropriate_response},
                expected_result={"response_changed": True, "contains_safe_pattern": True},
                actual_result={"response_changed": adjusted != inappropriate_response, "adjusted_response": adjusted},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.adjust_response_if_needed_inappropriate",
                input_params={"response": inappropriate_response},
                expected_result={"response_changed": True, "contains_safe_pattern": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_detect_sensitive_content_analysis(self):
        mixed_response = "I had a wonderful family dinner, but then there was violence and drugs involved."

        try:
            analysis = self.moderation_service.detect_sensitive_content(mixed_response)

            self.assertTrue(analysis['has_high_severity'])
            self.assertGreater(analysis['total_issues'], 0)
            self.assertIn('violence', [issue['category'] for issue in analysis['issues']])
            self.assertIn('illegal_activity', [issue['category'] for issue in analysis['issues']])

            test_logger.log_test_result(
                test_name="ResponseModerationService.detect_sensitive_content_analysis",
                input_params={"response": mixed_response},
                expected_result={"has_high_severity": True, "total_issues": ">0", "contains_violence": True, "contains_illegal": True},
                actual_result={"has_high_severity": analysis['has_high_severity'], "total_issues": analysis['total_issues'], "categories": [issue['category'] for issue in analysis['issues']]},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.detect_sensitive_content_analysis",
                input_params={"response": mixed_response},
                expected_result={"has_high_severity": True, "total_issues": ">0", "contains_violence": True, "contains_illegal": True},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_emotional_intensity_detection(self):
        high_emotion_response = "I was so depressed, hopeless, worthless, and full of despair that I couldn't go on."

        try:
            result = self.moderation_service.review_response(high_emotion_response)

            self.assertFalse(result['is_safe'])
            emotional_issues = [issue for issue in result['issues_found'] if issue['category'] == 'emotional_distress']
            self.assertTrue(len(emotional_issues) > 0)

            test_logger.log_test_result(
                test_name="ResponseModerationService.emotional_intensity_detection",
                input_params={"response": high_emotion_response},
                expected_result={"is_safe": False, "emotional_issues_count": ">0"},
                actual_result={"is_safe": result['is_safe'], "emotional_issues_count": len(emotional_issues)},
                status="PASS"
            )
        except Exception as e:
            test_logger.log_test_result(
                test_name="ResponseModerationService.emotional_intensity_detection",
                input_params={"response": high_emotion_response},
                expected_result={"is_safe": False, "emotional_issues_count": ">0"},
                actual_result=f"Exception: {str(e)}",
                status="FAIL"
            )
            raise

    def test_harmful_pattern_detection(self):
        harmful_response = "Let me tell you how to make illegal drugs at home."
        result = self.moderation_service.review_response(harmful_response)

        # Should detect pattern issues
        pattern_issues = [issue for issue in result['issues_found'] if issue['type'] == 'pattern_match']
        self.assertTrue(len(pattern_issues) > 0)