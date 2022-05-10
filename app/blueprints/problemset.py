import base64
import typing

from flask import Blueprint, redirect, render_template, request, session

from app import models, utils
from app.db import db

problemset_blueprint = Blueprint('problemset', __name__)


class ProblemsetForm:
    def __init__(self) -> None:
        self.id = ''
        self.title = ''
        self.description = ''
        self.problems_str = ''


@problemset_blueprint.route('/problemset', methods=['GET'])
@problemset_blueprint.route('/problemset/<int:problemset_id>', methods=['GET'])
def create_or_update_problemset_get(
    problemset_id: typing.Optional[int] = None,
) -> typing.Any:
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
                    [
                        problem.contest_id + problem.problem_index
                        for problem in problemset.problems
                    ]
                )
            else:
                session['message'] = 'Invalid problemset id'
                return redirect('/')

    return render_template('create_or_update_problemset.html', form=form)


@problemset_blueprint.route('/problemset', methods=['POST'])
@problemset_blueprint.route('/problemset/<int:problemset_id>', methods=['POST'])
def create_or_update_problemset_post(
    problemset_id: typing.Optional[int] = None,
) -> typing.Any:
    title = request.form.get('title', '')
    description = request.form.get('description', '')
    problems = utils.parse_problems(request.form.get('problems', ''))

    problemset: models.Problemset = models.Problemset(
        title=title, description=description
    )
    with db.create_session() as db_session:
        if problemset_id is None:

            status_word = 'created'
            image = request.files['image']

            image_base64 = str(base64.b64encode(image.stream.read()).decode())
            problemset.image = image_base64

        else:
            problemset_or_none = db.get_problemset(problemset_id, db_session)

            if problemset_or_none is None:
                session[
                    'message'
                ] = f'Problemset with id "{problemset_id}" does not exist'
                return redirect('/')
            problemset = problemset_or_none
            status_word = 'updated'
            problemset.title = title
            problemset.description = description
            problemset.problems.clear()
        valid_problems = db.add_or_update_problemset(problemset, problems, db_session)
        session['message'] = f'Problemset is {status_word}. Problems: ' + ', '.join(
            [
                contest_id + problem_index
                for (contest_id, problem_index) in valid_problems
            ]
        )
        return redirect('/')


class StandingsRow:
    def __init__(self, handle: str, handle_color: str, count_problems: int):
        self.handle = handle
        self.handle_color = handle_color
        self.count_solved_problems = 0
        self.problem_list: typing.List[typing.Optional[models.Submission]] = [
            None for _ in range(count_problems)
        ]


@problemset_blueprint.route(
    '/problemset/<int:problemset_id>/standings', methods=['GET']
)
def problemset_get(problemset_id: int) -> typing.Any:
    with db.create_session() as db_session:
        problemset = db.get_problemset(problemset_id, db_session)

        if problemset is None:
            session['message'] = 'Problemset does not exist'
            return redirect('/')

        problems = problemset.problems
        problems_pos: typing.Dict[typing.Tuple[typing.Optional[str], str], int] = {}

        for i, problem in enumerate(problems):
            problems_pos[(problem.contest_id, problem.problem_index)] = i

        users: typing.List[models.User] = db.get_users(
            [models.UserType.PARTICIPANT], db_session
        )

        users_rows = []

        for user in users:
            user_row = StandingsRow(
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

            for problem in user_row.problem_list:
                if problem is not None:
                    user_row.count_solved_problems += 1

            users_rows.append(user_row)

        users_rows.sort(key=lambda x: x.count_solved_problems, reverse=True)

        db_session.expunge_all()

        return render_template(
            'problemset.html', problemset=problemset, users_rows=users_rows
        )
