import io

from flask import Flask, redirect, render_template, request, send_file, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root123@localhost/service_booking"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["GOOGLE_MAPS_API_KEY"] = "AIzaSyBsUNoGj9kdjfybBeJeLiJFW1cVLQM38vw"

db = SQLAlchemy(app)

SERVICE_CATEGORIES = [
    "Electrical Repairs",
    "Plumbing Solutions",
    "AC & Appliance Repairs",
    "Deep Cleaning",
    "Carpentry Services",
    "Painting & Renovation",
    "Home Security",
    "Gardening & Outdoor",
    "Interior & Furniture",
]

PAGE_CATEGORY_MAP = {
    "electrician": "Electrical Repairs",
    "plumbing": "Plumbing Solutions",
    "ac": "AC & Appliance Repairs",
    "deepclean": "Deep Cleaning",
    "carpentry": "Carpentry Services",
    "painting": "Painting & Renovation",
    "homesecurity": "Home Security",
    "gardening": "Gardening & Outdoor",
    "interior": "Interior & Furniture",
}

SERVICE_KEYWORDS = {
    "Electrical Repairs": ["electrical", "fan", "light", "wiring", "bulb", "switch", "tubelight"],
    "Plumbing Solutions": ["plumbing", "tap", "toilet", "sink", "water tank", "motor", "drain"],
    "AC & Appliance Repairs": ["ac", "air conditioner", "washing machine", "tv", "appliance"],
    "Deep Cleaning": ["clean", "cleaning", "kitchen", "sofa", "carpet", "home"],
    "Carpentry Services": ["carpentry", "cupboard", "drawer", "shelf", "curtain", "chair", "bed"],
    "Painting & Renovation": ["paint", "painting", "wall", "wallpaper", "panel"],
    "Home Security": ["security", "cctv", "camera", "lock", "biometric", "surveillance"],
    "Gardening & Outdoor": ["garden", "plant", "lawn", "grass", "soil"],
    "Interior & Furniture": ["interior", "furniture", "wardrobe", "tv unit", "wallpaper"],
}

MAX_ACTIVE_JOBS_PER_PROFESSIONAL = 2


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)


class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150))
    message = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())


class SavedLocation(db.Model):
    __tablename__ = "saved_locations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Numeric(10, 7), nullable=False)
    longitude = db.Column(db.Numeric(10, 7), nullable=False)
    place_id = db.Column(db.String(255))
    source = db.Column(db.String(30), nullable=False, default="manual")
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    service_summary = db.Column(db.String(255), nullable=False)
    service_category = db.Column(db.String(80))
    total_price = db.Column(db.Integer, nullable=False)
    slot = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    assigned_professional_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    professional_amount = db.Column(db.Integer, nullable=False, default=0)
    admin_commission = db.Column(db.Integer, nullable=False, default=0)
    work_status = db.Column(db.String(30), nullable=False, default="pending")
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())


class ProfessionalProfile(db.Model):
    __tablename__ = "professional_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(80), nullable=False)
    years_experience = db.Column(db.Integer, nullable=False, default=0)
    service_categories = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    aadhaar_number = db.Column(db.String(20), nullable=False)
    pan_number = db.Column(db.String(20), nullable=False)
    gst_number = db.Column(db.String(20))
    bank_account_holder = db.Column(db.String(120), nullable=False)
    bank_account_number = db.Column(db.String(40), nullable=False)
    ifsc_code = db.Column(db.String(20), nullable=False)
    verification_status = db.Column(db.String(20), nullable=False, default="pending")
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    rejection_reason = db.Column(db.Text)
    created_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())
    updated_at = db.Column(
        db.TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
    )


class ProfessionalDocument(db.Model):
    __tablename__ = "professional_documents"

    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey("professional_profiles.id"), nullable=False)
    document_type = db.Column(db.String(40), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.TIMESTAMP, server_default=func.current_timestamp())


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def require_role(role_name):
    user = get_current_user()
    if not user:
        return None, redirect(url_for("auth"))
    if user.role != role_name:
        return user, redirect(url_for("index"))
    return user, None


def get_profile(user_id):
    return ProfessionalProfile.query.filter_by(user_id=user_id).first()


def get_document_map(profile_id):
    documents = ProfessionalDocument.query.filter_by(professional_id=profile_id).all()
    result = {}
    for item in documents:
        result[item.document_type] = item
    return result


def format_status_label(value):
    return (value or "pending").replace("_", " ").title()


def format_customer_booking_status(value):
    labels = {
        "pending": "Placed",
        "assigned": "Professional Assigned",
        "in_progress": "Service In Progress",
        "completed": "Completed",
    }
    value = (value or "").strip().lower()
    if value in labels:
        return labels[value]
    return format_status_label(value or "placed")


def infer_service_category(items):
    page_names = []
    for item in items:
        page_name = (item.get("pageCategory") or item.get("page_category") or "").strip().lower()
        if page_name in PAGE_CATEGORY_MAP:
            page_names.append(PAGE_CATEGORY_MAP[page_name])

    if page_names:
        counts = {}
        for name in page_names:
            counts[name] = counts.get(name, 0) + 1
        return max(counts, key=counts.get)

    scores = {}
    for category in SERVICE_CATEGORIES:
        scores[category] = 0

    for item in items:
        name = (item.get("name") or "").lower()
        for category, words in SERVICE_KEYWORDS.items():
            for word in words:
                if word in name:
                    scores[category] += 1

    if max(scores.values()) == 0:
        return None
    return max(scores, key=scores.get)


def get_cart_service_categories(items):
    categories = []

    for item in items:
        page_name = (item.get("pageCategory") or item.get("page_category") or "").strip().lower()
        category = PAGE_CATEGORY_MAP.get(page_name)
        if category and category not in categories:
            categories.append(category)

    if categories:
        return categories

    for item in items:
        category = infer_service_category([item])
        if category and category not in categories:
            categories.append(category)

    return categories


def update_booking_amounts(booking):
    booking.admin_commission = int((booking.total_price or 0) * 0.20)
    booking.professional_amount = (booking.total_price or 0) - booking.admin_commission


def get_profile_categories(profile):
    categories = []
    if not profile or not profile.service_categories:
        return categories

    for item in profile.service_categories.split(","):
        value = item.strip()
        if value:
            categories.append(value)
    return categories


def professional_offers_service(profile, service_category):
    categories = get_profile_categories(profile)
    return service_category in categories


def get_professional_work_count(user_id, exclude_booking_id=None):
    active_statuses = ["assigned", "in_progress"]
    query = Booking.query.filter(
        Booking.assigned_professional_id == user_id,
        Booking.work_status.in_(active_statuses),
    )
    if exclude_booking_id:
        query = query.filter(Booking.id != exclude_booking_id)
    return query.count()


def get_last_assigned_time(user_id):
    booking = Booking.query.filter_by(assigned_professional_id=user_id).order_by(
        Booking.created_at.desc(),
        Booking.id.desc(),
    ).first()

    if booking:
        return booking.created_at
    return None


def auto_assign_professional(service_category):
    approved_profiles = ProfessionalProfile.query.filter_by(
        verification_status="approved",
        is_active=True,
    ).all()

    matching_profiles = []

    for profile in approved_profiles:
        active_jobs = get_professional_work_count(profile.user_id)
        if (
            professional_offers_service(profile, service_category)
            and active_jobs < MAX_ACTIVE_JOBS_PER_PROFESSIONAL
        ):
            matching_profiles.append(profile)

    if not matching_profiles:
        return None

    matching_profiles.sort(
        key=lambda profile: (
            get_professional_work_count(profile.user_id),
            get_last_assigned_time(profile.user_id) is not None,
            get_last_assigned_time(profile.user_id) or "",
            profile.user_id,
        )
    )

    return matching_profiles[0]


def make_message_url(endpoint, message="", message_type="success", anchor=""):
    if message:
        base_url = url_for(endpoint, message=message, message_type=message_type)
    else:
        base_url = url_for(endpoint)
    if anchor:
        base_url = f"{base_url}#{anchor}"
    return base_url


@app.route("/")
def index():
    return render_template(
        "index.html",
        current_user=get_current_user(),
        google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"],
    )


@app.route("/privacy")
def privacy():
    return render_template("privacy.html", current_user=get_current_user())


@app.route("/terms")
def terms():
    return render_template("terms.html", current_user=get_current_user())


@app.route("/about")
def about():
    return render_template("about.html", current_user=get_current_user())


@app.route("/reviews")
def reviews():
    return render_template("reviews.html", current_user=get_current_user())


@app.route("/categories")
def categories():
    return render_template("categories.html", current_user=get_current_user())


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        entry = Contact(
            name=request.form.get("name", "").strip(),
            email=request.form.get("email", "").strip(),
            message=request.form.get("message", "").strip(),
        )
        db.session.add(entry)
        db.session.commit()
        return redirect(
            make_message_url(
                "contact",
                "Your message has been received. Our support team will get in touch shortly.",
                "success",
            )
        )

    return render_template("contact.html", current_user=get_current_user())


@app.route("/my-orders")
def my_orders():
    if not session.get("user_id"):
        return redirect(url_for("index"))

    bookings = Booking.query.filter_by(user_id=session["user_id"]).order_by(
        Booking.created_at.desc(),
        Booking.id.desc(),
    ).all()

    return render_template(
        "my_orders.html",
        current_user=get_current_user(),
        bookings=bookings,
        format_status_label=format_status_label,
        format_customer_booking_status=format_customer_booking_status,
    )


@app.route("/electrician")
def electrician():
    return render_template("electrician.html", current_user=get_current_user())


@app.route("/plumbing")
def plumbing():
    return render_template("plumbing.html", current_user=get_current_user())


@app.route("/ac")
def ac():
    return render_template("ac.html", current_user=get_current_user())


@app.route("/deepclean")
def deepclean():
    return render_template("deepclean.html", current_user=get_current_user())


@app.route("/carpentry")
def carpentry():
    return render_template("carpentry.html", current_user=get_current_user())


@app.route("/painting")
def painting():
    return render_template("painting.html", current_user=get_current_user())


@app.route("/homesecurity")
def homesecurity():
    return render_template("homesecurity.html", current_user=get_current_user())


@app.route("/gardening")
def gardening():
    return render_template("gardening.html", current_user=get_current_user())


@app.route("/interior")
def interior():
    return render_template("interior.html", current_user=get_current_user())


@app.route("/cart")
def cart():
    return render_template(
        "cart.html",
        current_user=get_current_user(),
        google_maps_api_key=app.config["GOOGLE_MAPS_API_KEY"],
        cart_static_version="20260329",
    )


@app.route("/register", methods=["POST"])
def register():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    role = request.form.get("role", "user").strip().lower()
    next_page = request.form.get("next", "").strip()
    error_message = "An account with this email already exists."

    if not name or not email or not password:
        return redirect(url_for("index"))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        if next_page == url_for("cart"):
            return redirect(url_for("cart", register_error=error_message, auth="register"))
        if next_page == url_for("auth"):
            return redirect(url_for("auth", register_error=error_message, mode="register"))
        return redirect(url_for("index", register_error=error_message, auth="register"))

    new_user = User(
        name=name,
        email=email,
        password=generate_password_hash(password),
        role=role,
    )
    db.session.add(new_user)
    db.session.commit()

    session["user_id"] = new_user.id

    if role == "provider":
        return redirect(url_for("professional"))
    if role == "admin":
        return redirect(url_for("admin_dashboard"))
    if next_page:
        return redirect(next_page)
    return redirect(url_for("index"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    next_page = request.form.get("next", "").strip()

    error_message = "Invalid email or password."

    user = User.query.filter_by(email=email).first()
    if not user:
        if next_page == url_for("cart"):
            return redirect(url_for("cart", login_error=error_message, auth="login"))
        if next_page == url_for("auth"):
            return redirect(url_for("auth", login_error=error_message, mode="login"))
        return redirect(url_for("index", login_error=error_message, auth="login"))

    if not check_password_hash(user.password, password):
        if next_page == url_for("cart"):
            return redirect(url_for("cart", login_error=error_message, auth="login"))
        if next_page == url_for("auth"):
            return redirect(url_for("auth", login_error=error_message, mode="login"))
        return redirect(url_for("index", login_error=error_message, auth="login"))

    session["user_id"] = user.id

    if user.role == "admin":
        return redirect(url_for("admin_dashboard"))
    if user.role == "provider":
        return redirect(url_for("professional"))
    if next_page:
        return redirect(next_page)
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index", logged_out="1"))


@app.route("/auth")
def auth():
    next_page = request.args.get("next", "").strip() or url_for("auth")
    return render_template(
        "auth.html",
        current_user=get_current_user(),
        auth_next=next_page,
    )


@app.route("/professional")
def professional():
    user, redirect_response = require_role("provider")
    if redirect_response:
        return redirect_response

    profile = get_profile(user.id)
    documents = {}
    assigned_orders = []
    stats = {
        "active_orders": 0,
        "completed_orders": 0,
        "total_payout_value": 0,
        "available_payout": 0,
        "admin_commission": 0,
    }

    if profile:
        documents = get_document_map(profile.id)
        assigned_orders = Booking.query.filter_by(
            assigned_professional_id=user.id
        ).order_by(Booking.created_at.desc(), Booking.id.desc()).all()

        for order in assigned_orders:
            stats["total_payout_value"] += order.professional_amount or 0
            stats["admin_commission"] += order.admin_commission or 0
            if order.work_status == "completed":
                stats["completed_orders"] += 1
                stats["available_payout"] += order.professional_amount or 0
            if order.work_status in ["assigned", "in_progress"]:
                stats["active_orders"] += 1

    return render_template(
        "professional.html",
        current_user=get_current_user(),
        service_categories=SERVICE_CATEGORIES,
        format_status_label=format_status_label,
        profile_edit_mode=request.args.get("edit_profile") == "1",
        profile=profile,
        documents=documents,
        assigned_orders=assigned_orders,
        stats=stats,
    )


@app.route("/professional/complete-profile", methods=["POST"])
def complete_professional_profile():
    user, redirect_response = require_role("provider")
    if redirect_response:
        return redirect_response

    selected_categories = request.form.getlist("service_categories")
    if not selected_categories:
        return redirect(
            make_message_url(
                "professional",
                "Please choose at least one service category.",
                "error",
                "orders-section",
            )
        )

    profile = get_profile(user.id)
    if not profile:
        profile = ProfessionalProfile(user_id=user.id)
        db.session.add(profile)

    profile.phone = request.form.get("phone", "").strip()
    profile.city = request.form.get("city", "").strip()
    profile.years_experience = int(request.form.get("years_experience") or 0)
    profile.service_categories = ", ".join(selected_categories)
    profile.about = request.form.get("about", "").strip()
    profile.aadhaar_number = request.form.get("aadhaar_number", "").strip()
    profile.pan_number = request.form.get("pan_number", "").strip().upper()
    profile.gst_number = request.form.get("gst_number", "").strip().upper() or None
    profile.bank_account_holder = request.form.get("bank_account_holder", "").strip()
    profile.bank_account_number = request.form.get("bank_account_number", "").strip()
    profile.ifsc_code = request.form.get("ifsc_code", "").strip().upper()
    profile.verification_status = "pending"
    profile.is_active = False
    profile.rejection_reason = None

    required_values = [
        profile.phone,
        profile.city,
        profile.about,
        profile.aadhaar_number,
        profile.pan_number,
        profile.bank_account_holder,
        profile.bank_account_number,
        profile.ifsc_code,
    ]
    if not all(required_values):
        return redirect(
            make_message_url(
                "professional",
                "Please complete all required professional details.",
                "error",
                "orders-section",
            )
        )

    db.session.flush()

    required_documents = ["aadhaar_image", "pan_image"]
    if profile.gst_number:
        required_documents.append("gst_image")

    existing_documents = get_document_map(profile.id)
    for document_name in required_documents:
        if document_name not in existing_documents and document_name not in request.files:
            return redirect(
                make_message_url(
                "professional",
                "Please upload all required verification documents.",
                "error",
                "orders-section",
            )
            )

    for document_name in ["aadhaar_image", "pan_image", "gst_image"]:
        file = request.files.get(document_name)
        if not file or not file.filename:
            continue

        safe_name = secure_filename(file.filename) or f"{document_name}.bin"
        file_bytes = file.read()
        file_type = file.mimetype or "application/octet-stream"

        old_file = ProfessionalDocument.query.filter_by(
            professional_id=profile.id,
            document_type=document_name,
        ).first()

        if old_file:
            old_file.filename = safe_name
            old_file.data = file_bytes
            old_file.mimetype = file_type
        else:
            db.session.add(
                ProfessionalDocument(
                    professional_id=profile.id,
                    document_type=document_name,
                    filename=safe_name,
                    data=file_bytes,
                    mimetype=file_type,
                )
            )

    db.session.commit()
    return redirect(
        make_message_url(
            "professional",
            "Verification details submitted. Admin approval is required before orders start coming to your dashboard.",
            "success",
            "orders-section",
        )
    )


@app.route("/professional/order/<int:booking_id>/status", methods=["POST"])
def update_professional_order_status(booking_id):
    user, redirect_response = require_role("provider")
    if redirect_response:
        return redirect_response

    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(url_for("professional"))
    if booking.assigned_professional_id != user.id:
        return redirect(url_for("professional"))

    profile = get_profile(user.id)
    if not profile or profile.verification_status != "approved":
        return redirect(
            make_message_url(
                "professional",
                "Your profile must be approved before you can manage orders.",
                "error",
                "orders-section",
            )
        )

    next_status = request.form.get("work_status", "").strip()
    allowed_statuses = ["assigned", "in_progress", "completed"]
    if next_status not in allowed_statuses:
        return redirect(
            make_message_url(
                "professional",
                "Invalid order status selected.",
                "error",
                "orders-section",
            )
        )

    booking.work_status = next_status
    booking.status = format_status_label(next_status)
    db.session.commit()

    return redirect(url_for("professional") + "#orders-section")


@app.route("/document/<int:document_id>")
def view_document(document_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth"))

    document = ProfessionalDocument.query.get(document_id)
    if not document:
        return redirect(url_for("index"))
    profile = ProfessionalProfile.query.get(document.professional_id)
    if not profile:
        return redirect(url_for("index"))

    if user.role != "admin" and user.id != profile.user_id:
        return redirect(url_for("index"))

    return send_file(
        io.BytesIO(document.data),
        mimetype=document.mimetype,
        as_attachment=False,
        download_name=document.filename,
    )


@app.route("/admin")
def admin_dashboard():
    user, redirect_response = require_role("admin")
    if redirect_response:
        return redirect_response

    profiles = ProfessionalProfile.query.order_by(
        ProfessionalProfile.created_at.desc(),
        ProfessionalProfile.id.desc(),
    ).all()
    bookings = Booking.query.order_by(Booking.created_at.desc(), Booking.id.desc()).all()
    provider_users = User.query.filter_by(role="provider").order_by(User.name.asc()).all()

    profile_cards = []
    for profile in profiles:
        profile_cards.append(
            {
                "profile": profile,
                "user": User.query.get(profile.user_id),
                "documents": get_document_map(profile.id),
            }
        )

    booking_cards = []
    for booking in bookings:
        customer = User.query.get(booking.user_id)
        assigned_professional = None
        if booking.assigned_professional_id:
            assigned_professional = User.query.get(booking.assigned_professional_id)

        booking_cards.append(
            {
                "booking": booking,
                "customer": customer,
                "assigned_professional": assigned_professional,
            }
        )

    approved_provider_choices = []
    for provider in provider_users:
        profile = get_profile(provider.id)
        if profile and profile.verification_status == "approved" and profile.is_active:
            services = get_profile_categories(profile)
            approved_provider_choices.append(
                {
                    "user": provider,
                    "profile": profile,
                    "services": services,
                }
            )

    completed_orders = []
    for booking in bookings:
        if booking.work_status == "completed":
            completed_orders.append(booking)

    professional_payout_summary = []
    for provider in provider_users:
        provider_orders = []
        for order in completed_orders:
            if order.assigned_professional_id == provider.id:
                provider_orders.append(order)

        if not provider_orders:
            continue

        total_value = 0
        total_commission = 0
        total_payout = 0
        for order in provider_orders:
            total_value += order.total_price or 0
            total_commission += order.admin_commission or 0
            total_payout += order.professional_amount or 0

        profile = get_profile(provider.id)
        services = get_profile_categories(profile)

        professional_payout_summary.append(
            {
                "user": provider,
                "profile": profile,
                "services": services,
                "completed_orders": len(provider_orders),
                "gross_service_value": total_value,
                "admin_commission": total_commission,
                "professional_payout": total_payout,
            }
        )

    stats = {
        "pending_verifications": 0,
        "approved_professionals": 0,
        "total_orders": len(bookings),
        "completed_orders": len(completed_orders),
        "admin_revenue": 0,
    }

    for profile in profiles:
        if profile.verification_status == "pending":
            stats["pending_verifications"] += 1
        if profile.verification_status == "approved":
            stats["approved_professionals"] += 1

    for order in completed_orders:
        stats["admin_revenue"] += order.admin_commission or 0

    return render_template(
        "admin.html",
        current_user=get_current_user(),
        service_categories=SERVICE_CATEGORIES,
        format_status_label=format_status_label,
        edit_profile_id=request.args.get("edit_profile_id", type=int),
        edit_order_id=request.args.get("edit_order_id", type=int),
        profile_message=request.args.get("profile_message", ""),
        profile_message_type=request.args.get("profile_message_type", "success"),
        order_message=request.args.get("order_message", ""),
        order_message_type=request.args.get("order_message_type", "success"),
        profiles=profile_cards,
        bookings=booking_cards,
        approved_provider_choices=approved_provider_choices,
        professional_payout_summary=professional_payout_summary,
        stats=stats,
    )


@app.route("/admin/professional/<int:profile_id>/review", methods=["POST"])
def review_professional(profile_id):
    user, redirect_response = require_role("admin")
    if redirect_response:
        return redirect_response

    profile = ProfessionalProfile.query.get(profile_id)
    if not profile:
        return redirect(url_for("admin_dashboard"))

    def redirect_profile_message(message="", message_type="success", keep_edit_open=True):
        redirect_url = url_for(
            "admin_dashboard",
            edit_profile_id=profile_id if keep_edit_open else None,
            profile_message=message,
            profile_message_type=message_type,
        )
        return redirect(redirect_url + f"#profile-{profile_id}")

    decision = request.form.get("decision", "").strip()
    rejection_reason = request.form.get("rejection_reason", "").strip()

    if decision == "approve":
        profile.verification_status = "approved"
        profile.is_active = True
        profile.rejection_reason = None
    elif decision == "reject":
        profile.verification_status = "rejected"
        profile.is_active = False
        profile.rejection_reason = rejection_reason or "Please review and re-submit your documents."
    else:
        return redirect_profile_message("Invalid review action.", "error")

    db.session.commit()
    return redirect_profile_message("", "success", profile.verification_status != "approved")


@app.route("/admin/order/<int:booking_id>/update", methods=["POST"])
def update_admin_order(booking_id):
    user, redirect_response = require_role("admin")
    if redirect_response:
        return redirect_response

    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(url_for("admin_dashboard"))

    def redirect_order_message(message="", message_type="success", keep_edit_open=True):
        redirect_url = url_for(
            "admin_dashboard",
            edit_order_id=booking_id if keep_edit_open else None,
            order_message=message,
            order_message_type=message_type,
        )
        return redirect(
            redirect_url + f"#order-{booking_id}"
        )

    selected_professional_id = request.form.get("assigned_professional_id", "").strip()
    work_status = request.form.get("work_status", "").strip()
    admin_notes = request.form.get("admin_notes", "").strip()
    update_message = "Order updated from admin dashboard."
    update_message_type = "success"
    assignment_failed = False
    assignment_made = False

    if selected_professional_id == "auto":
        profile = auto_assign_professional(booking.service_category)
        if profile:
            booking.assigned_professional_id = profile.user_id
            assignment_made = True
            if booking.work_status == "pending":
                booking.work_status = "assigned"
                booking.status = "Assigned"
            assigned_user = User.query.get(profile.user_id)
            if assigned_user:
                update_message = f"Order automatically assigned to {assigned_user.name}."
        else:
            booking.assigned_professional_id = None
            booking.work_status = "pending"
            booking.status = "Pending"
            update_message = f"All matching professionals already have {MAX_ACTIVE_JOBS_PER_PROFESSIONAL} active jobs."
            update_message_type = "error"
            assignment_failed = True
    elif selected_professional_id:
        try:
            selected_user_id = int(selected_professional_id)
        except ValueError:
            return redirect_order_message("Invalid professional selection.", "error")

        selected_user = User.query.get(selected_user_id)
        selected_profile = get_profile(selected_user_id)
        if not selected_user or not selected_profile or selected_profile.verification_status != "approved":
            return redirect_order_message("Selected professional is not approved yet.", "error")

        if not professional_offers_service(selected_profile, booking.service_category):
            return redirect_order_message("Selected professional does not offer this service category.", "error")

        booking.assigned_professional_id = selected_user.id
        assignment_made = True
        if booking.work_status in ["pending", "assigned"] and booking.assigned_professional_id:
            booking.work_status = "assigned"
            booking.status = "Assigned"
        update_message = f"Order assigned to {selected_user.name}."

    if work_status and not assignment_failed:
        if assignment_made and work_status == "pending":
            work_status = "assigned"
        if work_status != "pending" and not booking.assigned_professional_id:
            work_status = "pending"
        booking.work_status = work_status
        booking.status = format_status_label(work_status)
        if work_status == "completed":
            update_message = "Order marked as completed."
        elif work_status == "in_progress":
            update_message = "Order marked as in progress."
        elif work_status == "assigned" and booking.assigned_professional_id:
            assigned_user = User.query.get(booking.assigned_professional_id)
            if assigned_user:
                update_message = f"Order assigned to {assigned_user.name}."
            else:
                update_message = "Order marked as assigned."
        elif work_status == "pending":
            update_message = "Order moved back to pending."

    booking.admin_notes = admin_notes or None
    update_booking_amounts(booking)
    db.session.commit()

    keep_edit_open = booking.work_status != "completed"
    show_message = update_message if update_message_type == "error" else ""
    return redirect_order_message(show_message, update_message_type, keep_edit_open)


@app.route("/place-order", methods=["POST"])
def place_order():
    if not session.get("user_id"):
        return redirect(url_for("auth", next=url_for("cart"), mode="login"))

    cart_text = request.form.get("cart_items", "").strip()
    address = request.form.get("address", "").strip()
    latitude = request.form.get("latitude", "").strip()
    longitude = request.form.get("longitude", "").strip()
    place_id = request.form.get("place_id", "").strip()
    slot_period = request.form.get("slot_period", "").strip()
    slot_time = request.form.get("slot_time", "").strip()
    payment_method = request.form.get("payment_method", "").strip()

    if not cart_text:
        return redirect(url_for("cart", message="Your cart is empty.", message_type="error"))

    if not address or not slot_period or not slot_time or not payment_method:
        return redirect(
            url_for(
                "cart",
                message="Please complete slot, location, and payment details.",
                message_type="error",
            )
        )

    if payment_method == "online_payment":
        return redirect(
            url_for(
                "cart",
                message="Online payment will be connected with Razorpay next.",
                message_type="error",
            )
        )

    if payment_method != "pay_after_service":
        return redirect(url_for("cart", message="Invalid payment method.", message_type="error"))

    service_list = []
    total_price = 0
    items = []
    parts = cart_text.split("||")
    for part in parts:
        values = part.split("##")
        if len(values) < 4:
            continue
        try:
            qty = int(values[2])
            price = int(values[1])
        except (TypeError, ValueError):
            continue

        name = values[0].strip()
        page_category = values[3].strip()
        if qty <= 0 or price < 0 or not name:
            continue

        items.append({"name": name, "qty": qty, "price": price, "pageCategory": page_category})
        service_list.append(f"{name} x{qty}")
        total_price += qty * price

    if not service_list:
        return redirect(url_for("cart", message="No valid cart items were found.", message_type="error"))

    cart_categories = get_cart_service_categories(items)
    if len(cart_categories) > 1:
        return redirect(
            url_for(
                "cart",
                message="Please place separate orders for different service categories.",
                message_type="error",
            )
        )

    booking = Booking(
        user_id=session["user_id"],
        service_summary=", ".join(service_list),
        service_category=cart_categories[0] if cart_categories else infer_service_category(items),
        total_price=total_price,
        slot=f"{slot_period} | {slot_time}",
        address=address,
        payment_method=payment_method,
        status="Pending",
        work_status="pending",
    )
    update_booking_amounts(booking)

    db.session.add(booking)

    if address and latitude and longitude:
        try:
            saved_location = SavedLocation(
                user_id=session["user_id"],
                address=address,
                latitude=float(latitude),
                longitude=float(longitude),
                place_id=place_id or None,
                source="cart_checkout",
            )
            db.session.add(saved_location)
        except ValueError:
            pass

    db.session.commit()

    return redirect(url_for("my_orders", ordered="1"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)
