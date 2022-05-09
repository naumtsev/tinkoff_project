import base64
import typing

from flask import Flask, render_template, request

from app import config, models, workers
from app.db import db

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

submission_updater = workers.UsersSubmissionsUpdater(db)
info_updater = workers.UsersInfoUpdater(db)

submission_updater.start()
info_updater.start()


@app.route('/', methods=['GET'])
def index() -> typing.Any:
    with db.create_session() as session:
        problemsets = session.query(models.Problemset).all()
        session.expunge_all()
        return render_template('problemsets.html', problemsets=problemsets)


@app.route('/add/<user>', methods=['GET'])
def add_user(user) -> typing.Any:
    db.add_user(user)
    return 'OK'


@app.route('/users', methods=['GET'])
def users_get() -> typing.Any:
    with db.create_session() as session:
        users = session.query(models.User).all()
        session.expunge_all()
        return render_template('users.html', users=users)


@app.route('/create-problemset', methods=['GET', 'POST'])
def create_problemset():
    if request.method == 'GET':
        return render_template('create_problemset.html')
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        problems_strs = request.form.get('problems').split()
        image = request.files['image']
        image_base64 = str(base64.b64encode(image.stream.read()).decode())

        problems = []
        used_problems = {}

        for problem_str in problems_strs:
            contest_id = None
            problem_index = None

            for j in range(len(problem_str)):
                if not problem_str[j].isdigit():
                    contest_id = problem_str[0:j]
                    problem_index = problem_str[j:]
                    break

            if (contest_id, problem_index) not in used_problems:
                problems.append((contest_id, problem_index))
                used_problems[(contest_id, problem_index)] = True

        valid_problems = db.add_problemset(title, description, problems, image_base64)
        return str(valid_problems)


@app.route('/problemset/<int:problemset_id>', methods=['GET'])
def problemset_get(problemset_id):
    with db.create_session() as session:
        problemset = (
            session.query(models.Problemset)
            .filter(models.Problemset.id == problemset_id)
            .one_or_none()
        )

        if problemset is None:
            return 'Problemset does not exist'

        problems = problemset.problems
        problems_pos: typing.Dict[typing.Tuple[typing.Optional[str], str], int] = {}
        for i, problem in enumerate(problems):
            problems_pos[(problem.contest_id, problem.problem_index)] = i

        users: typing.List[models.User] = (
            session.query(models.User)
            .filter(models.User.user_type == models.UserType.PARTICIPANT)
            .all()
        )

        class UserRow:
            def __init__(self, handle: str, handle_color: str, count_problems: int):
                self.handle = handle
                self.handle_color = handle_color
                self.count_solved_problems = 0
                self.problem_list: typing.List[typing.Optional[models.Submission]] = [
                    None for _ in range(count_problems)
                ]

        users_rows = []

        for user in users:
            user_row = UserRow(
                user.handle, models.get_rank_color(user.rank), len(problems)
            )
            submissions: typing.List[models.Submission] = user.submissions
            for sub in submissions:
                if (sub.contest_id, sub.problem_index) not in problems_pos:
                    continue
                if sub.verdict == models.Verdict.OK:
                    user_row.problem_list[
                        problems_pos[(sub.contest_id, sub.problem_index)]
                    ] = sub
                    user_row.count_solved_problems += 1

            users_rows.append(user_row)

        users_rows.sort(key=lambda x: x.count_solved_problems, reverse=True)

        session.expunge_all()

        return render_template(
            'problemset.html', problemset=problemset, users_rows=users_rows
        )


@app.route('/update_users_submissions', methods=['GET'])
def update_subs() -> typing.Any:
    workers.UsersSubmissionsUpdater().update_users_submissions()
    return


@app.route('/update_users_info', methods=['GET'])
def update_users_info() -> typing.Any:
    workers.UsersInfoUpdater().update_users_info()
    return 'OK'
