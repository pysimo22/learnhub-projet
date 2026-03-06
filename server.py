# server.py — API REST LearnHub (Python + Flask + PyMongo)
# Installer : pip install flask pymongo python-dotenv
# Démarrer  : python server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# ── Connexion MongoDB 
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017"))
db     = client["learnhub"]

# ── Helper : convertir ObjectId en string pour JSON     
def serialize(doc):
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize(d) for d in doc]
    result = {}
    for key, val in doc.items():
        if isinstance(val, ObjectId):
            result[key] = str(val)
        elif isinstance(val, datetime):
            result[key] = str(val)
        elif isinstance(val, dict):
            result[key] = serialize(val)
        elif isinstance(val, list):
            result[key] = [str(v) if isinstance(v, ObjectId) else v for v in val]
        else:
            result[key] = val
    return result

def valid_id(id_str):
    try:
        return ObjectId(id_str)
    except (InvalidId, Exception):
        return None


# ── POST /api/users ── insertOne ──────────────────────────────
@app.route("/api/users", methods=["POST"])
def create_user():
    body = request.json
    user = {
        "firstName":            body.get("firstName"),
        "lastName":             body.get("lastName"),
        "email":                body.get("email"),
        "role":                 body.get("role", "student"),
        "profile": {
            "bio":     body.get("profile", {}).get("bio", ""),
            "avatar":  body.get("profile", {}).get("avatar", ""),
            "city":    body.get("profile", {}).get("city", ""),
            "country": body.get("profile", {}).get("country", "France"),
        },
        "skills":               body.get("skills", []),
        "isActive":             True,
        "totalCoursesEnrolled": 0,
        "createdAt":            datetime.utcnow(),
        "lastLoginAt":          datetime.utcnow(),
    }
    result = db.users.insert_one(user)         # insertOne ✅
    return jsonify({"insertedId": str(result.inserted_id)}), 201


# ── GET /api/users ── find + filtres + pagination ─────────────
@app.route("/api/users", methods=["GET"])
def get_users():
    filter_ = {}

    if request.args.get("role"):
        filter_["role"] = request.args.get("role")

    if request.args.get("active") == "true":
        filter_["isActive"] = True

    # notation pointée ✅
    if request.args.get("city"):
        filter_["profile.city"] = request.args.get("city")

    page  = int(request.args.get("page",  1))
    limit = int(request.args.get("limit", 10))

    users = list(
        db.users.find(filter_, {"profile": 0})     # projection ✅
        .skip((page - 1) * limit)
        .limit(limit)
    )
    return jsonify({"page": page, "count": len(users), "data": serialize(users)})


# ── GET /api/users/:id ── findOne ─────────────────────────────
@app.route("/api/users/<id>", methods=["GET"])
def get_user(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    user = db.users.find_one({"_id": oid})         # findOne ✅
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify(serialize(user))


# ── PATCH /api/users/:id ── updateOne + $set/$push/$pull/$inc ─
@app.route("/api/users/<id>", methods=["PATCH"])
def update_user(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    body   = request.json
    update = {}

    if "set"  in body: update["$set"]  = body["set"]    # $set  ✅
    if "push" in body: update["$push"] = body["push"]   # $push ✅
    if "pull" in body: update["$pull"] = body["pull"]   # $pull ✅
    if "inc"  in body: update["$inc"]  = body["inc"]    # $inc  ✅

    if not update:
        return jsonify({"error": "Aucune opération fournie"}), 400

    result = db.users.update_one({"_id": oid}, update)  # updateOne ✅
    if result.matched_count == 0:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({"modifiedCount": result.modified_count})


# ── PUT /api/users/:id/profile ── updateOne + upsert ──────────
@app.route("/api/users/<id>/profile", methods=["PUT"])
def upsert_profile(id):
    oid  = valid_id(id)
    body = request.json

    result = db.users.update_one(
        {"_id": oid},
        {"$set": {"profile": {
            "bio":     body.get("bio", ""),
            "avatar":  body.get("avatar", ""),
            "city":    body.get("city", ""),
            "country": body.get("country", "France"),
        }}},
        upsert=True                                    # upsert ✅
    )
    status = 201 if result.upserted_id else 200
    return jsonify({"upserted": bool(result.upserted_id)}), status


# ── DELETE /api/users/:id ── deleteOne ────────────────────────
@app.route("/api/users/<id>", methods=["DELETE"])
def delete_user(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    result = db.users.delete_one({"_id": oid})        # deleteOne ✅
    if result.deleted_count == 0:
        return jsonify({"error": "Utilisateur introuvable"}), 404
    return jsonify({"message": "Utilisateur supprimé"})


# ── GET /api/users/:id/dashboard ── multi-collections ─────────
@app.route("/api/users/<id>/dashboard", methods=["GET"])
def dashboard(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    # findOne + projection ✅
    user = db.users.find_one(
        {"_id": oid},
        {"firstName": 1, "lastName": 1, "profile.bio": 1, "totalCoursesEnrolled": 1}
    )
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # find + filtre ✅
    enrollments = list(db.enrollments.find({"userId": oid, "status": "active"}))

    # find + tri + limit ✅
    reviews = list(db.reviews.find({"userId": oid}).sort("createdAt", -1).limit(3))

    return jsonify({
        "user":        serialize(user),
        "enrollments": serialize(enrollments),
        "reviews":     serialize(reviews),
    })


# ══════════════════════════════════════════════════════════════
# COURSES
# ══════════════════════════════════════════════════════════════

# ── POST /api/courses ── insertOne ────────────────────────────
@app.route("/api/courses", methods=["POST"])
def create_course():
    body   = request.json
    course = {
        "title":           body.get("title"),
        "description":     body.get("description", ""),
        "instructorId":    ObjectId(body["instructorId"]) if body.get("instructorId") else None,
        "category":        body.get("category", "Web"),
        "difficulty":      body.get("difficulty", "beginner"),
        "price":           float(body.get("price", 0)),
        "tags":            body.get("tags", []),
        "metadata": {
            "duration":     body.get("metadata", {}).get("duration", 0),
            "totalLessons": body.get("metadata", {}).get("totalLessons", 0),
            "language":     body.get("metadata", {}).get("language", "fr"),
        },
        "rating":          {"average": 0, "count": 0},
        "isPublished":     body.get("isPublished", False),
        "enrollmentCount": 0,
        "createdAt":       datetime.utcnow(),
        "updatedAt":       datetime.utcnow(),
    }
    result = db.courses.insert_one(course)             # insertOne ✅
    return jsonify({"insertedId": str(result.inserted_id)}), 201


# ── POST /api/courses/bulk ── insertMany ──────────────────────
@app.route("/api/courses/bulk", methods=["POST"])
def bulk_courses():
    body = request.json
    if not isinstance(body, list) or len(body) == 0:
        return jsonify({"error": "Fournissez un tableau de cours"}), 400

    result = db.courses.insert_many(body)              # insertMany ✅
    return jsonify({"insertedCount": len(result.inserted_ids)}), 201


# ── GET /api/courses ── find + filtres + sort + pagination ────
@app.route("/api/courses", methods=["GET"])
def get_courses():
    filter_ = {}

    # $in ✅
    if request.args.get("category"):
        cats = request.args.get("category").split(",")
        filter_["category"] = {"$in": cats} if len(cats) > 1 else cats[0]

    # $ne ✅
    if request.args.get("excludeDifficulty"):
        filter_["difficulty"] = {"$ne": request.args.get("excludeDifficulty")}
    elif request.args.get("difficulty"):
        filter_["difficulty"] = request.args.get("difficulty")

    # $gte / $lte ✅
    price_filter = {}
    if request.args.get("minPrice"): price_filter["$gte"] = float(request.args.get("minPrice"))
    if request.args.get("maxPrice"): price_filter["$lte"] = float(request.args.get("maxPrice"))
    if price_filter: filter_["price"] = price_filter

    if request.args.get("published") == "true":
        filter_["isPublished"] = True

    # notation pointée + $gte ✅
    if request.args.get("minRating"):
        filter_["rating.average"] = {"$gte": float(request.args.get("minRating"))}

    # tri
    sort_map = {"price": "price", "rating": "rating.average", "popular": "enrollmentCount"}
    sort_field = request.args.get("sort", "")
    sort_dir   = -1 if sort_field.startswith("-") else 1
    sort_key   = sort_map.get(sort_field.lstrip("-"), "createdAt")

    page  = int(request.args.get("page",  1))
    limit = int(request.args.get("limit", 10))

    # projection minimale si ?minimal=true ✅
    projection = {"_id": 0, "title": 1, "price": 1, "rating.average": 1} \
                 if request.args.get("minimal") == "true" else {}

    courses = list(
        db.courses.find(filter_, projection or None)
        .sort(sort_key, sort_dir)
        .skip((page - 1) * limit)
        .limit(limit)
    )
    total = db.courses.count_documents(filter_)
    return jsonify({"page": page, "total": total, "data": serialize(courses)})


# ── GET /api/courses/search ── $regex + $or ───────────────────
@app.route("/api/courses/search", methods=["GET"])
def search_courses():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "Paramètre ?q= requis"}), 400

    # $or + $regex ✅
    courses = list(db.courses.find({
        "$or": [
            {"title":       {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
            {"tags":        {"$regex": q, "$options": "i"}},
        ],
        "isPublished": True
    }).sort("rating.average", -1))
    return jsonify({"query": q, "count": len(courses), "data": serialize(courses)})


# ── GET /api/courses/:id ── findOne ───────────────────────────
@app.route("/api/courses/<id>", methods=["GET"])
def get_course(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    course = db.courses.find_one({"_id": oid})         # findOne ✅
    if not course:
        return jsonify({"error": "Cours introuvable"}), 404
    return jsonify(serialize(course))


# ── PATCH /api/courses/:id ── updateOne + $set/$push/$pull/$inc
@app.route("/api/courses/<id>", methods=["PATCH"])
def update_course(id):
    oid  = valid_id(id)
    body = request.json
    update = {}

    if "set"  in body:
        body["set"]["updatedAt"] = datetime.utcnow()
        update["$set"]  = body["set"]
    if "push" in body: update["$push"] = body["push"]
    if "pull" in body: update["$pull"] = body["pull"]
    if "inc"  in body: update["$inc"]  = body["inc"]

    if not update:
        return jsonify({"error": "Aucune opération fournie"}), 400

    result = db.courses.update_one({"_id": oid}, update)
    return jsonify({"modifiedCount": result.modified_count})


# ── DELETE /api/courses/:id ── cascade ────────────────────────
@app.route("/api/courses/<id>", methods=["DELETE"])
def delete_course(id):
    oid = valid_id(id)
    if not oid:
        return jsonify({"error": "ID invalide"}), 400

    course = db.courses.find_one({"_id": oid})
    if not course:
        return jsonify({"error": "Cours introuvable"}), 404

    db.courses.delete_one({"_id": oid})                        # deleteOne ✅
    lessons_del   = db.lessons.delete_many({"courseId": oid})  # deleteMany ✅
    reviews_del   = db.reviews.delete_many({"courseId": oid})  # deleteMany ✅
    enroll_update = db.enrollments.update_many(                 # updateMany + $set ✅
        {"courseId": oid},
        {"$set": {"status": "cancelled"}}
    )
    return jsonify({
        "message":            "Cours supprimé avec cascade",
        "deletedLessons":     lessons_del.deleted_count,
        "deletedReviews":     reviews_del.deleted_count,
        "cancelledEnrollments": enroll_update.modified_count,
    })


# ══════════════════════════════════════════════════════════════
# LESSONS
# ══════════════════════════════════════════════════════════════

# ── GET /api/courses/:id/lessons ── find + sort ───────────────
@app.route("/api/courses/<id>/lessons", methods=["GET"])
def get_lessons(id):
    oid     = valid_id(id)
    lessons = list(db.lessons.find({"courseId": oid}).sort("order", 1))  # find + sort ✅
    return jsonify({"count": len(lessons), "data": serialize(lessons)})


# ── POST /api/lessons ── insertOne ────────────────────────────
@app.route("/api/lessons", methods=["POST"])
def create_lesson():
    body   = request.json
    lesson = {
        "courseId":  ObjectId(body["courseId"]),
        "title":     body.get("title"),
        "content":   body.get("content", ""),
        "type":      body.get("type", "video"),
        "order":     body.get("order", 1),
        "duration":  body.get("duration", 0),
        "resources": body.get("resources", []),
        "isFree":    body.get("isFree", False),
        "createdAt": datetime.utcnow(),
    }
    result = db.lessons.insert_one(lesson)             # insertOne ✅
    return jsonify({"insertedId": str(result.inserted_id)}), 201


# ── DELETE /api/lessons/:id ── deleteOne ──────────────────────
@app.route("/api/lessons/<id>", methods=["DELETE"])
def delete_lesson(id):
    oid    = valid_id(id)
    result = db.lessons.delete_one({"_id": oid})       # deleteOne ✅
    if result.deleted_count == 0:
        return jsonify({"error": "Leçon introuvable"}), 404
    return jsonify({"message": "Leçon supprimée"})


# ══════════════════════════════════════════════════════════════
# ENROLLMENTS
# ══════════════════════════════════════════════════════════════

# ── POST /api/enrollments ── logique multi-étapes ─────────────
@app.route("/api/enrollments", methods=["POST"])
def create_enrollment():
    body      = request.json
    user_oid  = valid_id(body.get("userId"))
    course_oid = valid_id(body.get("courseId"))

    if not user_oid or not course_oid:
        return jsonify({"error": "IDs invalides"}), 400

    # findOne — vérifier que l'utilisateur existe ✅
    user = db.users.find_one({"_id": user_oid})
    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    # findOne — vérifier que le cours existe et est publié ✅
    course = db.courses.find_one({"_id": course_oid, "isPublished": True})
    if not course:
        return jsonify({"error": "Cours introuvable ou non publié"}), 404

    # findOne — vérifier pas de doublon ✅
    existing = db.enrollments.find_one({"userId": user_oid, "courseId": course_oid})
    if existing:
        return jsonify({"error": "Déjà inscrit à ce cours"}), 409

    # insertOne — créer l'inscription ✅
    db.enrollments.insert_one({
        "userId":    user_oid,
        "courseId":  course_oid,
        "status":    "active",
        "progress":  {"completedLessons": [], "percentage": 0, "lastAccessedAt": datetime.utcnow()},
        "payment":   {"amount": course["price"], "method": body.get("method", "card"), "paidAt": datetime.utcnow()},
        "enrolledAt": datetime.utcnow(),
        "completedAt": None,
    })

    # updateOne + $inc — incrémenter les compteurs ✅
    db.courses.update_one({"_id": course_oid}, {"$inc": {"enrollmentCount": 1}})
    db.users.update_one({"_id": user_oid},     {"$inc": {"totalCoursesEnrolled": 1}})

    return jsonify({"message": "Inscription créée"}), 201


# ── GET /api/enrollments ── find + $nin ───────────────────────
@app.route("/api/enrollments", methods=["GET"])
def get_enrollments():
    filter_ = {}

    if request.args.get("userId"):
        filter_["userId"] = valid_id(request.args.get("userId"))

    if request.args.get("status"):
        filter_["status"] = request.args.get("status")

    # $nin ✅
    if request.args.get("exclude"):
        excluded = request.args.get("exclude").split(",")
        filter_["status"] = {"$nin": excluded}

    enrollments = list(db.enrollments.find(filter_).sort("enrolledAt", -1))
    return jsonify({"count": len(enrollments), "data": serialize(enrollments)})


# ── PATCH /api/enrollments/:id/progress ── $push + $set ───────
@app.route("/api/enrollments/<id>/progress", methods=["PATCH"])
def update_progress(id):
    oid        = valid_id(id)
    lesson_oid = valid_id(request.json.get("lessonId"))

    if not oid or not lesson_oid:
        return jsonify({"error": "IDs invalides"}), 400

    enrollment = db.enrollments.find_one({"_id": oid})
    if not enrollment:
        return jsonify({"error": "Inscription introuvable"}), 404

    # $push — ajouter la leçon complétée ✅
    db.enrollments.update_one({"_id": oid}, {"$push": {"progress.completedLessons": lesson_oid}})

    course      = db.courses.find_one({"_id": enrollment["courseId"]})
    updated     = db.enrollments.find_one({"_id": oid})
    total       = course["metadata"]["totalLessons"]
    percentage  = min(100, round(len(updated["progress"]["completedLessons"]) / total * 100))

    set_fields  = {"progress.percentage": percentage, "progress.lastAccessedAt": datetime.utcnow()}
    if percentage >= 100:
        set_fields["status"]      = "completed"
        set_fields["completedAt"] = datetime.utcnow()

    # $set — recalculer le pourcentage ✅
    db.enrollments.update_one({"_id": oid}, {"$set": set_fields})

    return jsonify({"percentage": percentage, "completed": percentage >= 100})


# ══════════════════════════════════════════════════════════════
# REVIEWS
# ══════════════════════════════════════════════════════════════

# ── POST /api/reviews ── insertOne + recalcul moyenne ─────────
@app.route("/api/reviews", methods=["POST"])
def create_review():
    body       = request.json
    user_oid   = valid_id(body.get("userId"))
    course_oid = valid_id(body.get("courseId"))

    # findOne — vérifier l'inscription ✅
    enrollment = db.enrollments.find_one({
        "userId": user_oid, "courseId": course_oid,
        "status": {"$in": ["active", "completed"]}    # $in ✅
    })
    if not enrollment:
        return jsonify({"error": "Vous devez être inscrit au cours"}), 403

    # findOne — vérifier pas de doublon ✅
    if db.reviews.find_one({"userId": user_oid, "courseId": course_oid}):
        return jsonify({"error": "Avis déjà soumis"}), 409

    # insertOne ✅
    db.reviews.insert_one({
        "userId":       user_oid,
        "courseId":     course_oid,
        "rating":       int(body.get("rating")),
        "title":        body.get("title", ""),
        "comment":      body.get("comment", ""),
        "isVerified":   enrollment["status"] == "completed",
        "helpfulCount": 0,
        "createdAt":    datetime.utcnow(),
        "updatedAt":    None,
    })

    # Recalculer la moyenne
    all_reviews = list(db.reviews.find({"courseId": course_oid}))
    avg = round(sum(r["rating"] for r in all_reviews) / len(all_reviews), 1)

    # $set + $inc ✅
    db.courses.update_one(
        {"_id": course_oid},
        {"$set": {"rating.average": avg}, "$inc": {"rating.count": 1}}
    )
    return jsonify({"message": "Avis créé", "newAverage": avg}), 201


# ── GET /api/reviews ── find + $exists ────────────────────────
@app.route("/api/reviews", methods=["GET"])
def get_reviews():
    filter_ = {}

    if request.args.get("courseId"):
        filter_["courseId"] = valid_id(request.args.get("courseId"))

    if request.args.get("userId"):
        filter_["userId"] = valid_id(request.args.get("userId"))

    # $exists ✅
    if request.args.get("updated") == "true":
        filter_["updatedAt"] = {"$exists": True, "$ne": None}

    reviews = list(db.reviews.find(filter_).sort("createdAt", -1))
    return jsonify({"count": len(reviews), "data": serialize(reviews)})


# ── DELETE /api/reviews/:id ── deleteOne ──────────────────────
@app.route("/api/reviews/<id>", methods=["DELETE"])
def delete_review(id):
    oid    = valid_id(id)
    result = db.reviews.delete_one({"_id": oid})       # deleteOne ✅
    if result.deleted_count == 0:
        return jsonify({"error": "Avis introuvable"}), 404
    return jsonify({"message": "Avis supprimé"})


# ══════════════════════════════════════════════════════════════
# STATS
# ══════════════════════════════════════════════════════════════

# ── GET /api/stats ── countDocuments ──────────────────────────
@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "totalUsers":       db.users.count_documents({}),
        "totalCourses":     db.courses.count_documents({}),
        "publishedCourses": db.courses.count_documents({"isPublished": True}),
        "totalLessons":     db.lessons.count_documents({}),
        "totalEnrollments": db.enrollments.count_documents({}),
        "totalReviews":     db.reviews.count_documents({}),

    })

@app.route("/api/export", methods=["GET"])
def export_data():
    return jsonify({
        "users":       serialize(list(db.users.find())),
        "courses":     serialize(list(db.courses.find())),
        "lessons":     serialize(list(db.lessons.find())),
        "enrollments": serialize(list(db.enrollments.find())),
        "reviews":     serialize(list(db.reviews.find())),
    })


# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 API démarrée sur http://localhost:{port}")
    app.run(debug=True, port=port)
