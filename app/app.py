import base64
import typing

from flask import Flask, redirect, render_template, request, session, url_for

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
    message = session.get('message', '')
    session['message'] = ''

    with db.create_session() as db_session:
        problemsets = db_session.query(models.Problemset).all()
        db_session.expunge_all()
        return render_template(
            'problemsets.html', problemsets=problemsets, message=message
        )


@app.route('/add/<user>', methods=['GET'])
def add_user(user) -> typing.Any:
    db.add_user(user)
    return 'OK'


@app.route('/users', methods=['GET'])
def users_get() -> typing.Any:
    with db.create_session() as session:
        users = session.query(models.User).all()
        session.expunge_all()
        users_rows = []

        class UserRow:
            def __init__(
                self, handle: str, handle_color: str, user_type: models.UserType
            ):
                self.handle = handle
                self.handle_color = handle_color
                self.user_type = user_type

        for user in users:
            users_rows.append(
                UserRow(user.handle, models.get_rank_color(user.rank), user.user_type)
            )
        return render_template('users.html', users=users_rows, UserType=models.UserType)


@app.route('/change_user_type/<handle>', methods=['POST'])
def change_user_type_post(handle) -> typing.Any:
    with db.create_session() as db_session:
        user = (
            db_session.query(models.User)
            .filter(models.User.handle == handle)
            .one_or_none()
        )
        if user is None:
            session['message'] = 'User is not registered'
            return redirect(url_for('index'))

        new_user_type = int(
            request.form.get('user_type', models.UserType.PARTICIPANT.value)
        )
        user.user_type = models.UserType(new_user_type)
        db_session.merge(user)
        return redirect('/users')


@app.route('/add-user', methods=['POST'])
def add_user_post() -> typing.Any:
    handle = request.form['handle']
    db.add_user(handle)
    return redirect('/users')


@app.route('/problemset', methods=['GET', 'POST'])
@app.route('/problemset/<int:problemset_id>', methods=['GET', 'POST'])
def problemset_handler(problemset_id: int = None):
    if request.method == 'GET':
        class ProblemsetForm:
            def __init__(self):
                self.id = ''
                self.title = ''
                self.description = ''
                self.problems_str = ''

        form = ProblemsetForm()

        if problemset_id is not None:
            with db.create_session() as db_session:
                problemset = (
                    db_session.query(models.Problemset)
                    .filter(models.Problemset.id == problemset_id)
                    .one_or_none()
                )
                if problemset:
                    form.id = str(problemset.id)
                    form.title = problemset.title
                    form.description = problemset.description
                    form.problems_str = ' '.join(
                        list(
                            map(
                                lambda x: x.contest_id + x.problem_index,
                                problemset.problems,
                            )
                        )
                    )
                else:
                    session['message'] = 'Invalid problemset id'
                    return redirect('/')
        return render_template('create_or_edit_problemset.html', form=form)
    elif request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        problems_strs = request.form.get('problems').split()

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

        problemset = models.Problemset(title=title, description=description)

        with db.create_session() as db_session:
            if problemset_id is None:
                image = request.files['image']
                image_base64 = str(base64.b64encode(image.stream.read()).decode())
                problemset.image = image_base64
            else:
                    problemset = (
                        db_session.query(models.Problemset)
                            .filter(models.Problemset.id == problemset_id)
                            .one_or_none()
                    )
                    problemset.title = title
                    problemset.description = description
                    problemset.problems.clear()

            valid_problems = db.add_or_update_problemset(problemset, problems, db_session)
            return str(valid_problems)


@app.route('/problemset/<int:problemset_id>/standings', methods=['GET'])
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
def update_users_submissions() -> typing.Any:
    workers.UsersSubmissionsUpdater().update_users_submissions()
    session['message'] = 'Users submissions updated'
    return redirect(url_for('index'))


@app.route('/update_users_info', methods=['GET'])
def update_users_info() -> typing.Any:
    workers.UsersInfoUpdater().update_users_info()
    session['message'] = 'Users info updated'
    return redirect(url_for('index'))
