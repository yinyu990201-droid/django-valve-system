import os
import tempfile
import unittest
from io import BytesIO


os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["UPLOAD_DIR"] = tempfile.mkdtemp(prefix="valve-test-uploads-")
os.environ["SECRET_KEY"] = "test-secret"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "Admin@123"
os.environ["DEMO_USERNAME"] = "viewer"
os.environ["DEMO_PASSWORD"] = "Viewer@123"
os.environ["SHOW_DEMO_CREDENTIALS"] = "false"

from app import create_app, db
from app.models import Customer, Document


class ValveAppTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def setUp(self):
        with self.app.app_context():
            Document.query.delete()
            Customer.query.delete()
            db.session.commit()
        self.client.get("/logout")

    def login(self, username="admin", password="Admin@123"):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )

    def test_health_and_auth_redirects(self):
        self.assertEqual(self.client.get("/healthz").status_code, 200)
        self.assertEqual(self.client.get("/catalog").status_code, 302)

        response = self.login()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/catalog"))

    def test_catalog_filter_detail_and_quick_select_pages(self):
        self.login()
        response = self.client.get("/catalog?function=压力控制&pressure=350")
        self.assertEqual(response.status_code, 200)
        self.assertIn("RPEP-25".encode("utf-8"), response.data)
        self.assertIn("RDDA-80".encode("utf-8"), response.data)
        self.assertIn("应用筛选".encode("utf-8"), response.data)

        detail = self.client.get("/catalog/RPEP-25")
        self.assertEqual(detail.status_code, 200)
        self.assertIn("SUN RPEI".encode("utf-8"), detail.data)

        quick = self.client.get("/quick-select?ports=3&flow=60-120")
        self.assertEqual(quick.status_code, 200)
        self.assertIn("候选型号".encode("utf-8"), quick.data)

    def test_catalog_pagination_preserves_filters(self):
        self.login()
        first_page = self.client.get("/catalog")
        self.assertEqual(first_page.status_code, 200)
        self.assertIn("第 1 / 2 页".encode("utf-8"), first_page.data)
        self.assertIn("page=2".encode("utf-8"), first_page.data)

        second_page = self.client.get("/catalog?page=2&sort=model")
        self.assertEqual(second_page.status_code, 200)
        self.assertIn("第 2 / 2 页".encode("utf-8"), second_page.data)
        self.assertIn("sort=model".encode("utf-8"), second_page.data)

    def test_cross_reference_and_contact_prefill(self):
        self.login()
        replacement = self.client.get("/sun-replacement?q=RPEI")
        self.assertEqual(replacement.status_code, 200)
        self.assertIn("RPEP-25".encode("utf-8"), replacement.data)

        contact = self.client.get("/contact?model=RPEP-25")
        self.assertEqual(contact.status_code, 200)
        self.assertIn("RPEP-25".encode("utf-8"), contact.data)
        self.assertIn("RPEI".encode("utf-8"), contact.data)

    def test_model_detail_pdf_upload_and_download_work_for_admin(self):
        self.login()
        response = self.client.post(
            "/catalog/RPEP-25/documents/upload",
            data={
                "title": "测试 PDF 资料",
                "description": "功能测试上传",
                "pdf_file": (BytesIO(b"%PDF-1.4\n%test\n"), "sample.pdf"),
            },
            content_type="multipart/form-data",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith("/catalog/RPEP-25"))

        with self.app.app_context():
            doc = Document.query.filter_by(title="测试 PDF 资料").first()
            self.assertIsNotNone(doc)
            self.assertEqual(doc.model_code, "RPEP-25")
            self.assertTrue(os.path.exists(doc.full_path))
            doc_id = doc.id

        detail = self.client.get("/catalog/RPEP-25")
        self.assertIn("测试 PDF 资料".encode("utf-8"), detail.data)
        self.assertIn("下载最新PDF".encode("utf-8"), detail.data)

        download = self.client.get(f"/documents/{doc_id}/download")
        self.assertEqual(download.status_code, 200)
        download.close()

    def test_document_standalone_pages_redirect_to_catalog(self):
        self.login()
        self.assertEqual(self.client.get("/documents").status_code, 302)
        self.assertEqual(self.client.get("/documents/upload").status_code, 302)

    def test_viewer_cannot_open_admin_pages(self):
        self.login("viewer", "Viewer@123")
        self.assertEqual(self.client.get("/documents/upload").status_code, 403)
        self.assertEqual(self.client.get("/customers/new").status_code, 403)
        self.assertEqual(self.client.get("/catalog").status_code, 200)


if __name__ == "__main__":
    unittest.main()
