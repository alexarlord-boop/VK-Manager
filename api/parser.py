from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', required=True)
parser.add_argument('age', required=True)
parser.add_argument('position', required=True)
parser.add_argument('email', required=True)


job_parser = reqparse.RequestParser()
job_parser.add_argument('job', required=True)
job_parser.add_argument('team_leader', required=True)
job_parser.add_argument('work_size', required=True)
job_parser.add_argument('collaborators', required=True)
job_parser.add_argument('is_finished', required=True)
