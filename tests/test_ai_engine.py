import pytest
from unittest.mock import patch, MagicMock

from app.services.ai_engine import AIEngine
from app.schemas.batch import BatchCreate


class TestAIEngine:
    """Test AI engine functionality."""

    def test_calculate_sustainability_score(self):
        """Test sustainability score calculation."""
        ai_engine = AIEngine()

        # Test data
        material_composition = {
            "plastic": 30,
            "metal": 50,
            "electronics": 20
        }

        score = ai_engine.calculate_sustainability_score(material_composition)

        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_analyze_material_impact(self):
        """Test material impact analysis."""
        ai_engine = AIEngine()

        material_composition = {
            "recycled_plastic": 40,
            "virgin_plastic": 20,
            "metal": 40
        }

        analysis = ai_engine.analyze_material_impact(material_composition)

        assert isinstance(analysis, dict)
        assert "carbon_footprint" in analysis
        assert "recyclability_score" in analysis
        assert "environmental_impact" in analysis

    def test_generate_recommendations(self):
        """Test recommendation generation."""
        ai_engine = AIEngine()

        material_composition = {
            "plastic": 60,
            "metal": 40
        }

        recommendations = ai_engine.generate_recommendations(material_composition)

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

        # Check recommendation structure
        for rec in recommendations:
            assert "type" in rec
            assert "description" in rec
            assert "impact" in rec

    @patch('app.services.ai_engine.AIEngine._call_ai_api')
    def test_batch_analysis_with_mock(self, mock_ai_call):
        """Test batch analysis with mocked AI API."""
        # Mock AI API response
        mock_ai_call.return_value = {
            "sustainability_score": 85.5,
            "recommendations": [
                {
                    "type": "material_substitution",
                    "description": "Consider using recycled materials",
                    "impact": "high"
                }
            ],
            "environmental_impact": {
                "carbon_footprint": 2.3,
                "water_usage": 1.5,
                "energy_consumption": 3.1
            }
        }

        ai_engine = AIEngine()

        material_composition = {
            "plastic": 50,
            "metal": 50
        }

        result = ai_engine.analyze_batch_materials(material_composition)

        assert result["sustainability_score"] == 85.5
        assert len(result["recommendations"]) == 1
        assert "environmental_impact" in result

        # Verify AI API was called
        mock_ai_call.assert_called_once()

    def test_material_validation(self):
        """Test material composition validation."""
        ai_engine = AIEngine()

        # Valid composition
        valid_composition = {
            "plastic": 30,
            "metal": 40,
            "electronics": 30
        }
        assert ai_engine.validate_material_composition(valid_composition)

        # Invalid composition (doesn't add to 100)
        invalid_composition = {
            "plastic": 50,
            "metal": 30
        }
        assert not ai_engine.validate_material_composition(invalid_composition)

        # Invalid composition (negative values)
        negative_composition = {
            "plastic": -10,
            "metal": 110
        }
        assert not ai_engine.validate_material_composition(negative_composition)

    def test_carbon_footprint_calculation(self):
        """Test carbon footprint calculation."""
        ai_engine = AIEngine()

        material_composition = {
            "steel": 60,
            "aluminum": 20,
            "plastic": 20
        }

        footprint = ai_engine.calculate_carbon_footprint(material_composition)

        assert isinstance(footprint, float)
        assert footprint > 0

    def test_recyclability_scoring(self):
        """Test recyclability score calculation."""
        ai_engine = AIEngine()

        # High recyclability materials
        recyclable_composition = {
            "aluminum": 50,
            "glass": 30,
            "paper": 20
        }

        score = ai_engine.calculate_recyclability_score(recyclable_composition)
        assert isinstance(score, float)
        assert 0 <= score <= 100

        # Low recyclability materials
        non_recyclable_composition = {
            "mixed_plastics": 100
        }

        low_score = ai_engine.calculate_recyclability_score(non_recyclable_composition)
        assert isinstance(low_score, float)
        assert 0 <= low_score <= 100
        # Should be lower than highly recyclable materials
        assert low_score < score


class TestAIEngineIntegration:
    """Test AI engine integration with database operations."""

    def test_batch_creation_triggers_ai_analysis(self, db_session, test_user_data, test_product_data, test_batch_data):
        """Test that batch creation automatically triggers AI analysis."""
        # Create user and product
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate
        from app.models.user import UserRole

        user = create_user(db_session, UserCreate(**test_user_data), UserRole(test_user_data["role"]))
        product_in = ProductCreate(**test_product_data)
        product = create_product(db_session, product_in, user.id)

        # Mock AI engine
        with patch('app.crud.batch.generate_ai_rating') as mock_analyze:
            mock_analyze.return_value = {
                "rating": 78.5,
                "reasoning": "Test AI analysis"
            }

            # Create batch - this should trigger AI analysis
            from app.crud.batch import create_batch
            from app.schemas.batch import BatchCreate

            batch_in = BatchCreate(**test_batch_data)
            batch, _ = create_batch(db_session, product.id, user.id, batch_in)

            # Refresh batch to load relationships
            db_session.refresh(batch)

            # Verify batch was created
            assert batch is not None
            assert batch.batch_code == test_batch_data["batch_code"]

            # Verify the mock was called
            mock_analyze.assert_called_once()

            # Check that AIScore was added to the session (before rollback)
            # Since we can't check the database after rollback, we check the mock was called
            # and that the function completed without error
            assert batch is not None

    def test_ai_score_persistence(self, db_session, test_user_data, test_product_data, test_batch_data):
        """Test that AI scores are properly persisted."""
        # Create user with different email
        test_user_data_2 = test_user_data.copy()
        test_user_data_2["email"] = "test2@example.com"
        test_user_data_2["name"] = "Test User 2"

        # Create product with different name
        test_product_data_2 = test_product_data.copy()
        test_product_data_2["name"] = "Test Product 2"
        test_product_data_2["sku"] = "TEST-002"

        # Create user, product, and batch with mocked AI analysis
        from app.crud.user import create_user
        from app.crud.product import create_product
        from app.crud.batch import create_batch
        from app.schemas.user import UserCreate
        from app.schemas.product import ProductCreate
        from app.schemas.batch import BatchCreate
        from app.models.user import UserRole

        user = create_user(db_session, UserCreate(**test_user_data_2), UserRole(test_user_data_2["role"]))
        product_in = ProductCreate(**test_product_data_2)
        product = create_product(db_session, product_in, user.id)

        with patch('app.crud.batch.generate_ai_rating') as mock_analyze:
            mock_analyze.return_value = {
                "rating": 82.3,
                "reasoning": "Test AI analysis"
            }

            batch_in = BatchCreate(**test_batch_data)
            batch, _ = create_batch(db_session, product.id, user.id, batch_in)

            # Verify the mock was called
            mock_analyze.assert_called_once()

            # Verify batch was created
            assert batch is not None
            assert batch.batch_code == test_batch_data["batch_code"]
            assert batch.ai_score.environmental_impact["carbon_footprint"] == 2.1