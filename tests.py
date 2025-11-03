import pytest
from fastapi.testclient import TestClient
from main import app, Patient

client = TestClient(app)

@pytest.fixture
def sample_patient():
    """Sample patient data for testing"""
    return {
        "id": "P999",
        "name": "Test Patient",
        "city": "Test City",
        "age": 25,
        "gender": "male",
        "height": 1.75,
        "weight": 70
    }

@pytest.fixture(autouse=True)
def cleanup_test_patient():
    """Cleanup fixture to remove test patient after test"""
    yield
    data = client.get('/view').json()
    if 'P999' in data:
        client.delete('/delete/P999')

class TestPatientModel:
    def test_bmi_calculation(self, sample_patient):
        """Test if BMI is calculated correctly"""      
        patient = Patient(**sample_patient)
        expected_bmi = round(70 / (1.75 ** 2), 2)
        assert patient.bmi == expected_bmi

    def test_bmi_validation(self, sample_patient):
        """Test if BMI validation works correctly"""
        patient = Patient(**sample_patient)
        assert patient.verdict == 'Normal'

class TestEndpoints:
    """Test API endpoints"""

    def test_view_patients(self):
        """Test GET /view endpoint returns all patients"""
        response = client.get('/view')
        assert response.status_code == 200

    def test_get_patient_by_id(self):
        """Test GET /patient/{patient_id} with valid ID"""
        response = client.get('/patient/P001')
        assert response.status_code == 200

    def test_patient_not_found(self):
        """Test GET /patient/{patient_id} with invalid ID returns 404"""
        response = client.get('/patient/P999999')
        assert response.status_code == 404

    def test_create_patient_success(self, sample_patient):
        """Test POST /create with valid patient data"""
        response = client.post('/create', json = sample_patient)
        assert response.status_code == 201

    def test_create_patient_failure(self, sample_patient):
        """Test POST /create with duplicate patient ID returns 400"""
        client.post('/create', json = sample_patient)
        response = client.post('/create', json = sample_patient)
        assert response.status_code == 400

    def test_update_patient_success(self, sample_patient):
        """Test PUT /edit/{patient_id} with valid data"""
        client.post('/create', json = sample_patient)

        updated_data = {
            "name" : "Nahian",
            "city" : "Dhaka",
            "height": 1.65,
            "weight": 67
        }

        response  = client.put(f'/edit/{sample_patient["id"]}', json = updated_data)
        assert response.status_code == 200

    def test_update_patient_failure(self):
        """Test PUT /edit/{patient_id} with invalid data"""
        updated_data = {
            "name" : "Nahian",
            "city" : "Dhaka",
            "height": 1.65,
            "weight": 67
        }

        response  = client.put('/edit/P1000', json = updated_data)
        assert response.status_code == 404

