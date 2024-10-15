from mongoengine import Document, StringField, BooleanField

class Todo(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    completed = BooleanField(default=False)

    meta = {'collection': 'todos'}

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "completed": self.completed
        }