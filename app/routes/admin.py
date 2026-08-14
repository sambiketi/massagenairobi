from datetime import datetime, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    current_app,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from sqlalchemy import func, desc

from app import db
from app.models import (
    Therapist,
    Service,
    Booking,
    GalleryImage,
    BlogPost,
)
from app.models.settings import SiteSetting
from app.models.admin import AdminUser

from app.services.upload_service import UploadService
from app.services.supabase_storage import SupabaseStorage


admin_bp = Blueprint("admin", __name__)


# ============================================================
# AUTH
# ============================================================

@admin_bp.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("admin/login.html")

        user = AdminUser.query.filter_by(username=username).first()

        if user and user.check_password(password) and user.is_active:

            login_user(user, remember=True)

            user.last_login = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get("next")

            return redirect(
                next_page
                if next_page
                else url_for("admin.dashboard")
            )

        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out.", "info")

    return redirect(url_for("admin.login"))


# ============================================================
# DASHBOARD
# ============================================================

@admin_bp.route("/")
@login_required
def dashboard():

    total_bookings = Booking.query.count()

    pending_bookings = Booking.query.filter_by(
        status="Pending"
    ).count()

    confirmed_bookings = Booking.query.filter_by(
        status="Confirmed"
    ).count()

    completed_bookings = Booking.query.filter_by(
        status="Completed"
    ).count()

    cancelled_bookings = Booking.query.filter_by(
        status="Cancelled"
    ).count()

    week_start = datetime.utcnow() - timedelta(days=7)

    new_bookings = Booking.query.filter(
        Booking.created_at >= week_start
    ).count()

    active_therapists = Therapist.query.filter_by(
        is_available=True
    ).count()

    total_therapists = Therapist.query.count()

    total_services = Service.query.filter_by(
        is_active=True
    ).count()

    chart_data = []

    for i in range(6, -1, -1):

        date = datetime.utcnow() - timedelta(days=i)

        count = Booking.query.filter(
            func.date(Booking.appointment_date) == date.date()
        ).count()

        chart_data.append(count)

    recent_bookings = Booking.query.order_by(
        desc(Booking.created_at)
    ).limit(10).all()

    stats = {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "new_bookings": new_bookings,
        "active_therapists": active_therapists,
        "total_therapists": total_therapists,
        "total_services": total_services,
    }

    return render_template(
        "admin/dashboard.html",
        stats=stats,
        chart_data=chart_data,
        recent_bookings=recent_bookings,
    )


# ============================================================
# THERAPISTS
# ============================================================

@admin_bp.route("/therapists")
@login_required
def therapists():

    therapists = Therapist.query.order_by(
        Therapist.name
    ).all()

    return render_template(
        "admin/therapists.html",
        therapists=therapists,
    )


@admin_bp.route("/api/therapist", methods=["POST"])
@login_required
def create_therapist():

    try:

        name = request.form.get("name", "").strip()
        specialty = request.form.get("specialty")
        bio = request.form.get("bio")
        is_available = request.form.get("is_available") == "on"

        if not name:
            return jsonify({
                "success": False,
                "error": "Name is required",
            }), 400

        therapist = Therapist(
            name=name,
            specialty=specialty,
            bio=bio,
            is_available=is_available,
        )

        if "photo" in request.files:

            file = request.files["photo"]

            if file and file.filename:

                result = UploadService.upload_image(
                    file,
                    "therapists",
                )

                if not result.get("success"):

                    return jsonify({
                        "success": False,
                        "error": result.get(
                            "error",
                            "Photo upload failed",
                        ),
                    }), 400

                therapist.photo_url = result.get("url")

        db.session.add(therapist)
        db.session.commit()

        return jsonify({
            "success": True,
            "therapist": therapist.to_dict(),
        })

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            "CREATE THERAPIST ERROR"
        )

        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@admin_bp.route(
    "/api/therapist/<therapist_id>",
    methods=["GET", "PUT", "DELETE"],
)
@login_required
def therapist_operations(therapist_id):

    therapist = Therapist.query.get_or_404(
        therapist_id
    )

    if request.method == "GET":

        return jsonify(
            therapist.to_dict()
        )

    if request.method == "PUT":

        try:

            name = request.form.get("name")
            specialty = request.form.get("specialty")
            bio = request.form.get("bio")

            if name:
                therapist.name = name.strip()

            if specialty is not None:
                therapist.specialty = specialty

            if bio is not None:
                therapist.bio = bio

            therapist.is_available = (
                request.form.get("is_available") == "on"
            )

            if "photo" in request.files:

                file = request.files["photo"]

                if file and file.filename:

                    old_url = therapist.photo_url

                    result = UploadService.upload_image(
                        file,
                        "therapists",
                    )

                    if not result.get("success"):

                        return jsonify({
                            "success": False,
                            "error": result.get(
                                "error",
                                "Photo upload failed",
                            ),
                        }), 400

                    therapist.photo_url = result.get(
                        "url"
                    )

                    if old_url:
                        UploadService.delete_file(
                            old_url
                        )

            db.session.commit()

            return jsonify({
                "success": True,
                "therapist": therapist.to_dict(),
            })

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "UPDATE THERAPIST ERROR"
            )

            return jsonify({
                "success": False,
                "error": str(e),
            }), 500

    if request.method == "DELETE":

        try:

            if therapist.photo_url:
                UploadService.delete_file(
                    therapist.photo_url
                )

            db.session.delete(therapist)
            db.session.commit()

            return jsonify({
                "success": True
            })

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "DELETE THERAPIST ERROR"
            )

            return jsonify({
                "success": False,
                "error": str(e),
            }), 500


# ============================================================
# SERVICES
# ============================================================

@admin_bp.route("/services")
@login_required
def services():

    services = Service.query.order_by(
        Service.title
    ).all()

    return render_template(
        "admin/services.html",
        services=services,
    )


@admin_bp.route("/api/service", methods=["POST"])
@login_required
def create_service():

    try:

        title = request.form.get("title", "").strip()
        description = request.form.get("description")

        price_kes = request.form.get(
            "price_kes",
            type=int,
        )

        duration_minutes = request.form.get(
            "duration_minutes",
            type=int,
        )

        is_active = (
            request.form.get("is_active") == "on"
        )

        if not title:
            return jsonify({
                "success": False,
                "error": "Title is required",
            }), 400

        if price_kes is None:
            return jsonify({
                "success": False,
                "error": "Price is required",
            }), 400

        if duration_minutes is None:
            return jsonify({
                "success": False,
                "error": "Duration is required",
            }), 400

        service = Service(
            title=title,
            description=description,
            price_kes=price_kes,
            duration_minutes=duration_minutes,
            is_active=is_active,
        )

        if "image" in request.files:

            file = request.files["image"]

            if file and file.filename:

                result = UploadService.upload_image(
                    file,
                    "services",
                )

                if not result.get("success"):

                    return jsonify({
                        "success": False,
                        "error": result.get(
                            "error",
                            "Image upload failed",
                        ),
                    }), 400

                service.image_url = result.get("url")

        db.session.add(service)
        db.session.commit()

        return jsonify({
            "success": True,
            "service": service.to_dict(),
        })

    except Exception as e:

        db.session.rollback()

        current_app.logger.exception(
            "CREATE SERVICE ERROR"
        )

        return jsonify({
            "success": False,
            "error": str(e),
        }), 500


@admin_bp.route(
    "/api/service/<service_id>",
    methods=["GET", "PUT", "DELETE"],
)
@login_required
def service_operations(service_id):

    service = Service.query.get_or_404(
        service_id
    )

    if request.method == "GET":

        return jsonify(
            service.to_dict()
        )

    if request.method == "PUT":

        try:

            title = request.form.get("title")
            description = request.form.get("description")

            price_kes = request.form.get(
                "price_kes",
                type=int,
            )

            duration_minutes = request.form.get(
                "duration_minutes",
                type=int,
            )

            if title:
                service.title = title.strip()

            if description is not None:
                service.description = description

            if price_kes is not None:
                service.price_kes = price_kes

            if duration_minutes is not None:
                service.duration_minutes = (
                    duration_minutes
                )

            service.is_active = (
                request.form.get("is_active") == "on"
            )

            if "image" in request.files:

                file = request.files["image"]

                if file and file.filename:

                    old_url = service.image_url

                    result = UploadService.upload_image(
                        file,
                        "services",
                    )

                    if not result.get("success"):

                        return jsonify({
                            "success": False,
                            "error": result.get(
                                "error",
                                "Image upload failed",
                            ),
                        }), 400

                    service.image_url = result.get(
                        "url"
                    )

                    if old_url:
                        UploadService.delete_file(
                            old_url
                        )

            db.session.commit()

            return jsonify({
                "success": True,
                "service": service.to_dict(),
            })

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "UPDATE SERVICE ERROR"
            )

            return jsonify({
                "success": False,
                "error": str(e),
            }), 500

    if request.method == "DELETE":

        try:

            if service.image_url:
                UploadService.delete_file(
                    service.image_url
                )

            db.session.delete(service)
            db.session.commit()

            return jsonify({
                "success": True
            })

        except Exception as e:

            db.session.rollback()

            current_app.logger.exception(
                "DELETE SERVICE ERROR"
            )

            return jsonify({
                "success": False,
                "error": str(e),
            }), 500


# ============================================================
# BOOKINGS
# ============================================================

@admin_bp.route("/bookings")
@login_required
def bookings():

    try:

        status = request.args.get("status")
        date = request.args.get("date")

        query = Booking.query

        if status:
            query = query.filter_by(
                status=status
            )

        if date:

            try:

                booking_date = datetime.strptime(
                    date,
                    "%Y-%m-%d",
                ).date()

                query = query.filter_by(
                    appointment_date=booking_date
                )

            except ValueError:

                flash(
                    "Invalid date format.",
                    "danger",
                )

        bookings = query.order_by(
            Booking.appointment_date.desc(),
            Booking.appointment_time.desc(),
        ).all()

        stats = {
            "total": Booking.query.count(),
            "pending": Booking.query.filter_by(
                status="Pending"
            ).count(),
            "confirmed": Booking.query.filter_by(
                status="Confirmed"
            ).count(),
            "completed": Booking.query.filter_by(
                status="Completed"
            ).count(),
            "cancelled": Booking.query.filter_by(
                status="Cancelled"
            ).count(),
        }

        return render_template(
            "admin/bookings.html",
            bookings=bookings,
            stats=stats,
        )

    except Exception:

        current_app.logger.exception(
            "BOOKINGS PAGE ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Unable to load bookings",
        }), 500


@admin_bp.route(
    "/api/booking/<booking_id>",
    methods=["GET", "PUT", "DELETE"],
)
@login_required
def booking_operations(booking_id):

    booking = Booking.query.get_or_404(
        booking_id
    )

    if request.method == "GET":

        return jsonify({
            "success": True,
            "booking": booking.to_dict(),
        })

    if request.method == "PUT":

        try:

            data = request.get_json(
                silent=True
            ) or {}

            if "client_name" in data:

                name = str(
                    data["client_name"]
                ).strip()

                if not name:
                    return jsonify({
                        "success": False,
                        "error": "Client name is required",
                    }), 400

                booking.client_name = name

            if "client_phone" in data:

                phone = str(
                    data["client_phone"]
                ).strip()

                if not phone:
                    return jsonify({
                        "success": False,
                        "error": "Client phone is required",
                    }), 400

                booking.client_phone = phone

            if "appointment_date" in data:

                try:

                    booking.appointment_date = (
                        datetime.strptime(
                            data["appointment_date"],
                            "%Y-%m-%d",
                        ).date()
                    )

                except (ValueError, TypeError):

                    return jsonify({
                        "success": False,
                        "error": "Invalid appointment date",
                    }), 400

            if "appointment_time" in data:

                try:

                    booking.appointment_time = (
                        datetime.strptime(
                            data["appointment_time"],
                            "%H:%M",
                        ).time()
                    )

                except (ValueError, TypeError):

                    return jsonify({
                        "success": False,
                        "error": "Invalid appointment time",
                    }), 400

            if "notes" in data:
                booking.notes = data["notes"]

            if "status" in data:

                allowed_statuses = {
                    "Pending",
                    "Confirmed",
                    "Completed",
                    "Cancelled",
                }

                if data["status"] not in allowed_statuses:

                    return jsonify({
                        "success": False,
                        "error": "Invalid booking status",
                    }), 400

                booking.status = data["status"]

            db.session.commit()

            return jsonify({
                "success": True,
                "booking": booking.to_dict(),
            })

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "UPDATE BOOKING ERROR"
            )

            return jsonify({
                "success": False,
                "error": "Failed to update booking",
            }), 500

    if request.method == "DELETE":

        try:

            db.session.delete(booking)
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Booking deleted",
            })

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "DELETE BOOKING ERROR"
            )

            return jsonify({
                "success": False,
                "error": "Failed to delete booking",
            }), 500


@admin_bp.route(
    "/api/booking/<booking_id>/confirm",
    methods=["PUT"],
)
@login_required
def confirm_booking(booking_id):

    try:

        booking = Booking.query.get_or_404(
            booking_id
        )

        booking.status = "Confirmed"

        db.session.commit()

        return jsonify({
            "success": True,
            "booking": booking.to_dict(),
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "CONFIRM BOOKING ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to confirm booking",
        }), 500


# ============================================================
# GALLERY
# ============================================================

@admin_bp.route("/gallery")
@login_required
def gallery():

    images = GalleryImage.query.order_by(
        GalleryImage.sort_order
    ).all()

    return render_template(
        "admin/gallery.html",
        gallery_images=images,
    )


@admin_bp.route(
    "/api/gallery",
    methods=["POST"],
)
@login_required
def upload_gallery():

    try:

        files = request.files.getlist(
            "gallery_images"
        )

        if not files:
            return jsonify({
                "success": False,
                "error": "No images provided",
            }), 400

        uploaded = []

        for file in files:

            if not file or not file.filename:
                continue

            result = UploadService.upload_image(
                file,
                "gallery",
                create_thumbnail=True,
            )

            if not result.get("success"):

                current_app.logger.error(
                    f"GALLERY UPLOAD FAILED: "
                    f"{result.get('error')}"
                )

                continue

            gallery_image = GalleryImage(
                title=file.filename,
                url=result.get("url"),
                thumbnail_url=result.get(
                    "thumbnail_url"
                ),
            )

            db.session.add(gallery_image)

            uploaded.append(
                gallery_image
            )

        db.session.commit()

        return jsonify({
            "success": True,
            "images": [
                image.to_dict()
                for image in uploaded
            ],
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "GALLERY UPLOAD ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Gallery upload failed",
        }), 500


@admin_bp.route(
    "/api/gallery/<image_id>",
    methods=["DELETE"],
)
@login_required
def delete_gallery_image(image_id):

    try:

        image = GalleryImage.query.get_or_404(
            image_id
        )

        if image.url:
            UploadService.delete_file(
                image.url
            )

        if (
            image.thumbnail_url
            and image.thumbnail_url != image.url
        ):
            UploadService.delete_file(
                image.thumbnail_url
            )

        db.session.delete(image)
        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "DELETE GALLERY IMAGE ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to delete image",
        }), 500


# ============================================================
# BLOG
# ============================================================

@admin_bp.route("/blog")
@login_required
def blog():

    posts = BlogPost.query.order_by(
        desc(BlogPost.created_at)
    ).all()

    return render_template(
        "admin/blog.html",
        posts=posts,
    )


@admin_bp.route(
    "/api/blog",
    methods=["POST"],
)
@login_required
def create_blog_post():

    try:

        title = request.form.get(
            "title",
            "",
        ).strip()

        slug = request.form.get(
            "slug",
            "",
        ).strip()

        content = request.form.get(
            "content",
            "",
        )

        excerpt = request.form.get(
            "excerpt"
        )

        is_published = (
            request.form.get(
                "is_published"
            ) == "on"
        )

        meta_description = request.form.get(
            "meta_description"
        )

        meta_keywords = request.form.get(
            "meta_keywords"
        )

        if not title or not content:

            return jsonify({
                "success": False,
                "error": "Title and content are required",
            }), 400

        if not slug:

            slug = (
                title.lower()
                .replace(" ", "-")
                .replace(".", "")
                .replace(",", "")
                .replace("'", "")
                .replace('"', "")
            )

        post = BlogPost(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            is_published=is_published,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
        )

        if "image" in request.files:

            file = request.files["image"]

            if file and file.filename:

                result = UploadService.upload_image(
                    file,
                    "blog",
                )

                if not result.get("success"):

                    return jsonify({
                        "success": False,
                        "error": result.get(
                            "error",
                            "Image upload failed",
                        ),
                    }), 400

                post.image_url = result.get(
                    "url"
                )

        db.session.add(post)
        db.session.commit()

        return jsonify({
            "success": True,
            "post": post.to_dict(),
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "CREATE BLOG ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to create blog post",
        }), 500


@admin_bp.route(
    "/api/blog/<post_id>",
    methods=["GET", "PUT", "DELETE"],
)
@login_required
def blog_operations(post_id):

    post = BlogPost.query.get_or_404(
        post_id
    )

    if request.method == "GET":

        return jsonify(
            post.to_dict()
        )

    if request.method == "PUT":

        try:

            title = request.form.get("title")
            slug = request.form.get("slug")
            content = request.form.get("content")
            excerpt = request.form.get("excerpt")

            if title:
                post.title = title

            if slug:
                post.slug = slug

            if content:
                post.content = content

            if excerpt is not None:
                post.excerpt = excerpt

            post.is_published = (
                request.form.get(
                    "is_published"
                ) == "on"
            )

            meta_description = request.form.get(
                "meta_description"
            )

            meta_keywords = request.form.get(
                "meta_keywords"
            )

            if meta_description is not None:
                post.meta_description = (
                    meta_description
                )

            if meta_keywords is not None:
                post.meta_keywords = (
                    meta_keywords
                )

            if "image" in request.files:

                file = request.files["image"]

                if file and file.filename:

                    old_url = post.image_url

                    result = UploadService.upload_image(
                        file,
                        "blog",
                    )

                    if not result.get("success"):

                        return jsonify({
                            "success": False,
                            "error": result.get(
                                "error",
                                "Image upload failed",
                            ),
                        }), 400

                    post.image_url = result.get(
                        "url"
                    )

                    if old_url:
                        UploadService.delete_file(
                            old_url
                        )

            db.session.commit()

            return jsonify({
                "success": True,
                "post": post.to_dict(),
            })

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "UPDATE BLOG ERROR"
            )

            return jsonify({
                "success": False,
                "error": "Failed to update blog post",
            }), 500

    if request.method == "DELETE":

        try:

            if post.image_url:
                UploadService.delete_file(
                    post.image_url
                )

            db.session.delete(post)
            db.session.commit()

            return jsonify({
                "success": True
            })

        except Exception:

            db.session.rollback()

            current_app.logger.exception(
                "DELETE BLOG ERROR"
            )

            return jsonify({
                "success": False,
                "error": "Failed to delete blog post",
            }), 500


# ============================================================
# SETTINGS
# ============================================================

@admin_bp.route("/settings")
@login_required
def settings():

    settings = SiteSetting.get_settings()

    gallery_images = GalleryImage.query.order_by(
        GalleryImage.sort_order
    ).all()

    return render_template(
        "admin/settings.html",
        settings=settings,
        gallery_images=gallery_images,
    )


@admin_bp.route(
    "/api/settings",
    methods=["POST"],
)
@login_required
def update_settings():

    try:

        fields = [
            "business_name",
            "business_location",
            "business_phone",
            "business_email",
            "till_number",
            "whatsapp_number",
            "weekday_hours",
            "saturday_hours",
            "sunday_hours",
            "business_tagline",
            "business_description",
            "facebook_url",
            "instagram_url",
            "twitter_url",
            "youtube_url",
            "meta_title",
            "meta_description",
            "meta_keywords",
        ]

        data = {}

        for field in fields:

            value = request.form.get(field)

            if value is not None:
                data[field] = value

        SiteSetting.update_settings(data)

        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "UPDATE SETTINGS ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to update settings",
        }), 500


# ============================================================
# HERO VIDEO
# ============================================================

@admin_bp.route(
    "/api/settings/hero-video",
    methods=["POST"],
)
@login_required
def upload_hero_video():

    try:

        file = request.files.get(
            "hero_video"
        )

        if not file or not file.filename:

            return jsonify({
                "success": False,
                "error": "No video provided",
            }), 400

        result = UploadService.upload_video(
            file,
            "hero",
        )

        if not result.get("success"):

            return jsonify({
                "success": False,
                "error": result.get("error"),
            }), 400

        SiteSetting.set_setting(
            "hero_video_url",
            result.get("url"),
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "url": result.get("url"),
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "HERO VIDEO UPLOAD ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Video upload failed",
        }), 500


@admin_bp.route(
    "/api/settings/hero-video",
    methods=["DELETE"],
)
@login_required
def remove_hero_video():

    try:

        old_video = SiteSetting.get_setting(
            "hero_video_url"
        )

        if old_video:
            UploadService.delete_file(
                old_video
            )

        SiteSetting.set_setting(
            "hero_video_url",
            None,
        )

        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "REMOVE HERO VIDEO ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to remove video",
        }), 500


# ============================================================
# LOGO
# ============================================================

@admin_bp.route(
    "/api/settings/logo",
    methods=["POST"],
)
@login_required
def upload_logo():

    try:

        file = request.files.get("logo")

        if not file or not file.filename:

            return jsonify({
                "success": False,
                "error": "No logo provided",
            }), 400

        result = UploadService.upload_image(
            file,
            "logo",
        )

        if not result.get("success"):

            return jsonify({
                "success": False,
                "error": result.get("error"),
            }), 400

        old_logo = SiteSetting.get_setting(
            "logo_url"
        )

        SiteSetting.set_setting(
            "logo_url",
            result.get("url"),
        )

        db.session.commit()

        if old_logo:
            UploadService.delete_file(
                old_logo
            )

        return jsonify({
            "success": True,
            "url": result.get("url"),
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "LOGO UPLOAD ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Logo upload failed",
        }), 500


@admin_bp.route(
    "/api/settings/logo",
    methods=["DELETE"],
)
@login_required
def remove_logo():

    try:

        old_logo = SiteSetting.get_setting(
            "logo_url"
        )

        if old_logo:
            UploadService.delete_file(
                old_logo
            )

        SiteSetting.set_setting(
            "logo_url",
            None,
        )

        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "REMOVE LOGO ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to remove logo",
        }), 500


# ============================================================
# BACKGROUND IMAGE
# ============================================================

@admin_bp.route(
    "/api/settings/background-image",
    methods=["POST"],
)
@login_required
def upload_background_image():

    try:

        file = request.files.get(
            "background_image"
        )

        if not file or not file.filename:

            return jsonify({
                "success": False,
                "error": "No image provided",
            }), 400

        result = UploadService.upload_image(
            file,
            "background",
        )

        if not result.get("success"):

            return jsonify({
                "success": False,
                "error": result.get("error"),
            }), 400

        old_bg = SiteSetting.get_setting(
            "background_image_url"
        )

        SiteSetting.set_setting(
            "background_image_url",
            result.get("url"),
        )

        db.session.commit()

        if old_bg:
            UploadService.delete_file(
                old_bg
            )

        return jsonify({
            "success": True,
            "url": result.get("url"),
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "BACKGROUND IMAGE UPLOAD ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Background upload failed",
        }), 500


@admin_bp.route(
    "/api/settings/background-image",
    methods=["DELETE"],
)
@login_required
def remove_background_image():

    try:

        old_bg = SiteSetting.get_setting(
            "background_image_url"
        )

        if old_bg:
            UploadService.delete_file(
                old_bg
            )

        SiteSetting.set_setting(
            "background_image_url",
            None,
        )

        db.session.commit()

        return jsonify({
            "success": True
        })

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "REMOVE BACKGROUND ERROR"
        )

        return jsonify({
            "success": False,
            "error": "Failed to remove background",
        }), 500


# ============================================================
# STORAGE DEBUG
# ============================================================

@admin_bp.route("/api/test-storage")
@login_required
def test_storage():

    try:

        result = SupabaseStorage.debug_connection()

        return jsonify(result)

    except Exception as e:

        current_app.logger.exception(
            "STORAGE DEBUG ERROR"
        )

        return jsonify({
            "success": False,
            "error": str(e),
        }), 500