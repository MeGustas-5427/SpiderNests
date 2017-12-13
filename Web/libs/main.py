# main.py
# Author:Lengyue
# manage users

from flask import Blueprint, render_template

main = Blueprint('main', __name__,
                        template_folder='templates')
@main.route("/")
def Index():
    return render_template("index.html")

@main.route("/admin/")
def AdminIndex():
    return render_template("main.html")

@main.route("/admin/codedit")
def Admincodedit():
    return render_template("codeedit.html")
