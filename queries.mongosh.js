use("learnhub");

// ══════════════════════════════════════════════
// 2.1 — CRUD
// ══════════════════════════════════════════════

// 1. Insérer un nouvel utilisateur étudiant
db.users.insertOne({
  firstName: "Léa", lastName: "Dupuis", email: "lea.dupuis@email.com",
  role: "student",
  profile: { bio: "Étudiante en développement web", avatar: "https://i.pravatar.cc/150?img=25", city: "Paris", country: "France" },
  skills: ["HTML", "CSS"],
  isActive: true, totalCoursesEnrolled: 0,
  createdAt: new Date(), lastLoginAt: new Date()
});

// 2. Insérer 3 nouveaux cours en une seule opération
db.courses.insertMany([
  { title: "TypeScript pour Débutants", description: "Apprenez TypeScript de zéro.", category: "Web", difficulty: "beginner", price: 29.99, tags: ["typescript","javascript"], metadata: { duration: 600, totalLessons: 8, language: "fr" }, rating: { average: 0, count: 0 }, isPublished: false, enrollmentCount: 0, createdAt: new Date(), updatedAt: new Date() },
  { title: "GraphQL & Apollo",          description: "Construisez des APIs GraphQL.",  category: "Web", difficulty: "intermediate", price: 59.99, tags: ["graphql","apollo","api"], metadata: { duration: 900, totalLessons: 10, language: "fr" }, rating: { average: 0, count: 0 }, isPublished: false, enrollmentCount: 0, createdAt: new Date(), updatedAt: new Date() },
  { title: "Terraform & IaC",           description: "Infrastructure as Code avec Terraform.", category: "DevOps", difficulty: "intermediate", price: 69.99, tags: ["terraform","iac","devops"], metadata: { duration: 1000, totalLessons: 12, language: "fr" }, rating: { average: 0, count: 0 }, isPublished: false, enrollmentCount: 0, createdAt: new Date(), updatedAt: new Date() }
]);

// 3. Modifier la ville dans le profil d'un utilisateur (notation pointée + $set)
db.users.updateOne(
  { email: "alice.martin@email.com" },
  { $set: { "profile.city": "Lyon" } }
);

// 4. Incrémenter le compteur d'inscriptions d'un cours de 1 ($inc)
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

// 7. Désactiver les utilisateurs inactifs depuis plus de 6 mois (updateMany + $lt)
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
db.users.updateMany(
  { lastLoginAt: { $lt: sixMonthsAgo } },
  { $set: { isActive: false } }
);

// 8. Créer ou mettre à jour le profil d'un utilisateur (upsert)
db.users.updateOne(
  { email: "nouveau.user@email.com" },
  { $set: { firstName: "Nouveau", lastName: "User", email: "nouveau.user@email.com", role: "student", isActive: true, totalCoursesEnrolled: 0, "profile.city": "Paris", createdAt: new Date(), lastLoginAt: new Date() } },
  { upsert: true }
);

// 9. Supprimer une review par son identifiant
const reviewToDelete = db.reviews.findOne();
db.reviews.deleteOne({ _id: reviewToDelete._id });

// 10. Supprimer toutes les inscriptions "cancelled"
db.enrollments.deleteMany({ status: "cancelled" });

// ══════════════════════════════════════════════
// 2.2 — REQUÊTES DE SÉLECTION
// ══════════════════════════════════════════════

// 11. Cours entre 20€ et 80€ ($gte / $lte)
db.courses.find({ price: { $gte: 20, $lte: 80 } }).toArray();

// 12. Cours dans les catégories "Database" ou "Web" ($in)
db.courses.find({ category: { $in: ["Database", "Web"] } }).toArray();

// 13. Cours dont la difficulté n'est PAS "advanced" ($ne)
db.courses.find({ difficulty: { $ne: "advanced" } }).toArray();

// 14. Utilisateurs actifs ET étudiants ($and)
db.users.find({ $and: [{ isActive: true }, { role: "student" }] }).toArray();

// 15. Cours gratuits OU note moyenne ≥ 4.5 ($or + $gte)
db.courses.find({ $or: [{ price: 0 }, { "rating.average": { $gte: 4.5 } }] }).toArray();

// 16. Reviews dont updatedAt existe et n'est pas null ($exists + $ne)
db.reviews.find({ updatedAt: { $exists: true, $ne: null } }).toArray();

// 17. Utilisateurs habitant à Paris (notation pointée)
db.users.find({ "profile.city": "Paris" }).toArray();

// 18. Cours publiés avec note ≥ 4 ($and explicite + $gte)
db.courses.find({ $and: [{ isPublished: true }, { "rating.average": { $gte: 4 } }] }).toArray();

// 19. Inscriptions ni "cancelled" ni "paused" ($nin)
db.enrollments.find({ status: { $nin: ["cancelled", "paused"] } }).toArray();

// 20. Titre et prix des cours uniquement, sans _id (projection)
db.courses.find({}, { _id: 0, title: 1, price: 1 }).toArray();

// 21. Tous les champs des utilisateurs SAUF le profil (projection exclusion)
db.users.find({}, { profile: 0 }).toArray();

// 22. Les 5 cours les mieux notés (sort + limit)
db.courses.find().sort({ "rating.average": -1 }).limit(5).toArray();

// 23. Tous les cours triés par prix croissant
db.courses.find().sort({ price: 1 }).toArray();

// 24. Page 2 des cours — 10 résultats par page (skip + limit)
const page = 2;
const pageSize = 10;
db.courses.find().skip((page - 1) * pageSize).limit(pageSize).toArray();

// 25. Compter le nombre total de cours publiés
db.courses.countDocuments({ isPublished: true });

// ══════════════════════════════════════════════
// 2.3 — REQUÊTES MÉTIER
// ══════════════════════════════════════════════

// 26. Inscription : vérifier, inscrire, mettre à jour les compteurs
const userToEnroll  = db.users.findOne({ email: "clara.lefebvre@email.com" });
const courseToEnroll = db.courses.findOne({ title: "Vue.js 3 — Composition API" });

const alreadyEnrolled = db.enrollments.findOne({
  userId: userToEnroll._id,
  courseId: courseToEnroll._id
});

if (!alreadyEnrolled) {
  db.enrollments.insertOne({
    userId: userToEnroll._id,
    courseId: courseToEnroll._id,
    status: "active",
    progress: { completedLessons: [], percentage: 0, lastAccessedAt: new Date() },
    payment: { amount: courseToEnroll.price, method: "card", paidAt: new Date() },
    enrolledAt: new Date(),
    completedAt: null
  });
  db.courses.updateOne({ _id: courseToEnroll._id }, { $inc: { enrollmentCount: 1 } });
  db.users.updateOne({ _id: userToEnroll._id }, { $inc: { totalCoursesEnrolled: 1 } });
  print("✅ Inscription réussie !");
} else {
  print("⚠️  Déjà inscrit !");
}

// 27. Catalogue : cours Web, publiés, < 70€, note ≥ 4, triés par popularité, page 1
db.courses.find(
  { $and: [{ category: "Web" }, { isPublished: true }, { price: { $lt: 70 } }, { "rating.average": { $gte: 4 } }] },
  { _id: 0, title: 1, price: 1, "rating.average": 1 }
).sort({ enrollmentCount: -1 }).skip(0).limit(10).toArray();

// 28. Progression : marquer une leçon comme complétée et recalculer le pourcentage
const enrollment = db.enrollments.findOne({ status: "active" });
const lesson      = db.lessons.findOne({ courseId: enrollment.courseId });
const course      = db.courses.findOne({ _id: enrollment.courseId });

db.enrollments.updateOne(
  { _id: enrollment._id },
  { $push: { "progress.completedLessons": lesson._id } }
);

const updated    = db.enrollments.findOne({ _id: enrollment._id });
const percentage = Math.min(100, Math.round((updated.progress.completedLessons.length / course.metadata.totalLessons) * 100));

db.enrollments.updateOne(
  { _id: enrollment._id },
  { $set: { "progress.percentage": percentage, "progress.lastAccessedAt": new Date() } }
);

if (percentage >= 100) {
  db.enrollments.updateOne(
    { _id: enrollment._id },
    { $set: { status: "completed", completedAt: new Date() } }
  );
}
print("✅ Progression mise à jour : " + percentage + "%");

// 29. Cascade : supprimer un cours et toutes ses données liées
const courseToDelete = db.courses.findOne({ title: "Flutter — Dev Multiplateforme" });

db.courses.deleteOne({ _id: courseToDelete._id });
db.lessons.deleteMany({ courseId: courseToDelete._id });
db.reviews.deleteMany({ courseId: courseToDelete._id });
db.enrollments.updateMany({ courseId: courseToDelete._id }, { $set: { status: "cancelled" } });
print("✅ Cours supprimé avec cascade !");

// 30. Dashboard : infos utilisateur, inscriptions actives, derniers avis
const dashUser          = db.users.findOne({ email: "felix.garnier@email.com" }, { profile: 0 });
const activeEnrollments = db.enrollments.find({ userId: dashUser._id, status: "active" }).toArray();
const recentReviews     = db.reviews.find({ userId: dashUser._id }).sort({ createdAt: -1 }).limit(3).toArray();

print(JSON.stringify({ user: dashUser, enrollments: activeEnrollments, reviews: recentReviews }, null, 2));
