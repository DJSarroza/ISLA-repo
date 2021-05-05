from flask_app import db
import datetime

from flask_app.models import UserActivePlanners

existing_planner_session = UserActivePlanners.query.filter_by(status="IN_PROGRESS").update(dict(status="FAILED", date_end=datetime.datetime.utcnow()))
db.session.commit()

