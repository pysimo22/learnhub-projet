use("learnhub");

// 2.1 — CRUD


// 1. Insérer un nouvel utilisateur étudiant
db.users.insertOne({
  firstName: "Simo",
  lastName: "Martin",
  email: "simo.martin@email.com",
  role: "student",
  profile: { city: "Paris", country: "France" },
  skills: ["HTML", "CSS"],
  isActive: true,
  totalCoursesEnrolled: 0,
  createdAt: new Date(),
  lastLoginAt: new Date()
});

// 2. Insérer 3 cours en une seule opération
db.courses.insertMany([
  { title: "JavaScript Débutant", category: "Web", difficulty: "beginner", price: 19.99, isPublished: true, enrollmentCount: 0, rating: { average: 0, count: 0 }, tags: ["js"], createdAt: new Date() },
  { title: "Python Avancé",       category: "Web", difficulty: "advanced", price: 49.99, isPublished: true, enrollmentCount: 0, rating: { average: 0, count: 0 }, tags: ["python"], createdAt: new Date() },
  { title: "Docker & DevOps",     category: "DevOps", difficulty: "intermediate", price: 59.99, isPublished: false, enrollmentCount: 0, rating: { average: 0, count: 0 }, tags: ["docker"], createdAt: new Date() }
]);

// 3. Modifier la ville d'un utilisateur ($set + notation pointée)
db.users.updateOne(
  { email: "alice.martin@email.com" },
  { $set: { "profile.city": "Lyon" } }
);

// 4. Incrémenter le compteur d'inscriptions d'un cours ($inc)
db.courses.updateOne(
  { title: "MongoDB pour Débutants" },
  { $inc: { enrollmentCount: 1 } }
);

// 5. Ajouter un skill à un utilisateur ($push)
db.users.updateOne(
  { email: "alice.martin@email.com" },
  { $push: { skills: "MongoDB" } }
);

// 6. Retirer un tag d'un cours ($pull)
db.courses.updateOne(
  { title: "MongoDB pour Débutants" },
  { $pull: { tags: "nosql" } }
);

// 7. Désactiver les utilisateurs inactifs depuis 6 mois (updateMany + $lt)
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
db.users.updateMany(
  { lastLoginAt: { $lt: sixMonthsAgo } },
  { $set: { isActive: false } }
);

// 8. Upsert — créer ou mettre à jour un utilisateur
db.users.updateOne(
  { email: "nouveau@email.com" },
  { $set: { firstName: "Nouveau", role: "student", isActive: true, createdAt: new Date() } },
  { upsert: true }
);

// 9. Supprimer une review par son id
const review = db.reviews.findOne();
db.reviews.deleteOne({ _id: review._id });

// 10. Supprimer toutes les inscriptions annulées
db.enrollments.deleteMany({ status: "cancelled" });


// ══════════════════════════════════════════════
// 2.2 — REQUÊTES DE SÉLECTION
// ══════════════════════════════════════════════

// 11. Cours entre 20€ et 80€ ($gte + $lte)
db.courses.find({ price: { $gte: 20, $lte: 80 } }).toArray();

// 12. Cours de catégorie "Database" ou "Web" ($in)
db.courses.find({ category: { $in: ["Database", "Web"] } }).toArray();

// 13. Cours dont la difficulté n'est PAS "advanced" ($ne)
db.courses.find({ difficulty: { $ne: "advanced" } }).toArray();

// 14. Utilisateurs actifs ET étudiants ($and)
db.users.find({ $and: [{ isActive: true }, { role: "student" }] }).toArray();

// 15. Cours gratuits OU note >= 4.5 ($or + $gte)
db.courses.find({ $or: [{ price: 0 }, { "rating.average": { $gte: 4.5 } }] }).toArray();

// 16. Reviews dont updatedAt existe et n'est pas null ($exists + $ne)
db.reviews.find({ updatedAt: { $exists: true, $ne: null } }).toArray();

// 17. Utilisateurs habitant à Paris (notation pointée)
db.users.find({ "profile.city": "Paris" }).toArray();

// 18. Cours publiés avec note >= 4 ($and explicite + $gte)
db.courses.find({ $and: [{ isPublished: true }, { "rating.average": { $gte: 4 } }] }).toArray();

// 19. Inscriptions ni "cancelled" ni "paused" ($nin)
db.enrollments.find({ status: { $nin: ["cancelled", "paused"] } }).toArray();

// 20. Afficher seulement titre et prix, sans _id (projection)
db.courses.find({}, { _id: 0, title: 1, price: 1 }).toArray();

// 21. Tous les champs utilisateurs SAUF le profil (projection exclusion)
db.users.find({}, { profile: 0 }).toArray();

// 22. Les 5 cours les mieux notés (sort + limit)
db.courses.find().sort({ "rating.average": -1 }).limit(5).toArray();

// 23. Cours triés par prix croissant (sort)
db.courses.find().sort({ price: 1 }).toArray();

// 24. Page 2 des cours — 10 par page (skip + limit)
db.courses.find().skip(10).limit(10).toArray();

// 25. Compter les cours publiés (countDocuments)
db.courses.countDocuments({ isPublished: true });


// ══════════════════════════════════════════════
// 2.3 — REQUÊTES MÉTIER
// ══════════════════════════════════════════════

// 26. Inscription : trouver user + cours, inscrire, mettre à jour les compteurs
const user   = db.users.findOne({ email: "clara.lefebvre@email.com" });
const course = db.courses.findOne({ title: "Vue.js 3 — Composition API" });

db.enrollments.insertOne({ userId: user._id, courseId: course._id, status: "active", enrolledAt: new Date() });
db.courses.updateOne({ _id: course._id }, { $inc: { enrollmentCount: 1 } });
db.users.updateOne({ _id: user._id }, { $inc: { totalCoursesEnrolled: 1 } });

// 27. Catalogue : cours Web, publiés, < 70€, note >= 4, triés par popularité, page 1
db.courses.find(
  { $and: [{ category: "Web" }, { isPublished: true }, { price: { $lt: 70 } }, { "rating.average": { $gte: 4 } }] },
  { _id: 0, title: 1, price: 1, "rating.average": 1 }
).sort({ enrollmentCount: -1 }).limit(10).toArray();

// 28. Progression : marquer une leçon complétée et recalculer le pourcentage
const enrollment = db.enrollments.findOne({ status: "active" });
const lesson     = db.lessons.findOne({ courseId: enrollment.courseId });
const courseP    = db.courses.findOne({ _id: enrollment.courseId });

db.enrollments.updateOne({ _id: enrollment._id }, { $push: { "progress.completedLessons": lesson._id } });

const updated    = db.enrollments.findOne({ _id: enrollment._id });
const percentage = Math.round((updated.progress.completedLessons.length / courseP.metadata.totalLessons) * 100);

db.enrollments.updateOne({ _id: enrollment._id }, { $set: { "progress.percentage": percentage } });

// 29. Cascade : supprimer un cours et toutes ses données liées
const toDelete = db.courses.findOne({ title: "Flutter — Dev Multiplateforme" });

db.courses.deleteOne({ _id: toDelete._id });
db.lessons.deleteMany({ courseId: toDelete._id });
db.reviews.deleteMany({ courseId: toDelete._id });
db.enrollments.updateMany({ courseId: toDelete._id }, { $set: { status: "cancelled" } });

// 30. Dashboard : infos utilisateur + inscriptions actives + derniers avis
const dashUser      = db.users.findOne({ email: "felix.garnier@email.com" }, { profile: 0 });
const enrollments   = db.enrollments.find({ userId: dashUser._id, status: "active" }).toArray();
const recentReviews = db.reviews.find({ userId: dashUser._id }).sort({ createdAt: -1 }).limit(3).toArray();

print(JSON.stringify({ user: dashUser, enrollments, reviews: recentReviews }, null, 2));