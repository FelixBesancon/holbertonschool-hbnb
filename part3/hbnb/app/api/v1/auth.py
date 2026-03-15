from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('auth', description='Authentication operations')

# Model for input validation
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})


@api.route('/login')
class Login(Resource):
    """
    Resource handling user authentication and JWT token generation.
    """
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        # Get the email and password from the request payload

        # Step 1: Retrieve the user based on the provided email
        user = facade.get_user_by_email(credentials['email'])

        # Step 2: Check if the user exists and the password is correct
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Step 3: Create a JWT token with the user's id and is_admin flag
        access_token = create_access_token(
            identity=str(user.id),  # only user ID goes here
            additional_claims={"is_admin": user.is_admin}  # extra info here
        )

        # Step 4: Return the JWT token to the client
        return {'access_token': access_token}, 200


@api.route('/protected')
class ProtectedResource(Resource):
    """
    Example protected resource accessible only with a valid JWT token.
    """
    @jwt_required()
    def get(self):
        """
        Access a protected endpoint requiring a valid JWT token.

        This endpoint demonstrates how to retrieve the current user's identity
        and additional claims from the JWT token. If the authenticated user has
        administrative privileges, the response includes that information.

        Returns:
            tuple:
                - dict: Message containing the authenticated user's identity
                - int: HTTP status code
        """
        print("jwt------")
        print(get_jwt_identity())
        current_user = get_jwt_identity()
        # Retrieve the user's identity from the token
        # if you need to see if the user is an admin or not,
        # you can access additional claims using get_jwt() :
        # addtional claims = get_jwt()
        # additional claims["is_admin"] -> True or False
        claims = get_jwt()
        if claims["is_admin"]:
            return {'message': f'Hello, user {current_user}, admin: true'}, 200
        return {'message': f'Hello, user {current_user}'}, 200
