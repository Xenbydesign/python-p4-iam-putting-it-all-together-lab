from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from config import db, bcrypt


class User(db.Model, SerializerMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    serialize_rules = (
        "-recipes.user",
        "-_password_hash",
    )

    recipes = db.relationship(
        "Recipe", back_populates="user", cascade="all, delete-orphan"
    )

    @hybrid_property
    def password(self):
        raise AttributeError("Passwords cannot be inspected")

    @password.setter
    def password(self, password):
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        self._password_hash = hashed_password

    def authenticate(self, password_to_check):
        return bcrypt.check_password_hash(self._password_hash, password_to_check)


class Recipe(db.Model, SerializerMixin):
    __tablename__ = "recipes"
    __table_args__ = (db.CheckConstraint("length(instructions) >= 50"),)
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))

    user = db.relationship("User", back_populates="recipes")
