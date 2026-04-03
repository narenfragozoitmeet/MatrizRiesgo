import requests
import sys
import json
import os
from datetime import datetime
from io import BytesIO

class RiskMatrixAPITester:
    def __init__(self, base_url="https://risk-assessment-hub-12.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.document_id = None
        self.analysis_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None, response_type='json'):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}" if endpoint else self.api_url
        headers = {}
        
        if files is None and data is not None:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, timeout=120)
                else:
                    response = requests.post(url, json=data, headers=headers, timeout=120)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                
                if response_type == 'json' and response.content:
                    try:
                        return success, response.json()
                    except:
                        return success, {"raw_response": response.text}
                else:
                    return success, {"status": "success", "content_length": len(response.content)}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:500]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        success, response = self.run_test(
            "Root API Endpoint",
            "GET",
            "",
            200
        )
        return success

    def test_upload_document(self):
        """Test document upload with a sample PDF"""
        # Create a simple test PDF content (minimal PDF structure)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test legal document) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        files = {
            'file': ('test_document.pdf', BytesIO(pdf_content), 'application/pdf')
        }
        
        success, response = self.run_test(
            "Upload Document",
            "POST",
            "upload",
            200,
            files=files
        )
        
        if success and 'id' in response:
            self.document_id = response['id']
            print(f"   Document ID: {self.document_id}")
        
        return success

    def test_upload_invalid_file(self):
        """Test upload with invalid file type"""
        files = {
            'file': ('test.txt', BytesIO(b'This is a text file'), 'text/plain')
        }
        
        success, response = self.run_test(
            "Upload Invalid File Type",
            "POST",
            "upload",
            400,
            files=files
        )
        return success

    def test_analyze_document(self):
        """Test document analysis"""
        if not self.document_id:
            print("❌ Skipping analysis test - no document uploaded")
            return False
            
        success, response = self.run_test(
            "Analyze Document",
            "POST",
            f"analyze/{self.document_id}",
            200
        )
        
        if success and 'id' in response:
            self.analysis_id = response['id']
            print(f"   Analysis ID: {self.analysis_id}")
            print(f"   Total Risks: {response.get('total_risks', 'N/A')}")
        
        return success

    def test_get_analysis(self):
        """Test getting analysis results"""
        if not self.analysis_id:
            print("❌ Skipping get analysis test - no analysis available")
            return False
            
        success, response = self.run_test(
            "Get Analysis",
            "GET",
            f"analysis/{self.analysis_id}",
            200
        )
        
        if success:
            print(f"   Document: {response.get('document_name', 'N/A')}")
            print(f"   Status: {response.get('status', 'N/A')}")
            print(f"   Risks Count: {len(response.get('risks', []))}")
        
        return success

    def test_download_excel(self):
        """Test Excel file download"""
        if not self.analysis_id:
            print("❌ Skipping download test - no analysis available")
            return False
            
        success, response = self.run_test(
            "Download Excel",
            "GET",
            f"download/{self.analysis_id}",
            200,
            response_type='binary'
        )
        
        if success:
            print(f"   File size: {response.get('content_length', 0)} bytes")
        
        return success

    def test_list_analyses(self):
        """Test listing all analyses"""
        success, response = self.run_test(
            "List Analyses",
            "GET",
            "analyses",
            200
        )
        
        if success:
            analyses_count = len(response) if isinstance(response, list) else 0
            print(f"   Total analyses: {analyses_count}")
        
        return success

    def test_nonexistent_analysis(self):
        """Test getting non-existent analysis"""
        success, response = self.run_test(
            "Get Non-existent Analysis",
            "GET",
            "analysis/nonexistent-id",
            404
        )
        return success

    def test_nonexistent_download(self):
        """Test downloading non-existent analysis"""
        success, response = self.run_test(
            "Download Non-existent Analysis",
            "GET",
            "download/nonexistent-id",
            404
        )
        return success

def main():
    print("🚀 Starting Risk Matrix API Tests")
    print("=" * 50)
    
    tester = RiskMatrixAPITester()
    
    # Test sequence
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Upload Valid Document", tester.test_upload_document),
        ("Upload Invalid File", tester.test_upload_invalid_file),
        ("Analyze Document", tester.test_analyze_document),
        ("Get Analysis", tester.test_get_analysis),
        ("Download Excel", tester.test_download_excel),
        ("List Analyses", tester.test_list_analyses),
        ("Non-existent Analysis", tester.test_nonexistent_analysis),
        ("Non-existent Download", tester.test_nonexistent_download),
    ]
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    success_rate = (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())