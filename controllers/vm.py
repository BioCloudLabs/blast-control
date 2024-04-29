from flask_smorest import Blueprint, abort
from flask.views import MethodView

blp = Blueprint("vm", __name__, description="VMs endpoint", url_prefix="/vm")

@blp.route("/test")
class TestVm(MethodView):
    def get(self):
        """
        API Endpoint to log in an user.

        :param data: User login data.
        :return: HTTP response with the login result. If login it's correct, return an access_token.
        """

        return {"message": "Hello World"}, 200
