import typing


def parse_problems(problems_str: str) -> typing.List[typing.Tuple[str, str]]:
    problems = []
    taked_problems = {}

    for problem_str in problems_str.split():
        contest_id = None
        problem_index = None
        for j, ch in enumerate(problem_str):
            if not ch.isdigit():
                contest_id = problem_str[0:j]
                problem_index = problem_str[j:]
                break

        if contest_id and problem_index:
            problem = (contest_id, problem_index)
            if problem not in taked_problems:
                problems.append(problem)
                taked_problems[problem] = True
    return problems
