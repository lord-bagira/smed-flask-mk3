from flask_restplus import Namespace, Resource
from flask import request
from Core.UserLifecycle.Schemas import *
from Core.UserLifecycle.Models import *
from sqlalchemy import exc

user_namespace = Namespace( 'user', description="User management functions." )

@user_namespace.route('', methods=['GET', 'POST'])
@user_namespace.route('/username/<username>', methods=['GET'])
@user_namespace.route('/id/<user_id>', methods=['GET', 'DELETE'])
class UserRoute(Resource):
    def get( self, username=None, user_id=None ):
        # retrieve one or all users
        if username is not None:
            users = UserModel.query.filter_by( username=username )
        elif user_id is not None:
            users = UserModel.query.filter_by( id=user_id )
        else:
            users = UserModel.query.all()

        return user_schema.dump( users )

    @user_namespace.expect( user_creation_schema( user_namespace ) )
    @user_namespace.response(201, 'User Created.')
    @user_namespace.response(409, 'User already exists.')
    def post(self):
        # create a user

        json_data = request.json

        user = UserModel(
            username=json_data['username'],
            email=json_data['email'],
            password=json_data['password']
        )
        db.session.add( user )

        try:
            db.session.commit()
        except exc.IntegrityError as err:
            db.session.rollback()
            if err.orig.args[0] == 1062:
                return user_schema.dump( [ user ] ), 409

        return user_schema.dump( [ user ] ), 201

    @user_namespace.response(204, 'User has been disabled.')
    @user_namespace.response(409, 'User is already inactive.')
    def delete( self, user_id ):
        # disable a user

        user = UserModel.query.get( user_id )
        if user.active:
            user.active = False
        else:
            return user_schema.dump( [ user ] ), 409

        db.session.commit()

        return user_schema.dump( [ user ] ), 204