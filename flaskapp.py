from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api, Resource, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)

employee_model = api.model('Employees', {
    'id': fields.Integer,
    'name': fields.String(attribute=lambda x: f'{x.fname} {x.lname}'),
    'salary': fields.Integer
})

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(30), nullable=True)
    lname = db.Column(db.String(30), nullable=True)
    salary = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f"{self.fname}-{self.lname}"

@api.route('/employees')
class EmployeeList(Resource):
    @api.marshal_with(employee_model)
    def get(self):
        employees = Employee.query.all()
        return employees

    @api.expect([employee_model])
    def post(self):
        data = request.json
        added_employees = []
        for employee_data in data:
            employee = Employee(fname=employee_data['name'].split(' ')[0], lname=employee_data['name'].split(' ')[1], salary=employee_data['salary'])
            db.session.add(employee)
            added_employees.append(employee)
        db.session.commit()
        return {'message': 'Employees added successfully', 'added_employees': len(added_employees)}, 201

@api.route('/employees/<int:id>')
class EmployeeItem(Resource):
    @api.marshal_with(employee_model)
    def get(self, id):
        employee = Employee.query.get(id)
        if employee:
            return employee
        else:
            api.abort(404, 'Employee not found')

    @api.expect(employee_model)
    def put(self, id):
        data = request.json
        employee = Employee.query.get(id)
        if not employee:
            api.abort(404, 'Employee not found')

        if 'name' in data:
            employee.fname = data['name'].split(' ')[0]
            employee.lname = data['name'].split(' ')[1]
        if 'salary' in data:
            employee.salary = data['salary']
        db.session.commit()
        return {'message': 'Employee updated successfully'}

    def delete(self, id):
        employee = Employee.query.get(id)
        if not employee:
            api.abort(404, 'Employee not found')

        db.session.delete(employee)
        db.session.commit()
        return {'message': 'Employee deleted successfully'}

if __name__ == '__main__':
    app.run(debug=True)
