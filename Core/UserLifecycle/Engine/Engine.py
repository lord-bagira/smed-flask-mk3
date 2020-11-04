from Core.UserLifecycle.StorageModels import *
from Core.UserLifecycle.IO_Schemas import *
from config import *

from sqlalchemy import exc
import smtplib, ssl

class UserLifeCycleController:
    def __init__(self):
        pass

    def get_all_users( self ):
        users = UserModel.query.all()
        return EResp( STATUS.SUCCESS, "Dumping ALL users.", user_schema.dumps( users ) )

    def get_user_by_uid( self, user_id ):
        user = UserModel.query.filter_by( id=user_id ).first()
        return EResp( STATUS.SUCCESS, "Found the user.", user_schema.dumps( [ user ] ) )

    def get_user_by_username( self, username ):
        user = UserModel.query.filter_by( username=username ).first()
        return EResp( STATUS.SUCCESS, "Found the user.", user_schema.dumps( [ user ] ) )

    def create_user( self, username, email, password ):
        user = UserModel( username=username, email=email, password=password )
        db.session.add(user)

        try:
            db.session.commit()
        except exc.IntegrityError as err:
            db.session.rollback()
            if err.orig.args[0] == 1062:
                return EResp( STATUS.DATA_CONFLICT, "User already exists.", [ user ] )
            else:
                return EResp( STATUS.FAILURE, "Couldn't create the user.  Report this.", user_schema.dumps( [ user ] ) )

        self.require_email_validation( user.email )

        return EResp( STATUS.SUCCESS, "User successfully created.", user_schema.dumps( [ user ] ) )

    def deactivate_user( self, user_id ):
        user = UserModel.query.get( user_id )
        if user.active:
            user.active = False
        else:
            return EResp( STATUS.DATA_CONFLICT, "User is already disabled.", user_schema.dumps( [ user ] ) )

        db.session.commit()

        return EResp( STATUS.SUCCESS, "User disabled.", user_schema.dumps( [ user ] ) )


    def activate_user(self, user_id ):
        user = UserModel.query.get( user_id )
        if not user.active:
            user.active = True
        else:
            return EResp( STATUS.DATA_CONFLICT, "User is already active.", user_schema.dumps( [ user ] ) )

        db.session.commit()

        return EResp( STATUS.SUCCESS, "User activated.", user_schema.dumps( [ user ] ) )

    def require_email_validation( self, email ):
        user_validation = EmailValidationModel( email=email )

        db.session.add( user_validation )
        try:
            db.session.commit()
        except exc.IntegrityError as err:
            db.session.rollback()
            if err.orig.args[0] == 1062:
                return EResp(STATUS.DATA_CONFLICT, "There was a data conflict.", user_validation )
            else:
                return EResp(STATUS.FAILURE, "Couldn't create the user validation.  Report this.", user_validation )

        self.send_validation_email( email, user_validation.code )

        return EResp( STATUS.SUCCESS, "Email validation is now required for that email address.", user_validation )

    def validate_email_code(self, code):
        # get a validation entry for that code
        validation_entry = EmailValidationModel.query.filter_by( code=code ).first()

        if validation_entry is not None:
            email = validation_entry.email

            # delete the entry in the validation table
            db.session.delete( validation_entry )

            # set the associated user to active
            user = UserModel.query.filter_by( email=email ).first()
            user.verified = True
            db.session.commit()

        else:
            return EResp( STATUS.FAILURE, "Invalid code." )

        return EResp( STATUS.SUCCESS, "The email '{0}' has now been verified.".format( email ), user_schema.dumps( [ user ] ) )

    def send_validation_email(self, recipient, code):
        user = UserModel.query.filter_by( email=recipient ).first()

        url = "{0}/user/verify/{1}".format(
            BASE_API_MASK,
            code
        )

        message = """
        Dear {0},
        
        Thanks for signing up on {1}.
        
        To get started, you'll need to verify your email address.
        
        Your activation URL is:
        {2}
        
        By clicking the above link, your email will be verified.
        
        Sincerely,
        
        The {1} Team.
        """.format(
            user.username,
            SITE_NAME,
            url
        )

        # create a secure SSL context
        # whatever that means
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL( SMTP_SERVER, SMTP_PORT, context=context ) as server:
            server.login( SMTP_USER, SMTP_PASSWORD )
            server.sendmail( email_sender, recipient, message )
