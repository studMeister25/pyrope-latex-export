
import os
import subprocess
import sys
import unittest
from uuid import uuid4
from datetime import datetime
import shutil

import nbformat
from nbconvert import LatexExporter

from pyrope import examples, ExercisePool, ExerciseRunner
from pyrope.core import CLIParser, ParametrizedExercise
from pyrope.formatters import TemplateFormatter
from pyrope.frontends import ConsoleFrontend, LaTeXGenerator


parser = CLIParser(prog='python3 -m pyrope')
args = parser.parse_args()

pool = ExercisePool()
if not args.filepaths:
    pool.add_exercises_from_module(examples)
else:
    for path in args.filepaths:
        pool.add_exercises_from_file(path)

if args.subcommand == 'run':

    if args.frontend == 'console':
        for exercise in pool:
            runner = ExerciseRunner(exercise, debug=args.debug)
            frontend = ConsoleFrontend()
            runner.set_frontend(frontend)
            frontend.set_runner(runner)
            runner.run()
            pexercise = runner.pexercise
            print('trivial input:', pexercise.trivial_input)
            print('dummy input:', pexercise.dummy_input)
            print('the solution:', pexercise.the_solution)
            print('a solution:', pexercise.a_solution)
            print('solution:', pexercise.solution)
            print('answers:', pexercise.answers)
            print('scores:', {
                ifield: '{}/{}'.format(
                    pexercise.scores[ifield], pexercise.max_scores[ifield]
                )
                for ifield in pexercise.ifields
            })
            print(
                f'total score: '
                f'{pexercise.total_score}/{pexercise.max_total_score}'
            )
            print('score weights:', pexercise.score_weights)
            print('correct:', pexercise.correct)

    if args.frontend == 'jupyter':
        nb = nbformat.v4.new_notebook()
        filename = str(uuid4())
        file = f'{filename}.ipynb'
        try:
            assert os.path.isdir(args.path)
        except AssertionError:
            raise NotADirectoryError(
                f'{args.path} does not exist or is not a directory.'
            )
        else:
            file = os.path.join(args.path, file)
        code = (
            'import pyrope\n\n'
            f'%pyrope run {" ".join(args.filepaths)}'
            f'{" --debug" if args.debug else ""}'
        )
        nb['exercise_cells'] = [nbformat.v4.new_code_cell(code)]
        nb.metadata['pyrope'] = {'autoexecute': True}
        nb = nbformat.validator.normalize(nb)[1]
        with open(file, 'w') as f:
            nbformat.write(nb, f)

        jupyter_server = subprocess.Popen(['jupyter', 'notebook', file])
        try:
            jupyter_server.wait()
        except KeyboardInterrupt:
            pass

        # Cleanup
        while True:
            try:
                try:
                    os.remove(file)
                except FileNotFoundError:
                    pass
                checkpoint_path = os.path.join(
                    args.path,
                    '.ipynb_checkpoints'
                )
                try:
                    checkpoint_file = os.path.join(
                        checkpoint_path,
                        f'{filename}-checkpoint.ipynb'
                    )
                    os.remove(checkpoint_file)
                except FileNotFoundError:
                    pass
                if (
                    os.path.isdir(checkpoint_path) and
                    not os.listdir(checkpoint_path)
                ):
                    os.rmdir(checkpoint_path)
                break
            except KeyboardInterrupt:
                print('Please wait for cleanup.')

if args.subcommand == 'test':
    test_cases = [
        test_case
        for exercise in pool
        for test_case in exercise.test_cases()
    ]
    suite = unittest.TestSuite(test_cases)
    runner = unittest.TextTestRunner()
    test_result = runner.run(suite)
    if not test_result.wasSuccessful():
        sys.exit(1)

if args.subcommand == 'generate':
    print('Generating LaTeX')

    try:
        assert os.path.isdir(args.path)
    except AssertionError:
        raise NotADirectoryError(
            f'{args.path} does not exist or is not a directory.'
        )

    # Create test folder
    test_name = args.testname
    test_path = os.path.join(args.path, test_name)
    try:
        os.mkdir(test_path)
        print(f"- Directory '{test_path}' created successfully.")
    except FileExistsError:
        print(f"- Directory '{test_path}' already exists; generation aborted")
        sys.exit(1)

    file = 'generator.ipynb'
    
    #file = os.path.join(args.path, 'generator.ipynb')

    amount = args.amount
    includes_solutions = args.solutions
    num_of_hints = args.hints

    for test_num in range(1, amount+1):

        print(f'\n- File {test_num} of {amount}')

        latex_generator = LaTeXGenerator(includes_solutions, num_of_hints)
        for exercise in pool:
            pexercise = ParametrizedExercise(exercise)
            latex_generator.generate_cells_of_exercise(pexercise)
        
        (exercise_cells, solution_cells) = latex_generator.get_notebook_cells()

        if includes_solutions:
            cycles = 2
        else:
            cycles = 1
        
        for cycle_num in range(0,cycles):
            nb = nbformat.v4.new_notebook()
            if cycle_num == 1:
                print('\tCollecting solutions')
                nb['cells'] = solution_cells
            else:
                nb['cells'] = exercise_cells
            nb = nbformat.validator.normalize(nb)[1]
            with open(file, 'w') as f:
                nbformat.write(nb, f)

            # widgets = pexercise.model.widgets
            # parameters = pexercise.parameters
            # for widget in widgets:
            #     #print(widget.ifield_name)
            #     print(widget.toLaTeX())

            #os.system(f'jupyter nbconvert --to latex {file} >/dev/null 2>/dev/null')
            latex_exporter = LatexExporter(template_name="latex")
            (body, resources) = latex_exporter.from_notebook_node(nb)

            texFile = 'generator.tex'
            with open(texFile, 'w') as f:
                f.write(body)

            print('\tInserting into template')

            # try:
            #     assert os.path.isdir(args.path)
            # except AssertionError:
            #     raise NotADirectoryError(
            #         f'{args.path} does not exist or is not a directory.'
            #     )
            # else:
            #     texFile = os.path.join(args.path, texFile)

            if not args.template:
                templateFile = 'latexTemplate.tex'
            else:
                templateFile = args.template
            # try:
            #     assert os.path.isdir(args.path)
            # except AssertionError:
            #     raise NotADirectoryError(
            #         f'{args.path} does not exist or is not a directory.'
            #     )
            # else:
            #     templateFile = os.path.join(args.path, templateFile)

            if cycle_num == 1:
                test_file = f'{test_path}/{test_name}-SOLUTION-{test_num :03d}.tex'
            else:
                test_file = f'{test_path}/{test_name}-{test_num :03d}.tex'

            try:
                with open(texFile, "r") as tex, open(templateFile, "r") as template, open(test_file, "w") as result:
                    resultLines = []
                    templateLines = template.readlines()
                    templateLineCounter = 0
                    while not templateLines[templateLineCounter].__contains__("<<exercises>>"):
                        resultLines.append(templateLines[templateLineCounter])
                        templateLineCounter += 1
                    
                    texLines = tex.readlines()
                    foundBegin = False
                    for line in texLines:
                        if line.__contains__("\\PyRopeExercise{"):
                            foundBegin = True
                        if line.__contains__("% Add a bibliography block to the postdoc"):
                            foundBegin = False
                            break
                        if foundBegin:
                            resultLines.append(line)
                    
                    templateLineCounter += 1
                    while templateLineCounter < templateLines.__len__():
                        resultLines.append(templateLines[templateLineCounter])
                        templateLineCounter += 1
                    
                    result.writelines(resultLines)
                    result.close()
                
            except FileNotFoundError as fnfe:
                print(f"The file {fnfe.filename} was not found.")
            except IOError as ioe:
                print(f"An error occurred while reading the file {ioe.filename}.")
            
        if test_num == 1 and not args.template:
            shutil.copytree('assets', test_path + '/assets')

    # try:
    #     os.remove(file)
    #     os.remove(texFile)
    # except FileNotFoundError:
    #     pass
