#!/usr/bin/env python3

from flask import Flask, jsonify, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort
from sqlalchemy.exc import SQLAlchemyError

from models import db, Plant

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)

class PlantsList(Resource):

    def get(self):
        plants = [plant.to_dict() for plant in Plant.query.all()]
        return make_response(jsonify(plants), 200)

    def post(self):
        data = request.get_json()

        # Validate required fields
        if not data or not all(key in data for key in ['name', 'image', 'price']):
            abort(400, message="Missing required fields: name, image, price")

        try:
            new_plant = Plant(
                name=data['name'],
                image=data['image'],
                price=data['price'],
            )

            db.session.add(new_plant)
            db.session.commit()

            return make_response(new_plant.to_dict(), 201)
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error: {str(e)}")

class PlantsDetail(Resource):

    def get(self, id):
        plant = Plant.query.filter_by(id=id).first()

        if not plant:
            abort(404, message=f"Plant with id={id} not found")

        return make_response(plant.to_dict(), 200)

    def patch(self, id):
        data = request.get_json()

        try:
            plant = Plant.query.filter_by(id=id).first()

            if not plant:
                abort(404, message=f"Plant with id={id} not found")

            # Update fields based on data received
            if 'is_in_stock' in data:
                plant.is_in_stock = data['is_in_stock']

            db.session.commit()

            return make_response(plant.to_dict(), 200)
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error: {str(e)}")

    def delete(self, id):
        try:
            plant = Plant.query.filter_by(id=id).first()

            if not plant:
                abort(404, message=f"Plant with id={id} not found")

            db.session.delete(plant)
            db.session.commit()

            return make_response('', 204)
        except SQLAlchemyError as e:
            db.session.rollback()
            abort(500, message=f"Database error: {str(e)}")

# Assign resources to their respective routes
api.add_resource(PlantsList, '/plants')
api.add_resource(PlantsDetail, '/plants/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
