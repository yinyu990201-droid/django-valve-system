import os
import uuid
from functools import wraps
from math import ceil
from urllib.parse import urlencode

from flask import (
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from . import db
from .catalog import (
    FLOW_BUCKET_LABELS,
    PRESSURE_BUCKET_LABELS,
    all_catalog_items,
    facet_values,
    filter_catalog,
    get_catalog_item,
    selected_label,
)
from .models import Customer, Document, User


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)

    return wrapped


def _validate_pdf_upload(file):
    if not file or not file.filename:
        flash("请上传 PDF 文件", "danger")
        return None
    if not file.filename.lower().endswith(".pdf"):
        flash("仅支持 PDF 文件", "danger")
        return None
    return secure_filename(file.filename)


def _create_document_from_request(model_code: str | None = None, product_model_id: int | None = None):
    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    file = request.files.get("pdf_file")
    original_name = _validate_pdf_upload(file)
    if not original_name:
        return None

    if not title:
        title = os.path.splitext(original_name)[0] or "PDF 资料"

    stored_filename = f"{uuid.uuid4()}.pdf"
    target_path = os.path.join(current_app.config["UPLOAD_DIR"], stored_filename)
    file.save(target_path)

    doc = Document(
        product_model_id=product_model_id,
        model_code=model_code,
        title=title,
        original_filename=original_name,
        stored_filename=stored_filename,
        description=description,
        uploaded_by=current_user.id,
    )
    db.session.add(doc)
    db.session.commit()
    return doc


def register_routes(app):
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("catalog_index"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                next_url = request.args.get("next")
                return redirect(next_url or url_for("catalog_index"))
            flash("用户名或密码错误", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        doc_count = Document.query.count()
        customer_count = Customer.query.count()
        model_count = len(all_catalog_items())
        return render_template(
            "dashboard.html",
            doc_count=doc_count,
            customer_count=customer_count,
            model_count=model_count,
        )

    @app.route("/catalog")
    @login_required
    def catalog_index():
        items, selected, query = filter_catalog(request.args)
        facets = facet_values()
        per_page = 6
        try:
            page = max(int(request.args.get("page", "1")), 1)
        except ValueError:
            page = 1
        total_filtered = len(items)
        total_pages = max(ceil(total_filtered / per_page), 1)
        page = min(page, total_pages)
        start = (page - 1) * per_page
        page_items = items[start : start + per_page]

        def page_url(target_page: int) -> str:
            args = request.args.to_dict(flat=False)
            args["page"] = [str(target_page)]
            return f"{url_for('catalog_index')}?{urlencode(args, doseq=True)}"

        return render_template(
            "catalog.html",
            items=items,
            page_items=page_items,
            facets=facets,
            selected=selected,
            selected_label=selected_label,
            query=query,
            flow_labels=FLOW_BUCKET_LABELS,
            pressure_labels=PRESSURE_BUCKET_LABELS,
            total_count=len(all_catalog_items()),
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_filtered=total_filtered,
            page_url=page_url,
        )

    @app.route("/catalog/<model_code>")
    @login_required
    def catalog_detail(model_code: str):
        item = get_catalog_item(model_code)
        if not item:
            abort(404)
        docs = Document.query.filter_by(model_code=item.code).order_by(Document.created_at.desc()).all()
        related = [
            candidate
            for candidate in all_catalog_items()
            if candidate.code != item.code
            and (candidate.category == item.category or candidate.function == item.function)
        ][:4]
        return render_template("catalog_detail.html", item=item, related=related, docs=docs)

    @app.route("/catalog/<model_code>/documents/upload", methods=["POST"])
    @login_required
    @admin_required
    def catalog_document_upload(model_code: str):
        item = get_catalog_item(model_code)
        if not item:
            abort(404)
        doc = _create_document_from_request(model_code=item.code, product_model_id=item.id)
        if doc:
            flash("型号资料上传成功", "success")
        return redirect(url_for("catalog_detail", model_code=item.code))

    @app.route("/quick-select")
    @login_required
    def quick_select():
        items, selected, query = filter_catalog(request.args)
        return render_template(
            "quick_select.html",
            items=items,
            selected=selected,
            selected_label=selected_label,
            query=query,
            flow_labels=FLOW_BUCKET_LABELS,
            pressure_labels=PRESSURE_BUCKET_LABELS,
            categories=facet_values()["category"],
            functions=facet_values()["function"],
            total_count=len(all_catalog_items()),
        )

    @app.route("/sun-replacement")
    @login_required
    def sun_replacement():
        items, selected, query = filter_catalog(request.args)
        return render_template(
            "sun_replacement.html",
            items=items,
            selected=selected,
            query=query,
            total_count=len(all_catalog_items()),
        )

    @app.route("/contact")
    @login_required
    def contact_quote():
        model_code = request.args.get("model", "").strip().upper()
        item = get_catalog_item(model_code) if model_code else None
        return render_template("contact.html", item=item)

    @app.route("/documents")
    @login_required
    def document_list():
        flash("PDF 资料已整合到各型号明细页，请先选择插装阀型号。", "warning")
        return redirect(url_for("catalog_index"))

    @app.route("/documents/upload", methods=["GET", "POST"])
    @login_required
    @admin_required
    def document_upload():
        if request.method == "POST":
            model_code = request.form.get("model_code", "").strip().upper()
            item = get_catalog_item(model_code) if model_code else None
            doc = _create_document_from_request(
                model_code=item.code if item else None,
                product_model_id=item.id if item else None,
            )
            if doc:
                flash("资料上传成功", "success")
                if item:
                    return redirect(url_for("catalog_detail", model_code=item.code))
            return redirect(url_for("catalog_index"))

        flash("请进入具体型号明细页上传 PDF 资料。", "warning")
        return redirect(url_for("catalog_index"))

    @app.route("/documents/<int:doc_id>/preview")
    @login_required
    def document_preview(doc_id: int):
        doc = Document.query.get_or_404(doc_id)
        return render_template("preview.html", doc=doc)

    @app.route("/documents/<int:doc_id>/file")
    @login_required
    def document_file(doc_id: int):
        doc = Document.query.get_or_404(doc_id)
        if not os.path.exists(doc.full_path):
            abort(404)
        return send_file(doc.full_path, mimetype="application/pdf", as_attachment=False)

    @app.route("/documents/<int:doc_id>/download")
    @login_required
    def document_download(doc_id: int):
        doc = Document.query.get_or_404(doc_id)
        if not os.path.exists(doc.full_path):
            abort(404)
        return send_file(doc.full_path, as_attachment=True, download_name=doc.original_filename)

    @app.route("/documents/<int:doc_id>/delete", methods=["POST"])
    @login_required
    @admin_required
    def document_delete(doc_id: int):
        doc = Document.query.get_or_404(doc_id)
        model_code = doc.model_code
        if os.path.exists(doc.full_path):
            os.remove(doc.full_path)
        db.session.delete(doc)
        db.session.commit()
        flash("资料已删除", "success")
        if model_code:
            return redirect(url_for("catalog_detail", model_code=model_code))
        return redirect(url_for("catalog_index"))

    @app.route("/customers")
    @login_required
    def customer_list():
        customers = Customer.query.order_by(Customer.created_at.desc()).all()
        return render_template("customers.html", customers=customers)

    @app.route("/customers/new", methods=["GET", "POST"])
    @login_required
    @admin_required
    def customer_new():
        if request.method == "POST":
            customer = Customer(
                name=request.form.get("name", "").strip(),
                contact_person=request.form.get("contact_person", "").strip(),
                phone=request.form.get("phone", "").strip(),
                email=request.form.get("email", "").strip(),
                notes=request.form.get("notes", "").strip(),
            )
            if not customer.name:
                flash("客户名称不能为空", "danger")
                return render_template("customer_form.html", customer=None)
            db.session.add(customer)
            db.session.commit()
            flash("客户创建成功", "success")
            return redirect(url_for("customer_list"))
        return render_template("customer_form.html", customer=None)

    @app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
    @login_required
    @admin_required
    def customer_edit(customer_id: int):
        customer = Customer.query.get_or_404(customer_id)
        if request.method == "POST":
            customer.name = request.form.get("name", "").strip()
            customer.contact_person = request.form.get("contact_person", "").strip()
            customer.phone = request.form.get("phone", "").strip()
            customer.email = request.form.get("email", "").strip()
            customer.notes = request.form.get("notes", "").strip()
            if not customer.name:
                flash("客户名称不能为空", "danger")
                return render_template("customer_form.html", customer=customer)
            db.session.commit()
            flash("客户信息更新成功", "success")
            return redirect(url_for("customer_list"))
        return render_template("customer_form.html", customer=customer)

    @app.route("/customers/<int:customer_id>/delete", methods=["POST"])
    @login_required
    @admin_required
    def customer_delete(customer_id: int):
        customer = Customer.query.get_or_404(customer_id)
        db.session.delete(customer)
        db.session.commit()
        flash("客户已删除", "success")
        return redirect(url_for("customer_list"))

    @app.errorhandler(403)
    def forbidden(_):
        return render_template("error.html", code=403, message="您没有权限执行该操作"), 403

    @app.errorhandler(404)
    def not_found(_):
        return render_template("error.html", code=404, message="资源不存在"), 404
