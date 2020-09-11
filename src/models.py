from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    groups = db.relationship('Group', secondary="links", lazy='subquery',
        backref=db.backref('contacts', lazy=True))

    def __init__(self, full_name, email, address, phone):
        """ crea y devuelve una instancia de esta clase """
        self.full_name = full_name
        self.email = email
        self.address = address
        self.phone = phone
    
    @classmethod
    def register(cls, full_name, email, address, phone):
        """ normaliza insumos, crea un objeto de la clase Contact
            con esos insumos y devuelve la instancia creada
        """
        new_contact = cls(
            full_name,
            email,
            address,
            phone
        )
        return new_contact

    def serialize(self):
        """ devuelve un diccionario del objeto """
        groups_list = self.groups
        list_id = []
        for group in groups_list:
            list_id.append(group.name)
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "address": self.address,
            "phone": self.phone,
            "groups": list_id
        }
    
    def update_contact(self, dictionary):
        """ actualiza propiedades del donante segun 
            contenido del diccionario 
        """
        for (key, value) in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return True

#tabla que relaciona muchos con muchos a contact y group 
link = db.Table('links',
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'), primary_key=True),
    db.Column('contact_id', db.Integer, db.ForeignKey('contact.id'), primary_key=True)
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def create_group(cls, name):
        new_group = cls(
            name
        )
        return new_group

    def serialize(self):
        contacts_list = self.contacts
        list_id = []
        for contact in contacts_list:
            list_id.append(contact.full_name)
        return{
        "id": self.id,
        "name": self.name,
        "contacts": list_id
        }
    
    def update_group(self, dictionary):
        """ actualiza propiedades del donante segun 
            contenido del diccionario 
        """
        for (key, value) in dictionary.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return True

